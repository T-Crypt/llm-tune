# llm-tune

**Quality-aware tuning for local LLMs — on hardware you actually have.**

llm-tune teaches your agent to tune local models the way a senior engineer would: measure before changing, understand why a setting works, and know when the numbers lie. Not "which quant fits" — **why it fits, what it costs, and what breaks first**.

Unlike existing tools that optimise for "fits" or tok/s (llama.cpp `--fit`, llama-optimus, llm-server Smart-Launcher, generic hardware-heuristic skills), llm-tune is **quality-aware**: it recommends settings backed by measured evidence — recall at depth, bench scores, agent behaviour, and documented failure modes and traps.

> **Flight 6 (post-flight 6): skill v0.2** — written against measured evidence and bench fixes from a live run on 2026-10-05. Local until tested; nothing is released. Every measured number is from one machine class (24 GB card, 31 GB RAM), so the skill hands you a bench to run on your own box.

---

## What it does

The skill is a 9-step decision procedure. At each step: the rule, the evidence, the trap, and how to verify.

| Step | What it decides | Why it matters |
|---|---|---|
| **1 — Fit** | VRAM, runtime, and host RAM | Load-time fit ≠ runtime fit. A model that loads can OOM mid-inference as buffers grow with depth. |
| **2 — Context vs quant** | The actual lever | Every 32k of context is worth a quant tier — but declared context is not usable context (HTTP 400 at depth is silent). |
| **3 — KV cache type** | Whether KV quantisation is your lever | Architecture-dependent: on a dense 27B only 16/64 layers carry growing KV; on a hybrid MoE, 6 + 23 layers cost 1.50 GiB. |
| **4 — Offload and MoE** | Where the model lives | Decode speed is architecture-bound, not quant-bound. MoE entries hit 246–324 t/s vs ~52–119 t/s for dense 27B on the same card. |
| **5 — Prefill and ubatch** | Chunking strategy | `-ub 1024` gained +31–34% on MoE, zero gain on dense 27B — hardware-class dependent, not universal. |
| **6 — Speculative / MTP** | Draft head depth | Flat +0.42 GiB cost. Optimal depth is workload-dependent: d3 best overall, d5 best prose, d3 best code. |
| **7 — Sampling and reasoning** | Per-model config | **Read this model's own card.** Vendor specs don't transfer. `--reasoning-budget -1` produces 20k-token thinking loops with no output. |
| **8 — Harness and client** | Agent-level settings | Tool-call parsing tolerance turned 5/16 failures into 0/16 — without touching the model. |
| **9 — Non-NVIDIA** | Apple Silicon, Intel Arc, AMD, vLLM | Every backend has different memory accounting, flag names, and traps. Fit arithmetic is universal; the rest is not. |

**Verification** is built in: hold quality constant, check recall at depth (not declared window), run three repeats, alternate arms A/B, one model on the GPU at a time, and grade `finish=length` separately from fail.

---

## Supported agents

llm-tune ships as a **skill** — a self-contained instruction file (`skill/SKILL.md`). Any agent that can load a skill or rules file can use it. Install instructions per agent:

### Claude Code (primary)

The skill is written for Claude Code. Copy `skill/SKILL.md` into your skills directory:

```bash
# Global install (every project)
mkdir -p ~/.claude/skills/llm-tune && cp -r skill/SKILL.md skill/bench/ skill/references/ ~/.claude/skills/llm-tune/

# Or project-scoped
mkdir -p .claude/skills/llm-tune && cp -r skill/SKILL.md skill/bench/ skill/references/ .claude/skills/llm-tune/
```

The `bench/` directory is the user-side verification toolkit — run it before quoting any number as yours.

### OpenCode

```bash
# As a plugin (if available)
opencode plugin add <path-to-llm-tune>

# Or manually: copy SKILL.md into the OpenCode skills path, or set
# the OPENCODE_SKILLS_PATH env var to point at this repo's skill/ directory.
```

The harness-specific tuning in `skill/references/harnesses.md` includes OpenCode-specific context.

### Claude Code via OpenCode

Both paths work simultaneously. OpenCode loads the skill; Claude Code provides the plan/sub-agent context. See `skill/references/local-orchestration.md` for the LOCAL.md command-frontier pattern.

