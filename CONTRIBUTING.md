# Contributing measurements and findings

llm-tune is quality-aware tuning advice for local LLMs. Its accuracy depends on the
breadth of hardware it covers. **Every measurement submitted by a user makes the
tuning advice better for everyone.** This document explains what we need and how
to submit it.

## What we need

The evidence base is thin on hardware: every number in the skill was measured on
one 24 GB RTX 4090-class card with 31 GB RAM. We need measurements from other
cards, other RAM classes, other engines, and other operating systems.

**Hardware coverage is now broad** - `references/hardware-tiers.md` covers every
class from 8 GB Intel Arc through 512 GB Mac Studio and DGX clusters, with sourced
data from external verification (community reports, official docs, hardware reviews).
These data are NOT measurements from this repo - they are placeholders waiting for
your real numbers. **The single most valuable contribution is a fit/crash
measurement on hardware we don't have.**

The most valuable contributions, ranked:

1. **Fit and crash data from cards we don't have** - file size, peak VRAM at
   context N, whether it crashed mid-inference, host RAM peak. The shape of the
   failure (load fail vs. mid-run OOM vs. HTTP 400 at depth) matters more than
   the numbers. Applies to ALL hardware classes in `hardware-tiers.md`
   - Intel Arc, AMD Strix/Gorgon Halo, all Mac tiers, RTX 5090 and above, clusters.
2. **Recall at depth from your hardware** - three planted facts at 10/50/90%
   depth, or any declarative-context-limit failures you hit (HTTP 400, silent
   clipping). This is the single most missing dimension.
3. **Quality probes with repeats** - a planted-bug review or equivalent, run
   3-5 times per arm, so run-to-run variance is visible. The spread, not the
   best run, is the data point.
4. **Prefill/decode at depth** - any engine, any card. Prefill t/s falling with
   depth is universal; the shape and the numbers are hardware-specific.
5. **Engine-specific traps** — flag defaults that differ from deployed behaviour,
   flag names that changed between builds, engine-version A/B results, anything
   where "fit on paper" diverged from "worked in practice." Particularly needed
   for SYCL (Intel Arc), HIP/ROCm (AMD Strix/Gorgon), MLX/Metal (all Mac), and
   vLLM local serving.
6. **Apple Silicon / MLX measurements** - the whole MLX section is documented
   from cited sources and not measured anywhere. Even a single load test plus
   recall check would fill the biggest gap.
7. **Multi-user / concurrent serving** - currently completely unmeasured.
   Batching, cache contention, multiple models resident at once.

We do **not** currently need: more numbers from the hardware we already have
(another 24 GB card run adds nothing), or single-run scores (noisy, not data).

## How to submit

### Quick path - file a GitHub issue

Use the **Measurement Report** issue template (`.github/ISSUE_TEMPLATE/`). Fill in
as many sections as you can, including your hardware class (tier number from
`references/hardware-tiers.md` if known). You do not need a PR; the maintainers
will tabulate it into the tables and cite your hardware class as a new source.

If your hardware is covered by a reference file (`hardware-tiers.md`, `mlx-mac-tuning.md`,
`intel-amd-unified.md`, `engine-backends.md`), link to it in your report so maintainers
can check whether your numbers align with the sourced estimates.

### Full path - a PR with your data

1. Run `bench/quick_bench.md` on your machine (or the equivalent for your engine).
2. Record the results in the submission template below.
3. Open a PR adding your hardware class to `data/INVENTORY.md` and the
   relevant table(s) in `skill/references/tables/`. Tag the PR `data-submission`.
4. If your measurements contradict an existing finding, explain why in the PR.
   Corrections go through `CORRECTIONS.md`.

## Submission template

Copy this and fill in what you measured. "n/a" or "not measured" is fine - we
prefer honest gaps over invented numbers.

