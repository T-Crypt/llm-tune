# Bench

The skill's numbers came from one machine class (24 GB card, 31 GB RAM). On any other box,
run this before quoting a figure as the user's.

What it measures, in order:

1. **Memory accounting** — what the engine actually reserves (model file, KV buffer, compute
   buffer, draft head), not what arithmetic predicts. The single measurement that would make
   the fit table exact is the engine's own buffer-size log line.
2. **Peak VRAM and peak host RAM per run** — load-time fit is not runtime fit.
3. **Prefill and decode at depth** — the same prompt sizes at ~10/50/90% depth, three runs each.
4. **Recall at depth** — three planted facts, scored found/total. A declared window is not a
   usable window.
5. **A small quality probe with repeats** — planted-bug review, five runs, so run-to-run noise
   is visible. ±1–2 bugs on a 12-bug test is normal.

Rules that make the numbers readable:

- One model on the GPU at a time; nothing else may hold VRAM during a run.
- Same prompt set, same sizes, for every arm. Change one thing per arm.
- Alternating-arm A/B, not "run A then run B an hour later".
- A speed claim needs a quality metric held constant in the same run.
- Record finish_reason: `finish=length` with no output is a budget failure, not a model failure.

Scripts (stdlib only):

- `needle.py` — plants a fact at a given depth in a filler haystack, calls an
  OpenAI-compatible `/v1/chat/completions` URL given on the command line, prints JSON per
  depth: prompt size, seconds, recall, status, and the reasoning length.
- `quality_probe.py` — five verifier-graded tasks (strict JSON, bug trace, tool-call shape,
  constrained format, short needle), run R times, prints pass / fail / **BUDGET** counts per
  task. BUDGET means the run hit the answer cap with nothing to show — a settings failure, not
  a model failure. These graders check the answer text; the confidence tier runs a model's
  patch against a real test suite, which a single-file probe cannot do.
- `mlx_quant_search.py` — estimates which `mlx-community` quants fit an Apple Silicon box,
  using the wired limit rather than total RAM. Estimates only; verify with a real load.

Both request scripts work against any OpenAI-compatible server, including `mlx_lm.server` —
confirm its flags with `--help` (untested here).

Live-test fixes (2026-10-05): `needle.py` crashed on `str.format` with an expression inside
the braces; `quality_probe.py` scored 0/2 on a thinking task because the 600-token answer cap
was spent entirely on reasoning (`finish_reason: length`, empty content) — the cap is now a
flag with a 4096 default, and the empty-answer case is graded as BUDGET rather than fail. The
refusal task was removed because the prompt itself contained the secret, so echoing it leaked
nothing, and it named lab services; it is replaced by a constraint-following task. The fixed
versions have not been re-run here.

Status: the memory-accounting, needle-at-depth, and repeat-run patterns are the ones the lab
actually ran (`references/tables/`). The specific commands in `quick_bench.md` are written for a
generic llama.cpp install and have not been executed here — anything unrun is marked
"(untested here)". Confirm flag names against `llama-bench --help` and `llama-server --help`
on the user's build; flag names change between versions.
