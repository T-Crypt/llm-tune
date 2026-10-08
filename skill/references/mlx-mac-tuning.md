# MLX + unified memory on Apple Silicon Macs

Tuning guide for all Mac tiers, Mac mini M6, MacBook, Mac Studio, Mac Max, from 16 GB to 512 GB unified memory. Covers MLX engine, Metal backend, wired limit, and the 75% rule.

**Status:** Documented from cited sources. NOT measured in this repo. No Apple Silicon run exists here; all numbers are from community sources and one orchestrator-verified data point.

---

## The two numbers that decide everything on Mac

1. **How much unified memory**: determines which models you can load at all
2. **Memory bandwidth (GB/s)**: determines how fast they generate. Decoding reads memory linearly, so bandwidth is the speed limiter.

**The 75% rule:** macOS reserves ~25% of unified memory for system. The GPU can use ~75% for model + KV + overhead. Sources: https://llmconfigurator.com/en/guides/mac-local-ai-buying-guide

| Mac | Total RAM | Usable for GPU | Bandwidth |
|---|---|---|---|
| Mac mini M6 base | 16 GB | ~12 GB | 170 GB/s |
| Mac mini M6 24 GB | 24 GB | ~18 GB | 170 GB/s |
| Mac mini M6 32 GB | 32 GB | ~24 GB | 170 GB/s |
| Mac mini M5 Pro 64 GB | 64 GB | ~48 GB | 307 GB/s |
| Mac Studio M5 Max 128 GB | 128 GB | ~96 GB | 614 GB/s |
| Mac Studio M5 Ultra 256 GB | 256 GB | ~192 GB | 1,229 GB/s |
| Mac Studio M5 Ultra 512 GB | 512 GB | ~384 GB | 1,229 GB/s |

**Critical:** Bandwidth matters more than capacity for speed. A Mac mini M5 Pro (64 GB, 307 GB/s) outperforms a Mac mini M6 (16 GB, 170 GB/s) on speed despite having 4× the RAM.

---

## The wired limit (the budget)

The budget on macOS is the GPU's wired limit, NOT total RAM. This is different from NVIDIA where VRAM is fixed.

### Check your current limit:

```bash
# System wired limit (MiB):
sysctl iogpu.wired_limit_mb

# MLX's view of the device:
python -c "import mlx.core as mx; print(mx.metal.device_info())"
# → max_recommended_working_set_size (MiB), memory_size (total RAM in bytes)
```

### Default fractions (community-reported):

| RAM | Default GPU budget | Source |
|---|---|---|
| ≤ 36 GB | ~2/3 of RAM | headroom issue #13 (GitHub) |
| > 36 GB | ~3/4 of RAM | headroom issue #13 (GitHub) |

**Sources disagree on exact figures for large machines.** Treat as "about" and always read the actual value.

### Raise it (in steps, close other apps):

```bash
sudo sysctl iogpu.wired_limit_mb=<MB>  # keep strictly under total RAM
# Practitioners stop around 85–90% of RAM
# Resets on reboot; /etc/sysctl.conf persistence is community-reported, unverified
```

### Older macOS:

- Ventura / Monterey used `debug.iogpu.wired_limit` in bytes, community-reported, unverified here.

---

## Engine: MLX / Metal

### MLX quants (mlx-community org on HF)

Verified via HF API:
- List: `https://huggingface.co/api/models?author=mlx-community&search=<name>&limit=50&expand[]=safetensors&expand[]=downloads`
- Sizes: `https://huggingface.co/api/models/<repo_id>/tree/main` → sum `size` of `*.safetensors`

### Fit estimate:

```bash
python bench/mlx_quant_search.py   # estimate
# Then confirm with a real load: never by arithmetic alone
```

### Worked example (orchestrator-verified, 2026-10-05):

`mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` = **16.0 GiB** of weights.
- Does NOT fit a 24 GB Mac's default ~16 GB wired limit
- Fits with limit raised to 20 GB, with ~4 GB left for KV and overhead (tight)
- The 20 GB is the general setting for a 24 GB Mac, not a figure reported for that model

### Ollama as MLX wrapper:

Ollama previews MLX as an alternative engine (March 2026) and makes it the default on Macs with >32 GB unified memory. For tuning purposes, Ollama handles backend detection automatically but exposes fewer tuning knobs.

---

## Per-tier Mac guide

### Mac mini M6 16 GB (entry)

- Budget: ~12 GB for GPU
- What fits: Cosmos 3 Nano (11.9 GiB), Gemma 3 12B (11.1 GiB)
- Bandwidth: 170 GB/s → 8B at ~11–22 tok/s
- Use case: chat, email, light agent tasks
- **Raise wired limit?** 16 GB Mac defaults to ~16 GB for GPU; models at 16 GiB weight won't fit without raising it to ~20 GB (leaving ~4 GB for everything else, very tight)

### Mac mini M6 32 GB (budget AI)

