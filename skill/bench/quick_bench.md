# Quick bench (llama.cpp)

Copy-paste, single-user, one model resident. Adjust paths and the port. Everything marked
"(untested here)" has not been run in this repo — confirm flag names with `--help` on the
user's build before trusting them.

## 1. Memory accounting — read the engine, not the arithmetic

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
2.85 GiB "everything else" in `data/tables/kv-cache.md` is an estimate from one run; this
log is what turns it into a measurement.

## 2. Peak VRAM and host RAM during a run

```bash
# Peak per process, sampled during the run (untested here as a loop; the query itself is standard):
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
free -m
```

Any PID on the card that is not the model server is a bug — check before blaming the model.
Record peak, not the value at load. A model that loads fine can OOM mid-inference.

## 3. Prefill and decode at depth

```bash
# Confirm -d, -r, -o against llama-bench --help on this build (untested here).
llama-bench -m /path/to/model.gguf -ngl 99 -fa 1 -ctk q8_0 -ctv q8_0 \
  -b 1024 -d 32768,65536,131072 -n 64 -r 3 -o json > bench.json
```

Read prefill t/s as a function of depth, and decode t/s at depth. On the measured card,
prefill fell roughly 2,500 -> 2,000 -> 1,500 t/s across 32k/120k/240k on a dense 27B; that
shape (falling with depth) is the transferable part, the values are not.

## 4. Needle at depth — recall, not just window

```python
# needle.py - generic version, untested here. Three facts planted at 10/50/90% depth.
import json, time, urllib.request

SERVER = "http://127.0.0.1:8080/v1/chat/completions"
MODEL  = "local"
FACTS  = {"a": "port 9443", "b": "quota 18 TiB", "c": "build 751866"}
SIZES  = [6000, 30000, 60000]   # haystack lines; roughly the lab's 60k/120k/200k char prompts

def haystack(n_lines, plant_at, facts):
    lines = [f"{i:06d} INFO worker thread {i%7} processed batch {i} in {i%97} ms"
            for i in range(n_lines)]
    for k, idx in plant_at.items():
        lines[idx] = f"{idx:06d} NOTE {k}: {facts[k]}"
    return "\n".join(lines)

for size in SIZES:
    plant = {"a": int(size * 0.10), "b": int(size * 0.50), "c": int(size * 0.90)}
    text = haystack(size, plant, FACTS)
    body = {"model": MODEL,
            "messages": [{"role": "user", "content": text + "\n\nReport the three NOTE values exactly."}],
            "max_tokens": 200, "temperature": 0.0}
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(
        urllib.request.Request(SERVER, json.dumps(body).encode(),
                               {"Content-Type": "application/json"})).read())
    secs = time.time() - t0
    ans = r["choices"][0]["message"]["content"]
    usage = r.get("usage", {})
    pt = usage.get("prompt_tokens", 0)
    found = sum(1 for k in FACTS if FACTS[k] in ans)
    print(f"size {size} prompt_tokens {pt} prefill_tps {pt/max(secs,1):.0f} "
          f"found {found}/3 finish {r['choices'][0].get('finish_reason')} {secs:.1f}s")
```

Read: `found 3/3` at every depth, or the window is not usable. A 400 at a depth means the
prompt exceeded the served window — that is a harness bug, not a model failure. Run the same
depths twice; recall is stable but scores are not.

## 5. Quality probe with repeats

Plant 12 known defects in a small file (mutable default, swallowed exception, wrong operator
precedence, path join, timezone compare, unclosed resource, etc.), ask the model to review it
with a tool call, and score found/12. Run it five times per arm.

```bash
for i in 1 2 3 4 5; do
  curl -s http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{
    "model": "local",
    "messages": [{"role":"user","content":"Review /tmp/planted.py for bugs. List each as name: line."}],
    "max_tokens": 2000, "temperature": 0.0
  }' | tee "run-$i.json"
done
```

Read: the spread, not the best run. ±1–2 bugs on a 12-bug test is normal noise; a single run
is not a result. Compare arms only with alternating runs (A, B, A, B), same prompt, one change.

## 6. Tool-call probe

Send a prompt whose answer must be a tool call, and check `finish_reason` is `tool_calls` and
the first call has the right arguments. Then re-run with tolerant parsing if the engine has it.
On the measured engine, strict parsing failed 5/16 and tolerant parsing 0/16 on the same model
and tasks — the parser, not the model, was the variable. Thinking-off on Qwen-class models made
them answer in prose and skip the call entirely.

## 7. What counts as evidence

- A number from the user's own run, not from `data/tables/`.
- A speed claim needs a quality metric held constant in the same run.
- Three repeats minimum; alternating arms for A/B.
- One model on the GPU at a time, nothing else holding VRAM.
- finish_reason recorded for every run.
