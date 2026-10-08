# Quality bench measurements

Harnesses: blind answer ranking (5 axes x 1-10), planted-bug code review (8-bug round 1, 12-bug round 2+), structural build scoring, program-verifier task suites, DeepSWE. Hardware: single 24 GB class RTX card.

## Table 1: blind ranking, round 1 (30-day ops question, 5 axes, /50)

Key: A = Nemotron-Cascade-2-Reasoning, B = Qwen3.6-Stock, C = Qwen3.8-27B-Q4-Quality, D = Qwen3.8-GAIN-V1.1-IQ3_M, E = Qwen3.8-Whittle-MoE.

| Answer | Specificity | Correctness | Actionability | Prioritisation | Concision | Total /50 |
|---|---|---|---|---|---|---|
| A | 6 | 3 | 5 | 5 | 4 | 23 |
| B | 8 | 6 | 7 | 5 | 6 | 32 |
| C | 10 | 9 | 10 | 9 | 3 | 41 |
| D | 7 | 8 | 8 | 8 | 9 | 40 |
| E | 3 | 2 | 3 | 2 | 7 | 17 |

Source: `state/evals/2026-09-25/think-ranking.md`.

## Table 2: blind ranking, round 2 re-rank (adds F = Qwen3.8-27B-Research, temp 1.0, 16K budget, 280 s)

| Answer | Specificity | Correctness / no invented facts | Actionability | Prioritisation | Concision | Total /50 |
|---|---|---|---|---|---|---|
| A | 7 | 3 | 6 | 5 | 5 | 26 |
| B | 7 | 5 | 8 | 5 | 7 | 32 |
| C | 9 | 8 | 9 | 8 | 4 | 38 |
| D | 8 | 9 | 8 | 9 | 9 | 43 |
| E | 3 | 4 | 2 | 2 | 8 | 19 |
| F | 9 | 8 | 9 | 7 | 4 | 37 |

Judge noise note in source: C and D swapped between the two runs (41/40 then 38/43), so +/-4 points is within noise.

Source: `state/evals/2026-09-25/think-ranking.md`.

## Table 3: think-task times, round 2 group D (same models, single answer)

| Model | Seconds | Answer chars | Reasoning chars | Tokens |
|---|---|---|---|---|
| Qwen3.8-27B-Q4-Quality | 209 | 17884 | 44601 | 15907 |
| Qwen3.8-Whittle-MoE | 39 | 3725 | 5607 | 2200 |
| Nemotron-Cascade-2-Reasoning | 17 | 10041 | 3563 | 3622 |
| Qwen3.8-GAIN-V1.1-IQ3_M | 69 | 6498 | 11995 | 4522 |
| Qwen3.6-Stock | 25 | 7827 | 12743 | 4830 |

Source: `state/evals/2026-09-25/r2.log` (group D).

## Table 4: planted-bug review, round 1 (8 bugs, 8192 cap) + structural build score

| Model | Review /8 | Review s | CSS rules | CSS props |
|---|---|---|---|---|
| Qwen3.6-35B-A3B-IQ4-Agent | 7/8 | 14 | 0 (no build) | 0 |
| Qwen3.8-27B-Q4-Quality | 0/8 | 73 | 0 (no build) | 0 |
| Qwen3.6-35B-A3B-IQ4-CoderFast | 7/8 | 2 | 37 | 171 |
| Qwen3.6-TwinTurbo-NeoMax-UnHeretic-IQ3_M | 7/8 | 18 | 95 | 135 |
| Qwen3.8-GAIN-V1.1-IQ3_M | 7/8 | 71 | 0 (no build) | 0 |
| Qwen3.8-27B-Stock-IQ3_S | 0/8 | 71 | 0 (no build) | 0 |
| Nail-Qwen3.6 | 7/8 | 13 | 103 | 151 |
| Qwen3-Coder-Stock-Q3_K_XL | 7/8 | 3 | 34 | 144 |
| Qwen3.6-Stock | 7/8 | 15 | 115 | 207 |
| Qwen3.6-APEX | 7/8 | 11 | 0 (no build) | 0 |
| TielCoder | 7/8 | 12 | 86 | 177 |
| Qwen3.8-TwinTurbo-Tools | 7/8 | 10 | 86 | 318 |
| Qwen3.8-TwinTurbo-NeoCoder-IQ3_M | 7/8 | 25 | 84 | 302 |
| Qwen3.8-Distill-APEX-Compact | 7/8 | 2 | 98 | 151 |
| Qwen3.8-Distill-APEX-Mini | 7/8 | 2 | 81 | 295 |
| Gemma-4-26B | 7/8 | 2 | 34 | 161 |
| Nemotron-Lightning-3.5 | 6/8 | 2 | 54 | 223 |
| Nemotron-Cascade-2 | 6/8 | 4 | 24 | 100 |
| Devstral-Small-2-Abliterated | 7/8 | 6 | 34 | 135 |
| CyberTiel-IQ3_XXS | 7/8 | 14 | 102 | 371 |
| Ornith-1.5-CoderX | 7/8 | 12 | 0 (no build) | 0 |
| Qwen3.8-Whittle-MoE | 6/8 | 10 | 0 (no build) | 0 |
| Qwen3.8-TwinTurbo-NeoMax-IQ3_M | 7/8 | 15 | 60 | 147 |
| Qwen3.6-Coder-Pruned-262K | 0/8 | 26 | 59 | 176 |
| Qwen3.6-Genesis-Hermes | 7/8 | 16 | 0 (no build) | 0 |
| Qwen3.6-Abliterated | 7/8 | 16 | 94 | 182 |
| Qwen3-Coder-Abliterated | 7/8 | 2 | 42 | 158 |
| Occult-Nail | 7/8 | 25 | 85 | 321 |
| MoziAI-Finance | 7/8 | 22 | 0 (no build) | 0 |
| Qwen3.8-Distill-APEX-Compact-Reasoning | 7/8 | 3 | 65 | 119 |
| Nemotron-Cascade-2-Reasoning | 6/8 | 8 | 20 | 122 |
| Nemotron-Lightning-3.5-Reasoning | 7/8 | 10 | 47 | 162 |
| Qwen3.5-9B-Aggressive | 0/8 | 68 | 121 | 394 |
| Qwen3.5-9B-Defiant-Fable | 7/8 | 47 | 96 | 310 |

