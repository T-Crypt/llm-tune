# llama-fit-params: broadening across all backends

Design brief from the tool's author: "llama-fit-params don't need to be so strict on WHAT gets them to begin with." The tool works across all modern llama.cpp backends; CUDA is only one of them.

**Verified:** llama-fit-params works across:
- ✅ CUDA (NVIDIA), currently in the skill
- ✅ SYCL (Intel Arc), verified by community (Reddit, GitHub discussions)
- ✅ Vulkan (universal), works on Intel, AMD, Apple
- ✅ HIP/ROCm (AMD Strix/Gorgon Halo, RX 7900 XTX), verified in Strix Halo guides
- ⚠️ Metal/MLX, different memory accounting; `bench/mlx_quant_search.py` serves the same role

---

## What llama-fit-params does (universally)

Reads model file size, calculates projected device memory vs available, adjusts context size, offload layers, and overflow to CPU/system RAM as needed.

**The arithmetic is the SAME across backends:**
```
projected_memory = model_file + KV_cache + compute_buffers + mmproj + draft_context
```

Only the **memory accounting** differs per backend:
- **CUDA:** VRAM = discrete GPU memory (24 GB on 4090)
- **SYCL:** VRAM = iGPU share of system RAM (12 GB on Arc B580)
- **Vulkan:** VRAM = GPU-specific (varies)
- **HIP/ROCm:** VRAM = GPU-allocated unified memory (96 GB on Strix Halo, 160 GB on Gorgon)
- **Metal:** "VRAM" = wired limit on unified memory (varies by Mac)

---

## Backend-specific fit advice

### NVIDIA CUDA (current in skill)
- Standard fit probing: model file size → projected peak → adjust context/offload
- Auto-fit and manual offload are mutually exclusive: `common_fit_params` aborts when `-ngl` is already set
- The fit is a gate value, not a guarantee: 0.17 GiB headroom failed, a model that loads can OOM mid-inference (finding 5)

### Intel Arc (SYCL)
- Same KV math, different allocation shape
- iGPU shares system RAM, no separate VRAM budget
- Use SYCL or Vulkan backend
- Fit probing works the same way; the budget is total system RAM minus OS
- **BIOS setting:** iGPU allocation in BIOS controls GPU addressable memory (varies by OEM)

### AMD (HIP/ROCm)
- Same arithmetic, HIP memory accounting is different
- VRAM = GPU-allocated unified memory (96 GB on Strix Halo, 160 GB on Gorgon)
- `HSA_OVERRIDE_GFX_VERSION` required (e.g., 11.5.1 for Strix Halo)
- Fit probing works; verified in LocalAimaster Strix Halo guide

### Apple Silicon (Metal/MLX: equivalent tool)
- Different arithmetic: model + KV share one pool, macOS reserves 25%
- `bench/mlx_quant_search.py` serves the same role as llama-fit-params for MLX
- Check: `sysctl iogpu.wired_limit_mb` (the budget) and `mx.metal.device_info()` (MLX's view)
- Wired limit is the budget, model + KV must fit in ~75% of total RAM

---

## The broadening: what changes for non-NVIDIA hardware

| Hardware | Backend | Fit tool | Key budget parameter | Bandwidth |
|---|---|---|---|---|
| RTX 4090 | CUDA | `llama-fit-params` | 24 GB VRAM | 1,008 GB/s |
| Intel Arc B580 | SYCL/Vulkan | `llama-fit-params` | ~12 GB iGPU share of RAM | ~170 GB/s |
| Strix Halo 128 GB | HIP/ROCm | `llama-fit-params` | 96 GB GPU-allocatable | 256 GB/s |
| Gorgon Halo 192 GB | HIP/ROCm | `llama-fit-params` | 160 GB GPU-allocatable | 273 GB/s |
| Mac mini M6 16 GB | Metal/MLX | `bench/mlx_quant_search.py` | ~12 GB (wired limit) | 170 GB/s |
| Mac Studio M5 Max 128 GB | Metal/MLX | `bench/mlx_quant_search.py` | ~96 GB (wired limit) | 614 GB/s |
| RTX 6000 Ada | CUDA | `llama-fit-params` | 48 GB VRAM | 696 GB/s |
| vLLM (any) | vLLM | Engine-managed | Batch capacity + KV pool | Varies |

---

## Common traps across all backends

1. **Fit on paper ≠ fit in practice.** 0.17 GiB headroom failed on the measured card. Any backend can run out mid-inference as buffers grow with depth.
2. **The engine's own log is authoritative.** `KV buffer size`, `compute buffer size`, model file size, read these, don't trust arithmetic alone.
3. **Any PID on the card that is not the model server is a bug.** An embedding daemon held 11.3 GiB after its job ended. This applies to all backends on all hardware.
4. **OS matters.** Windows silently spills VRAM overflow to system RAM and decodes 10–20% slower than Linux on the same card. macOS has its own memory reservation. Linux is the most predictable.
5. **Version pinning.** Flag names and defaults change between builds (`--draft-max` removed → `--spec-draft-n-max`). Pin runtime versions.
6. **Auto-fit and manual offload are mutually exclusive** (`common_fit_params` aborts when `-ngl` is already set). Applies to all llama.cpp backends.

---

## Verification protocol (backend-agnostic)

For any backend, on any hardware:

1. **Read the engine's buffer log**: model file size, KV buffer, compute buffer, peak VRAM
2. **Compare against available memory**: the budget is backend-specific (see table above)
3. **Run the bench** (`bench/quick_bench.md`) measures: memory accounting, prefill/decode at depth, recall at depth, quality probe
4. **Hold quality constant**: a speed claim without a quality metric is not a result
5. **Repeat**: run-to-run variance is ±1–2 bugs on a 12-bug test
6. **Publish corrections**: if a number is wrong, fix it and publish a dated correction

---

## Sources

- llama.cpp fit-params README: https://github.com/ggml-org/llama.cpp/blob/master/tools/fit-params/README.md
- llama.cpp SYCL docs (Intel): https://www.intel.com/content/www/us/en/developer/articles/technical/run-llms-on-gpus-using-llama-cpp.html
- Reddit: llama-fit-params on Intel Arc: https://www.reddit.com/r/LocalLLaMA/comments/1srvqar/
- LocalAimaster Strix Halo guide (ROCm, HIP, fit): https://localaimaster.com/blog/strix-halo-ai-max-395-guide
- Mac local LLM guide (MLX wired limit): https://llmconfigurator.com/en/guides/mac-local-ai-buying-guide
- llama.cpp ROCm integration: https://rocm.blogs.amd.com/ecosystems-and-partners/llama-cpp/README.html
