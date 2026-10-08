# Evidence inventory (flight 1)

Catalogue of the source measurements behind llm-tune. Sources are in the homelab repo, cited repo-relative. Hardware described generically (RTX 4090 24 GB class, 64 GB RAM host). Tags: **FINDING** (generalisable lesson), **DATA** (raw measurements worth tabulating), **LOCAL-ONLY** (specific to the source lab, skip).

Note: the evals tree is ~18 MB, not the ~7 MB stated in the brief; large .log/.jsonl files were skimmed with head/tail/grep, not read whole.

---

## state/evals/2026-09-25

### state/evals/2026-09-25/gain-research.md — quant naming, VRAM fit math, samplers, MTP, reasoning modes
- **Measured:** exact GGUF file sizes (HF tree), one real peak-VRAM measurement (21.5 GiB for a 13.5 GiB IQ3_M MTP run with mmproj at 131k ctx), derived KV-cache math, sampler specs from model cards.
- **Method:** research log with explicit UNVERIFIED flags; single-measurement calibration of fixed non-file VRAM overhead (~7.97 GiB total at 131k: 0.87 mmproj + 4.25 KV + 2.85 CUDA/compute/GDN residual).
- **Headline numbers:** MTP tensors cost a flat +0.42 GiB per quant (≈ the price of the next quant tier up); KV at q8_0 ≈ 0.033 GiB per 1k tokens; only 16 of 64 layers carry a growing KV (Gated DeltaNet layers hold fixed state); IQ4_XS-MTP estimated 23.83/24.00 GiB — does not fit in practice; dropping ctx 131k→65k buys a full quant tier (IQ3_M→Q4_K_M).
- **Findings:** quant fit must budget KV + compute buffer + mmproj, not just the file; the context/quant trade is the actual lever; vendor sampler spec (thinking mode temp 1.0/top_p 0.95/top_k 20/min_p 0) beats generic house-style numbers; MTP: keep temp ≤ 1.0, rep_pen exactly 1.0, abandon MTP if token acceptance < 50%; `reasoning_effort=medium` injects *nothing* (silent mode, trap); unbounded reasoning budget (-1) caused 20K-token thinking loops; `--jinja` is required for template-driven reasoning kwargs to work at all.
- **Tag:** FINDING (strongest source in the tree) + DATA (fit table).

### state/evals/2026-09-25/think-ranking.md — blind ranking of five models on an open reasoning question
- **Measured:** 5 models (Nemotron-Cascade-2-Reasoning, Qwen3.6-Stock, Qwen3.8-27B-Q4-Quality, GAIN IQ3_M, Whittle-MoE) scored 1–10 on specificity/correctness/actionability/prioritisation/concision.
- **Method:** anonymous lettered answers, human/Claude read, reasoning block excluded from scoring; caveat that a 1-point gap is noise.
- **Headline numbers:** 41/40/32/23/17 out of 50; GAIN IQ3_M answered in 69 s vs 280 s for the 27B at comparable quality.
- **Findings:** quality-per-second, not raw quality, should drive role choice; blind ranking is the verification method for quality claims; a model that fabricates a measurement (invented baseline %) is penalised — quality-aware tuning needs falsifiable criteria.
- **Tag:** FINDING (methodology) + DATA (score table).

### state/evals/2026-09-25/full.log and r2.log — tool-call bakeoff (Windows run, then rerun with caps)
- **Measured:** per model: load time, peak VRAM, decode t/s, MTP draft acceptance, tool-call behaviour, planted-bug review score (8 then 12 bugs), finish_reason.
- **Method:** bakeoff.py — entries from the llama-swap config expanded and run against a side llama-server, one model on the GPU at a time; single-turn dashboard build via `write_file` tool call, then a code review scored by keyword match.
- **Headline numbers:** MoE 35B A3B quants decode 246–287 t/s vs dense 27B ~100 t/s; load 34–244 s; peak VRAM 20.3–23.6 GiB on the 24 GB card; several models hit `finish=length` (budget truncation) and scored 0/8 while tool-calling models scored 7/8; r2 with configured caps lifted scores to 10–11/12.
- **Findings:** single-turn scores mislead for agent roles — the harness fix (turn-2 handling, caps) changed results; decode speed is architecture-bound (MoE vs dense), not quant-bound; review-quality and generation-quality are separable measurements.
- **Tag:** DATA (tabulate) + FINDING (harness behaviour traps).

### state/evals/2026-09-25/r3, r4, r5, r5clean — follow-up rounds
- **Measured:** r3: 27B research configs (temp 1.0, budget 4096, -ub 1024, draft n-max 4) — 12/12 review, draft acc 21110/29420; r4: IQ4 vs IQ3_XXS on the same task; r5/r5clean (Arch rerun): Nemotron Lightning 3.5 vs IQ4 vs IQ4 with NVIDIA sampler (top-k 0), TielCoder Q3 vs IQ4, GAIN IQ3 vs IQ4 at temp 1.0, plus host RAM peak (5.7–7.1 GB).
- **Method:** same bakeoff harness; r5clean added host RAM measurement and per-round entry variants.
- **Headline numbers:** Lightning MoE 298–363 t/s decode; IQ4 vs IQ3_XXS both scored 11/12 (quant tier did not change review score on this task); NVIDIA-sampler variant scored same as vendor-spec variant (7/12); one entry failed to load (exit 3221225794) on Windows.
- **Findings:** sampler changes (top-k 0 vs 20) showed no measurable quality delta on this task — A/B before adopting card advice; quant tier gains show in output size/richness, not always in correctness score; cross-OS reruns change load time dramatically (10–14 s vs 80–240 s).
- **Tag:** DATA + FINDING (weak-result caution).

