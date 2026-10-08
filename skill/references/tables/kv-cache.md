# KV cache measurements

Architecture-dependent: only full-attention layers carry a growing KV cache; hybrid (Mamba / Gated DeltaNet) layers hold fixed state. Hardware: single 24 GB class RTX card.

## Table 1: KV cache size at q8_0 by context (derived arithmetic, 27B dense model: 64 layers, 16 full-attention, 4 KV heads, head dim 256)

| ctx | KV cache @ q8_0 (GiB) |
|---|---|
| 32,768 | 1.06 |
| 65,536 | 2.125 |
| 131,072 | 4.25 |

Per-token derivation: 2 x 4 x 256 x 1.0625 B = 2,176 B per attention layer per token; x 16 layers = 34,816 B/token; 0.0332 GiB per 1k tokens.

Source: `state/evals/2026-09-25/gain-research.md` (Note 1c, 1f).

## Table 2: fixed non-file VRAM overhead, calibrated against one measured peak (131k ctx, q8_0 KV, mmproj loaded)

| Component | GiB |
|---|---|
| Model file (MTP-IQ3_M) | 13.53 |
| mmproj-BF16 | 0.87 |
| KV cache @ 131k | 4.25 |
| "Everything else" (CUDA context + compute/graph buffers + GDN state + allocator) | 2.85 (not verified) |
| Observed peak | 21.50 |

The 2.85 GiB residual is derived from a single measurement; the hypothesis for its size is the 248,320-token padded vocab plus 16-bit output tensor. The authoritative number is llama.cpp's own `CUDA0 compute buffer size` log line.

Source: `state/evals/2026-09-25/gain-research.md` (Note 1d).

## Table 3: the context/quant trade (24 GB budget, q8_0 KV)

| ctx | KV (GiB) | Fixed total (GiB) | Largest MTP quant with >= 0.9 GiB free |
|---|---|---|---|
| 131,072 | 4.25 | 7.97 | MTP-IQ3_M (13.53 GiB) |
| 65,536 | 2.13 | 5.85 | MTP-Q4_K_M (17.23 GiB, 23.08 peak, 0.92 free) |
| 32,768 | 1.06 | 4.78 | MTP-Q4_K_M comfortably; Q5_K_S right at the edge |

Source: `state/evals/2026-09-25/gain-research.md` (Note 1f).

## Table 4: hybrid architecture: fixed state instead of growing KV (30B MoE, 52 layers = 6 attention + 23 Mamba + 23 MoE)

At 262,144 ctx: ~1.50 GiB attention KV + ~46 MiB Mamba state, the full window stays cheap. (Derived from architecture, not measured on this box.)

Source: `state/evals/2026-09-25/nemotron-research.md`.

## Table 5: Strata KV footprint by variant (engine log lines, IQ2_XS MoE, 24 GB card, 31 GB class RAM box)

| Variant | KV cells in VRAM | KV in pinned host RAM (GiB) |
|---|---|---|
| k8v4, 262k, `--kv-resident 32768` | 32,768 of 262,144 per QSA layer | 2.39 |
| k8v4, 262k, full in VRAM | 262,144 | 0 (resident mode, no streaming line) |
| q4_0, 262k, `--kv-resident 32768` | 32,768 of 262,144 per QSA layer | 1.69 |
| q4_0, 512k, `--kv-resident 32768`, yarn 2 | 32,768 of 524,288 per QSA layer | 3.38 |

Source: `state/evals/2026-10-03/strata-k8v4/sweep.jsonl` (`engine_mem_lines`).

## Table 6: NInfer state pools, 27B groupwise-int at 262k (engine startup accounting, bytes as logged)

| Pool | Bytes | GiB |
|---|---|---|
| text_kv | 4,563,402,752 | 4.25 |
| mtp_kv | 285,282,304 | 0.27 |
| gdn_state | 307,888,128 | 0.29 |
| replay_records | 7,151,616 | 0.01 |
| persistent_arena | 5,178,365,184 | 4.82 |
| workspace | 433,324,032 | 0.40 |
| runtime_reservation | 5,701,866,752 | 5.31 |
| kv_headroom | 0 | 0 |

Host KV pinned at startup: 8.00 GiB; host state pinned: 1.15 GiB; weights 16.9 GiB. `kv_headroom_bytes=0`, the KV budget was fully consumed at startup.

Source: `state/evals/2026-10-02/r12-ninfer/side-NInfer-Qwen3.8-27B.log`.
