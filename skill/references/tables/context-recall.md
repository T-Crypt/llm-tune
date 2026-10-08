# Context recall measurements

Needle-in-haystack: three planted facts at ~10% / 50% / 90% depth (prompt sizes 60,000 / 120,000 / 200,000 chars). Recall is found/total per depth. Hardware: single 24 GB class RTX card.

## Table 1: r7 long-context sweep (needle task)

| Model | ctx | -ub | Depth (prompt chars) | Found / total | Notes |
|---|---|---|---|---|---|
| TielCoder-262K | 262144 | 1024 | 60,000 | 3/3 | |
| TielCoder-262K | 262144 | 1024 | 120,000 | 3/3 | |
| TielCoder-262K | 262144 | 1024 | 200,000 | 3/3 | |
| AgentFast-262K | 262144 | 1024 | 60,000 | 3/3 | |
| AgentFast-262K | 262144 | 1024 | 120,000 | 3/3 | |
| AgentFast-262K | 262144 | 1024 | 200,000 | 3/3 | |
| Quality-131K-ub512 | 131072 | 512 | 60,000 | 3/3 | |
| Quality-131K-ub512 | 131072 | 512 | 120,000 | 0/3 | HTTP 400, prompt exceeds declared window |
| Quality-131K-ub1024 | 131072 | 1024 | 60,000 | 3/3 | |
| Quality-131K-ub1024 | 131072 | 1024 | 120,000 | 0/3 | HTTP 400, prompt exceeds declared window |

Source: `state/evals/2026-09-26/r7-longctx/results.jsonl`.

## Table 2: r7b, 27B dense models within their declared window

| Model | ctx | -ub | Depth (prompt chars) | Found / total |
|---|---|---|---|---|
| Quality-131K | 131072 | 512 | 60,000 | 3/3 |
| Quality-131K | 131072 | 512 | 120,000 | 3/3 |
| GAIN-163K | 163840 | 1024 | 60,000 | 3/3 |
| GAIN-163K | 163840 | 1024 | 120,000 | 3/3 |

Source: `state/evals/2026-09-26/r7b-27b-longctx/results.jsonl`.

## Table 3: r9 context ladder, 27B quant pair (needle, depths 60k / 120k / 200k chars)

| Entry | Quant | ctx | -ub | KV | MTP | 60k | 120k | 200k | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Q4XL-131K | Q4_K_XL | 131072 | 512 | q8_0 | yes | 3/3 | 3/3 | n/a | |
| IQ4XS-131K | IQ4_XS | 131072 | 512 | q8_0 | yes | 3/3 | 3/3 | n/a | |
| IQ4XS-196K | IQ4_XS | 196608 | 512 | q8_0 | yes | 3/3 | 3/3 | n/a | |
| IQ4XS-262K-q4 | IQ4_XS | 262144 | 512 | q4_0 | yes | 3/3 | 3/3 | 3/3 | |
| Q4XL-144K | Q4_K_XL | 147456 | 512 | q8_0 | yes | 3/3 | 3/3 | n/a | |
| Q4XL-152K | Q4_K_XL | 155648 | 512 | q8_0 | yes | 0/3 | 0/3 | n/a | crashed mid-run (server died at 24,142 MiB peak) |
| Q4XL-163K-noMTP | Q4_K_XL | 163840 | 512 | q8_0 | no | 3/3 | 3/3 | n/a | |
| IQ4XS-229K-noMTP | IQ4_XS | 229376 | 512 | q8_0 | no | 3/3 | 3/3 | 3/3 | |
| IQ4XS-262K-q8-noMTP | IQ4_XS | 262144 | 512 | q8_0 | no | 3/3 | 3/3 | 3/3 | |
| IQ4XS-262K-q8-noMTP-ub256 | IQ4_XS | 262144 | 256 | q8_0 | no | 3/3 | 3/3 | 3/3 | |

Source: `state/evals/2026-09-30/r9-27b-context/results.jsonl`.

## Table 4: Strata sparse-attention recall at depth (IQ2_XS MoE, synthetic service-log haystack, planted number)

| Variant | 32K prompt | 120K prompt | 240K prompt | 480K prompt | Recall |
|---|---|---|---|---|---|
| base 131K int8 | n/a | n/a | n/a | n/a | all depths |
| 262K int8 | yes | yes | yes | n/a | all |
| 262K q4_0 | yes | yes | yes | n/a | all |
| 262K q4_0 streamed | yes | yes | yes | n/a | all |
| 512K q4_0 streamed, yarn 2 | yes | yes | yes | yes | all |

Source: `state/evals/2026-10-03/strata-ctx/RESULTS.md`.

## Table 5: Strata 512k live check (deploy engine + PR #646 + #700, greedy, thinking off)

| Prompt tokens | Recall |
|---|---|
| 31,841 | yes |
| 119,233 | yes |
| 238,480 | yes |
| 476,820 | yes |

Source: `state/evals/2026-10-03/strata-512k-live/RESULTS.md`.

## Table 6: Strata PR #646 A/B, same variant (kv-q4-262k), two arms x two runs

| Arm | 32K prompt | 120K prompt |
|---|---|---|
| main run 1 | recall True | recall True |
| pr646 run 1 | recall True | recall True |
| main run 2 | recall True | recall True |
| pr646 run 2 | recall True | recall True |

Source: `state/evals/2026-10-03/strata-pr646/ab.log`.

## Table 7: Strata k8v4 KV variants, recall at 32K / 119K / 238K

| Variant | 32K | 119K | 238K |
|---|---|---|---|
| k8v4-262k-res (streamed) | yes | yes | yes |
| k8v4-262k (in VRAM) | yes | yes | yes |
| q4-262k-res-p (streamed) | yes | yes | yes |
| q4-512k-yarn-res-p | n/a | yes | yes (477K: yes) |

Source: `state/evals/2026-10-03/strata-k8v4/sweep.jsonl`.