- Budget: ~24 GB for GPU
- What fits: Qwen3.5 35B-A3B (23.8 GiB), Qwen3.6 35B-A3B (23.8 GiB) at Q4, comfortable daily driver
- Bandwidth: 170 GB/s
- **Raise wired limit?** Likely yes for 24+ GiB models; default is ~24 GB for GPU at 32 GB RAM

### Mac mini M5 Pro 64 GB (prosumer)

- Budget: ~48 GB for GPU
- What fits: Qwen2.5 72B (47.0 GiB), serious local AI at 307 GB/s
- Bandwidth: 307 GB/s, significant speed upgrade over M6

### Mac Studio M5 Max 128 GB (workstation)

- Budget: ~96 GB for GPU
- What fits: GPT-OSS 120B (71.9 GiB), Llama 4.5 Scout (69.4 GiB)
- Bandwidth: 614 GB/s, 3.6× faster than M6 per the bandwidth ladder
- Source: ModelFit Mac Studio guide (2026)

### Mac Studio M5 Ultra 256 GB (frontier)

- Budget: ~192 GB for GPU
- What fits: DeepSeek V4-Flash (173 GiB) at tight fit
- Bandwidth: 1,229 GB/s, 7× faster than M6
- Multi-unit: 5 on a network (user scenario), Thunderbolt 5 + RDMA, Apple claims 3× inference of one (unbenchmarked)

### Mac Studio M5 Ultra 512 GB (bleeding edge)

- Budget: ~384 GB for GPU
- What fits: Qwen3-Coder 480B-A35B (292 GiB), MiniMax M3 428B (264 GiB)
- Announced late 2026

---

## Claude Code on Mac

Native Anthropic endpoint via oMLX works, point Claude Code at a local model via env vars:

```bash
export ANTHROPIC_BASE_URL=<local-mlx-endpoint>
export ANTHROPIC_AUTH_TOKEN=<token>
export ANTHROPIC_DEFAULT_SONNET_MODEL=<local-model>
```

The `bench/` tools work against `mlx_lm.server` (OpenAI-compatible endpoint). Flags for the server haven't been checked here, confirm with `--help`.

---

## Traps (Mac specific)

1. **Wired limit resets on reboot.** Persisting via `/etc/sysctl.conf` is community-reported, unverified here.
2. **Weights are not the working set.** KV cache, engine overhead, and macOS all compete for the same wired pool. A quant that fits on paper can fail on load.
3. **Bandwidth is the speed limiter.** More RAM ≠ faster. A 64 GB Mac with 307 GB/s beats a 16 GB Mac with 170 GB/s on speed.
4. **mlx-community quants are multi-file (sharded).** Check safetensors sum via HF API, don't trust single-file estimates.
5. **macOS version matters.** The 75% fraction varies; newer macOS may differ from community reports.
6. **No MTP draft context separate allocation** (unlike llama.cpp), but MLX speculative decoding works differently; confirm with `--help`.
7. **Ollama default MLX for >32 GB Macs** (March 2026). Verify which engine Ollama selected.

---

## Sources

- Mac local LLM buying guide (LLM Configurator, Sep 2026): https://llmconfigurator.com/en/guides/mac-local-ai-buying-guide
- Mac Studio LLM guide (ModelFit, 2026): https://modelfit.io/mac-studio/m2/
- Apple Silicon LLM guide (canitrun.dev, 2026): https://canitrun.dev/guides/apple-silicon-llm-guide/
- MLX-LM 2026 explanation (PromptQuorum): https://www.promptquorum.com/power-local-llm/mlx-lm-explained
- M6 Mac mini local AI (ModelFit, 2026): https://modelfit.io/blog/m6-mac-mini-local-llm/
- Apple Silicon inference SOTA (Reddit r/LocalLLaMA, Aug 2026): https://www.reddit.com/r/LocalLLaMA/comments/1vphr8u/
- Mac Studio Ultra 256GB and LLM (Reddit r/MacStudio): https://www.reddit.com/r/MacStudio/comments/1w30wks/
- How to choose hardware for LLM inference (Medium): https://medium.com/@michael.hannecke/how-to-choose-hardware-for-local-llm-inference-163632d93dcb
- Mac mini M6 local AI (Contra Collective, 2026): https://contracollective.com/blog/mac-mini-m6-local-llm-inference-refresh-2026
- Mac mini M6 vs M5 Studio (Wavect): https://wavect.io/blog/mac-mini-m6-vs-mac-studio-m5-local-ai/
- Mac mini M6 vs M5 Ultra (PopularAI): https://www.popularai.org/p/m5-ultra-local-ai-unified-memory-guide
- RTX 5090 multi-GPU (Reddit r/LocalLLaMA): https://www.reddit.com/r/LocalLLaMA/comments/1wbj1tk/ (for cross-reference)
- MLX docs (wired limit): https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html
- headroom issue #13 (default fractions): https://github.com/blaine-hiers/headroom/issues/13
