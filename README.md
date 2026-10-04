# llm-tune

llm-tune is a Claude skill that teaches Claude how to tune local LLMs — engine
flags, quantization, KV cache, context size, sampling, and harness settings —
for other people's hardware. Unlike existing tools that optimize for "fits" or
tok/s (llama.cpp `--fit` / `llama-fit-params`, llama-optimus, llm-server
Smart-Launcher, generic hardware-heuristic skills), llm-tune is QUALITY-aware:
it recommends settings backed by measured evidence — recall at depth, bench
scores, agent/harness behaviour, and documented failure modes and traps.

Status: **flight 1: inventory** — the evidence base is being catalogued; tuning
advice itself is not written yet.

## Layout

| Path | Contents |
|---|---|
| `skill/SKILL.md` | The skill itself (skeleton; sections are TODOs until flight 2) |
| `data/INVENTORY.md` | Catalogue of the source evidence: what was measured, how, headline numbers, usefulness tag |
| `data/FINDINGS-DRAFT.md` | The most generalisable lessons pulled from the inventory |

Usefulness tags in the inventory: `FINDING` (generalisable lesson), `DATA`
(raw measurements worth tabulating), `LOCAL-ONLY` (specific to the source lab,
skip).
