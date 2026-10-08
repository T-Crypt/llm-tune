# VRAM fit measurements

Hardware: single 24 GB class RTX card (24,564 MiB as measured), 64 GB class host RAM. All figures as recorded in the sources; nothing rounded.

## Table 1: quant file sizes and estimated peak at 131k ctx (24 GB budget, q8_0 KV, `--parallel 1`, mmproj loaded)

| File | GiB | MTP delta | Est. peak | Free | Verdict |
|---|---|---|---|---|---|
| IQ2_M | 10.87 | | 18.84 | 5.16 | fits, lots of room |
| MTP-IQ2_M | 11.29 | +0.42 | 19.26 | 4.74 | fits, lots of room |
| IQ3_M | 13.11 | | 21.08 | 2.92 | fits |
| MTP-IQ3_M | 13.53 | +0.42 | 21.50 | 2.50 | fits; reproduces the measured peak exactly |
| LOW-MTP-IQ4_XS | 14.26 | | 22.23 | 1.77 | fits, comfortable |
| IQ4_XS | 15.44 | | 23.41 | 0.59 | fits on paper, tight |
| MTP-IQ4_XS | 15.86 | +0.42 | 23.83 | 0.17 | does not fit in practice |
| Q4_K_S | 15.91 | | 23.88 | 0.12 | does not fit in practice |
| MTP-Q4_K_S | 16.33 | +0.42 | 24.30 | -0.30 | over budget |
| Q4_K_M | 16.81 | | 24.78 | -0.78 | over |
| MTP-Q4_K_M | 17.23 | +0.42 | 25.20 | -1.20 | over |
| Q5_K_S | 18.79 | | 26.76 | -2.76 | over |
| MTP-Q5_K_S | 19.21 | +0.42 | 27.18 | -3.18 | over |
| Q5_K_M | 19.31 | | 27.28 | -3.28 | over |
| MTP-Q5_K_M | 19.73 | +0.42 | 27.70 | -3.70 | over |
| LOW-MTP-Q6_K | 20.89 | | 28.86 | -4.86 | over |
| Q6_K | 21.97 | | 29.94 | -5.94 | over |
| MTP-Q6_K | 22.38 | +0.42 | 30.35 | -6.35 | over |
| Q8_0 | 27.74 | | 35.71 |, | file alone exceeds the card |
| MTP-Q8_0 | 28.16 | +0.42 | 36.13 |, | file alone exceeds the card |

Estimated peak = file GiB + 7.97 GiB fixed (see kv-cache.md Table 2). The MTP delta is flat across every quant.

Source: `state/evals/2026-09-25/gain-research.md` (Note 1b, 1e).

## Table 2: measured peak VRAM, 262k ctx sweep, one 24 GB card, desktop on iGPU

| Model | ctx | -ub | Peak VRAM (MiB) | Host RAM peak (MiB) | Status |
|---|---|---|---|---|---|
| TielCoder-262K | 262144 | 1024 | 22484 | 7287 | ok |
| AgentFast-262K | 262144 | 1024 | 22570 | 7855 | ok |
| Quality-131K-ub1024 | 131072 | 1024 | 23488 | 9481 | ok |
| Quality-163K | 163840 | 512 | n/a | n/a | load_failed (OOM on MTP draft context) |
| Nail-262K | 262144 | 1024 | 23680 | 7599 | ok |
| CyberTiel-262K | 262144 | 1024 | 23600 | 8093 | ok |
| MoziAI-262K | 262144 | 1024 | 21696 | 7129 | ok |
| GAIN-163K | 163840 | 1024 | 23220 | 9857 | ok |
| Occult-Nail | 131072 | 1024 | 19178 | 7600 | ok |
| Ornith-CoderX | 262144 | 1024 | 20136 | 8666 | ok |
| Genesis-Hermes | 262144 | 512 | 22334 | 7887 | ok |
| Abliterated | 262144 | 1024 | 21880 | 7778 | ok |
| APEX-Mini | 262144 | 1024 | 20564 | 7698 | ok |
| Defiant-Fable-9B | 262144 | 512 | 13566 | 7165 | ok |

Source: `state/evals/2026-09-26/r6-vram/results.jsonl` (peak VRAM); host RAM peak from `state/evals/2026-09-26/r6-vram/r6.log`.

## Table 3: context ladder on one 27B quant pair (measured peak VRAM)

