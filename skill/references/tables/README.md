# Measurement tables

Extracted from the DATA-tagged sources catalogued in the project inventory (project material, not part of the installed skill). Numbers copied exactly from the sources — no rounding, no averaging, no gap-filling; "n/a" means not measured. Hardware described generically; sources cited by repo-relative path in the source repo.

| File | Tables | Covers |
|---|---|---|
| `vram-fit.md` | 5 | Quant file sizes and estimated peak; measured peak VRAM per run (262k sweep, 27B context ladder); engine memory footprint across llama.cpp / Strata / NInfer; Strata expert-slot and RAM headroom by variant |
| `kv-cache.md` | 6 | Derived KV size by context at q8_0; fixed non-file overhead calibration; the context/quant trade; hybrid (Mamba/DeltaNet) fixed state; Strata KV pinned-RAM by variant; NInfer state-pool accounting |
| `context-recall.md` | 7 | Needle-in-haystack recall at depth per run (r7, r7b, r9 ladder), Strata sparse-attention recall including the 512k live check and the PR #646 A/B |
| `prefill-decode-speed.md` | 8 | NInfer prefill by activation mode (3 runs each); perplexity held constant; bakeoff decode t/s per run; prefill t/s at depth; Strata read t/s and decode-at-depth including the prefill-chunk correction; 512k live timings; PR #646 arm-by-arm; short-prompt bench |
| `speculative-mtp.md` | 6 | MTP tensor cost (flat +0.42 GiB, byte-exact); draft acceptance per run (rounds 1, 2, r6); NInfer draft-depth sweep; Strata draft-head memory; the acceptance gate and the model-card reference ratio |
| `quality-bench.md` | 15 | Blind answer rankings (two rounds); think-task times; planted-bug review scores and structural build scores per round; repeat-run variance; budget-held vs budget-removed; int8 vs a16 review repeats; DeepSWE; the program-verifier role suite; the earlier single-turn suite |
| `harness-toolcall.md` | 3 | Strict vs tolerant tool-call parser, task by task; no-tool-call observations; verifier-backed tool-call tasks |

Not extractable as tables: the flag census in `reference/llama-swap/config.yaml` (counts, not measurements), `runbooks/` prose figures (Windows sysmem tax, gate thresholds), `state/incidents.md` and `state/changes.md` (single-event numbers, cited in findings), the class-1 sampler screenshots referenced in `gain-research.md` (images), and the task content of the role-eval JSON (lab-specific, privacy).