### Pi agent / Oh My Pi (OMP)

Copy `skill/SKILL.md` into the Pi/OMP skills directory. Harness-specific tuning is in `skill/references/harnesses.md` — Pi and OMP need different tuning priorities than Claude Code (tool-call reliability over raw speed).

### Any other agent

1. Read `skill/SKILL.md` — it is self-contained (intake → decision procedure → verification → traps → limitations).
2. Copy `skill/references/` into your agent's reference path, or load the files that match your hardware and engine.
3. Run `skill/bench/` before quoting any figure.

**Agents confirmed compatible by format**: Claude Code, Codex, Cursor (rules file), Windsurf (rules file), GitHub Copilot (instructions file), Cline, Kiro, Qoder, Gemini CLI, Hermes Agent, Devin CLI. Agents that read `AGENTS.md` or a rules file get the full skill; agents with skill-system support get the structured procedure.

> **Missing your agent?** The install instructions above are a starting point. If your agent supports skills natively, point it at `skill/SKILL.md`. If it reads a rules file, copy `skill/SKILL.md` into it. If you need per-agent documentation, open an issue — `CONTRIBUTING.md` has the submission template.

---

## The bench — verify before you quote

Every number in this skill is from one machine class (24 GB RTX 4090-class card, 31 GB RAM). On any other box, run the bench before quoting a figure as yours.

```bash
cd skill/bench && bash quick_bench.md
```

What it measures:
1. **Memory accounting** — what the engine actually reserves (model file, KV buffer, compute buffer, draft head), not what arithmetic predicts.
2. **Peak VRAM and host RAM per run** — load-time fit ≠ runtime fit.
3. **Prefill and decode at depth** — same prompt sizes at ~10/50/90% depth, three runs each.
4. **Recall at depth** — three planted facts, scored found/total. A declared window is not a usable window.
5. **Quality probe with repeats** — planted-bug review, five runs, so run-to-run noise is visible (±1–2 bugs on a 12-bug test is normal).

Stdlib-only scripts: `needle.py`, `quality_probe.py`, `mlx_quant_search.py` (Apple Silicon estimates). All work against any OpenAI-compatible server.

---

## Layout

Organised by what it *does*, not by where it lives.

### The skill

| Path | Contents |
|---|---|
| `skill/SKILL.md` | The full decision procedure: intake, 9 steps, verification, traps, limitations |
| `skill/bench/` | User-side verification toolkit — commands + scripts (needle, quality probe, MLX estimate) |
| `skill/bench/README.md` | What the bench measures, rules for readable numbers, live-test fixes |

### Reference library

| Path | Contents |
|---|---|
| `skill/references/evidence.md` | Index: each decision step → the tables and findings behind it |
| `skill/references/hardware-tiers.md` | Every hardware class — 8 GB Intel Arc through 512 GB Mac Studio and DGX clusters (externally sourced, verify on your box) |
| `skill/references/engine-backends.md` | Per-backend fit arithmetic, commands, and traps (CUDA, SYCL, Vulkan, HIP/ROCm, MLX/Metal, Ollama, vLLM) |
| `skill/references/engine-research-sm89.md` | sm_89 (RTX 4090) engine coverage — vLLM, TensorRT-LLM, FlashInfer, SGLang, NInfer, TokenSpeed |
| `skill/references/harnesses.md` | Harness-specific tuning — Pi, OMP, Claude-local, OpenCode, Claude Code (Infralovers 2026 benchmark) |
| `skill/references/debloat.md` | MCP compression (Atlassian: 17,600 → 500 tokens), per-tier tool limits |
| `skill/references/safety.md` | Validate-with-operator protocol, model/file deletion safety |
| `skill/references/local-orchestration.md` | LOCAL.md pattern — chunk AGENTS.md into a ~4096-token local model command frontier |
| `skill/references/user-journeys.md` | 5 entry-state workflows from "I have no models" to "pushing the frontier" |
| `skill/references/model-management.md` | HF CLI download, model inventory template, deletion safety |
| `skill/references/vllm-local.md` | vLLM tuning for 2–3 endpoint local serving, multi-model, cluster |
| `skill/references/mlx-mac-tuning.md` | MLX + unified memory, all Mac tiers (M6 through M5 Ultra 512 GB), wired limit, 75% rule |
| `skill/references/intel-amd-unified.md` | Intel Arc SYCL/Vulkan, AMD Strix/Gorgon Halo HIP/ROCm, BIOS allocation, bandwidth reality |
| `skill/references/apple-mlx.md` | Apple Silicon / MLX — documented from cited sources, not measured here |
| `skill/references/llama-fit-broadening.md` | llama-fit-params across all backends (CUDA, SYCL, Vulkan, HIP/ROCm, Metal) |
| `skill/references/findings.md` | 32 generalisable lessons, each with source citation |
| `skill/references/CORRECTIONS.md` | Where findings disagreed with extracted data — corrections win over findings |
| `skill/references/tables/` | Measurements extracted from DATA-tagged sources, one table per measurement set |

