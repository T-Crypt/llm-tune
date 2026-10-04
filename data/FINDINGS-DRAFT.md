# Findings draft (flight 1)

The most generalisable lessons from the evidence inventory. Each line is one lesson plus its source (repo-relative path in the homelab repo). Anything inferred rather than measured is marked "(inferred)". These support the quality-aware angle: fit is necessary but not sufficient — recall at depth, tool-call reliability, and verifier-backed quality decide the tuning.

1. VRAM fit must budget KV cache + compute buffers + mmproj + draft context, not just the model file. — `state/evals/2026-09-25/gain-research.md`
2. MTP tensors cost a flat +0.42 GiB per quant (~the next quant tier up), and the MTP draft context is a separate allocation that can OOM even when the target model fits. — `state/evals/2026-09-25/gain-research.md`, `state/evals/2026-09-26/r6-vram/`
3. KV cache cost depends on architecture: only full-attention layers grow KV; hybrid (Mamba/DeltaNet) layers hold fixed state, so long context can stay cheap. (derived math, flagged in source) — `state/evals/2026-09-25/gain-research.md`, `state/evals/2026-09-25/nemotron-research.md`
4. The context/quant trade is the actual lever: every 32k of ctx is worth ~1.06 GiB of KV at q8_0, so dropping ctx buys a quant tier. (inferred arithmetic, confirmed by one measurement) — `state/evals/2026-09-25/gain-research.md`
5. Load-time fit is not runtime fit: a model that loads fine can OOM mid-inference as buffers grow with depth. — `state/evals/2026-09-30/r9-27b-context/`
6. KV quantization is a real lever: q4_0 KV beat int8 at 262k on every measured axis (decode, speed, RAM headroom) with recall held. — `state/evals/2026-10-03/strata-ctx/RESULTS.md`
7. Declared context is not usable context — verify recall at depth; requests beyond the window fail with 400 or need explicit clip behaviour. — `state/evals/2026-09-26/r7-longctx/`, `state/changes.md` (2026-10-03, fit_max_tokens)
8. Sparse-attention engines keep decode-at-depth within ~10% of shallow decode; the cost is memory, not attention quality. — `state/evals/2026-10-03/strata-ctx/RESULTS.md`
9. Engine defaults are hardware-class dependent: a prefill chunk setting that gained +21% on a 128 GB RAM box cost ~3x on a 31 GB box. — `state/evals/2026-10-03/strata-ctx/RESULTS.md` (correction section)
10. Verify a "faster mode" with a quality metric held constant: int8 prefill activations gave +70% prefill with perplexity identical to 4 decimals, and task-harness scores within noise. — `state/evals/2026-10-03/ninfer-int8-prefill/`, `state/evals/2026-10-03/r13-ninfer-int8/`
11. The optimal speculative depth is workload-dependent (d3 best overall, d5 best prose, d3 best code); the LM-head draft is worth ~12 t/s. — `state/evals/2026-10-03/ninfer-sweep1/`
12. MTP only changes speed — the target sampler picks every token; do not blame MTP for quality problems. — `projects/active/MODEL-ROLES-2026-09-25.md`
13. Log token acceptance and have a documented fallback: below ~50% acceptance, regular quants run faster than MTP. — `state/evals/2026-09-25/gain-research.md`, `runbooks/llama-swap.md` (bench gate ≥ 0.4)
14. Unbounded reasoning budget (-1) causes 20k-token thinking loops with no output; cap it per role. — `projects/active/MODEL-ROLES-2026-09-25.md`, `state/evals/2026-09-25/registry-audit-prompt.md`
15. `reasoning_effort=medium` is a silent mode that injects nothing; only the default (xhigh) injects reasoning instructions, and an invalid value hard-fails template render. — `state/evals/2026-09-25/gain-research.md`
16. Thinking-off makes Qwen-class models skip the tool call — no agent role should run thinking-off except a pure-speed role. — `projects/active/MODEL-ROLES-2026-09-25.md`
17. Harness/parser tolerance is a tunable: tolerant tool-call parsing turned 5/16 failures into 0/16 without touching the model. — `state/evals/2026-10-03/ninfer-toolcall/`
18. Single-turn evals can score 24/24 while the same model fails a real multi-turn build — evaluate multi-turn, and use two tiers: a quick proxy for iteration, program-verifier tasks for promotion. — `projects/active/MODEL-ROLES-2026-09-25.md`, `runbooks/model-eval.md`
19. Run-to-run quality variance is ±1–2 bugs on a 12-bug test — repeat runs before any tuning call; alternating-arm A/B controls drift. — `state/evals/2026-09-26/r7-longctx/`, `state/evals/2026-10-03/r13-ninfer-int8/`, `state/evals/2026-10-03/strata-pr646/`
20. Windows silently spills VRAM overflow into system RAM; "Prefer No Sysmem Fallback" makes large models fail loudly instead of hanging, and Windows decodes 10–20% slower than Linux on the same card. — `runbooks/llama-swap.md`
21. Ubatch gains are architecture-dependent: `-ub 1024` gave +31–34% prefill on MoE entries but no measurable gain on the dense 27B. — `state/evals/2026-09-25/registry-audit-prompt.md`, `state/evals/2026-09-26/r7-longctx/`
22. Auto-fit and manual offload are mutually exclusive: `common_fit_params` aborts when `-ngl` is already set by the user. — `state/evals/2026-09-26/r6-vram/` (side log), `state/evals/2026-09-30/swe-iq4-196k/`
23. A flag default can differ from deployed behaviour: `--prefill-activations` defaults to a16 while the running binary prefilled int8 — a rebuild without the flag loses ~40% prefill. — `state/changes.md` (2026-10-03 21:10)
24. Flag names and semantics change between builds (`--draft-max` removed → `--spec-draft-n-max`); pin runtime versions because MTP compatibility depends on exact builder/commit. — `state/evals/2026-09-25/registry-audit-prompt.md`, `runbooks/llama-swap.md`
25. Other processes holding VRAM are the bug — an embedding daemon kept 11.3 GiB after its job ended; unloading the model server is not enough, audit the whole box. — `state/incidents.md` (2026-09-23)
26. Freeing the desktop compositor to the iGPU is a real tuning lever on a shared card. — `state/changes.md` (2026-09-26 evening), `state/evals/2026-09-26/r6-vram/`
27. Host RAM is a first-class budget on expert-cache engines (28 GB peak observed; zram at the wall at 512k), and heavy parallel builds next to a resident engine can OOM-freeze the box. — `state/evals/2026-10-02/r11-strata-iq2xs/`, `state/incidents.md` (2026-10-03)
28. Harness context caps must match the served window: a hardcoded 262144 in the client overfills a 131k server. — `projects/active/MODEL-ROLES-2026-09-25.md`, `state/changes.md` (2026-10-03)
29. Publish corrections: three overstated VRAM figures were re-measured, and a withdrawn finding was kept as a dated correction rather than deleted. — `state/changes.md` (2026-09-30), `state/evals/2026-10-03/strata-ctx/RESULTS.md`
30. Quality-per-second, not raw quality, should drive role choice — a blind-ranking tie was broken by 69 s vs 280 s at equal quality. — `state/evals/2026-09-25/think-ranking.md`
