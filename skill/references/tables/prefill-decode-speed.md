# Prefill and decode speed measurements

Hardware: single 24 GB class RTX card. t/s as logged; runs listed where the source recorded repeats.

## Table 1: NInfer prefill activations, same artifact (qwen3.8-27b groupwise-int), three runs per target

| Mode | Target tokens | Prompt tokens | Prefill t/s | Runs |
|---|---|---|---|---|
| a16 | 8,192 | 6,233 | 2194.2 | 2195.0 / 2193.7 / 2194.0 |
| a16 | 32,768 | 25,263 | 2090.5 | 2091.9 / 2090.2 / 2089.4 |
| a16 | 65,536 | 51,465 | 1940.3 | 1941.2 / 1940.2 / 1939.4 |
| int8 | 8,192 | 6,232 | 3737.3 | 3740.3 / 3735.6 / 3736.0 |
| int8 | 32,768 | 25,262 | 3505.2 | 3506.1 / 3504.8 / 3504.8 |
| int8 | 65,536 | 51,464 | 3104.3 | 3105.2 / 3104.8 / 3102.9 |
| llamacpp-q4quality | 8,192 | 6,233 | 2782.2 | 2770.4 / 2787.1 / 2789.0 |
| llamacpp-q4quality | 32,768 | 25,263 | 2676.3 | 2676.6 / 2677.7 / 2674.7 |
| llamacpp-q4quality | 65,536 | 51,465 | 2410.8 | 2413.4 / 2410.6 / 2408.5 |

Source: `state/evals/2026-10-03/ninfer-int8-prefill/prefill.jsonl`.

## Table 2: perplexity held constant across the two NInfer modes (corpus ninfer-ppl-1m-v1, full, context/stride 4096/2048, kv int8-g64)

| Domain | Tokens | mean_nll a16 | ppl a16 | mean_nll int8 | ppl int8 |
|---|---|---|---|---|---|
| chinese_reference | 262,022 | 1.720528 | 5.587478 | 1.720717 | 5.588534 |
| english_long_form | 261,408 | 2.069748 | 7.922827 | 2.070097 | 7.925588 |
| english_reference | 261,223 | 1.850127 | 6.360625 | 1.849804 | 6.358572 |
| ninfer_code | 259,904 | 0.501920 | 1.651891 | 0.502157 | 1.652282 |
| overall | 1,044,557 | 1.537122 | 4.651185 | 1.537235 | 4.651710 |

Scoring rate: a16 1111.7 tok/s, int8 1961.4 tok/s.

Source: `state/evals/2026-10-03/ninfer-int8-prefill/ppl-a16.txt`, `ppl-int8.txt`.

## Table 3: bakeoff decode t/s per run (single-file build + 12-bug review harness, llama.cpp entries)

| Run | Model | ctx | -ub | Decode t/s |
|---|---|---|---|---|
| r6 | TielCoder-262K | 262144 | 1024 | 279 |
| r6 | AgentFast-262K | 262144 | 1024 | 306 |
| r6 | Quality-131K-ub1024 | 131072 | 1024 | 108 |
| r6 | Nail-262K | 262144 | 1024 | 301 |
| r6 | CyberTiel-262K | 262144 | 1024 | 260 |
| r6 | MoziAI-262K | 262144 | 1024 | 173 |
| r6 | GAIN-163K | 163840 | 1024 | 83 |
| r6 | Occult-Nail | 131072 | 1024 | 174 |
| r6 | Ornith-CoderX | 262144 | 1024 | 255 |
| r6 | Genesis-Hermes | 262144 | 512 | 311 |
| r6 | Abliterated | 262144 | 1024 | 324 |
| r6 | APEX-Mini | 262144 | 1024 | 318 |
| r6 | Defiant-Fable-9B | 262144 | 512 | 96 |
| r8 | Nail-Qwen3.6 | 131072 | 1024 | 275 |
| r8 | CyberTiel-IQ4 | 131072 | 1024 | 263 |
| r8 | Qwen3.8-GAIN-V1.1-IQ3_M | 131072 | 1024 | 76 |
| r8 | OrcaSAQ-2-27B-Uncensored | 131072 | 512 | 111 |
| r10 | Q4XL-131K | 131072 | 512 | 105 |
| r10 | IQ4XS-131K | 131072 | 512 | 111 |
| r10 | IQ4XS-196K | 196608 | 512 | 115 |
| r10 | IQ4XS-262K-q8-noMTP | 262144 | 512 | 52 |
| r10 | IQ4XS-262K-q4 | 262144 | 512 | 119 |
| r12 | NInfer-Qwen3.8-27B | 262144 | 512 | 130 |
| r12 | Qwen3.8-27B-Q4-Quality (llama.cpp control) | 196608 | 512 | 118 |
| r13 | NInfer-Qwen3.8-27B, int8 prefill | 262144 | 512 | 121 |
| r13 | NInfer-Qwen3.8-27B, a16 prefill | 262144 | 512 | 129 |
| r11 | Strata IQ2_XS | 131072 | n/a | 156 |
| r11 | Strata IQ2_XS (no-budget run) | 131072 | n/a | 148 |

