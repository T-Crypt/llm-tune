Short answer: **the 4-bit fits only if you raise the wired limit — at the default it doesn't.** Here's the fit math and the settings, with the caveat that Apple Silicon numbers in this skill are documented, not measured on my hardware, so confirm on your Mac.

## Fit check

- **Budget = wired limit, not 24 GB.** `iogpu.wired_limit_mb` defaults to 0, meaning macOS derives it — about 2/3 of RAM at ≤36 GB, so your 24 GB machine gets roughly **16 GB for the GPU** ([references/apple-mlx.md](<skill>/references/apple-mlx.md)). Read the real value on your machine:
  ```
  sysctl iogpu.wired_limit_mb
  python3 -c "import mlx.core as mx; print(mx.metal.device_info())"
  ```
- **Weights:** `mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` is **16.0 GiB** — that already exceeds the default ~16 GB limit before KV exists. So: no, not at default.
- **Raise it in steps, strictly under total RAM** (practitioners stop at 85–90%):
  ```
  sudo sysctl iogpu.wired_limit_mb=20480
  ```
  At 20 GB you get 16.0 GiB weights + ~4 GB for KV, overhead, and macOS. That's workable but tight — it's the commonly reported setting for exactly this model on a 24 GB Mac.

## What to set

- **Context: keep it modest, 16k–32k.** Derived arithmetic (not measured): Qwen3-30B-A3B is full-attention GQA — 48 layers, 4 KV heads, head_dim 128 → ~98 KB/token at fp16, so **~1.4 GiB KV at 16k, ~2.9 GiB at 32k**. At 32k you're at 16.0 + 2.9 + overhead ≈ the 20 GB wall. A model that fits on paper can fail on load once buffers grow with depth — that's the trap. If you want 64k+ or headroom for other apps, drop to the **3-bit** variant (~12 GiB weights) instead of raising the limit further.
- **Sampling — follow Qwen3's own spec**, not generic house style: temp 1.0, top_p 0.95, top_k 20, min_p 0, rep_pen 1.0. For coding-agent use, keep thinking **on** (thinking-off makes Qwen-class models skip tool calls), and cap the reasoning budget — never unlimited; runaway thinking produces long runs with no output.
- **Server:** `mlx_lm.server` is OpenAI-compatible, so the bench scripts work against it. Its flags aren't verified in this repo — confirm with `--help` on your install.

## Verify before trusting it

Run the bench **on the Mac itself** — nothing in this skill has run on Apple Silicon:

1. `bench/mlx_quant_search.py --model Qwen3-Coder-30B --ram-gb 24 --limit-gb 20` for the estimate (I couldn't run it here — no shell in this session, and it's the wrong box anyway).
2. A real load, then `bench/needle.py` at ~10/50/90% depth — declared context is not usable context.
3. `bench/quality_probe.py` with repeats for the coding loop; single-turn evals pass models that fail multi-turn tool-calling work.

One more expectation-setting note: decode speed for an A3B MoE is architecture-bound and should be comfortable on MLX, but I won't quote a t/s figure as yours — every speed number in the evidence base is from a 24 GB RTX card, and cross-hardware transfer is exactly what the skill forbids. Measure it on your box.
