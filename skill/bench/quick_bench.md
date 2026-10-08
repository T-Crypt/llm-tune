# Quick bench (llama.cpp)

Copy-paste, single-user, one model resident. Adjust paths and the port. Everything marked
"(untested here)" has not been run in this repo, confirm flag names with `--help` on the
user's build before trusting them.

## 1. Memory accounting: read the engine, not the arithmetic

Start the server once and keep its log. The lines that matter:

```bash
llama-server -m /path/to/model.gguf --mmproj /path/to/mmproj.gguf \
  -ngl 99 --ctx-size 131072 -ub 1024 -fa on -ctk q8_0 -ctv q8_0 --parallel 1 \
  --host 127.0.0.1 --port 8080 | tee load.log
```

Then read:

```bash
grep -Ei "KV buffer size|compute buffer size|model size|memory" load.log
```

Record: model file size, KV buffer size, compute buffer size, mmproj, draft-head size if
speculative decoding is on. These are the numbers the fit arithmetic should use. The
2.85 GiB "everything else" in `references/tables/kv-cache.md` is an estimate from one run; this
log is what turns it into a measurement.

## 2. Peak VRAM and host RAM during a run

```bash
# Peak per process, sampled during the run (untested here as a loop; the query itself is standard):
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
free -m
```

Any PID on the card that is not the model server is a bug; check before blaming the model.
Record peak, not the value at load. A model that loads fine can OOM mid-inference.

## 3. Prefill and decode at depth

```bash
# Confirm -d, -r, -o against llama-bench --help on this build (untested here).
llama-bench -m /path/to/model.gguf -ngl 99 -fa 1 -ctk q8_0 -ctv q8_0 \
  -b 1024 -d 32768,65536,131072 -n 64 -r 3 -o json > bench.json
```

Read prefill t/s as a function of depth, and decode t/s at depth. On the measured card,
prefill fell roughly 2,500 -> 2,000 -> 1,500 t/s across 32k/120k/240k on a dense 27B; that
shape (falling with depth) is the transferable part; the values are not.

## 4. Needle at depth: recall beyond the declared window

```bash
python3 needle.py --url http://127.0.0.1:8080/v1/chat/completions --model local \
  --depths 0.10,0.50,0.90 --lines 6000 --fact "build 751866"
```

(needle.py is untested here; it has not been run in this repo.)

Read: `recall: yes` at every depth, or the window is not usable. An error at a depth means the
prompt exceeded the served window: that is a harness bug, not a model failure. Run the same
depths twice; recall is stable but scores are not.

## 5. Quality probe with repeats

Plant 12 known defects in a small file (mutable default, swallowed exception, wrong operator
precedence, path join, timezone compare, unclosed resource, and similar), ask the model to
review it with a tool call, and score found/12. Run it five times per arm.

```bash
python3 quality_probe.py --url http://127.0.0.1:8080/v1/chat/completions --model local --runs 5
```

(quality_probe.py is untested here; it has not been run in this repo. Its graders check the
answer text; the planted-bug review in step 5 is the stronger form when you can score against
a known defect list.)

Read: the spread, not the best run. ±1–2 bugs on a 12-bug test is normal noise; a single run
is not a result. Compare arms only with alternating runs (A, B, A, B), same prompt, one change.

## 6. Tool-call probe

Send a prompt whose answer must be a tool call, and check `finish_reason` is `tool_calls` and
the first call has the right arguments. Then re-run with tolerant parsing if the engine has it.
On the measured engine, strict parsing failed 5/16 and tolerant parsing 0/16 on the same model
and tasks, the parser, not the model, was the variable. Thinking-off on Qwen-class models made
them answer in prose and skip the call entirely.

## 7. What counts as evidence

- A number from the user's own run, not from `references/tables/`.
- A speed claim needs a quality metric held constant in the same run.
- Three repeats minimum; alternating arms for A/B.
- One model on the GPU at a time, nothing else holding VRAM.
- finish_reason recorded for every run.
