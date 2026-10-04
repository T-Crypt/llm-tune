## The hard constraint first

A 27B dense model does not fit in 12 GB in any quant worth using for coding. Quant file sizes are physical facts (from `references/tables/vram-fit.md` T1, the measured 27B family):

| Quant | File | Fits on 12 GB? |
|---|---|---|
| Q4_K_M | 16.81 GiB | no |
| IQ3_M | 13.11 GiB | no |
| IQ2_M | 10.87 GiB | yes, but ~1 GiB left for KV + compute buffers + CUDA context |

So `-ngl 99` is off the table. Your actual decision is one of:

1. **Partial offload** — Q4_K_M or IQ3_XXS with `-ngl` set so the GPU-resident layers + KV + buffers fit in 12 GB, rest on CPU. 32 GB host RAM is comfortable for this. Cost: dense CPU layers are memory-bandwidth-bound, so decode drops hard. The measured direction (T6): more offload = more headroom, less speed. Dense 27B decoded 52–119 t/s on a 4090-class card; a 3060 is ~3x lower bandwidth, so expect low double-digit t/s — **that's an estimate, not a measurement; bench it on your box.**
2. **IQ2_M fully on GPU** — fits, but IQ2 is a quality tier you don't want for a coding agent (the skill's trap: quant-tier gains show in output richness; IQ4 vs IQ3 both scored 11/12, but IQ2 is a different story).
3. **A smaller model that actually fits** (14B-class Q4) — if decode speed matters more than the 27B's reasoning.

## Settings I'd start from (confirm every flag against `--help` on your build)

- **Fit arithmetic:** budget = file + KV + compute/graph buffers + draft context, not the file alone. Read llama.cpp's own `KV buffer size` / `compute buffer size` log lines — the 2.85 GiB "everything else" from the lab is one measurement on a 24 GB card and does not transfer.
- **KV:** if your 27B is the same hybrid architecture as the measured one (16 full-attention layers of 64, 4 KV heads, head dim 256), KV at q8_0 is 0.0332 GiB per 1k tokens — 16k ctx ≈ 0.53 GiB, cheap. If it's pure attention (Qwen3-32B-style), it's ~3x that. Check the architecture; it decides whether you can afford 16k–32k context.
- **`-fa on -ctk q8_0 -ctv q8_0`**, `-ub 512` — `-ub 1024` gave no measurable gain on the dense 27B, and bigger chunks cost more on smaller-RAM boxes (finding 21).
- **MTP:** only if the file carries MTP tensors *and* you have headroom. Flat +0.42 GiB plus a separate draft-context allocation that can OOM even when the target fits. Log acceptance; below ~50% the non-MTP file runs faster. d3 was best for code on the measured engine. On 12 GB I'd trade MTP for context.
- **Sampling (Qwen vendor spec, findings 14–15):** temp 1.0, top_p 0.95, top_k 20, min_p 0, rep_pen 1.0, presence 0.0; keep rep_pen exactly 1.0 on MTP files. Cap the reasoning budget per role — never `-1` (20k-token thinking loops, no output). `--jinja` is required for template-driven reasoning kwargs.
- **Harness (findings 16–17, 28):** keep thinking **on** — thinking-off made Qwen-class models skip the tool call entirely. Use tolerant tool-call parsing if your build has it (5/16 strict failures → 0/16 tolerant, same model). Client context cap must equal the served window.

## Verify before trusting any of the above

Run `bench/quick_bench.md` on your machine — it's the only source of numbers that are yours: engine memory accounting from the load log, peak VRAM via `nvidia-smi --query-compute-apps` (any PID that isn't llama-server is the bug — check whether your desktop compositor is sharing the card), llama-bench prefill/decode at depth, needle recall at 10/50/90% depth, and a tool-call probe plus a 12-defect review run five times per arm.

Two intake gaps I'd want filled before finalizing: **the exact GGUF file** (hybrid DeltaNet vs pure attention changes the KV budget by ~3x, and whether it carries MTP tensors) and **your llama.cpp version** (flag names changed between builds — `--draft-max` → `--spec-draft-n-max`). If you paste the load log, I can turn the arithmetic into a real fit table for your card.
