# Speculative decoding / MTP measurements

Hardware: single 24 GB class RTX card. Acceptance is logged as accepted/attempted tokens.

## Table 1 — MTP tensor cost

Flat +0.42 GiB (451,320,768 bytes measured on the IQ3_M pair) across every quant in the repo — the Q8_0 MTP tensors. Exception: the LOW tier files carry MTP tensors at lower precision (LOW-MTP-IQ4_XS is 1.19 GiB smaller than regular IQ4_XS; precision claim unverified). The MTP draft context is a separate allocation that can OOM even when the target model fits.

Source: `state/evals/2026-09-25/gain-research.md` (Note 1b), `state/evals/2026-09-26/r6-vram/` (Quality-163K load_failed).

## Table 2 — draft acceptance, round 1 bakeoff (8-bug review, 8192 cap)

| Model | Draft acc (accepted/attempted) | Decode t/s |
|---|---|---|
| Qwen3.6-35B-A3B-IQ4-Agent | 10136/11589 | 268 |
| Qwen3.8-27B-Q4-Quality | 9933/12196 | 104 |
| Qwen3.6-35B-A3B-IQ4-CoderFast | 5186/5985 | 246 |
| Qwen3.6-TwinTurbo-NeoMax-UnHeretic-IQ3_M | 5916/7215 | 96 |
| Qwen3.8-GAIN-V1.1-IQ3_M | 9734/12793 | 90 |
| Qwen3.8-27B-Stock-IQ3_S | 9015/14950 | 96 |
| Nail-Qwen3.6 | 9979/11331 | 268 |
| Qwen3-Coder-Stock-Q3_K_XL | n/a | 204 |
| Qwen3.6-Stock | 8595/9978 | 264 |
| Qwen3.6-APEX | 10171/11484 | 280 |
| TielCoder | 6935/10053 | 227 |
| Qwen3.8-TwinTurbo-Tools | 10028/11496 | 112 |
| Qwen3.8-TwinTurbo-NeoCoder-IQ3_M | 6786/7917 | 98 |
| Qwen3.8-Distill-APEX-Compact | 6177/7509 | 270 |
| Qwen3.8-Distill-APEX-Mini | 7218/8157 | 275 |
| Gemma-4-26B | 3862/4398 | 236 |
| Nemotron-Lightning-3.5 | 4584/5532 | 314 |
| Nemotron-Cascade-2 | n/a | 231 |
| Devstral-Small-2-Abliterated | n/a | 63 |
| CyberTiel-IQ3_XXS | 8303/11187 | 249 |
| Ornith-1.5-CoderX | 10328/11010 | 293 |
| Qwen3.8-Whittle-MoE | n/a | 57 |
| Qwen3.8-TwinTurbo-NeoMax-IQ3_M | 5718/7017 | 93 |
| Qwen3.6-Coder-Pruned-262K | 7046/8670 | 244 |
| Qwen3.6-Genesis-Hermes | 10072/11779 | 267 |
| Qwen3.6-Abliterated | 6333/7746 | 270 |
| Qwen3-Coder-Abliterated | n/a | 201 |
| Occult-Nail | n/a | 167 |
| MoziAI-Finance | 7230/20303 | 155 |
| Qwen3.8-Distill-APEX-Compact-Reasoning | 5808/6951 | 273 |
| Nemotron-Cascade-2-Reasoning | n/a | 231 |
| Nemotron-Lightning-3.5-Reasoning | 4183/5589 | 295 |
| Qwen3.5-9B-Aggressive | n/a | 88 |
| Qwen3.5-9B-Defiant-Fable | n/a | 94 |

Source: `state/evals/2026-09-25/full.log`.

## Table 3 — draft acceptance, round 2 (12-bug review)

