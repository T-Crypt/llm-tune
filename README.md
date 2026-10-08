# llm-tune

llm-tune is a Claude skill that teaches Claude how to tune local LLMs — engine
flags, quantization, KV cache, context size, sampling, and harness settings —
for other people's hardware. Unlike existing tools that optimize for "fits" or
tok/s (llama.cpp `--fit` / `llama-fit-params`, llama-optimus, llm-server
Smart-Launcher, generic hardware-heuristic skills), llm-tune is QUALITY-aware:
it recommends settings backed by measured evidence — recall at depth, bench
scores, agent/harness behaviour, and documented failure modes and traps.

Status: **flight 6 (post-flight 6): skill v0.2** — written against the measured evidence, bench fixes from a
live run on 2026-10-05, plus an Apple Silicon / MLX section that is documented from cited
sources and not measured here. Local until tested; nothing is released. Every measured number
is from one machine class (24 GB card, 31 GB RAM), so the skill hands the user a bench to run
on their own box.

## Contributing

The evidence base is thin on hardware diversity — every number was measured on one
24 GB RTX 4090-class card with 31 GB RAM. **Your measurements make the tuning advice better
for everyone.** See `CONTRIBUTING.md` for the submission template, quality standards, and
what kinds of data are most valuable (cards we don't have, recall at depth from other hardware,
multi-user serving, Apple Silicon measurements). You can submit via a GitHub issue using the
Measurement Report template, or a PR tagged `data-submission`.

## Layout

| Path | Contents |
|---|---|
| `skill/SKILL.md` | The skill: intake, decision procedure, verification, traps, what it does not know |
| `skill/bench/` | The user-side bench — commands plus three stdlib scripts (needle, quality probe, MLX fit estimate) |
| `skill/references/evidence.md` | Index from each decision step to the tables and findings behind it |
| `skill/references/apple-mlx.md` | Apple Silicon / MLX — documented from cited sources, not measured here |
| `skill/references/hardware-tiers.md` | Every hardware class — 8 GB Intel Arc through 512 GB Mac Studio and DGX clusters (sourced, externally verified) |
| `skill/references/engine-backends.md` | Per-backend fit arithmetic, commands, and traps (CUDA, SYCL, Vulkan, HIP/ROCm, MLX/Metal, Ollama, vLLM) |
| `skill/references/harnesses.md` | Harness-specific tuning — Pi, OMP, Claude-local, OpenCode, Claude Code (Infralovers 2026 benchmark) |
| `skill/references/debloat.md` | Harness debloat, MCP compression (Atlassian: 17,600→500 tokens), per-tier tool limits |
| `skill/references/safety.md` | Validate-with-operator protocol, model/file deletion safety |
| `skill/references/llama-fit-broadening.md` | llama-fit-params across all backends (CUDA, SYCL, Vulkan, HIP/ROCm, Metal), broadening beyond NVIDIA |
| `skill/references/user-journeys.md` | 5 entry-state workflows from "I have no models" to "pushing the frontier" |
| `skill/references/model-management.md` | HF CLI download, model inventory template, deletion safety |
| `skill/references/vllm-local.md` | vLLM tuning for 2–3 endpoint local serving, multi-model, cluster |
| `skill/references/mlx-mac-tuning.md` | MLX + unified memory, all Mac tiers (M6 through M5 Ultra 512 GB), wired limit, 75% rule |
| `skill/references/intel-amd-unified.md` | Intel Arc SYCL/Vulkan, AMD Strix/Gorgon Halo HIP/ROCm, BIOS allocation, bandwidth reality |
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
- **Hardware tier data** in `references/hardware-tiers.md` and per-engine advice in
  `references/engine-backends.md` are sourced from external verification (web sources, community
  reports, official docs) but **not measured in this repo**. Every tier number must be verified
  on the user's own box before quoting.
