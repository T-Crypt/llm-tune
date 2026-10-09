# Changelog

## 2026-10-08 (in-repo bench run, fixes, data re-verification)

- First in-repo run of the bench scripts against a live server: `needle.py`
  held recall at 10/50/90% depth (the 6000-line default is about 142k prompt
  tokens, so it needs a 262k-context model), `quality_probe.py` passed 25/25
  with zero BUDGET, and `mlx_quant_search.py` ran against the HF API. Commands
  and raw output in `tests/2026-10-08-bench/`.
- The README status line and the "(untested here)" markers rewritten from the
  real run; the marker survives only where still true (the llama-bench prefill
  sweep).
- The model-management page now checks for the HF CLI before suggesting an
  install (`command -v hf && hf --version || pip install -U huggingface_hub`).
- All 49 unique citations re-checked live (45 return 200, 4 block bots) and
  the vLLM serve defaults plus the llama.cpp fit-params flags verified against
  the current docs; `vllm-local.md` updated with the verified defaults.

## 2026-10-08 (release prep)

- README rewritten for public release: install and use instructions, scope
  section, updated repository layout. Banner added under `assets/`, tagline
  "settings with receipts"; README framed agent-agnostic.
- Internal build plans and review notes moved from the repository root to
  `docs/dev/`.
- Credit and compare-and-contribute section added for the local-ai-registry
  (sybil-solutions): its RTX 4090 recipes by 0xSero served as baselines during
  this repo's testing.
- Repo-wide typographic cleanup: em dashes removed, formulaic phrasing
  rewritten. Meaning unchanged.
- Added this changelog, a note on the frozen scenario records in `tests/`,
  and a CI workflow that syntax-checks the bench scripts.

## 2026-10-08 (skill v0.2)

- Model-specific sampling rules: read the model's own card, never reuse
  another model's numbers, and never state a card's values from memory.
- Overclaim guard: an inferred mechanism is never written as a measurement
  (the MTP draft context can OOM as a separate allocation; that it grows
  during generation is not in the data).
- Intake rule: if the user has already given most facts, answer with stated
  assumptions and ask only for what is missing.
- Scenario test 1 re-run after the fixes: pass.

## 2026-10-05 (bench fixes from a live run)

- `needle.py`: fixed a `str.format` crash with an expression inside the
  braces; single-token default fact after one run was graded a miss on an
  equivalent answer.
- `quality_probe.py`: the answer cap is now a flag (4096 default) after a
  thinking task spent a 600-token cap on reasoning and returned empty content;
  that case is graded BUDGET, a settings failure, instead of fail.
- The refusal task was removed (its prompt contained the secret it asked the
  model to refuse) and replaced with a constraint-following task.

## 2026-10-04 (scenario test 1)

- Three prompts (RTX 3060 12 GB agent, 4090 mid-request crash, M3 24 GB MLX)
  run against the skill, graded against its own rules. Defects found and
  fixed in v0.2. Records in `tests/2026-10-04-scenarios/`.

## 2026-10-04 (initial skill)

- Intake, decision procedure, verification rules, traps, and the evidence
  base: one 24 GB RTX 4090-class card, 31 GB host RAM, llama.cpp b11115,
  plus two expert-cache engines (Strata, NInfer). Tables, findings, and
  corrections extracted from the source measurements.