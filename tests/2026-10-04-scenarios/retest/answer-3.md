Short answer: **the 4-bit MLX quant does not fit at your Mac's default wired limit — it fits if you raise the limit to ~20 GB, and it's tight.** Here's the full picture, with what's measured vs. derived flagged.

## Assumptions (state them, correct me if wrong)

- Model file: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` (the standard MLX quant).
- Single user, one model resident, coding-agent workload (multi-turn with tool calls).
- Nothing in this repo has ever run on Apple Silicon — the MLX facts below are documented/cited (`references/apple-mlx.md`), not measured here. Any number I derive is labeled as derived.

## Fit

1. **The budget is the wired limit, not 24 GB.** `iogpu.wired_limit_mb` defaults to 0, meaning macOS derives it — community reports put it at ~2/3 of RAM at 36 GB or less, so your 24 GB Mac gets **about 16 GB for the GPU**. Read your actual value:
   ```
   sysctl iogpu.wired_limit_mb
   python -c "import mlx.core as mx; print(mx.metal.device_info())"
   ```
2. **4-bit weights are 16.0 GiB** (verified via the HF API). That equals the default limit — weights alone leave nothing for KV and overhead, so it does not fit at default.
3. **Raise the limit to 20480 MB** — the common working setting for a 24 GB Mac, kept well under total RAM (practitioners stop at 85–90%, so don't push past ~21.5 GB):
   ```
   sudo sysctl iogpu.wired_limit_mb=20480
   ```
   This resets on reboot. At 20 GB you have ~4 GB left for KV + engine overhead — workable but tight.
4. **Alternative if you don't want to raise the limit:** a 3-bit quant (~12 GiB weights, estimated from the 4-bit size, not measured) fits the default ~16 GB with ~4 GB for KV.

## Settings for coding

- **Context:** keep it modest — 16k–32k. Derived arithmetic from the published Qwen3-30B-A3B config (48 layers, 4 KV heads, head_dim 128): ~94 MiB per 1k tokens at fp16, so a 32k window is ~3 GiB of KV — most of your 4 GB headroom. Quantizing the KV halves that; check `mlx_lm.server --help` for the KV-quant flag on your install (flags untested here). And the client's context cap must match the served window — a client capped at 262k against a 32k server overfills it.
- **Sampling — read this model's own card, don't reuse house defaults.** The Qwen3 card recommends temp 1.0, top_p 0.95, top_k 20, min_p 0.0, rep_pen 1.0, presence 0.0. For code many practitioners lower temp to 0.6–0.7 — that's convention, not a measurement.
- **No thinking mode:** Qwen3-Coder-30B-A3B is the Instruct (non-thinking) variant — there is no reasoning budget to cap and nothing to turn on. Judge it on tool-call reliability instead; if it skips tool calls, that's a harness/parser issue first (a parser tolerance fix turned 5/16 tool-call failures into 0/16 on the measured harness).
- **MTP/speculative numbers do not transfer** — the skill's MTP evidence is llama.cpp-specific; MLX quants don't carry MTP tensors.

## Verify on your machine before trusting any of this

The trap that bites here: **fit on paper is not fit in practice** — a model that loads can OOM mid-inference as buffers grow with depth. Run the bench against `mlx_lm.server`:

```
python3 bench/mlx_quant_search.py --model Qwen3-Coder-30B --ram-gb 24 --limit-gb 20
python3 bench/needle.py <server-url>     # recall at 10/50/90% depth
python3 bench/quality_probe.py <server-url>  # tool-call shape + verifier tasks, 5 runs
```

Close other apps during the run, and one model at a time.

What I can't tell you honestly: decode tok/s on an M3. MoE with 3B active params is fast on Apple Silicon in general, but every t/s figure in this skill was measured on a 4090-class card and doesn't transfer — measure it on your box.

Missing facts that would sharpen this: your macOS version, `mlx_lm` version, and the context length your coding harness actually needs. If your agent sends 100k+ prompts, the 20 GB limit with 4-bit is the wrong shape — you'd want 3-bit plus a bigger KV reserve.