### state/evals/2026-09-25/nemotron-research.md — MoE/Mamba architecture notes
- **Measured:** layer breakdown (6 attention + 23 Mamba + 23 MoE), KV + state cost at 262k ctx (~1.50 GiB + 46 MiB), official quant sizes.
- **Method:** source-code reading + model card, flagged as inferred-not-run.
- **Headline numbers:** hybrid-attention models keep long context cheap; MTP heads shared with target (no separate draft file).
- **Findings:** KV budget math depends on how many layers actually carry a KV cache — hybrid architectures break the naive "full attention" assumption; llama.cpp flag names change between versions (`--draft-max` removed → `--spec-draft-n-max`).
- **Tag:** FINDING.

### state/evals/2026-09-25/registry-audit-prompt.md — audit brief with verified runtime facts
- **Measured:** not a measurement itself, but records verified facts: `-ub 1024` gave +31–34% prefill in A/B; `--reasoning-budget -1` caused 20K-token loops; `${common}` = `-fa on -ctk q8_0 -ctv q8_0 --parallel 1`; b11115 flag changes.
- **Method:** audit prompt comparing config entries against model cards and a hardware registry; output format = setting/ours/recommended/source/verdict table + top-10 changes ranked by expected impact; explicit rule: never invent numbers, mark unsourced UNVERIFIED; SGLang/vLLM/ExLlama recipes do not transfer to llama.cpp.
- **Findings:** the audit method itself is a template for the skill's decision procedure; cross-engine flag advice does not transfer.
- **Tag:** FINDING (methodology) + DATA (verified facts list).

### state/evals/2026-09-25 harness scripts (bakeoff.py, review_eval.py, review2.py, score.py, think.py, loop_repro.py)
- **Measured:** the harness definitions: side-server bakeoff, planted-bug review scoring, HTML/CSS structural scoring, open-question think test, tool-call write-loop reproduction.
- **Method:** loop_repro.py reproduces an agent write-loop and shows where file content gets mangled — a harness-behaviour failure mode.
- **Findings:** verification needs both structural scoring (did the file parse/close) and semantic scoring (planted bugs found); tool-call reliability is a tunable dimension separate from model quality.
- **Tag:** FINDING (methodology).

### state/evals/2026-09-25/review2/*.md, think/*.md, results JSON
- **Measured:** per-model outputs for the blind ranking and planted-bug review; results JSON has pass/fail per task category (lookup, tool-call) with turns and seconds.
- **Method:** outputs saved for human read; JSON results scored by exact match / first-call correctness.
- **Findings:** role assignment by short single-turn evals failed a real multi-turn build — the central motivation for quality-aware, multi-turn evaluation.
- **Tag:** DATA + FINDING.

---

## state/evals/2026-09-26

### state/evals/2026-09-26/r6-vram — VRAM headroom sweep, 14 entries at 262k ctx
- **Measured:** per entry load time, peak VRAM, host RAM peak, decode t/s, draft acceptance, planted-bug review (12 bugs); run happened after the desktop compositor was moved off the GPU to the iGPU, freeing headroom.
- **Method:** bakeoff harness (same as 09-25), results.jsonl per run; config.yaml shows the exact flags tested (`-fa on -ctk q8_0 -ctv q8_0 --parallel 1` common macro, `-ub 512` vs `-ub 1024`, `--spec-draft-n-max 4`, `--chat-template-file` jinja overrides).
- **Headline numbers:** 262k-ctx MoE quants fit in 24 GB with 19.2–23.7 GiB peak and decode 173–324 t/s; dense 27B at 131k peaked 23.5 GiB and decoded ~108 t/s; Quality-163K **failed to load** — OOM allocating the MTP draft context; review scores 9–12/12 for most, Ornith-CoderX 2/12 (finish=length truncation).
- **Findings:** the MTP draft context is a separate VRAM allocation that can OOM even when the target model fits — budget it explicitly; `common_fit_params` aborts when the user has already set `-ngl`, so llama.cpp's auto-fit and a fixed `-ngl 99` are mutually exclusive (a trap for anyone mixing `--fit` with manual offload); moving the desktop to the iGPU is a real tuning lever on a shared card; `--reasoning-budget -1` was still present in several entries and is the known loop trap.
- **Tag:** DATA (tabulate) + FINDING (OOM/fit traps).

### state/evals/2026-09-26/r7-longctx — needle-at-depth recall
- **Measured:** needle recall at 60k/120k/200k prompt sizes (3 needles each), prefill t/s at depth, peak VRAM.
- **Method:** needle-in-haystack probe against the same entries; results.jsonl.
- **Headline numbers:** TielCoder-262K and AgentFast-262K 9/9 at all depths; prefill t/s falls with depth (6498→3981 MoE, 2279→1852 dense); Quality-131K scored 3/6 because the 120k prompt returned HTTP 400 — prompt exceeded declared ctx; ub512 vs ub1024 made no recall difference.
- **Findings:** declared context size is not usable context — recall and request limits must be verified at depth, not assumed; quality-aware tuning needs a depth-recall metric, which this round is exactly; prefill cost grows with depth even when recall holds.
- **Tag:** FINDING (core to the quality-aware angle) + DATA.

### state/evals/2026-09-26/r7b-27b-longctx — dense 27B needle control
- **Measured:** needle 6/6 for Quality-131K and GAIN-163K at 60k/120k.
- **Method:** same needle harness, smaller prompt ladder.
- **Headline numbers:** dense models recall fine within their declared ctx; the r7 failure was the ctx ceiling, not recall.
- **Findings:** separates "model can't recall at depth" from "harness sent more tokens than ctx" — verification must distinguish the two.
- **Tag:** FINDING + DATA.

### state/evals/2026-09-26 fleet-tidy reruns (in r7.log)
- **Measured:** three repeat runs of Genesis-Hermes (10/9/10 out of 12), Occult-Nail (9/10/8), Ornith-CoderX (8/12 after 2/12).
- **Method:** same harness, repeated entries.
- **Findings:** run-to-run review variance is ±1–2 bugs on a 12-bug test — single-run scores are noise; the skill should require repeat runs before a tuning call.
- **Tag:** FINDING.

