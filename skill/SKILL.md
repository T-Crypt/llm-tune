---
name: llm-tune
description: Use when the user wants to tune, size, or choose settings for a local LLM: quant, context window, KV cache, offload, speculative decoding / MTP, sampling, reasoning budget, or harness and client settings. Also use when a local model OOMs, truncates, loses recall at depth, or skips tool calls. Quality-aware tuning: fit is necessary but not sufficient.
---

# llm-tune

Tuning a local model is a chain of
budget decisions (VRAM, host RAM, context, KV, draft head) followed by a quality check
(recall at depth, tool-call reliability, verifier-backed output), and the two can disagree.
The biggest quant that fits is only the first gate.

**Evidence base:** every number here was measured on ONE machine class: a 24 GB RTX
4090-class card with 31 GB host RAM, llama.cpp b11115 / llama-swap v257, plus two
expert-cache engines (Strata, NInfer). **Do not transfer a number to another card or RAM
class.** Transfer the method and the traps, and run the bench in `bench/` on the
user's own box before quoting any figure as theirs.

**Hardware coverage:** `references/hardware-tiers.md` covers every class: 8 GB Intel Arc,
16–32 GB consumer, 24 GB sweet spot, 32–48 GB high-end, 64–128 GB unified (Mac Studio,
Strix Halo), 192–256 GB unified (Gorgon Halo, Mac Studio Ultra), and cluster/DGX-tier.
Every tier table is sourced and verified externally; none are measurements from this repo.
**Verify on your own box.**

Detail lives in `references/tables/` and `references/findings.md`; cite them when you make a
claim. `references/CORRECTIONS.md` wins over `references/findings.md` where they differ.
New reference files: `references/hardware-tiers.md`, `references/engine-backends.md`,
  `references/harnesses.md`, `references/debloat.md`, `references/safety.md`,
  `references/user-journeys.md`, `references/model-management.md`, `references/vllm-local.md`,
  `references/mlx-mac-tuning.md`, `references/intel-amd-unified.md`,
  `references/llama-fit-broadening.md`, `references/local-orchestration.md`.

**Claim discipline:** every number or behaviour you state must come from a table, a finding, or
a cited source. Anything you infer must be said as inferred ("I expect", "derived, not
measured", "on this architecture it is likely") and never written as a measurement. Do not
extend a measured fact into a mechanism the data does not show (for example, a separate
allocation that can OOM is measured; that it grows during generation is not).

## 1. Intake

Ask, in this order, before recommending anything:

1. **GPU model and VRAM**: the exact card, not "a big NVIDIA". Note whether the desktop
   compositor shares the card. On Apple Silicon, ask the Mac model, the chip, the unified
   memory size, and the macOS version: the GPU's wired limit, not total RAM, is the budget.
2. **System RAM**: this is a first-class budget on MoE / expert-cache engines, not a footnote.
3. **OS**: Windows and Linux behave differently on the same card (see Traps).
4. **Engine and version**: llama.cpp build, llama-swap, Ollama, LM Studio, vLLM. Flag names
   and defaults change between builds; a recommendation is version-scoped.
5. **Model and quant file**: exact file, its size, whether it carries MTP tensors.
6. **Workload**: chat, agent (multi-turn with tool calls), long-document read, code build,
   summarisation. This decides which budget line you cut.
7. **Single or multi-user**: all evidence here is single-user, one model resident.
8. **What "good" means to them**: tok/s, answer quality, recall at depth, tool-call
   reliability, or "it stops crashing". Pick the metric before tuning; the metric decides
   which trade is worth making.

**When to ask and when to answer:** if the user has already given most of these facts, answer at
once and state the assumptions you are making at the top of the answer, then ask only for what is
still missing. If a key fact is missing (GPU/VRAM, system RAM, or the engine), ask first:
the whole procedure depends on it.

Then read the engine's own memory accounting (its load log: model file, KV buffer, compute
buffer, draft head) before applying any arithmetic from this skill.

## 2. Decision procedure

Run the steps in order. Each step: the rule, the evidence, the trap, how to verify.

### Step 1. Fit: VRAM, runtime, and host RAM

- **Rule:** budget = model file + KV cache + compute/graph buffers + mmproj + MTP draft
  context, not the file alone. On the measured card the non-file cost was 7.97 GiB at 131k
  ctx (0.87 mmproj + 4.25 KV + 2.85 residual, single measurement, breakdown unverified).
  A working gate value was 22,900 MiB on a 24,564 MiB card.
