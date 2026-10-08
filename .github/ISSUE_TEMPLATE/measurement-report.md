---
name: Measurement Report
about: Report hardware-specific LLM tuning measurements for the skill
title: "[data-submission] "
labels: data-submission
assignees: ''
---

## Your hardware (required)

- **Card**: exact model, VRAM as measured
- **Host RAM**: total and available during runs
- **OS**: Linux / Windows / macOS, version
- **Engine**: llama.cpp build / llama-swap / Strata / NInfer / other, version or commit

## The measurement

### Memory
- Model file size: ___ GiB
- Peak VRAM at context N: ___ MiB (or "OOM")
- Host RAM peak: ___ MiB (or "not measured")
- Load time: ___ s
- Mid-inference crash at context M: yes/no (peak VRAM if known)

### Speed (3 runs each)
- Decode t/s at depth N: ___, ___, ___ (mean: ___)
- Prefill t/s at depth N: ___, ___, ___ (mean: ___)
- Draft acceptance: ___/___ (if MTP used)

### Recall at depth
- 10% depth: yes / no (HTTP status if error: ___)
- 50% depth: yes / no
- 90% depth: yes / no
- Client cap that failed: ___ (if any 400 responses)

### Quality (optional, very valuable)
- Planted-bug review over 3+ runs: ___, ___, ___ → mean ___/12
- Perplexity held constant against a speed change: ___
- Verifier pass rate: ___/N

### Traps encountered
- Anything surprising: fit-but-crashed, flag-does-not-do-what-it-says,
  default-changed-in-upgrade, VRAM-squatter, OS-spill, etc.

## Model details

- Model file: name and exact path/repo
- MTP tensors: yes / no
- Quant: Q4_K_M / IQ4_XS / etc.

## Notes

Anything else that would help tabulate this: what you were trying to do
(coding agent, long document, chat), what you tried that worked, what failed.