---

## state/evals/2026-09-30

### state/evals/2026-09-30/r8-rebench — re-bench at registered context
- **Measured:** four role models at their registered ctx: load, peak VRAM, host RAM, decode t/s, draft acceptance, 12-bug review.
- **Method:** same bakeoff harness.
- **Headline numbers:** MoE ~263–275 t/s vs dense 76–111 t/s; GAIN IQ3_M took 413 s on turn 1 (thinking-heavy) yet scored 9/12; CyberTiel-IQ4 12/12.
- **Findings:** thinking-heavy roles trade wall-clock for depth; quality scores at registered ctx are stable across quants on the same family — quant choice is a VRAM/speed decision, not a quality one, on this task class.
- **Tag:** DATA.

### state/evals/2026-09-30/r9-27b-context — context ladder + KV-quant + MTP on/off
- **Measured:** one quant (Q4_K_XL and IQ4_XS of the same 27B) at ctx 131k/144k/152k/163k/196k/229k/262k, with q8_0 vs q4_0 KV, MTP on vs noMTP, ub 512 vs 256; needle recall at each step.
- **Method:** needle-at-depth harness (r7 lineage), side llama-server per entry.
- **Headline numbers:** IQ4_XS fits 262k only with q4_0 KV (21.65 GiB) or with noMTP (23.44 GiB at q8 KV); IQ4_XS at 229k with q8 KV + MTP OOM'd on compute-buffer reserve; Q4_K_XL OOM'd **during inference** at 152k (peak 24142 MiB on a ~24.5 GB card) after loading fine at 131k; every entry that loaded scored 6/6 or 9/9 needle recall.
- **Findings:** load-time fit is not runtime fit — compute buffers grow with ubatch and depth, so a model that loads can die mid-run; KV quant is a real lever worth ~1.8 GiB at 262k; MTP is a VRAM cost (draft context) that can be traded for context; recall does not degrade with ctx on these models — the binding constraint is memory, not attention quality.
- **Tag:** FINDING (strong) + DATA.

### state/evals/2026-09-30/r10-27b-decode — quality vs speed at the context ceiling
- **Measured:** decode t/s and 12-bug review for the same ladder winners.
- **Method:** bakeoff harness.
- **Headline numbers:** noMTP at 262k decodes 52 t/s vs 119 t/s with MTP+q4 KV, but review scores stay 11–12/12; the 52 t/s run took 539 s on turn 1.
- **Findings:** the MTP/KV trade costs speed, not quality — choose by workload latency budget; a quality-aware tuner should report both t/s and quality score, since they decouple.
- **Tag:** FINDING + DATA.

### state/evals/2026-09-30/swe-iq4-196k — single SWE-style task attempt
- **Measured:** one agentic coding task (deepswe subset) against the 27B IQ4 at 196k; three errored attempts (rc 130/137) then a scored run: 0/1 pass, partial 0.98 (f2p 40/43, p2p 109/109).
- **Method:** external SWE runner via llama-swap; results.jsonl.
- **Findings:** agentic harness stability is itself a failure mode worth measuring (interrupted runs before a clean one); partial-credit scoring shows near-miss quality that pass/fail hides — supports the quality-aware metric angle.
- **Tag:** DATA + FINDING (methodology); the specific task result is LOCAL-ONLY.

---

## state/evals/2026-10-02

### state/evals/2026-10-02/r11-strata-iq2xs — Strata engine at IQ2_XS
- **Measured:** peak VRAM 23966 MiB, host RAM peak ~28 GB, decode 148–156 t/s, planted-bug review, tool-call behaviour, prefix cache hit.
- **Method:** bakeoff harness against a Strata engine entry; the entry config records the flags: `--spec 4 --spec-min-p 0.5 --kv int8 --resident-experts`, split GGUF with a separate PLE (per-layer expert) file, auto expert cache and prefill.
- **Headline numbers:** an IQ2_XS quant — normally a quality red line — scored 11/12 on the bug review with Strata's expert residency; but the second run scored 0/12 because the model never made the tool call and hit `finish=length` at 32k tokens.
- **Findings:** extreme low quants can be quality-acceptable on engines that keep experts resident and use int8 KV, but tool-call reliability is the fragile part — a single no-tool-call run turns a good model into a zero; host RAM becomes a real budget on expert-cache engines (28 GB peak); prefix caching changes results and must be controlled in A/B tests.
- **Tag:** FINDING + DATA.

### state/evals/2026-10-02/r12-ninfer — NInfer engine vs llama.cpp on the same model
- **Measured:** NInfer (groupwise-int 27B): load 37 s, peak VRAM 23136 MiB, host RAM 15.3 GB, decode 130 t/s, draft acc 16025/23028, review 10/12; llama.cpp Q4_K_XL control at 196k: decode 118 t/s, review 11/12.
- **Method:** same bakeoff harness; NInfer side log shows its memory accounting in detail — weights 16.9 GiB, pinned host KV 8 GiB, runtime reservation 5.7 GB, `kv_headroom_bytes=0` (zero headroom at 262k), CUDA graph allowance 90 MB.
- **Headline numbers:** first Q4-Quality attempt failed to load (fit-params abort with user-set `-ngl 99`, same trap as r6); NInfer's first request decoded at 95 t/s before settling to 130.
- **Findings:** engines that pin host KV/state trade VRAM for host RAM — the VRAM-fit arithmetic changes shape per engine; an engine reporting zero KV headroom is one request away from failure; the `--fit`/`-ngl` conflict recurs across engines and rounds, so it belongs in the Traps section.
- **Tag:** FINDING + DATA.

