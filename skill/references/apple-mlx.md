# Apple Silicon / MLX

**Documented, not measured here.** Every number below is from the cited sources, not from a
run on this project's hardware. The fit arithmetic in the main skill assumes a discrete card
with its own VRAM; on Apple Silicon the card and the host share one pool, and the GPU can only
wire down part of it.

## The budget is the wired limit, not total RAM

- The system wired limit is the sysctl `iogpu.wired_limit_mb`. A value of `0` (the default)
  means macOS derives the limit from installed RAM.
  Source: MLX docs, https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html
- Community guides report the derived default as about 2/3 of RAM on machines with 36 GB or
  less, and about 3/4 above that. Sources disagree on exact figures for large machines, so
  treat it as "about" and read the value on the actual machine.
  Community source: https://github.com/blaine-hiers/headroom/issues/13
- Worked example (community-reported, not measured here): a 24 GB Mac defaults to about 16 GB
  available to the GPU. Raising the limit to 20 GB is a commonly used setting for a 24 GB Mac in
  general, it leaves several GB for macOS. It is **not** a figure reported for any particular
  model; do not present it as one. The model example below happens to need a raised limit, and
  20 GB is the general setting used to show the arithmetic.
- Read the real current limit, do not assume it:
  - `sysctl iogpu.wired_limit_mb`
  - `python -c "import mlx.core as mx; print(mx.metal.device_info())"` →
    `max_recommended_working_set_size` and `memory_size` (MLX docs).

## Raising the limit

- `sudo sysctl iogpu.wired_limit_mb=<MB>` (MLX docs).
- The limit "should remain strictly less than the total memory size" (MLX docs). In practice
  practitioners stop around 85–90% of RAM.
- Raise in steps, close other apps, and verify with a real load plus the bench, never by
  arithmetic alone. A model that fits on paper can still fail once KV and overhead are added.
- The sysctl resets on reboot (community guides). Persisting it via `/etc/sysctl.conf` is
  reported but unverified here.
- Older macOS (Ventura / Monterey) used `debug.iogpu.wired_limit` in bytes, community-reported,
  unverified here.

## Quants and the fit check

- MLX quants come from the `mlx-community` org on Hugging Face. Verified API:
  - list: `https://huggingface.co/api/models?author=mlx-community&search=<name>&limit=50&expand%5B%5D=safetensors&expand%5B%5D=downloads`
    (the brackets must be URL-encoded as `%5B%5D`)
  - sizes: `https://huggingface.co/api/models/<repo_id>/tree/main` → sum the `size` of
    `*.safetensors`
- Measured example (orchestrator-verified, 2026-10-05):
  `mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit` = 16.0 GiB of weights. That does not fit a
  24 GB Mac's default ~16 GB wired limit, and fits with the limit raised to 20 GB, with about
  4 GB left for KV and overhead, which is tight.
- Weights are only part of the budget. KV cache, the model's fixed overhead, and macOS all
  compete for the same wired pool. Use `bench/mlx_quant_search.py` for the estimate, then
  confirm with a real load.

## Server

`mlx_lm.server` exposes an OpenAI-compatible endpoint, so `bench/needle.py` and
`bench/quality_probe.py` work against it. Its flags have not been checked here, confirm with
`--help` on the user's install.

## Broader Mac coverage

For all Mac tiers (Mac mini M6 through Mac Studio M5 Ultra 512 GB), the wired limit, 75% rule,
per-tier model fit, bandwidth ladder, and upgrade decisions: see `references/mlx-mac-tuning.md`.

For Intel Arc and AMD Strix/Gorgon Halo (unified memory, SYCL/Vulkan/HIP/ROCm backends): see
`references/intel-amd-unified.md` and `references/llama-fit-broadening.md`.