### Data and evidence

| Path | Contents |
|---|---|
| `data/INVENTORY.md` | Catalogue of every source: what was measured, how, headline numbers, usefulness tag (`FINDING`, `DATA`, `LOCAL-ONLY`) |
| `CITED.md` | 50 external sources, every one verified live 2026-10-08, with what was extracted and which file uses it |

### Contribution

| Path | Contents |
|---|---|
| `CONTRIBUTING.md` | Submission template, quality standards, ranked data needs, what happens after you submit |
| `.github/ISSUE_TEMPLATE/measurement-report.md` | GitHub issue template for quick data submissions |

---

## Evidence & honesty

This skill makes claims it can defend and says clearly when it can't.

**What IS backed by measurement** (one 24 GB RTX 4090-class card, 31 GB RAM, llama.cpp b11115 / llama-swap v257):

- Fit arithmetic: model + KV + compute + context + overhead
- Recall at depth failures (declared context ≠ usable context)
- Prefill/decode speed at depth, with repeats
- MTP tensor cost and draft acceptance rates
- Harness tool-call parsing behaviour
- KV cache architecture dependence

**What is NOT backed by measurement in this repo** — and how to contribute:

| Unmeasured | Status | How to fill the gap |
|---|---|---|
| Hardware diversity | Every tier in `hardware-tiers.md` is sourced externally, not measured here | Submit fit/crash data via `CONTRIBUTING.md` — most valuable contribution |
| Apple Silicon / MLX | Documented from cited sources, zero Apple runs | Even one load test + recall check fills the biggest gap |
| Intel Arc / AMD | SYCL, HIP/ROCm, Vulkan — all external sources | Submit engine-specific traps and fit data |
| Multi-user serving | Completely unmeasured | Batching, cache contention, concurrent models |
| Bench scripts | Marked "(untested here)" | The measurement *patterns* are proven; the specific commands are generic llama.cpp |
| Ollama, LM Studio | Method and traps only, no numbers | What transfers: fit arithmetic, quality method, recall check, harness traps |

> **The single most valuable contribution** is a fit/crash measurement on hardware we don't have — especially recall-at-depth from other hardware classes. See `CONTRIBUTING.md` for the ranked list and submission template.

---

## Contributing

The evidence base is thin on hardware diversity — **your measurements make the tuning advice better for everyone.**

- **Submit measurements** via GitHub issue (Measurement Report template) or PR tagged `data-submission`
- **Ranked priorities**: fit/crash data from new hardware → recall at depth from other machines → quality probes with repeats → engine-specific traps → Apple Silicon measurements → multi-user serving data
- **Quality standards**: three runs minimum, no rounding before submission, record `finish_reason`, alternating arms for A/B, one model on the GPU at a time
- **Honesty policy**: we do not accept fabricated data. "Not measured on my hardware" is better than an estimate.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full submission template, quality standards, and what happens after you submit.

---

## Trap of the day

*A process that is not the model server holding VRAM is the bug.* A background session loading a model spoiled an entire sweep. On a shared desktop compositor, that 11.3 GiB squatter is waiting for you too. Check `nvidia-smi --query-compute-apps=pid,process_name,used_memory` before every run.

More traps in `skill/SKILL.md` §4 — eleven in total, each sourced from a measurement that went wrong.

---

## Licence

[MIT](LICENSE).