Sources: `state/evals/2026-09-26/r6-vram/results.jsonl`, `state/evals/2026-09-30/r8-rebench/results.jsonl`, `state/evals/2026-09-30/r10-27b-decode/results.jsonl`, `state/evals/2026-10-02/r12-ninfer/results.jsonl`, `state/evals/2026-10-03/r13-ninfer-int8/results.jsonl`, `state/evals/2026-10-02/r11-strata-iq2xs/results.jsonl` + `results.nobudget.jsonl`.

## Table 4: prefill t/s at depth, llama.cpp needle runs (60k / 120k / 200k char prompts)

| Model | ctx | -ub | 60k | 120k | 200k |
|---|---|---|---|---|---|
| TielCoder-262K | 262144 | 1024 | 6498 | 5068 | 3981 |
| AgentFast-262K | 262144 | 1024 | 6622 | 5111 | 4005 |
| Quality-131K-ub512 | 131072 | 512 | 2186 | n/a (400) | n/a |
| Quality-131K-ub1024 | 131072 | 1024 | 2186 | n/a (400) | n/a |
| Quality-131K (r7b) | 131072 | 512 | 2279 | 1852 | n/a |
| GAIN-163K | 163840 | 1024 | 2213 | 1809 | n/a |
| Q4XL-131K | 131072 | 512 | 2286 | 1866 | n/a |
| IQ4XS-131K | 131072 | 512 | 2358 | 1913 | n/a |
| IQ4XS-196K | 196608 | 512 | 2356 | 1911 | n/a |
| IQ4XS-262K-q4 | 262144 | 512 | 2357 | 1915 | 1518 |
| Q4XL-144K | 147456 | 512 | 2277 | 1860 | n/a |
| Q4XL-152K | 155648 | 512 | n/a (crashed) | n/a | n/a |
| Q4XL-163K-noMTP | 163840 | 512 | 2428 | 1983 | n/a |
| IQ4XS-229K-noMTP | 229376 | 512 | 2493 | 2030 | 1624 |
| IQ4XS-262K-q8-noMTP | 262144 | 512 | 2524 | 2045 | 1632 |
| IQ4XS-262K-q8-noMTP-ub256 | 262144 | 256 | 2319 | 1888 | 1511 |

Sources: `state/evals/2026-09-26/r7-longctx/results.jsonl`, `state/evals/2026-09-26/r7b-27b-longctx/results.jsonl`, `state/evals/2026-09-30/r9-27b-context/results.jsonl`.

## Table 5: Strata read t/s and decode-at-depth (IQ2_XS MoE, 31 GB class RAM box)

