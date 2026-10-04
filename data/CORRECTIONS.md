# Corrections (flight 2)

Where a number in `data/FINDINGS-DRAFT.md` disagreed with the extracted tables. Findings updated in place; original claim kept here.

| # | Finding | Old claim | New claim | Source |
|---|---|---|---|---|
| 2 | MTP cost | "+0.42 GiB per quant (~the next quant tier up)" | The +0.42 GiB is flat across all quants, but it is not a tier step: the tier steps in the same table range from 0.47 GiB (Q4_K_S -> Q4_K_M) to 5.77 GiB (Q6_K -> Q8_0). +0.42 GiB matches only the smallest sub-tier step. The source's "next quant tier up" phrasing is not supported by its own size table. | `state/evals/2026-09-25/gain-research.md` (Note 1b) |
| 10 | int8 prefill quality | "perplexity identical to 4 decimal places" | Overall ppl is identical to 3 decimal places only: 4.651185 (a16) vs 4.651710 (int8) — they differ at the 4th. Per-domain values differ at the 3rd-4th decimal. | `state/evals/2026-10-03/ninfer-int8-prefill/ppl-a16.txt`, `ppl-int8.txt` |
| 27 | Host RAM peak | "28 GB peak observed" | 28,289 MiB = 27.63 GiB. Stated as MiB to avoid the GiB/GB ambiguity the source itself flags in Note 1d. | `state/evals/2026-10-02/r11-strata-iq2xs/results.nobudget.jsonl` |
| 30 | Quality-per-second tie | "69 s vs 280 s at equal quality" | The round-1 tie (C 41 vs D 40) was timed 69 s (GAIN) vs 209 s (Q4-Quality) in r2.log group D. The 280 s figure belongs to the r3 27B-Research run added in the re-rank, not to the tied pair. | `state/evals/2026-09-25/r2.log` (group D), `state/evals/2026-09-25/think-ranking.md` |

No other finding numbers conflicted with the extracted tables.
