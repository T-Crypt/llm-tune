Before quoting numbers as yours: every figure in this skill's evidence base was measured on a **24 GB card class with 31 GB RAM** — your 3060 is a different hardware class, so I transfer the method and the traps, not the t/s or GiB figures. Here's the fit arithmetic for your card, with derived numbers flagged as derived.

## The headline: 27B dense on 12 GB is a fit problem first

Quant **file sizes** do transfer between cards (they depend on params and bits, not hardware). From `vram-fit.md` T1, the measured 27B files: IQ2_M 10.87 GiB, IQ3_M 13.11, IQ4_XS 15.44, Q4_K_M 16.81. On a 12 GB card, **only IQ2-class files fit, and only if you leave room for KV + compute buffers** — the file alone is not the budget (finding 1).

Derived for your card, not measured:

- IQ2_M leaves ~1.1 GiB for KV + CUDA context + compute/graph buffers. That is the whole budget.
- KV at q8_0 is architecture-dependent (finding 3). If your "Qwen 27B" is the hybrid DeltaNet architecture the lab measured (16 of 64 layers carry growing KV), KV is 0.0332 GiB per 1k tokens (`kv-cache.md` T1) — 32k ctx ≈ 1.06 GiB, which already exceeds your headroom. If it's a plain full-attention dense 27B, KV is roughly 4× that per token (derived from 64 vs 16 attention layers) — 32k would be ~4 GiB. **Check which file you have; it decides everything.**
- The 2.85 GiB "everything else" residual in `kv-cache.md` T2 is 4090-specific and unverified — do not assume it on a 3060. The authoritative number is llama.cpp's own `KV buffer size` / `compute buffer size` log lines on your load.

So the only fully-GPU path on 12 GB is: **IQ2-class quant, small context (8–16k), q4_0 KV, no mmproj, no MTP.** Anything bigger means CPU offload, and for a dense model that means `-ngl` partial offload — the measured direction is more offload = more headroom, less speed (finding 32; the `--n-cpu-moe` lever is MoE-only, so it doesn't apply to a dense 27B).

## Settings I'd start from (version-scoped — confirm against `--help` on your build, finding 24)

```
-ngl 99                       # full offload; drop toward -ngl 40-50 only if you accept slow decode
--ctx-size 16384              # or 8192; every 32k of ctx is ~1 GiB of KV on the measured hybrid (T1)
-fa on -ctk q4_0 -ctv q4_0    # q4_0 KV beat int8 on every measured axis with recall held (finding 6)
-ub 512                       # -ub 1024 showed no measurable gain on the dense 27B (finding 21)
--jinja                       # required for template-driven kwargs
--reasoning on --reasoning-budget <cap>   # never -1: unbounded budget produced 20k-token loops with no output (finding 14)
```

- **Skip MTP on this card.** It's a flat +0.42 GiB of tensors (finding 2, corrected) plus a *separate draft-context allocation that can OOM even when the target fits* — that exact failure is measured (`vram-fit.md` T2, Quality-163K load_failed). On a 12 GB card that allocation is your entire headroom. If you do use an MTP file, log acceptance and fall back to a regular quant below ~50% (finding 13).
- **Sampling: read this model's own card.** The vendor spec in the evidence base (temp 1.0, top_p 0.95, top_k 20) is one hybrid thinking model's numbers and does not transfer (finding 15's trap, restated in the traps list). On MTP files keep temp ≤ 1.0 and rep_pen exactly 1.0.
- **Tool-call reliability settings, which matter more than the quant for an agent:** keep thinking **on** — thinking-off made Qwen-class models skip the tool call entirely (finding 16); use tolerant tool-call parsing in your client/harness (finding 17: 5/16 failures → 0/16 without touching the model); make your client's context cap equal the served window, or long prompts get 400s or silent clipping (findings 7, 28).

## Two things that will bite you on a 3060 specifically

1. **The desktop compositor shares the card.** On a 12 GB card that's a large fraction of the budget; freeing it to the iGPU is a real lever (finding 26). And audit the card for squatters — any PID on the GPU that isn't llama-server is the bug (finding 25).
2. **Load-time fit is not runtime fit.** A model that loads can OOM mid-inference as buffers grow with depth (finding 5) — with ~1 GiB of headroom, you're in exactly the regime where that happens. Watch peak VRAM per run: `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`.

## Honest expectation, stated as inference

Decode speed for a dense 27B is bandwidth-bound. The measured dense 27B decoded 52–119 t/s on a 4090 (`prefill-decode-speed.md` T3); a 3060 has roughly a third the bandwidth, so I'd expect low-20s t/s or less fully offloaded at IQ2, and single-digit t/s with heavy CPU offload — **that is inference, not a measurement, and I won't quote it as yours.** If the coding agent needs to read whole files and iterate, a 14B-class model at Q4_K_M fits a 12 GB card with room for context, and it will beat a starved 27B on tool-call reliability; that's a trade worth considering before you commit to the 27B.

## Verify before trusting any of this

Run `bench/quick_bench.md` on your box — memory accounting, prefill/decode at depth, recall at depth (needles at 10/50/90%), and a small quality probe with repeats, three runs per arm (finding 19). Check `finish_reason` per run: `finish=length` with no content is a budget failure, not a model failure. Evaluate multi-turn tool calls, not single-turn evals (finding 18).

**What I still need to make the numbers yours:** the exact llama.cpp build, the exact GGUF file (and whether it's the DeltaNet-hybrid 27B or full-attention — it changes the KV arithmetic 4×), whether the file carries MTP tensors, and whether the desktop shares the card. Give me the load log's KV/compute buffer lines and I can turn the fit table into your actual budget.