- **Evidence:** `references/tables/vram-fit.md` T1–T3, `references/tables/kv-cache.md` T2; finding 1.
- **Trap:** load-time fit is not runtime fit: IQ4_XS-MTP estimated 23.83/24.00 GiB and
  "does not fit in practice"; a Q4_K_XL entry loaded fine at 131k, peaked 24,142 MiB at
  152k and crashed mid-inference. Windows spills VRAM overflow into system RAM silently;
  "Prefer No Sysmem Fallback" makes it fail loudly instead of hanging.
- **Verify:** the engine's own `KV buffer size` / `compute buffer size` log lines, and peak
  VRAM per run (`nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`
  or the engine's reported peak). Any PID on the card that is not the model server is a bug:
  an embedding daemon held 11.3 GiB after its job ended.

### Step 2. Context vs quant: the actual lever

- **Rule:** KV at q8_0 is 0.0332 GiB per 1k tokens, so every 32k of context is worth ~1.06
  GiB; dropping context buys a quant tier (131k→65k bought IQ3_M→Q4_K_M on the measured
  model). But declared context is not usable context: a request beyond the window returns 400
  unless the engine clips it.
- **Evidence:** `references/tables/kv-cache.md` T1, T3; `references/tables/context-recall.md` T1 (the
  131k entry scored 0/3 at 120k depth with HTTP 400); findings 4, 7.
- **Trap:** the client's context cap must match the served window: a hardcoded 262144 in the
  client overfilled a 131k server. Set the clip behaviour explicitly if a harness sends long
  prompts.
- **Verify:** recall at depth (needle at ~10/50/90% depth), which the declared window does not prove.

### Step 3. KV cache type

- **Rule:** KV quantisation is a real lever, and it is architecture-dependent. On the measured
  dense 27B only 16 of 64 layers carry a growing KV (the Gated DeltaNet layers hold fixed
  state), so long context stayed cheap; on a hybrid MoE, 6 attention layers + 23 Mamba layers
  cost ~1.50 GiB KV + 46 MiB state at 262k. At 262k on the Strata engine, q4_0 KV beat int8 on
  every measured axis (decode, prompt speed, RAM headroom) with recall held at every depth.
- **Evidence:** `references/tables/kv-cache.md` T1, T4, T5, T6; `references/tables/prefill-decode-speed.md`
  T5; findings 3, 6.
- **Trap:** KV quality beyond needle recall was not measured: the upstream quality bench for
  q4 KV stops at 128k. Do not claim quality parity at 262k from a recall test alone.
- **Verify:** run the same prompt set with both KV types, quality metric held constant.

### Step 4. Offload and MoE

- **Rule:** decode speed is architecture-bound, not quant-bound: MoE entries decoded 246–324
  t/s while dense 27B entries decoded ~52–119 t/s on the same card. CPU offload is a deliberate
  lever (`--n-cpu-moe`), not an automatic fallback, and the measured direction is: more offload
  = more headroom, less speed (68–124 t/s across `--n-cpu-moe` settings on one MoE entry, vs
  234–245 t/s fully on GPU). On expert-cache engines, host RAM is the binding budget, not VRAM:
  28,289 MiB (27.63 GiB) host RAM peak on a 31 GB box, zram at the wall at 512k.
- **Evidence:** `references/tables/prefill-decode-speed.md` T3; `references/tables/vram-fit.md`
  T4, T5, T6, T7; findings 20, 27, 32.
- **Trap:** heavy parallel builds next to a resident engine can OOM-freeze the box. Freeing the
  desktop compositor to the iGPU is a real lever on a shared card. **Re-measure host RAM
  headroom after every engine upgrade**: defaults that pin memory can change: an upgrade grew
  the default page-locked copy from 17.24 to 19.20 GiB and cut min free RAM at a 477K prompt
  from 3.36 to 1.41 GiB on the same box and config, with no change in VRAM.
- **Verify:** peak host RAM and peak VRAM per run, plus the engine's slot/pinned figures, before
  and after any engine upgrade.

### Step 5. Prefill and ubatch

- **Rule:** `-ub 1024` gave +31–34% prefill on MoE entries and no measurable gain on the dense
  27B (2186 t/s at both `-ub 512` and `-ub 1024`). Prefill chunk settings are hardware-class
  dependent: a chunk setting that gained +21% on a 128 GB RAM box cost 2.7–3.4x on the 31 GB
  box, because the bigger chunk's buffers come out of a cache that is already short.
- **Evidence:** `references/tables/prefill-decode-speed.md` T4, T5; findings 9, 21.
- **Trap:** a flag default can differ from deployed behaviour: int8 prefill activations were
  running while the flag documented a16; a rebuild without the flag lost ~40% prefill.
- **Verify:** three runs per arm at the same prompt size, quality held constant. int8
  activations gave +70% prefill with perplexity identical to 3 decimal places (4.651185 vs
  4.651710) and review scores within noise.

### Step 6. Speculative decoding / MTP

- **Rule:** MTP changes speed only: the target sampler picks every token, so do not blame MTP
  for quality problems. Cost: flat +0.42 GiB of tensors (byte-exact 451,320,768 on the measured
  pair) plus a separate draft-context allocation. Log token acceptance; below ~50% acceptance
  regular quants run faster, so have a documented fallback file. Optimal depth is
  workload-dependent: on the measured engine, 3 draft tokens was best overall (mean 107.9 t/s),
  5 best prose (140.0), 3 best code (94.8); the LM-head draft was worth ~11.8 t/s.
- **Evidence:** `references/tables/speculative-mtp.md` T1–T5; findings 2 (corrected), 11, 12, 13.
- **Trap:** the draft context is a separate allocation that can OOM even when the target model
  fits. That is the measured fact. Do not claim it grows during generation; the measured runtime
  growth is the compute buffers (finding 5). MTP compatibility depends
  on exact builder/commit: flag names changed between builds (`--draft-max` removed →
  `--spec-draft-n-max`), so pin versions. Auto-fit and manual offload are mutually exclusive:
  `common_fit_params` aborts when `-ngl` is already set.
- **Verify:** acceptance rate per run (gate ≥ 0.4) and decode t/s, before and after.

### Step 7. Sampling and reasoning budget

- **Rule, in this order:**
  1. Read **this model's own card**: its recommended sampling, whether it has a thinking mode
     at all, and whether thinking is a toggle. Never reuse another model's numbers: house-style
     defaults are not a spec. If you cannot read the card in this session (no web access), say so
     and give the user the lookup (the model's Hugging Face page, "Best Practices" / sampling
     section). Never state what a card recommends from memory or from the example below: in
     scenario test 1 the example values were wrongly presented as Qwen3-Coder's (its card says
     temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05).
  2. The values below are one hybrid thinking model's vendor spec (the evidence base). Example
     only, not a default for any other model: temp 1.0, top_p 0.95, top_k 20, min_p 0,
     rep_pen 1.0, presence 0.0.
  3. Reasoning-budget rules apply **only where a thinking mode exists**. Cap it per role, never
     `-1`. A model with no thinking mode has no budget to cap and nothing to turn on.
  4. On MTP files keep temp ≤ 1.0 and repetition_penalty exactly 1.0 (raising rep_pen degrades
     MTP). This is about the file, not about thinking.