### state/evals/2026-10-02/strata-5070ti-buddybox-62tps.png
- **Measured:** benchmark screenshot — Strata decode on an RTX 5070 Ti (16 GB class), 62 t/s.
- **Tag:** DATA (single datapoint for the smaller-card tier); image not machine-readable here, so recorded as a pointer only.

---

## state/evals/2026-10-03

### state/evals/2026-10-03/ninfer-int8-prefill — int8 prefill vs a16, with perplexity control
- **Measured:** prefill t/s at 8k/32k/65k prompts for a16 and int8 modes plus a llama.cpp Q4 control (3 runs each), and a 1M-token multi-domain perplexity run for both modes.
- **Method:** fixed-corpus prefill benchmark + PPL harness (corpus, context/stride 4096/2048).
- **Headline numbers:** int8 prefill +70% over a16 (3737 vs 2194 t/s at 8k) and +34% over llama.cpp q4; PPL identical to 4 decimal places (4.651185 vs 4.651710) — the speed is free.
- **Findings:** the right verification for a "faster mode" is a quality metric held constant (PPL), not just t/s; llama.cpp's own prefill sits between the two engine modes — engine choice changes prefill more than quant does.
- **Tag:** FINDING (strong, core to the quality-aware angle) + DATA.

### state/evals/2026-10-03/ninfer-sweep1 — speculative draft-token sweep by workload
- **Measured:** decode t/s for draft-tokens 2/3/4/5 with and without `--lm-head-draft`, split by workload (code/agent/prose), 3 runs each.
- **Method:** NInfer sweep harness, same build, flag swapped per arm.
- **Headline numbers:** d3+lm-head-draft best overall mean (107.9); d5 wins prose (140 t/s) but loses code (86.3); d3 without lm-head-draft drops to 96.1 — the LM-head draft is worth ~12 t/s.
- **Findings:** the optimal speculative depth is workload-dependent, not a global max — a quality-aware tuner should sweep per workload, not per model; single-flag A/B with 3-run medians is the right shape.
- **Tag:** FINDING + DATA.

### state/evals/2026-10-03/ninfer-toolcall — strict vs tolerant tool-call parsing
- **Measured:** 8 tool-call tasks x 2 rounds under strict parsing, then under `--tolerant-tool-calls`.
- **Method:** tool-call stress script against the same engine build; requests logged to JSONL.
- **Headline numbers:** strict 5/16 failed (model emitted XML-style tags, harness fell back to plain content); tolerant 0/16.
- **Findings:** harness/parser tolerance is a tunable that changes agent reliability without touching the model — belongs in the skill's harness-settings section; measure tool-call success separately from generation quality.
- **Tag:** FINDING (strong) + DATA.

### state/evals/2026-10-03/r13-ninfer-int8 — int8 vs a16 on the quality harness, with repeats
- **Measured:** bakeoff run per mode plus a 5-run planted-bug review repeat for each.
- **Method:** same bakeoff harness; review-repeat script.
- **Headline numbers:** int8 decode 121 t/s, a16 129 t/s; review means over 5 runs 11.0 (int8) vs 10.8 (a16) — within noise; single-run scores ranged 9–12.
- **Findings:** confirms the PPL result on the task harness — int8 prefill costs nothing in quality; repeats are mandatory because single-run review scores swing ±2.
- **Tag:** FINDING + DATA.

### state/evals/2026-10-03/strata-ctx — context sweep with KV quant, KV streaming, YaRN, and a published correction
- **Measured:** five variants (131K int8, 262K int8, 262K q4_0, q4_0 streamed, 512K q4_0 YaRN 2) — GPU expert slots, pinned experts, RAM headroom, short decode, prefill and decode-at-depth, needle recall at 32k/120k/240k/480k.
- **Method:** ctx_sweep harness, one variant at a time, llama-swap stopped; synthetic log haystacks with a planted number.
- **Headline numbers:** q4_0 KV beat int8 at 262K on every axis (decode 116.4 vs 112.6, +1.1 GiB RAM headroom, recall held); `--prefill auto:32768` cut long-prompt reading 2.7–3.4x on a 31 GB RAM box — the opposite of upstream's +21% on a 128 GB 5090; 512K works but leaves ~2.3 GiB RAM with zram full.
- **Findings:** engine defaults are hardware-class dependent — a flag that helps on a big-RAM box can cost 3x on a small one; sparse-attention engines make deep context cheap in decode but expensive in VRAM/RAM; a mid-run measurement collision (another model loaded) produced false failures — measurement discipline (one model on the GPU) is part of the method; corrections published back to upstream show single-run claims being re-tested.
- **Tag:** FINDING (strong) + DATA.

### state/evals/2026-10-03/strata-512k-live — live check of the 512K config
- **Measured:** recall at 32k/119k/238k/477k, prefill and decode-at-depth, follow-up stability, RAM minimum, zram peak.
- **Method:** check.py harness, greedy, thinking off.
- **Headline numbers:** recall yes at all depths; decode at depth 111–131 t/s; verdict: usable for one-off huge documents, 262K stays the daily default.
- **Findings:** "fits" is not "usable" — the daily config is chosen by RAM headroom and stability, not by maximum window.
- **Tag:** FINDING + DATA.

### state/evals/2026-10-03/strata-k8v4 — K8/V4 KV experiment (data summarized in strata-ctx correction)
- **Measured:** k8v4 streamed vs in-VRAM vs q4_0 — short decode, prefill/decode at depth, RAM.
- **Method:** same sweep harness, fork feature branch.
- **Headline numbers:** k8v4 streamed short decode 126.2 vs 117.7 in-VRAM; RAM headroom tighter (1.59–1.69 GiB).
- **Findings:** mixed KV quantization trades VRAM for RAM headroom; no quality metric was run here — recall only, so it stays DATA not FINDING.
- **Tag:** DATA.