| Entry | Quant | ctx | -ub | Peak VRAM (MiB) | Status |
|---|---|---|---|---|---|
| Q4XL-131K | Q4_K_XL | 131072 | 512 | 23104 | ok |
| Q4XL-144K | Q4_K_XL | 147456 | 512 | 23808 | ok |
| Q4XL-152K | Q4_K_XL | 155648 | 512 | 24142 | ok at load, crashed mid-run |
| Q4XL-163K | Q4_K_XL | 163840 | 512 | n/a | load_failed |
| Q4XL-163K-noMTP | Q4_K_XL | 163840 | 512 | 22688 | ok |
| IQ4XS-131K | IQ4_XS | 131072 | 512 | 20116 | ok |
| IQ4XS-196K | IQ4_XS | 196608 | 512 | 22932 | ok |
| IQ4XS-229K | IQ4_XS | 229376 | 512 | n/a | load_failed (compute buffer reserve) |
| IQ4XS-229K-noMTP | IQ4_XS | 229376 | 512 | 22196 | ok |
| IQ4XS-262K-q4 | IQ4_XS | 262144 | 512 | 21652 | ok (q4_0 KV) |
| IQ4XS-262K-q8-noMTP | IQ4_XS | 262144 | 512 | 23444 | ok (q8_0 KV) |
| IQ4XS-262K-q8-noMTP-ub256 | IQ4_XS | 262144 | 256 | 23276 | ok |

Source: `state/evals/2026-09-30/r9-27b-context/results.jsonl`.

## Table 4: engine memory footprint, same model class, three engines

| Engine / mode | Peak VRAM (MiB) | Host RAM peak (MiB) | Load (s) |
|---|---|---|---|
| Strata IQ2_XS (expert cache, int8 KV, 131k) | 23966 | 27900 | n/a |
| Strata IQ2_XS (same, second run) | 23966 | 28289 | n/a |
| NInfer groupwise-int 27B (262k, pinned host KV 8 GiB) | 23136 | 15337 | 37 |
| NInfer int8 mode | 23134 | 19364 | 37 |
| NInfer a16 mode | 23136 | 19765 | 37 |
| llama.cpp Q4_K_XL control (196k) | 22914 | 8550 | 10 |

Source: `state/evals/2026-10-02/r11-strata-iq2xs/results.jsonl`, `state/evals/2026-10-02/r12-ninfer/results.jsonl`, `state/evals/2026-10-03/r13-ninfer-int8/results.jsonl`.

## Table 5: Strata expert-cache / RAM headroom by variant (24 GB card, 31 GB class RAM box)

| Variant | GPU expert slots | Pinned experts (GiB) | Min RAM avail (GiB) |
|---|---|---|---|
| base 131K int8 | 12112 | 20.87 | 2.87 |
| 262K int8 | 10686 | 22.37 | 1.42 |
| 262K q4_0 (chosen) | 11819 | 21.26 | 2.52 |
| 262K q4_0 streamed | 13033 | 20.52 + 1.69 KV | 2.51 |
| 512K q4_0 streamed, yarn 2 | 12702 | 18.85 | ~2.3, zram full |
| k8v4 262k streamed | 12953 | 19.62 | 1.59 |
| k8v4 262k in VRAM | 11208 | 22.08 | 1.69 |
| q4 512k streamed yarn 2 | 12702 | 19.04 | 1.66 |

Source: `state/evals/2026-10-03/strata-ctx/RESULTS.md`, `state/evals/2026-10-03/strata-k8v4/sweep.jsonl`.

## Table 6: CPU offload, measured (llama.cpp, 24 GB card, Windows box)

| Entry | Offload setting | Decode t/s | Note |
|---|---|---|---|
| CyberTiel Q4_K_XL | `--n-cpu-moe` varied | 68–124 | higher offload = more headroom, less speed; per-setting values not recorded |
| CyberTiel IQ4_XS | full GPU offload, no `--n-cpu-moe` | 234–245 | 23,624 MiB VRAM, 515 MiB headroom |

Guidance recorded with the measurement: `--n-cpu-moe` is the only correct overflow lever, never
`-ngl`; offloading the draft layer trades the MTP win away entirely. The idea that a partial
offload "costs far more t/s than the quant gains back" is the source's expectation; the measured part is the direction (more offload, less speed).

Source: `reference/LOCAL_MODELS.md` (CyberTiel measurements), `reference/llama-swap/TUNING-4090.md` (guidance).

## Table 7: host RAM headroom before and after an engine upgrade (Strata IQ2_XS, 512k, 31 GB class RAM box, engine-specific)

| Arm | Page-locked RAM pinned (GiB) | Min MemAvailable at 477K prompt (GiB) | zram peak (GiB) | 477K read t/s | Decode t/s at depth |
|---|---|---|---|---|---|
| 0.1.38 + #646 + #700 (baseline) | 17.24 | 3.36 | 3.47 | 2,990 | 111.3 |
| 0.1.39, headroom 4 (default) | 19.20 | **1.41** | 2.38 | 3,473 | 121.6 |
| 0.1.39, headroom 6 (deployed) | n/a | 3.53 | 2.50 | 3,411 | 122.0 |

The upgrade added a page-locked RAM copy for the prompt path's lent slots, sized to all but
`STRATA_RESIDENT_HEADROOM_GIB` (default 4) of the RAM free at start. VRAM was unchanged (12,702
expert slots, 17.02 GiB, ~385 MiB free). Arms were not interleaved, same box, same config.
Headroom 6 restores 3.53 GiB and keeps most of the long-prompt gain (-12% read at 477K vs the
default, +10% decode at depth). Recall held at all four depths on every arm.

Source: `state/evals/2026-10-04/strata-0139-512k/RESULTS.md`.