- **Evidence:** findings 14, 15, and `references/tables/quality-bench.md` T10 (same model, same
  harness: 11/12 with a budget, 0/12 with the budget removed; a 32,000-token run that hit the
  length cap and produced nothing reviewable).
- **Trap:** on models whose template implements a `reasoning_effort` switch, `medium` is a silent
  mode that injects nothing; only the default (xhigh) injects reasoning instructions, and an
  invalid value hard-fails the template render. `--jinja` is required for template-driven kwargs
  to work at all. None of this applies to a model that has no such switch.
- **Verify:** finish_reason per run. `finish=length` with no content is a budget failure, not a
  model failure; several models scored 0/8 in round 1 for exactly that.

### Step 8. Harness and client settings

- **Rule:** the harness is a tunable. Tool-call parsing tolerance turned 5/16 failures into 0/16
  without touching the model. For agent roles, keep thinking on for models that have a thinking
  mode: thinking-off made Qwen-class models skip the tool call entirely. A non-thinking
  (Instruct) variant has nothing to turn on: check its template for whether thinking is a toggle
  before recommending it, and judge it on tool-call reliability instead. Client context cap =
  served window.
- **Evidence:** `references/tables/harness-toolcall.md` T1, T2; findings 16, 17, 28;
  `references/harnesses.md`, `references/debloat.md`.
