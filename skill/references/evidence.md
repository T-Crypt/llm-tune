# Evidence index

Read this only when a decision needs backing. Paths are repo-relative to this repo; the
homelab sources they were extracted from are cited inside each table file.

| Decision step | Tables | Findings | Notes |
|---|---|---|---|
| 1. Fit (VRAM, runtime, host RAM) | `data/tables/vram-fit.md` T1 (quant sizes + est. peak), T2 (measured peak, 262k sweep), T3 (context ladder), T4 (engine footprints), T5 (expert slots / RAM headroom); `data/tables/kv-cache.md` T2 (fixed overhead) | 1, 2, 5, 22, 25, 26, 27 | The 2.85 GiB residual is one measurement, breakdown unverified. Gate value 22,900 MiB is for the measured card only. |
| 2. Context vs quant | `data/tables/kv-cache.md` T1, T3; `data/tables/context-recall.md` T1 (400 at depth), T3 (ladder) | 4, 7, 28 | The 0.0332 GiB/1k figure is derived arithmetic, confirmed by one measurement. |
| 3. KV cache type | `data/tables/kv-cache.md` T4 (hybrid fixed state), T5 (Strata pinned KV), T6 (NInfer state pools); `data/tables/prefill-decode-speed.md` T5 | 3, 6, 8 | q4_0-beats-int8 is Strata-specific and only measured to 262k recall; quality beyond recall unmeasured. |
| 4. Offload / MoE | `data/tables/prefill-decode-speed.md` T3; `data/tables/vram-fit.md` T4, T5 | 20, 27 | Architecture-bound, not quant-bound. Host RAM peak 28,289 MiB on a 31 GB box. |
| 5. Prefill / ubatch | `data/tables/prefill-decode-speed.md` T1, T4, T5, T6, T7, T8 | 9, 10, 21, 23 | The +21% chunk gain and the 2.7–3.4x loss are the same setting on different RAM classes — the clearest example of hardware-class dependence. |
| 6. Speculative / MTP | `data/tables/speculative-mtp.md` T1–T6 | 2 (corrected), 11, 12, 13, 24 | Acceptance gate >= 0.4; below ~50% regular quants win. Depth optimum is workload-dependent. |
| 7. Sampling / reasoning budget | `data/tables/quality-bench.md` T10 (budget held vs removed), T11 (repeats) | 14, 15, 16 | Vendor spec beats house style; medium effort is a silent mode; -1 loops. |
| 8. Harness / client | `data/tables/harness-toolcall.md` T1–T3; `data/tables/quality-bench.md` T14, T15 | 17, 18, 28 | Parser tolerance changed 5/16 to 0/16 with the model untouched. |
| Verification method | `data/tables/quality-bench.md` T7 (repeat runs), T11, T13 (DeepSWE), T14, T15 | 18, 19, 29, 30 | Two tiers: quick proxy for iteration, program verifiers for promotion. |

Corrections that override findings: `data/CORRECTIONS.md` #2 (MTP cost is not a tier step),
#10 (PPL identical to 3 decimals, not 4), #27 (28,289 MiB, not "28 GB"), #30 (69 s vs 209 s
for the tied pair).

Hardware-bound numbers — do not quote on another card: every t/s, every GiB/MiB peak, the
22,900 MiB gate, the 7.97 GiB fixed overhead, the 0.42 GiB MTP delta (this one is a file
property, so it does transfer), the 0.0332 GiB/1k KV rate (transfers only to the same
architecture and KV type).

Method that transfers: read the engine's own buffer log; budget KV + compute + mmproj + draft
context; check recall at depth; hold quality constant before claiming speed; repeat runs and
alternate arms; one model on the GPU at a time; publish corrections; pin versions.
