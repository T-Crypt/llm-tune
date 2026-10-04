# llm-tune

llm-tune is a Claude skill that teaches Claude how to tune local LLMs — engine
flags, quantization, KV cache, context size, sampling, and harness settings —
for other people's hardware. Unlike existing tools that optimize for "fits" or
tok/s (llama.cpp `--fit` / `llama-fit-params`, llama-optimus, llm-server
Smart-Launcher, generic hardware-heuristic skills), llm-tune is QUALITY-aware:
it recommends settings backed by measured evidence — recall at depth, bench
scores, agent/harness behaviour, and documented failure modes and traps.

Status: **flight 3: skill v0.1** — the skill is written against the measured evidence.
Local until tested; nothing is released. Every number is from one machine class (24 GB
card, 31 GB RAM), so the skill hands the user a bench to run on their own box.

## Layout

| Path | Contents |
|---|---|
| `skill/SKILL.md` | The skill: intake, decision procedure, verification, traps, what it does not know |
| `skill/bench/` | The user-side bench — commands to run on their own hardware |
| `skill/references/evidence.md` | Index from each decision step to the tables and findings behind it |
| `data/INVENTORY.md` | Catalogue of the source evidence: what was measured, how, headline numbers, usefulness tag |
| `skill/references/findings.md` | The most generalisable lessons pulled from the inventory |
| `skill/references/tables/` | Measurements extracted from the DATA-tagged sources, one table per measurement set |
| `skill/references/CORRECTIONS.md` | Where the findings disagreed with the extracted data; corrections win over findings |

Usefulness tags in the inventory: `FINDING` (generalisable lesson), `DATA`
(raw measurements worth tabulating), `LOCAL-ONLY` (specific to the source lab,
skip).

## Not backed by evidence

Rules in the skill that are method or judgement, not measurements:

- The intake order, and "pick the metric before tuning".
- "Three repeats minimum" — the lab used 3 and 5 runs; no measurement sets 3 as a threshold.
- The fit gate (22,900 MiB) is a lab convention, not a measured optimum.
- Multi-user serving, batching, cache contention, long-horizon agent behaviour: unmeasured.
- "Method transfers, numbers do not" for engines we never measured (Ollama, LM Studio, vLLM).
- The bench scripts and the llama-bench flag list are unrun here — marked "(untested here)".
- The idea that a partial CPU offload "costs more t/s than the quant gains back" was the
  source's expectation; the measured part is only the direction (more offload, less speed).