- **Trap:** single-turn evals can score 24/24 while the same model fails a real multi-turn
  build. Evaluate multi-turn, in two tiers: a quick proxy for iteration, program-verifier tasks
  for promotion.
- **Verify:** run the same task set with the parser change only, model and flags held constant.

### Step 9. Apple Silicon (MLX), Intel Arc, AMD unified memory, and other non-NVIDIA hardware

- **MLX / unified memory (all Mac tiers):** `references/mlx-mac-tuning.md` covers Mac mini M6
  through Mac Studio M5 Ultra 512 GB: the wired limit, the 75% rule, per-tier fit estimates,
  and MLX-specific tuning. No Apple Silicon run exists in this repo; all data is sourced and
  must be verified on the user's machine.
- **Intel Arc / AMD unified memory:** `references/intel-amd-unified.md` covers SYCL (Intel),
  HIP/ROCm (AMD Strix/Gorgon Halo), and Vulkan backends. llama-fit-params works on all of them
  (see `references/llama-fit-broadening.md`).
- **Engine-specific fit:** `references/engine-backends.md`: every backend's fit arithmetic,
  commands, and traps (CUDA, SYCL, Vulkan, HIP/ROCm, MLX/Metal, Ollama, vLLM). For sm_89 (RTX 4090)
  engine specifics (which backends actually run, which are Blackwell-only, open 4090 issues), see
  `references/engine-research-sm89.md`.
- **User journeys:** `references/user-journeys.md`: 5 entry-state workflows from "I have no
  models" to "I'm pushing the frontier."
- **Safety:** `references/safety.md`: validate-with-operator protocol for irreversible actions
  and model/file deletion safety.
- **Verify:** `bench/mlx_quant_search.py` for the estimate, then a real load. Sources and detail:
  `references/mlx-mac-tuning.md`.
- **The LOCAL.md pattern (optional):** `references/local-orchestration.md`
  documents an additional setup pattern, not a required step. A `LOCAL.md` (~4096 tokens) serves
  as the local model's command frontier while `AGENTS.md`/`CLAUDE.md` remain the global frontier.
  Uses a chunk function to trim any-size `AGENTS.md` down to local-model size, with a trim log so
  nothing is lost. The tested loopback router at `ai.ttindall.com/recipes/claude-code-local-subagents/`
  is the harness mechanism that routes local model requests to `LOCAL.md`.

## 3. Verification

Before any claim of "this setting helped":

1. **Hold quality constant.** A speed claim without a quality metric is not a result. Use a
   program-verifier task set (bugfix / config-edit / tool-call / refusal) or perplexity, not a
   vibe check.
2. **Check recall at depth**: three planted facts at ~10/50/90% depth. Declared context is not
   usable context.
3. **Repeat runs.** Run-to-run variance was ±1–2 bugs on a 12-bug test (int8 arm: 11, 11, 10,
   11, 12; a16 arm: 9, 10, 11, 12, 12). A single run is not a result.
4. **Alternating-arm A/B**: interleave arms to control drift, and use the same prompt sizes.
5. **One model on the GPU at a time**: with a lock file; refuse to start while another server is
   up. A run was spoiled by a background session loading a model mid-sweep.
6. **Publish corrections** rather than deleting a wrong number: three overstated VRAM figures
   were re-measured and kept as dated corrections.
7. **Grade BUDGET separately from fail.** `finish_reason: length` with an empty answer is a
   settings failure, not a model failure; a thinking model can spend the whole answer cap on
   reasoning and return nothing. Fix the budget before reading the pass rate.

## 4. Traps

One line each, from the data:

- A process that is not the model server holding VRAM is the bug (11.3 GiB squatter; a
  background session spoiled a sweep).
- Fit on paper is not fit in practice: 0.17 GiB headroom failed, and a model that loads can OOM
  mid-inference as buffers grow with depth.
- Windows silently spills VRAM overflow into system RAM and decodes 10–20% slower than Linux on
  the same card; fail loudly instead.
- Sampling numbers do not transfer between models. Read this model's card; a vendor spec for one
  thinking model is not a default for an Instruct variant.
- `--reasoning-budget -1` produces 20k-token thinking loops with no output (on models that have
  a thinking mode). A model without one has no budget to cap.
- `reasoning_effort=medium` injects nothing; an invalid effort value hard-fails the template
  (only on models whose template implements that switch).
