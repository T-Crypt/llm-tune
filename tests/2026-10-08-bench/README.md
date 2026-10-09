# Bench run - 2026-10-08

First in-repo execution of the bench scripts after the 2026-10-05 fixes. The
point is to prove the scripts run against a live OpenAI-compatible server and to
show the numbers they print, not to rank a model. Records:

- `needle.jsonl`: raw output of `needle.py`
- `quality_probe.txt`: raw output of `quality_probe.py`

Run against the working tree at commit `4ede306` (main).

## Environment

| Field | Value |
|---|---|
| Host | aphotic, Arch, Linux 7.2.6-arch2-1, 31 GiB RAM, 32 threads |
| GPU | RTX 4090, 24 GB (24,564 MiB), driver 615.71.09, idle before the run |
| Engine | llama-server 0.4.1-dev (build 1, commit d5f6649), via llama-swap |
| Model | Qwen3.6-35B-A3B-UD-IQ4_XS (`agent-fast` alias) |
| Load flags | `-ngl 99 --jinja -ub 1024 --ctx-size 262144 --spec-type draft-mtp --reasoning on --reasoning-format deepseek --reasoning-budget 4096 -fa on -ctk q8_0 -ctv q8_0 --parallel 1` |
| Peak VRAM | 22,576 MiB |

## Commands

```sh
python3 skill/bench/needle.py \
  --url http://127.0.0.1:9090/v1/chat/completions --model agent-fast \
  --depths 0.10,0.50,0.90 --lines 6000 --fact ZX-751866 \
  --max-tokens 8192 --timeout 600

python3 skill/bench/quality_probe.py \
  --url http://127.0.0.1:9090/v1/chat/completions --model agent-fast \
  --runs 5 --max-tokens 8192 --timeout 300
```

`--max-tokens 8192` overrides the script default of 4096. The role reasons with a
4096-token budget, so an answer cap equal to the reasoning budget leaves nothing
for the answer: a smoke request at `max_tokens 64` returned `finish=length` with
empty content and 260 reasoning characters. This is the BUDGET case both scripts
report, not a model failure. With 8192 the answer always fit.

## Results

`needle.py`, one fact per depth, 6000 filler lines per prompt:

| Depth | Prompt tokens | Prefill t/s | Seconds | Recall | Finish |
|---|---|---|---|---|---|
| 0.10 | 142,279 | 4,961.0 | 28.7 | yes | stop |
| 0.50 | 142,278 | 4,832.0 | 29.4 | yes | stop |
| 0.90 | 142,278 | 4,876.4 | 29.2 | yes | stop |

`quality_probe.py`, 5 tasks, 5 runs each (25 requests):

| Task | Pass | Fail | BUDGET | Error | Max reasoning chars |
|---|---|---|---|---|---|
| json-strict | 5 | 0 | 0 | 0 | 841 |
| bug-trace | 5 | 0 | 0 | 0 | 5,879 |
| tool-call-shape | 5 | 0 | 0 | 0 | 771 |
| constrained-format | 5 | 0 | 0 | 0 | 2,376 |
| short-needle | 5 | 0 | 0 | 0 | 760 |

25/25 pass, zero BUDGET, zero error.

`mlx_quant_search.py` was also run (it needs the Hugging Face API, not a Mac):
`--model Qwen3-Coder-30B --ram-gb 24` printed FITS / raised-limit / no-fit
verdicts for the mlx-community quants. Estimates only, as the script says.

## Notes and limits

- **6000 lines is about 142k tokens, not the ~32k a reader might assume.** The
  needle default only fits a 262k-context model. On a 131k model the same command
  returns HTTP 400 at every depth. That is a usable result (the window is not the
  declared window), but a reader on a smaller model should lower `--lines`.
- Both scripts ran at their written defaults except the answer budget. No code
  change was needed for them to work; the 2026-10-05 fixes hold on this build.
- One model on the GPU, nothing else resident (4 MiB used before the run).
- This is the same 24 GB card class as the rest of the evidence base, so it adds a
  fresh run of the scripts, not a new hardware class.