Source: `state/evals/2026-09-25/full.log`.

## Table 5: planted-bug review, round 2 (12 bugs) + structural build score

| Model | Review /12 | Review s | CSS rules | CSS props |
|---|---|---|---|---|
| Qwen3.6-35B-A3B-IQ4-Agent | 10/12 | 21 | 144 | 525 |
| Qwen3.6-Stock | 11/12 | 23 | 93 | 160 |
| Nail-Qwen3.6 | 11/12 | 22 | 73 | 129 |
| Qwen3.8-Distill-APEX-Compact | 10/12 | 5 | 99 | 378 |
| Qwen3.6-APEX | 10/12 | 25 | 121 | 418 |
| TielCoder | 11/12 | 17 | 94 | 225 |
| Qwen3.8-TwinTurbo-Tools | 8/12 | 17 | 84 | 277 |
| Qwen3.8-TwinTurbo-NeoCoder-IQ3_M | 9/12 | 15 | 69 | 217 |
| Qwen3.6-TwinTurbo-NeoMax-UnHeretic-IQ3_M | 9/12 | 49 | 105 | 394 |
| Qwen3-Coder-Stock-Q3_K_XL | 5/12 | 3 | 0 (no build) | 0 |
| Qwen3.6-35B-A3B-IQ4-CoderFast | 6/12 | 6 | 0 (no build) | 0 |
| Gemma-4-26B | 9/12 | 5 | 36 | 158 |
| Nemotron-Lightning-3.5 | 8/12 | 4 | 72 | 253 |
| Qwen3.8-27B-Q4-Quality (group B, 2048 cap) | 12/12 | 36 | 157 | 365 |
| Qwen3.8-27B-Stock-IQ3_S (group B) | 11/12 | 33 | 146 | 272 |
| Qwen3.8-GAIN-V1.1-IQ3_M (group B) | 11/12 | 40 | 88 | 200 |
| Qwen3.6-35B-A3B-IQ4-Agent (group C, 768 cap) | 9/12 | 7 | 106 | 174 |

Source: `state/evals/2026-09-25/r2.log`.

## Table 6: planted-bug review, r6 (12 bugs, 262k/131k entries) + structural build score

| Model | Review /12 | CSS rules | CSS props |
|---|---|---|---|
| TielCoder-262K | 12/12 | 73 | 329 |
| AgentFast-262K | 10/12 | 149 | 497 |
| Quality-131K-ub1024 | 11/12 | 156 | 638 |
| Quality-163K | n/a (load_failed) | n/a | n/a |
| Nail-262K | 11/12 | 114 | 161 |
| CyberTiel-262K | 10/12 | 94 | 206 |
| MoziAI-262K | 11/12 | 113 | 479 |
| GAIN-163K | 11/12 | 136 | 264 |
| Occult-Nail | 10/12 | 113 | 179 |
| Ornith-CoderX | 2/12 | 10 | 38 |
| Genesis-Hermes | 10/12 | 120 | 452 |
| Abliterated | 9/12 | 135 | 454 |
| APEX-Mini | 9/12 | 57 | 110 |
| Defiant-Fable-9B | 8/12 | 120 | 430 |

Source: `state/evals/2026-09-26/r6-vram/results.jsonl` (and `r6.log` for the 2/12 and 8/12 FAIL flags).

## Table 7: repeat runs, r7 fleet-tidy (same model, three runs, 12-bug review)