- Thinking-off makes Qwen-class models skip the tool call. This applies to models with a thinking
  mode; a non-thinking (Instruct) variant has nothing to turn on, so check its template before
  recommending the setting.
- A client cap larger than the served window overfills the server (400 or silent clipping).
- Flag defaults drift from deployed behaviour; flag names change between builds.
- Cross-engine advice does not transfer: SGLang/vLLM/ExLlama recipes do not apply to llama.cpp,
  and a hardware-class default can be a 3x loss on a smaller-RAM box.
- Single-turn evals pass models that fail multi-turn work; grader discrimination must be
  checked before trusting a score.
- A quant-tier gain shows in output richness, not always in correctness: IQ4 vs IQ3_XXS both
  scored 11/12 on the same task.
- Engine upgrades can change how much host RAM they pin by default; re-measure RAM headroom
  after every upgrade: a memory-pinning default can take the box to the wall with no
  change in VRAM at all.

## Engine notes (llama.cpp, build-specific)

The flag set the evidence was produced with (b11115, llama-swap v257): `-ngl 99`, `-ub 1024`,
`--ctx-size`, `-fa on -ctk q8_0 -ctv q8_0 --parallel 1` as the common macro, `--spec-type
draft-mtp` (with `--spec-draft-n-max`), `--jinja` for template-driven reasoning kwargs,
`--reasoning on` with a capped `--reasoning-budget`, `--n-cpu-moe` on three entries, and
`--tolerant-tool-calls` on the NInfer engine. Treat this list as what was measured, not as a
canonical flag set: names and defaults change between builds, so confirm against `--help` on
the user's version before recommending one.

Other engines (SYCL, Vulkan, HIP/ROCm, MLX/Metal, Ollama, vLLM) have different flag sets and
memory accounting. See `references/engine-backends.md` for each backend's commands and traps.
The fit arithmetic (model + KV + compute + context + overhead) is universal; only the memory
accounting and flag names differ.

## 5. What this skill does not know

- **Hardware:** every number in `references/tables/` is from one 24 GB card class with 31 GB RAM.
  Never extrapolate a figure to another card or RAM class. **`references/hardware-tiers.md`
  now covers every hardware class** (8 GB Intel Arc through 512 GB Mac Studio and DGX clusters)
  with sourced (externally verified) data per tier. Verify on the user's box before quoting.
  **Contributions from other hardware classes are actively sought**; `CONTRIBUTING.md` has the
  submission template. Most valuable: fit/crash data from cards we don't have, recall-at-depth
  from other hardware, multi-user serving behaviour.
- **Multi-user / concurrent serving:** all measurements are single-request, one model resident.
  Parallel slots, batching, and cache contention are unmeasured here. See `references/vllm-local.md`
  for a measurement methodology for 2–3 endpoint local serving.
- **Other engines (evidence is thin):** Ollama, LM Studio, vLLM, and expert-offload engines
  (Strata, NInfer) get method and traps only, not numbers. What transfers: the fit arithmetic,
  the quality-held-constant method, the recall-at-depth check, the harness traps, the pin-your-
  version rule. What does not: any t/s, GiB, or acceptance figure measured under a different
  engine. See `references/engine-backends.md` for per-engine details. The Strata and NInfer
  numbers in `references/tables/` are engine-specific and marked as such.
- **Apple Silicon / MLX:** covered in `references/mlx-mac-tuning.md`: documented from cited
  sources, not measured here. The wired-limit facts, the default fractions, and per-tier fit
  estimates come from the cited sources; nothing in this repo has run on an Apple Silicon machine.
- **Intel Arc / AMD unified memory:** covered in `references/intel-amd-unified.md`: SYCL (Intel),
  HIP/ROCm (AMD Strix/Gorgon Halo), Vulkan. All externally sourced, none measured here.
- **Long-horizon quality:** perplexity and planted-bug review are proxies; nothing here measures
  week-long agent behaviour.
- **Release state:** this is v0.2, published 2026-10-08. Scenario-tested
  (see `tests/`); the bench scripts were fixed from one live run and have not
  been re-run since. `CONTRIBUTING.md` has the template for verifying on your
  hardware.

## Bench

Run `bench/quick_bench.md` on the user's hardware before quoting any number as theirs.
It measures: memory accounting, prefill and decode at depth, recall at depth, and a small
quality probe with repeats.
