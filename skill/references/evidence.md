# Evidence index

Read this only when a decision needs backing. Paths below are relative to the skill folder;
the source measurements are cited by repo-relative path inside each table file.

| Decision step | Tables | Findings | Notes |
|---|---|---|---|
| 1. Fit (VRAM, runtime, host RAM) | `references/tables/vram-fit.md` T1 (quant sizes + est. peak), T2 (measured peak, 262k sweep), T3 (context ladder), T4 (engine footprints), T5 (expert slots / RAM headroom); `references/tables/kv-cache.md` T2 (fixed overhead) | 1, 2, 5, 22, 25, 26, 27 | The 2.85 GiB residual is one measurement, breakdown unverified. Gate value 22,900 MiB is for the measured card only. |
| 2. Context vs quant | `references/tables/kv-cache.md` T1, T3; `references/tables/context-recall.md` T1 (400 at depth), T3 (ladder) | 4, 7, 28 | The 0.0332 GiB/1k figure is derived arithmetic, confirmed by one measurement. |
| 3. KV cache type | `references/tables/kv-cache.md` T4 (hybrid fixed state), T5 (Strata pinned KV), T6 (NInfer state pools); `references/tables/prefill-decode-speed.md` T5 | 3, 6, 8 | q4_0-beats-int8 is Strata-specific and only measured to 262k recall; quality beyond recall unmeasured. |
| 4. Offload / MoE | `references/tables/prefill-decode-speed.md` T3; `references/tables/vram-fit.md` T4, T5, T6 (CPU offload), T7 (RAM headroom before/after an engine upgrade) | 20, 27, 31, 32 | Architecture-bound, not quant-bound. Host RAM peak 28,289 MiB on a 31 GB box. T7 is engine-specific (Strata). |
| 5. Prefill / ubatch | `references/tables/prefill-decode-speed.md` T1, T4, T5, T6, T7, T8 | 9, 10, 21, 23 | The +21% chunk gain and the 2.7–3.4x loss are the same setting on different RAM classes, the clearest example of hardware-class dependence. |
| 6. Speculative / MTP | `references/tables/speculative-mtp.md` T1–T6 | 2 (corrected), 11, 12, 13, 24 | Acceptance gate >= 0.4; below ~50% regular quants win. Depth optimum is workload-dependent. |
| 7. Sampling / reasoning budget | `references/tables/quality-bench.md` T10 (budget held vs removed), T11 (repeats) | 14, 15, 16 | Vendor spec beats house style; medium effort is a silent mode; -1 loops. |
| 8. Harness / client | `references/tables/harness-toolcall.md` T1–T3; `references/tables/quality-bench.md` T14, T15 | 17, 18, 28 | Parser tolerance changed 5/16 to 0/16 with the model untouched. |
| 9. Apple Silicon / MLX | `references/apple-mlx.md`, documented, not measured | none | No Apple Silicon run exists in this repo. Facts come from the MLX docs and one community source, listed below. |
| Verification method | `references/tables/quality-bench.md` T7 (repeat runs), T11, T13 (DeepSWE), T14, T15 | 18, 19, 29, 30 | Two tiers: quick proxy for iteration, program verifiers for promotion. |

Corrections that override findings: `references/CORRECTIONS.md` #2 (MTP cost is not a tier step),
#10 (PPL identical to 3 decimals, not 4), #27 (28,289 MiB, not "28 GB"), #30 (69 s vs 209 s
for the tied pair).

Hardware-bound numbers, do not quote on another card: every t/s, every GiB/MiB peak, the
22,900 MiB gate, the 7.97 GiB fixed overhead, the 0.42 GiB MTP delta (this one is a file
property, so it does transfer), the 0.0332 GiB/1k KV rate (transfers only to the same
architecture and KV type).

Method that transfers: read the engine's own buffer log; budget KV + compute + mmproj + draft
context; check recall at depth; hold quality constant before claiming speed; repeat runs and
alternate arms; one model on the GPU at a time; publish corrections; pin versions.

## Sources for the unmeasured Apple Silicon / MLX section

- MLX docs, wired limit: https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html
  (`iogpu.wired_limit_mb`, default 0 = derived from installed RAM, raise with
  `sudo sysctl iogpu.wired_limit_mb=<MB>`, limit "should remain strictly less than the total
  memory size", `mx.metal.device_info()` for `max_recommended_working_set_size` and `memory_size`).
- Community source for the default fractions and the 24 GB worked example:
  https://github.com/blaine-hiers/headroom/issues/13, about 2/3 of RAM at 36 GB or less, about
  3/4 above; sources disagree on exact figures for large machines. The reboot reset, the
  `/etc/sysctl.conf` persistence, and the older `debug.iogpu.wired_limit` (bytes, Ventura /
  Monterey) are community-reported and unverified.
- Hugging Face API used by `bench/mlx_quant_search.py`:
  `https://huggingface.co/api/models?author=mlx-community&search=<name>&limit=50&expand[]=safetensors&expand[]=downloads`
  (brackets URL-encoded as `%5B%5D`) and `https://huggingface.co/api/models/<repo_id>/tree/main`.
  Verified example: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` = 16.0 GiB of weights.
