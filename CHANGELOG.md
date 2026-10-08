# Changelog

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