### state/evals/2026-10-03/strata-pr646 — engine-version A/B, alternating arms
- **Measured:** main vs PR #646 on the live config, 2 rounds each, prefill/decode-at-depth/recall.
- **Method:** alternating-arm A/B script, same server, engine-only change.
- **Headline numbers:** PR #646 lifts decode-at-depth (~112–134 vs ~103–115 t/s) and short decode (~122 vs ~116–117); prefill unchanged; recall held.
- **Findings:** engine version is a tuning variable worth its own A/B; alternating arms control for drift.
- **Tag:** FINDING (methodology) + DATA.

### state/evals/2026-10-03/strata-iq2xs-speculum
- **What it is:** a simulated runtime-monitor dashboard (UI project), not a measurement.
- **Tag:** LOCAL-ONLY.

---

## runbooks

### runbooks/model-eval.md — the evaluation method itself
- **Measured:** not measurements; the standard procedure since 2026-09-26.
- **Method/harness:** two tiers — quick (`bakeoff.py`: build + 12-bug review + needle; a proxy that can pass a model that fails real work) and confidence (DeepSWE fixed 6-task subset at seed 0, program verifiers); promote configs on the confidence tier only; fixed subset + seed must never be re-sampled; needle = three facts at 10/50/90% depth; measurement discipline: one bench at a time, lock file, refuse to start while any llama-server is up, nothing else may use the GPU during a run (a run was spoiled by a background session loading a model); grader-discrimination gate before any eval run.
- **Findings:** the two-tier structure (fast proxy for iteration, real-task verifiers for promotion) is the skeleton of the skill's Verification section; publishing only redacted buckets with a redaction gate is how shared evidence stays privacy-safe.
- **Tag:** FINDING (methodology).