```
## [Your Hardware Class] - [date]

- **Card**: exact model, VRAM as measured (e.g. "RTX 4070 Ti Super, 16 GiB")
- **Host RAM**: total and available during runs
- **OS**: Linux/Windows/macOS, kernel or version
- **Engine**: llama.cpp bXXXXX / llama-swap vXXX / Strata / NInfer / other, commit or version
- **Model**: exact GGUF or model file, size on disk, MTP tensors yes/no
- **Workload**: chat / coding agent / long-document / code build (what you actually wanted to do)

### Memory
- File size: ___ GiB
- Peak VRAM at context N: ___ MiB (or "OOM")
- Host RAM peak: ___ MiB (or "not measured")
- Load time: ___ s
- Mid-inference crash at context M: yes/no (peak VRAM if known)

### Speed
- Decode t/s at depth N: ___ (3 runs: ___, ___, ___)
- Prefill t/s at depth N: ___ (3 runs: ___, ___, ___)
- Draft acceptance: ___/___ (if MTP/speculative used)

### Recall at depth
- Depth 10%: recall yes/no, HTTP status if error
- Depth 50%: recall yes/no
- Depth 90%: recall yes/no
- Client context cap that failed: ___ (if any 400s)

### Quality (optional but very valuable)
- Planted-bug review score: ___/12 over 3+ runs (list: ___, ___, ___)
- Or perplexity: ___ (held constant against a speed change)
- Or verifier task pass rate: ___/N

### Traps encountered
- Anything surprising: fit-on-paper-but-crashed, flag-that-does-not-do-what-it-says,
  default-that-changed-in-an-upgrade, process-holding-VRAM, OS-spill-behaviour, etc.
```

## Quality standards

- **Do not round or average** before submitting. Raw numbers are better than
  rounded ones; we round when tabulating.
- **Record `finish_reason`** for every quality run. `finish=length` with empty
  output is a settings failure, not a model failure - we need to see it.
- **Three runs minimum** for any speed or quality claim. One run is an anecdote.
- **Alternating arms for A/B**: A, B, A, B, not "run A then run B an hour later."
- **One model on the GPU at a time**, nothing else holding VRAM. A background
  session loading a model spoiled a whole sweep in the lab; same risk exists
  elsewhere.
- **Cite your source** if you are pulling a number from documentation or a
  model card rather than measuring it. The skill's claim discipline requires
  this; your submissions should too.

## What happens after you submit

Maintainers review submissions for consistency with the claim discipline
(every number traceable to a measurement or a cited source, inferences labelled).
Accepted submissions get:

1. Added to the relevant measurement table in `skill/references/tables/` with
   your hardware class as a new source.
2. Cross-checked against existing findings - if your data agrees, it strengthens
   the finding; if it disagrees, it may become a correction or a new finding.
3. The inventory (`data/INVENTORY.md`) gets a new entry with your hardware class
   and a usefulness tag (FINDING / DATA / LOCAL-ONLY).
4. The `SKILL.md` "What this skill does not know" section shrinks as coverage widens. Hardware classes that have real measurements move from "documented, not measured" to "measured, externally sourced" or just "measured."
5. Sourced tier estimates in `hardware-tiers.md`, `mlx-mac-tuning.md`, and `intel-amd-unified.md` get replaced with your real numbers.

## Tagging: USEFULNESS

Each submission is tagged:

| Tag | Meaning |
|---|---|
| **DATA** | Raw measurements worth tabulating. The numbers themselves. |
| **FINDING** | A generalisable lesson drawn from the data ("KV quant beats int8 on this axis"). |
| **LOCAL-ONLY** | Specific to your setup and unlikely to transfer (e.g. a specific driver bug, a dual-boot quirk). Still accepted - it helps others with the same setup, and the trap is worth recording. |

## Scope and honesty

- We do **not** accept or promote any measurement that was not actually run.
  Faking data is the fastest way to make the skill worse for everyone.
- If a run was spoiled (background process touched the GPU, power cut, etc.),
  say so. Invalid data quarantined is better than invalid data published.
- If you cannot measure something, say "not measured on my hardware" rather
  than estimating. Estimates are the source's responsibility, not ours.

## Further questions

Open an issue tagged `data-submission` or `question`. If you are unsure whether
your measurement is useful, submit it anyway - the maintainers will tell you.
