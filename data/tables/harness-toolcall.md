# Harness / tool-call measurements

Parser tolerance as a tunable: same model, same tasks, strict parser vs tolerant parser (`--tolerant-tool-calls`). Hardware: single 24 GB class RTX card.

## Table 1 — NInfer tool-call stress, strict vs tolerant parser (8 tasks x 2 rounds)

| Round | Task | Strict status | Strict t/s | Strict s | Tolerant status | Tolerant t/s | Tolerant s |
|---|---|---|---|---|---|---|---|
| 0 | 0 | fallback | 116.41815937475025 | 23 | ok | 123.52982561106242 | 15 |
| 0 | 1 | fallback | 122.49460594864347 | 17 | ok | 125.26703160483791 | 26 |
| 0 | 2 | ok | 118.28859285995406 | 40 | ok | 128.65773160854678 | 7 |
| 0 | 3 | ok (2 calls) | 117.15451038698896 | 4 | ok (3 calls) | 107.12441932990286 | 31 |
| 0 | 4 | fallback | 121.92572610358974 | 3 | ok | 124.08751777428449 | 3 |
| 0 | 5 | ok | 112.17643002462972 | 42 | ok | 116.16051029865837 | 45 |
| 0 | 6 | ok | 115.89975636905379 | 10 | ok | 120.20820757415505 | 4 |
| 0 | 7 | ok | 113.118329558204 | 23 | ok | 114.2519327638858 | 8 |
| 1 | 0 | ok | 114.78279005385752 | 17 | ok | 115.52585256744067 | 48 |
| 1 | 1 | fallback | 123.95889876232127 | 19 | ok | 133.6093189568116 | 4 |
| 1 | 2 | ok | 122.44813126291525 | 8 | ok | 157.5413941443424 | 2 |
| 1 | 3 | ok | 106.01917042270983 | 11 | ok | 99.6286521427277 | 4 |
| 1 | 4 | fallback | 114.75088547968203 | 3 | ok | 122.3809683271499 | 2 |
| 1 | 5 | ok | 117.11740618564674 | 40 | ok | 119.2610116196181 | 35 |
| 1 | 6 | ok | 117.12177948719797 | 5 | ok | 110.86107800790776 | 6 |
| 1 | 7 | ok | 126.91509493717847 | 5 | ok | 109.992222813788 | 40 |

Strict: 5/16 fallback (model emitted the call in text, parser rejected it — the emitted content contained `</parameter>` inside a parameter value, which closed the block early). Tolerant: 0/16.

Source: `state/evals/2026-10-03/ninfer-toolcall/results-strict.jsonl`, `results-tolerant.jsonl`.

## Table 2 — thinking-off / no-tool-call observations in the bakeoff harness

| Run | Model | Observation |
|---|---|---|
| Round 1 | Qwen3.6-35B-A3B-IQ4-CoderFast | NO TOOL CALL (finish=stop, answered in chat content) |
| Round 1 | Qwen3.8-Distill-APEX-Mini | NO TOOL CALL (finish=stop) |
| Round 2 | Qwen3-Coder-Stock-Q3_K_XL | NO TOOL CALL (2 completion tokens, finish=stop) |
| Round 2 | Qwen3.6-35B-A3B-IQ4-CoderFast | NO TOOL CALL (82 completion tokens, finish=stop) |
| r11 | Strata IQ2_XS (with budget) | NO TOOL CALL (finish=stop, 19129 completion tokens) |
| r11 | Strata IQ2_XS (no budget) | NO TOOL CALL (finish=length, 32000 completion tokens) |

Source: `state/evals/2026-09-25/full.log`, `state/evals/2026-09-25/r2.log`, `state/evals/2026-10-02/r11-strata-iq2xs/run.log`, `run.nobudget.log`.

## Table 3 — verifier-backed tool-call tasks, role suite 2026-09-25 (2 tasks x 2 attempts)

| Role | tool-call pass |
|---|---|
| fast | 4/4 |
| agent | 4/4 |
| coder | 4/4 |
| review | 4/4 |

Source: role-suite results JSON at the `state/evals/` root, dated 2026-09-25 (the filename contains a machine name, omitted here for privacy).