| Variant | Short decode t/s | 32K read / decode@depth | 119-120K | 238-240K | 477K |
|---|---|---|---|---|---|
| base 131K int8 | 125.1 | 4,157 / 97.8 | 4,225 / 124.4 | - | n/a |
| 262K int8 | 112.6 | 3,946 / 89.9 | 3,987 / 116.0 | 3,755 / 105.5 | n/a |
| 262K q4_0 (chosen) | 116.4 | 3,985 / 103.3 | 4,006 / 115.7 | 3,767 / 112.6 | n/a |
| 262K q4_0 streamed, `--prefill auto:32768` | 117.9 | 1,744 / 93.7 | 3,082 / 110.8 | 1,336 / 104.3 | n/a |
| 512K q4_0 streamed yarn 2, `--prefill auto:32768` | 118.2 | 711 / 92.8 | 1,073 / 106.7 | 1,151 / 115.2 | 1,147 / 92.6 (480K) |
| 262K q4_0 streamed, default `--prefill auto` | 117.8 | 4,090 / 99.9 | 4,045 / 108.2 | 3,796 / 120.1 | n/a |
| 512K q4_0 streamed yarn 2, default `--prefill auto` | 120.2 | - | 3,664 / 91.0 | n/a | 3,085 / 85.0 |
| 262K k8v4 streamed | 126.2 | 3,935 / 99.8 | 3,960 / 116.4 | 3,659 / 108.2 | n/a |
| 262K k8v4 in VRAM | 117.7 | 3,879 / 92.8 | 3,870 / 114.2 | 3,658 / 111.0 | n/a |

Source: `state/evals/2026-10-03/strata-ctx/RESULTS.md` (main table + 2026-10-03 correction), `state/evals/2026-10-03/strata-k8v4/sweep.jsonl`.

## Table 6: Strata 512k live check (default prefill, deploy engine + PR #646 + #700)

| Prompt tokens | Read time (s) | Prefill t/s | Decode t/s at depth |
|---|---|---|---|
| 31,841 | 15.1 | 2,133 (cold first request) | 112.9 |
| 119,233 | 32.0 | 3,748 | 131.0 |
| 238,480 | 64.8 | 3,444 | 121.8 |
| 476,820 | 154.6 | 2,990 | 111.3 |

Source: `state/evals/2026-10-03/strata-512k-live/RESULTS.md`.

## Table 7: Strata PR #646 A/B, arm by arm (kv-q4-262k, alternating arms)

| Arm | Run | 32K read t/s | 32K decode@depth | 120K read t/s | 120K decode@depth | Short decode t/s | RAM after (GiB) |
|---|---|---|---|---|---|---|---|
| main | 1 | 3990.5 | 103.7 | 4002.4 | 115.4 | 117.0 | 3.34 |
| pr646 | 1 | 3987.9 | 112.0 | 4032.8 | 133.5 | 121.9 | 3.97 |
| main | 2 | 4001.5 | 103.5 | 4007.3 | 115.4 | 115.3 | 4.06 |
| pr646 | 2 | 3994.6 | 112.2 | 4038.9 | 133.7 | 121.9 | 3.92 |

Source: `state/evals/2026-10-03/strata-pr646/ab.log`.

## Table 8: short-prompt bench, same Strata model at two configs

| Config | code | reason | agent |
|---|---|---|---|
| 131K int8 (live install v0.1.33) | 142 | 162 | 138 |
| 262K q4_0 (live install v0.1.33) | 129.1 | 141.4 | 122.1 |
| 512K live check (0.1.38 + #646 + #700) | 131.8 | 157.9 | 133.1 |
| 262K config, same live check | 139.5 | 154.3 | 133.6 |
| 512K, 0.1.39 headroom 4 (default) | 142.2 | 155.2 | 140.4 |
| 512K, 0.1.39 headroom 6 (deployed) | 132.2 | 154.5 | 138.1 |

Run-to-run spread inside each arm is +-20 t/s, so short-prompt decode is a wash; the long-prompt
difference is the one that held across depths.

Source: `state/evals/2026-10-03/strata-ctx/RESULTS.md`, `state/evals/2026-10-03/strata-512k-live/RESULTS.md`, `state/evals/2026-10-04/strata-0139-512k/RESULTS.md`.