| Model | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Genesis-Hermes (262k, ub512) | 10/12 | 9/12 | 10/12 |
| Occult-Nail-262K (ub1024) | 9/12 | 10/12 | 8/12 |
| Ornith-CoderX (262k, ub1024) | 8/12 | n/a | n/a |

Source: `state/evals/2026-09-26/r7-longctx/results.jsonl` (fleet-tidy rows).

## Table 8: r8 rebench (12-bug review) + structural

| Model | Review /12 | CSS rules | CSS props |
|---|---|---|---|
| Nail-Qwen3.6 | 10/12 | 97 | 165 |
| CyberTiel-IQ4 | 12/12 | 91 | 370 |
| Qwen3.8-GAIN-V1.1-IQ3_M | 9/12 | 151 | 684 |
| OrcaSAQ-2-27B-Uncensored | 10/12 | 215 | 390 |

Source: `state/evals/2026-09-30/r8-rebench/results.jsonl`.

## Table 9: r10 27B quality (12-bug review) + structural

| Model | Review /12 | CSS rules | CSS props |
|---|---|---|---|
| Q4XL-131K | 12/12 | n/a | n/a |
| IQ4XS-131K | 11/12 | 174 | 321 |
| IQ4XS-196K | 12/12 | 168 | 346 |
| IQ4XS-262K-q8-noMTP | 11/12 | 173 | 312 |
| IQ4XS-262K-q4 | 12/12 | 162 | 314 |

Source: `state/evals/2026-09-30/r10-27b-decode/results.jsonl`.

## Table 10: Strata IQ2_XS, reasoning budget held vs removed (same model, same harness)

| Run | Review /12 | Finish | Completion tokens |
|---|---|---|---|
| With budget (run.log) | 11/12 | stop | 19129 |
| No budget (run.nobudget.log) | 0/12 | length | 32000 |

Source: `state/evals/2026-10-02/r11-strata-iq2xs/run.log`, `run.nobudget.log`.

## Table 11: NInfer 27B, int8 vs a16 prefill mode (12-bug review)

| Arm | Single run | Repeat runs (5) |
|---|---|---|
| int8 | 10/12 | 11, 11, 10, 11, 12 |
| a16 | 12/12 | 9, 10, 11, 12, 12 |

Source: `state/evals/2026-10-03/r13-ninfer-int8/results.jsonl`, `review-repeat.log`.

## Table 12: NInfer vs llama.cpp control, same harness (r12)

| Model | Review /12 | CSS rules | CSS props |
|---|---|---|---|
| NInfer-Qwen3.8-27B | 10/12 | 148 | 327 |
| Qwen3.8-27B-Q4-Quality (llama.cpp) | 11/12 | 148 | 288 |

Source: `state/evals/2026-10-02/r12-ninfer/results.jsonl`.

## Table 13: DeepSWE, fixed 6-task subset seed 0 (Qwen3.8-27B-Q4-Quality)

| Run | Status | Passed | Binary | f2p | p2p | Partial |
|---|---|---|---|---|---|---|
| 1 | error (rc 130) | 0/0 | n/a | n/a | n/a | n/a |
| 2 | error (rc 137) | 0/0 | n/a | n/a | n/a | n/a |
| 3 | error (rc 137) | 0/0 | n/a | n/a | n/a | n/a |
| 4 | ok | 0/1 | n/a | n/a | n/a | n/a |
| 5 | ok | 0/1 | 0 | 40/43 | 109/109 | 0.9802631578947368 |

Source: `state/evals/2026-09-30/swe-iq4-196k/results.jsonl`.

## Table 14: program-verifier role suite, 2026-09-25 (17 tasks x 2 attempts per role)

| Role | Pass /34 | Failures |
|---|---|---|
| fast | 32/34 | configedit-rename-across-files (both attempts) |
| agent | 32/34 | configedit-rename-across-files (both attempts) |
| coder | 34/34 | none |
| review | 34/34 | none |

Overall 132/136, mean_seconds 3.2. Categories: lookup, tool-call, config-edit, bugfix, refusal, needle, json. Task content is lab-specific and not reproduced here.

Source: role-suite results JSON at the `state/evals/` root, dated 2026-09-25 (the filename contains a machine name, omitted here for privacy).

## Table 15: earlier single-turn suite (2026-09-23, 12 tasks x 2), as recorded in the deployed config header

| Model | Pass /24 |
|---|---|
| APEX-Mini | 24/24 |
| Coder-Pruned | 24/24 |
| GAIN | 24/24 |
| CyberTiel | 22/24 |
| APEX-Compact | 22/24 |
| Nemotron-Lightning | 16/24 |

The same models failed a real multi-turn build (see Table 4: Coder-Pruned 0/8; GAIN hit the length cap with no build; Mini skipped the tool call), the suite could not see it.

Source: `reference/llama-swap/config.yaml` (header comment, 2026-09-23).