| Model | Draft acc | Decode t/s |
|---|---|---|
| Qwen3.6-35B-A3B-IQ4-Agent | 13288/14400 | 277 |
| Qwen3.6-Stock | 9037/10086 | 272 |
| Nail-Qwen3.6 | 7644/8835 | 269 |
| Qwen3.8-Distill-APEX-Compact | 9717/10881 | 284 |
| Qwen3.6-APEX | 9655/10632 | 287 |
| TielCoder | 8402/11661 | 234 |
| Qwen3.8-TwinTurbo-Tools | 8259/9132 | 116 |
| Qwen3.8-TwinTurbo-NeoCoder-IQ3_M | 5524/6450 | 99 |
| Qwen3.6-TwinTurbo-NeoMax-UnHeretic-IQ3_M | 7953/8856 | 102 |
| Qwen3-Coder-Stock-Q3_K_XL | n/a | 72 |
| Qwen3.6-35B-A3B-IQ4-CoderFast | 47/102 | 160 |
| Gemma-4-26B | 4039/4599 | 232 |
| Nemotron-Lightning-3.5 | 5425/6423 | 305 |
| Qwen3.8-27B-Q4-Quality (group B) | 17562/21081 | 98 |
| Qwen3.8-27B-Stock-IQ3_S (group B) | 14723/19968 | 105 |
| Qwen3.8-GAIN-V1.1-IQ3_M (group B) | 6852/8994 | 91 |
| Qwen3.6-35B-A3B-IQ4-Agent (group C, 768 cap) | 8042/9144 | 270 |

Source: `state/evals/2026-09-25/r2.log`.

## Table 4 — draft acceptance, r6 VRAM round (262k, 12-bug review)

| Model | Draft acc | Decode t/s |
|---|---|---|
| TielCoder-262K | 7547/9822 | 279 |
| AgentFast-262K | 13861/15237 | 306 |
| Quality-131K-ub1024 | 19586/28140 | 108 |
| Nail-262K | 8459/9723 | 301 |
| CyberTiel-262K | 8455/12366 | 260 |
| MoziAI-262K | 7522/20229 | 173 |
| GAIN-163K | 14603/23157 | 83 |
| Occult-Nail | n/a | 174 |
| Ornith-CoderX | 3393/5769 | 255 |
| Genesis-Hermes | 11239/12801 | 311 |
| Abliterated | 10269/11553 | 324 |
| APEX-Mini | 4788/5535 | 318 |
| Defiant-Fable-9B | n/a | 96 |

Source: `state/evals/2026-09-26/r6-vram/r6.log`.

## Table 5 — NInfer draft-depth sweep (qwen3.8-27b groupwise-int, 262k, three runs per workload, mean t/s)

| Label | Flags | VRAM (MiB) | Code | Agent | Prose | Mean |
|---|---|---|---|---|---|---|
| d3-base | `--spec mtp --draft-tokens 3 --lm-head-draft` | 23134 | 94.8 | 100.6 | 128.4 | 107.9 |
| d2 | `--spec mtp --draft-tokens 2 --lm-head-draft` | 23132 | 93.7 | 93.4 | 114.3 | 100.5 |
| d4 | `--spec mtp --draft-tokens 4 --lm-head-draft` | 23136 | 90.2 | 100.2 | 132.3 | 107.6 |
| d5 | `--spec mtp --draft-tokens 5 --lm-head-draft` | 23138 | 86.3 | 88.1 | 140.0 | 104.8 |
| d3-nohead | `--spec mtp --draft-tokens 3` | 22794 | 90.0 | 86.5 | 111.9 | 96.1 |

Per-run values in the source. d3 best overall mean, d5 best prose, d3 best code; LM-head draft worth ~11.8 t/s mean (107.9 vs 96.1).

Source: `state/evals/2026-10-03/ninfer-sweep1/results.jsonl`.

## Table 6 — Strata MTP draft-head memory (engine log lines, IQ2_XS)

| Variant | Draft layer VRAM (MiB) | Draft head over tokens |
|---|---|---|
| k8v4-262k-res | 835 (experts 675, dense 111) | 106,299 tokens, 137.9 MiB |
| k8v4-262k | 1098 (experts 675, dense 111) | 106,299 tokens, 137.9 MiB |
| q4-262k-res-p | 820 (experts 675, dense 111) | 106,299 tokens, 137.9 MiB |
| q4-512k-yarn-res-p | 821 (experts 675, dense 111) | 106,299 tokens, 137.9 MiB |

Source: `state/evals/2026-10-03/strata-k8v4/sweep.jsonl` (`engine_mem_lines`).

Reference datapoint (model card, not measured here): Q4_K_S regular ~75 t/s vs MTP >90 t/s at 60% acceptance, 2 tokens — roughly +20% at 60% acceptance; the ratio, not the absolute t/s, is the transferable part. Gate: below ~50% acceptance, regular quants run faster. Source: `state/evals/2026-09-25/gain-research.md` (Note 3), `runbooks/llama-swap.md` (bench gate >= 0.4).