### runbooks/llama-swap.md — operating the serving stack
- **Measured:** bench gate facts: proc VRAM budget ~22,900 MiB with desktop resident, draft acceptance ≥ 0.4 whenever a draft is used; Windows decodes 10–20% slower than Arch on the same card.
- **Findings:** NVIDIA "Sysmem Fallback Policy = Prefer No Sysmem Fallback" — Windows silently spills VRAM overflow into system RAM making large models slow/hang; failing loudly is better than spilling; MTP compatibility depends on exact builder/commit (pin runtimes, don't mix builds); truncated GGUF downloads break embedded MTP; role aliases keep client names stable when quants change; refusal behaviour is an eval category and a model that echoes a planted secret loses its role; every model load evicts whatever is resident (single-GPU discipline).
- **Tag:** FINDING (traps) + LOCAL-ONLY (dual-boot, consumers, systemd specifics).

---

## reference

### reference/llama-swap/config.yaml — the live tuning decisions
- **Measured:** the flag set actually shipped: `${common}` = `-fa on -ctk q8_0 -ctv q8_0 --parallel 1`; 17 entries at `-ub 1024`, 7 at `-ub 512`, 1 at `-ub 2048`; `--n-cpu-moe` on 3 entries as headroom lever; per-entry samplers and reasoning budgets.
- **Findings:** the config header records the causal notes (budget, sysmem fallback, why apply-when-idle exists — a reload kills running models); note the live config still carries `--reasoning-budget -1` on 10 entries while the eval rule says never recommend -1 — an inconsistency worth flagging in Traps.
- **Tag:** DATA (flag census) + FINDING (inconsistency).

### reference/engines.yaml — non-llama.cpp engines in the roster
- **Measured:** Strata entry with its engine flags (`--spec 4 --spec-min-p 0.5 --kv int8/q4_0 --resident-experts --expert-cache auto --prefill auto`, split GGUF + PLE file); context changed 131K→262K based on the strata-ctx sweep.
- **Tag:** DATA (engine flag vocabulary for the Engine notes section).

---

## projects/active/MODEL-ROLES-2026-09-25.md — the roles rework, root causes

- **Measured:** root causes of agent "loops", measured on 2026-09-25: unlimited reasoning budget (20k thinking, no output); bad weights (a model that wrote 1 CSS rule and rewrote forever); VRAM spill when browser/desktop take ~2 GB against ~800 MiB headroom; MTP ruled out (target sampler picks every token — MTP only changes speed); tool parsing/template round-trip ruled out byte-for-byte; thinking OFF makes Qwen skip the tool call — so no role should run thinking-off except the fast role; short single-turn evals passed 24/24 while the real multi-turn build failed.
- **Findings:** the founding story of llm-tune — quality-aware, multi-turn evaluation catches what single-turn benchmarks miss; "fits" vs "usable" (headroom for the desktop/browser); harness bugs masquerade as model bugs (turn-2 max_tokens below the reasoning budget); an invalid round (stacked servers, memory pressure) was quarantined rather than quietly reused — report invalid data as invalid.
- **Tag:** FINDING (strongest narrative source).

---

## state/incidents.md and state/changes.md — relevant entries (date + heading)

Incidents:
- 2026-10-03 — CUDA build next to a resident Strata exhausted RAM (rule: no `-j > 4` builds while an engine is resident; check MemAvailable). FINDING.
- 2026-09-23 — an embedding daemon held 11.3 GiB of VRAM after its job ended; llama-swap could not load (rule: unloading llama-swap is not enough — audit other processes holding VRAM). FINDING.
- 2026-09-18 — container OOM at a 2 GB cap. LOCAL-ONLY.

Changes (model-tuning-relevant headings):
- 2026-10-03 21:10 — NInfer PR #15: `--prefill-activations` defaults to a16 while the deployed binary prefilled int8; rebuild without the flag loses ~40% prefill. FINDING (default-flag trap).
- 2026-10-03 20:10 — Strata prefill finding (`auto:32768` ~3x slower on a 31 GB box, opposite of upstream on a 128 GB box). FINDING.
- 2026-10-03 18:40 — Strata PR #646 A/B live; acceptance identical, decode-at-depth improved. DATA.
- 2026-10-03 17:45 — Strata 262K q4_0 chosen from the measured sweep; `fit_max_tokens` clip-vs-400 behaviour. FINDING.
- 2026-10-03 22:21 — Strata shard trap: hard-linked shards, deleting one freed only half; check link count before deleting. FINDING.
- 2026-10-03 — NInfer INT8 prefill +29–34% over llama.cpp; draft-token sweep found production flags already best; tolerant tool calls 5/16→0/16; thinking-effort value sets differ per engine (NInfer rejects some values). FINDING.
- 2026-10-02 — NInfer truncation in Pi: unbounded thinking + 16K cap interaction. FINDING (harness trap).
- 2026-09-30 — r8 re-bench: three earlier VRAM figures were overstated and corrected. FINDING (methodology: re-measure, publish corrections).
- 2026-09-26 evening — desktop moved to iGPU, card fully free for models. LOCAL-ONLY (but the lever is general).
- 2026-09-25 late night — round 5 clean re-run, losing quants deleted; prefill/decode visibility for agent traffic. DATA.
- 2026-09-23 evening — `-ub 1024` applied to 16 MoE entries (+31–34% prefill); sysmem fallback off. FINDING.
- 2026-09-22 — image-plane (ComfyUI) history on the same card. LOCAL-ONLY.

---

## External verification sources (cited in `references/`)

These are web sources verified live (2026-10-08) and cited in the new reference files. None are measurements from this repo; all are externally sourced and must be verified on the user's own hardware.

### Hardware tiers

- **Infralovers — 4 harnesses benchmark (2026-07-14):** same model across Pi, OpenCode, Claude Code, Copilot. "Friction and autonomy don't move together." Cited in `references/harnesses.md`. URL: https://www.infralovers.com/blog/2026-07-14-local-model-ai-coding-tools-benchmark/ — TAG: DATA (harness comparison data).
- **Intel Arc B580 best for local LLMs (PromptQuorum, 2026):** 12 GB VRAM, 7–14B Q4 quant fits. Cited in `references/hardware-tiers.md`, `references/intel-amd-unified.md`. URL: https://www.promptquorum.com/prompt-bites/best-intel-arc-gpu-local-llm — TAG: DATA.
- **Intel Arc SYCL guide (Intel developer, 2026):** Run LLMs on Intel GPUs using llama.cpp. Cited in `references/engine-backends.md`, `references/intel-amd-unified.md`. URL: https://www.intel.com/content/www/us/en/developer/articles/technical/run-llms-on-gpus-using-llama-cpp.html — TAG: DATA (backend info).
- **Intel Arc Pro B70 discussion (GitHub, 2026):** SYCL performance on B70. Cited in `references/intel-amd-unified.md`. URL: https://github.com/ggml-org/llama.cpp/discussions/27593 — TAG: DATA.
- **AMD Strix Halo guide (LocalAimaster, May 2026):** 128 GB unified, 96 GB GPU alloc, 256 GB/s, 70B Q4/Q8 fits, ROCm setup, BIOS allocation. Cited in `references/hardware-tiers.md`, `references/intel-amd-unified.md`, `references/llama-fit-broadening.md`. URL: https://localaimaster.com/blog/strix-halo-ai-max-395-guide — TAG: DATA.
- **Ryzen AI Max+ 395 specs (AMD Build 2026):** 128 GB unified LPDDR5X-8533, 131 TOPS. Cited in `references/hardware-tiers.md`. URL: https://www.amd.com/en/developer/resources/technical-articles/2026/amd-at-microsoft-build-2026.html — TAG: DATA.
- **Ryzen AI Max PRO 400 / Gorgon Halo (Tech Insider, Sep 2026):** 192 GB unified, 300B INT4, 160 GB VRAM alloc, 273 GB/s. Cited in `references/hardware-tiers.md`, `references/intel-amd-unified.md`. URL: https://tech-insider.org/amd-ryzen-ai-max-pro-400-192gb-unified-memory-2026/ — TAG: DATA.
- **192GB Framework Desktop (Medium, 2026):** 192GB mini PC GPU comparison. Cited in `references/intel-amd-unified.md`. URL: https://medium.com/@mayhemcode/the-new-192gb-mini-pcs-cost-nearly-twice-as-much-their-gpu-barely-changed-aab34807426a — TAG: DATA.
- **Mac local LLM buying guide (LLM Configurator, Sep 2026):** Mac mini M6 through M5 Ultra, 75% rule, bandwidth ladder, per-tier model fit. Cited in `references/hardware-tiers.md`, `references/mlx-mac-tuning.md`. URL: https://llmconfigurator.com/en/guides/mac-local-ai-buying-guide — TAG: DATA.
- **Mac Studio LLM guide (ModelFit, 2026):** M2 Ultra through M5 Ultra, model fit per RAM tier. Cited in `references/hardware-tiers.md`, `references/mlx-mac-tuning.md`. URL: https://modelfit.io/mac-studio/m2/ — TAG: DATA.
- **Apple Silicon LLM guide (canitrun.dev, 2026):** M1 to M6 complete, Ollama MLX default for >32 GB. Cited in `references/hardware-tiers.md`, `references/mlx-mac-tuning.md`. URL: https://canitrun.dev/guides/apple-silicon-llm-guide/ — TAG: DATA.
- **MLX-LM 2026 (PromptQuorum):** Apple's LLM toolkit, unified memory explanation. Cited in `references/hardware-tiers.md`. URL: https://www.promptquorum.com/power-local-llm/mlx-lm-explained — TAG: DATA.
- **M6 Mac mini local AI (ModelFit, 2026):** 16/24/32 GB tiers, bandwidth, what fits. Cited in `references/hardware-tiers.md`, `references/mlx-mac-tuning.md`. URL: https://modelfit.io/blog/m6-mac-mini-local-llm/ — TAG: DATA.
- **Mac mini 2026 Reddit (r/macmini):** 24→64 GB upgrade fits 6-bit at small context. Cited in `references/hardware-tiers.md`. URL: https://www.reddit.com/r/macmini/comments/1wo9de8/ — TAG: DATA.
- **RTX 5090 specs and VRAM requirements (ModelFit, 2026):** 32 GB GDDR7, 1792 GB/s, tier fits. "The RTX 5090 has 32GB GDDR7 VRAM with 1,792 GB/s bandwidth, the most of any consumer GPU. About 31GB is usable for models." Verified live 2026-10-08; replaces VRLA Tech source which returned 404. Cited in `references/hardware-tiers.md`. URL: https://modelfit.io/gpu/rtx-5090/ — TAG: DATA.
- **RTX 5090 multi-GPU strategies (Reddit r/LocalLLaMA, 2026):** 32 GB VRAM usage, dual 5090 setups. Cited in `references/hardware-tiers.md`. URL: https://www.reddit.com/r/LocalLLaMA/comments/1wbj1tk/ — TAG: DATA.

### Harness debloat

- **Atlassian mcp-compression (2026-03-29):** 94-tool GitHub MCP server compressed 17,600 → 500 tokens (97% reduction). Cited in `references/debloat.md`. URL: https://www.atlassian.com/blog/development/mcp-compression-preventing-tool-bloat-in-ai-agents — TAG: DATA.
- **Dev.to: MCP bloat hits local models harder (2026):** Cloud models absorb bloat; local models can't. Cited in `references/debloat.md`. URL: https://dev.to/shenao_yu_e15c14815264a44/mcp-tool-bloat-hits-local-models-harder-a-constraint-worth-talking-about-oon — TAG: DATA.

### Model management

- **HuggingFace Hub CLI docs:** pip install huggingface_hub, hf download, hf api. Cited in `references/model-management.md`. URL: https://huggingface.co/docs/huggingface_hub/en/guides/cli — TAG: DATA.
- **Unsloth Desktop docs:** model hub, connect harnesses to local models. Cited in `references/model-management.md`. URL: https://unsloth.ai/docs/desktop — TAG: DATA.

### vLLM

- **vLLM serve docs:** https://docs.vllm.ai/en/stable/cli/serve/ — TAG: DATA (command reference).
- **vLLM on DGX Spark (2026-06-01):** multi-node architecture, tensor parallel, sparkrun. Cited in `references/vllm-local.md`, `references/hardware-tiers.md`. URL: https://vllm.ai/blog/2026-06-01-vllm-dgx-spark — TAG: DATA.
- **NVIDIA DGX Spark vLLM:** https://build.nvidia.com/spark/vllm/multi-node — TAG: DATA.
- **MindStudio cluster guide:** RDMA clustering, tensor parallel. Cited in `references/vllm-local.md`. URL: https://www.mindstudio.ai/blog/how-to-cluster-dgx-spark-vllm — TAG: DATA.
- **vLLM production deployment (Spheron, 2026):** load balancing, FP8 quantization, multi-GPU. Cited in `references/vllm-local.md`, `references/hardware-tiers.md`. URL: https://www.spheron.network/blog/vllm-production-deployment-2026/ — TAG: DATA.
- **Multi-model serving (vLLM discussions #239):** multiple models per endpoint. Cited in `references/vllm-local.md`. URL: https://github.com/vllm-project/vllm/discussions/239 — TAG: DATA.

### llama-fit-params broadening

- **llama.cpp fit-params README:** https://github.com/ggml-org/llama.cpp/blob/master/tools/fit-params/README.md — TAG: DATA (tool documentation).
- **Reddit: llama-fit-params on Intel Arc:** https://www.reddit.com/r/LocalLLaMA/comments/1srvqar/ — TAG: DATA (confirms fit works on non-NVIDIA).
- **LM Studio bug tracker: llama_params_fit feature request:** https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1673 — TAG: DATA.
- **Local LLM optimization guide (carteakey.dev):** llama-fit-params description. Cited in `references/llama-fit-broadening.md`. URL: https://carteakey.dev/blog/local-inference/local-llm-optimization/ — TAG: DATA.
- **ROCm + llama.cpp (AMD blog):** https://rocm.blogs.amd.com/ecosystems-and-partners/llama-cpp/README.html — TAG: DATA.

### MLX

- **MLX docs (wired limit):** https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html — TAG: DATA (API reference).
- **headroom issue #13:** https://github.com/blaine-hiers/headroom/issues/13 — TAG: DATA (default fractions, 24 GB worked example).

### CUDA engine research for sm_89 (RTX 4090)

These are the 12 research dossier files at `../research/` (in the `ninfer-prep4qwen` repo), each covering a
CUDA inference engine or model with sm_89-specific findings. All researched 2026-10-06 through 2026-10-08
from public sources only (repos, docs, release notes, arXiv, model cards, community recipes) — no installs,
no weight downloads, no GPU jobs. Each entry below maps to which `skill/references/` file it feeds.

- **`../research/vllm.md` — vLLM 0.31.0 sm_89 specifics:** GDN Blackwell-only, open 4090 correctness/OOM issues,
  version churn (13 days, 717 commits), FlashInfer via Triton/FA on 4090 not FlashInfer. Feeds `references/engine-research-sm89.md` (vLLM section) and `references/engine-backends.md` (vLLM subsection). TAG: DATA.
- **`../research/tensorrt-llm.md` — TensorRT-LLM 1.3.0 sm_89 support matrix:** "Ada Lovelace (SM89) — FP32,
  FP16, BF16, FP8, INT8, INT4". Most complete precision stack of any engine for sm_89. PyTorch sole backend
  since 1.0. ModelOpt companion for FP8/NVFP4/INT8. Feeds `references/engine-research-sm89.md` (TensorRT-LLM
  section). TAG: DATA.
- **`../research/flashinfer.md` — FlashInfer 0.7.0 sm_89 kernel coverage:** Attention via FA2 yes on sm_89;
  every GDN/Gated-DeltaNet kernel, fast FMHA, FP4/FP8-MoE, XQA decode are Hopper/Blackwell-only. Adoption
  list: SGLang, vLLM, TensorRT-LLM, TGI, MLC-LLM, LightLLM, lorax, ScaleLLM. Feeds `references/engine-research-sm89.md`
  (FlashInfer section) and `references/engine-backends.md` (FlashInfer subsection). TAG: DATA.
- **`../research/sglang.md` — SGLang 0.5.21 sm_89 analysis:** CUDA 13 required (v0.5.20+), verified Qwen hybrid
  recipes are datacenter/Blackwell, RadixAttention, Unified Radix Cache. Feeds `references/engine-research-sm89.md`
  (SGLang section). TAG: DATA.
- **`../research/tokenspeed.md` — TokenSpeed 0.1.1 sm_89 CI status:** MIT license, day-0 Qwen3.8/GLM 5.3 flash
  recipes, but no CI on Ada/RTX consumer GPUs. Feeds `references/engine-research-sm89.md` (TokenSpeed section).
  TAG: DATA (track for future Ada CI).
- **`../research/eagle3-medusa-specforge.md` — EAGLE-3/Medusa/SpecForge drafters:** Draft-model speculative
  decoding alternatives to MTP on sm_89. EAGLE-3 (Peking U + MS Research), Medusa (dormant), SpecForge (LMSYS).
  Feeds `references/engine-research-sm89.md` (speculative alternatives section). TAG: DATA.
- **`../research/dflash-pard.md` — DFlash/PARD parallel draft:** Block-diffusion drafter (DFlash, Z Lab / UC San
  Diego) and target-independent parallel draft (PARD, AMD). Both shipped in TensorRT-LLM. ICLR 2026 for PARD.
  Feeds `references/engine-research-sm89.md` (speculative alternatives section). TAG: DATA.
- **`../research/ninfer-4090-udpsendtofailed.md` — NInfer 4090 community port (sm_89 native):** From-scratch
  C++20/CUDA engine specialized to RTX 4090 (sm_89, AD102, 128 SMs) running Qwen3.8-27B. Deleted 45+ Blackwell
  SM120/NVFP4 kernel files. Windows headline features (D3D12, DirectStorage) are Linux/Docker open issue. Feeds
  `references/engine-research-sm89.md` (NInfer 4090 section). TAG: DATA (community report, not measured here).
- **`../research/ninfer-windows-natpate.md` — NInfer Windows port (sm_120a, RTX 5090):** DFlash2 vs MTP
  comparison (~42% faster decode, community report, unverified). Feeds `references/engine-research-sm89.md`
  (NInfer Windows section) and Step 6 speculative guidance (flag as community report). TAG: DATA (unverified).
- **`../research/ktransformers.md` — KTransformers 0.7.1 sm_89 status:** CPU-GPU heterogeneous MoE framework.
  All Qwen support is MoE; no dense-model offload path. CPU kernels upstreamed into SGLang since Oct 2025.
  Feeds `references/engine-research-sm89.md` (KTransformers section). TAG: DATA (MoE only).
- **`../research/qwen38-flash-next.md` — Qwen3.8-Flash-Next architecture:** 125B MoE (6B active + 51B n-gram
  PLE + 4B MTP). Does not fit on sm_89 at any published precision (172.78 GiB FP8, ~60 GB in 4×3090). Feeds
  `references/engine-research-sm89.md` (Qwen3.8-Flash-Next section) and model management context. TAG: DATA.
- **`../research/qwen-official.md` — Qwen model vendor, architecture timeline:** Next dense Qwen prediction
  (~27-32B, GDN hybrid, MTP, 256K+, vision). Qwen3.8-Flash-Next custom license (qwen-community-1.0). Feeds
  `references/engine-research-sm89.md` (Qwen context) and model management guidance. TAG: DATA.

### Local model orchestration recipes (ai.ttindall.com, tested)

These are tested recipes from `https://ai.ttindall.com/recipes/` that implement the LOCAL.md pattern
described in `references/local-orchestration.md`. Each is a public, tested recipe with placeholders
for the operator's own paths and ports. All tested 2026-09-26 on a 1x RTX 4090 24 GB.

- **Claude Code on a local model through llama-swap:** Run Claude Code's agent loop against a model
  on your own GPU. llama.cpp `llama-server` does inference; llama-swap loads models on demand. Sets
  up the basic local-model-in-harness path. Cites in `references/local-orchestration.md`. URL:
  https://ai.ttindall.com/recipes/claude-code-llama-swap/ — TAG: DATA (setup pattern).
- **Local models as Claude Code subagents through a loopback router:** A loopback proxy between Claude
  Code and the API routes local role names to llama-swap while passing everything else to Anthropic.
  This is the harness mechanism that directs local model requests to LOCAL.md and cloud model requests
  to AGENTS.md/CLAUDE.md. Cites in `references/local-orchestration.md`. URL:
  https://ai.ttindall.com/recipes/claude-code-local-subagents/ — TAG: DATA (routing mechanism).
- **Stable role names for local models with llama-swap:** Maps stable role aliases (agent, coder, review,
  fast, thinker) to underlying model files with per-OS path macros and commit-first apply workflow.
  Determines which LOCAL.md guidance applies to each local role. Cites in `references/local-orchestration.md`.
  URL: https://ai.ttindall.com/recipes/llama-swap-roles/ — TAG: DATA (role configuration).
- **Cap thinking per role, not per model:** Same model file, different thinking budgets per role
  (agent 4096, coder 768, thinker 16384). Directly relevant to LOCAL.md sizing — reasoning budget per
  role is part of what LOCAL.md must specify for local model operation. Cites in
  `references/local-orchestration.md`. URL: https://ai.ttindall.com/recipes/reasoning-budget-per-role/
  — TAG: DATA (role configuration).
