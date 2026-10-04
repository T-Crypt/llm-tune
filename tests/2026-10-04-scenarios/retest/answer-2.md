## What's happening

Your case is the measured one — same card class, same quant. On the reference 24 GB card (24,564 MiB), the Q4_K_XL 27B ladder in `vram-fit.md` T3 reads:

| ctx | Peak VRAM | Status |
|---|---|---|
| 131k | 23,104 MiB | ok |
| 144k | 23,808 MiB | ok |
| 152k | 24,142 MiB | **ok at load, crashed mid-run** |
| 163k | — | load_failed |

So the load succeeds because it fits *at load time*. It crashes mid-request because fit at load is not fit at runtime (finding 5): the compute/graph buffers grow with depth during generation, and you start with only ~1.4 GiB of headroom at 131k — already past the 22,900 MiB gate value that was used as the working safety line. A long request that actually fills the window pushes the peak over the card.

Two things make this worse, and both are levers:

- **MTP.** The draft context is a separate allocation that can OOM even when the target model fits (finding 2). At 163k, the MTP entry failed to load while `Q4XL-163K-noMTP` ran fine at 22,688 MiB. Same pattern on the IQ4_XS pair at 229k. If your file carries MTP tensors, that allocation is likely what tips you over.
- **KV type.** At q8_0, KV on this architecture is 4.25 GiB at 131k (`kv-cache.md` T1) — 16 of 64 layers carry a growing KV, the Gated DeltaNet layers hold fixed state. q4_0 KV ran at 262k with recall held at every depth (`context-recall.md` T3), and the q4_0 arm beat int8 on every measured axis (finding 6, Strata-specific).

Note the crash cost more than stability: the 152k entry scored 0/3 at both 60k and 120k depth (`context-recall.md` T3). A crash mid-request is a recall failure too.

## What I'd change, in order

1. **Run a noMTP arm** (or cap `--spec-draft-n-max` low). Log token acceptance — below ~50% regular quants run faster anyway (finding 13, gate ≥ 0.4). MTP costs a flat +0.42 GiB of tensors plus the draft-context allocation.
2. **Cap the served window at the depth your peak actually stays under the gate**, not at the number you declared. On the measured card that means 131k is the ceiling for Q4_K_XL with q8_0 KV, and it is already tight.
3. **Switch `-ctk/-ctv` to q4_0** if you want depth past 131k. Recall held at every measured depth; quality beyond needle recall was not measured, so don't expect parity at 262k from a recall test alone.
4. **Drop mmproj if you don't need vision** — 0.87 GiB of the fixed 7.97 GiB overhead.
5. **Check the client cap matches the served window.** A hardcoded 262144 in the client overfills a 131k server (finding 28) — that gives a 400 or silent clipping rather than a crash, so it isn't your symptom, but it's worth ruling out as a second problem.
6. **Audit the card for squatters.** Any PID that isn't `llama-server` is the bug — an embedding daemon held 11.3 GiB after its job ended (finding 25). `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`. If the desktop compositor shares the card, moving it to the iGPU is a real lever (finding 26).

`-ub` is not your lever: no measurable prefill gain on the dense 27B at 1024 vs 512 (finding 21). The only measured ubatch effect on peak was ~168 MiB at ub256 — small.

## How to verify it actually helped

Three runs per arm, quality held constant, one model on the card at a time. Read llama.cpp's own `KV buffer size` / `compute buffer size` log lines rather than applying arithmetic, and record peak VRAM per run. Then recall at ~10/50/90% depth — declared context is not usable context.

## What I still need

- **System RAM** and **OS** — you report a crash, which reads like Linux; on Windows the overflow spills into system RAM silently and hangs instead (finding 20), so the symptom itself tells me something, but confirm.
- **Exact llama.cpp build** — flag names changed between builds (`--draft-max` → `--spec-draft-n-max`), so pin the version before recommending a flag.
- **Whether the file carries MTP tensors**, and its size on disk.
- **The workload** — agent multi-turn vs long-document read decides which budget line you cut.

One caveat on the numbers: every figure above is from one 24 GB card class, so it transfers to your card by class, not by identity. Run `bench/quick_bench.md` on your box before treating 23,104 MiB or the 22,900 MiB gate as yours.
