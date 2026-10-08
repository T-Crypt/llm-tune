# Intel Arc & AMD unified memory (Strix/Gorgon Halo)

Tuning for Intel Arc GPUs and AMD APU-based systems (Strix Halo, Gorgon Halo) — all unified memory, no discrete NVIDIA VRAM.

---

## The shared reality: unified memory

No VRAM split — model weights, KV cache, compute buffers, and OS all share one memory pool. This means:
- **More capacity** than a discrete card (Strix Halo: 128 GB, Gorgon Halo: 192 GB)
- **Less bandwidth** than a discrete card (Strix: 256 GB/s, Gorgon: 273 GB/s vs RTX 4090: 1,008 GB/s)
- **The trade is capacity vs speed** — big models fit, they run slower

---

## Intel Arc GPUs

### Hardware profile

| GPU | VRAM | Best for |
|---|---|---|
| Intel Arc B580 | 12 GB | 7–14B Q4 quant, entry-level local AI |
| Intel Arc Pro B70 | 16 GB+ | Community testing (llama.cpp SYCL) |

### Backend: SYCL (preferred for Intel) or Vulkan (universal)

```bash
# SYCL backend (Intel Arc specific):
./llama-server --backend sycl -ngl 99 -ub 1024 --ctx-size <N> ...

# Vulkan backend (universal, works on Intel):
./llama-server --backend vulkan -ngl 99 -ub 1024 --ctx-size <N> ...
```

### Memory accounting

**Key difference from NVIDIA:** iGPU shares system RAM. No separate VRAM budget. Model + KV + compute all from the system pool.

- Total system RAM is the budget (minus OS)
- BIOS iGPU allocation controls GPU addressable memory
- Memory pressure from other processes is more impactful (shared pool)

### Fit verification

Same as all backends: read engine's buffer log (`model file`, `KV buffer size`, `compute buffer size`), compare against system RAM. llama-fit-params works via SYCL/Vulkan.

### Sources

- Intel: Run LLMs on Intel GPUs using llama.cpp: https://www.intel.com/content/www/us/en/developer/articles/technical/run-llms-on-gpus-using-llama-cpp.html
- Best Intel Arc GPU for local LLMs (PromptQuorum, 2026): https://www.promptquorum.com/prompt-bites/best-intel-arc-gpu-local-llm
- Intel Arc Pro B70 discussion (GitHub, 2026): https://github.com/ggml-org/llama.cpp/discussions/27593
- vLLM support: minimal on Intel GPUs (vLLM alternatives guide, PremAI, 2026)

---

## AMD Strix Halo (Ryzen AI Max+ 395)

### Hardware profile

| Property | Value |
|---|---|
| Architecture | Ryzen AI Max+ 395 (16 Zen 5 CPU, 40 CU RDNA 3.5 iGPU) |
| Total unified memory | 128 GB LPDDR5X-8533 |
| GPU-allocatable | 96 GB |
| Bandwidth | 256 GB/s |
| AI compute | 131 TOPS combined |
| Price | ~$1,999 launch |

### What fits at 128 GB unified (96 GB GPU)

| Model | Quant | Fits |
|---|---|---|
| 70B | Q4 | ~40 GB — fits comfortably |
| 70B | Q8 | ~75 GB — fits with moderate context |
| 100B MoE | 4-bit active experts | Fits |
| DeepSeek V4-Flash | Default | Fits (128 GB total, ~96 GB GPU) |

### Backend: HIP/ROCm

```bash
# Set GPU architecture (REQUIRED):
export HSA_OVERRIDE_GFX_VERSION=11.5.1

# Standard flags:
./llama-server -ngl 99 -ub 1024 --ctx-size <N> ...
```

### BIOS setting (CRITICAL)

Raise iGPU allocation in BIOS:
- 128 GB system → set to 96 GB for GPU
- 192 GB system → set to 160 GB for GPU

Without this, the GPU may have far less addressable memory than the system has total.

### vLLM-ROCm

Available but bandwidth-bound. Same constraint as llama.cpp: 256 GB/s vs 1,008 GB/s (RTX 4090) means 4–7× slower on equivalent models.

### Sources

- LocalAimaster Strix Halo guide (May 2026): https://localaimaster.com/blog/strix-halo-ai-max-395-guide
- AMD Ryzen AI Max+ 395 specs: https://localaimaster.com/blog/strix-halo-ai-max-395-guide
- Strix Halo review (Micro Center): https://www.microcenter.com/site/mc-news/article/amd-ryzen-ai-halo-review.aspx
- Strix Halo benchmarks (Reddit r/StrixHalo, 2026): https://www.reddit.com/r/StrixHalo/comments/1tv41uh/
- Strix Halo buyer's guide (Reddit r/StrixHalo, 2026): https://www.reddit.com/r/StrixHalo/comments/1ufblem/
- Strix Halo vs DGX Spark comparison (Reddit): bandwidth close (256 vs 273 GB/s)

---

## AMD Gorgon Halo PRO (Ryzen AI Max PRO 400)

### Hardware profile

| Property | Value |
|---|---|
| Architecture | Ryzen AI Max PRO 400 |
| Total unified memory | 192 GB LPDDR5X-8533 |
| GPU-allocatable | 160 GB |
| Bandwidth | 273 GB/s |
| AI compute | 131 TOPS combined |
| Memory headroom | ~150 GB for model + KV at INT4 |
| Price | $3,449+ (coming) |

### What fits at 192 GB unified (160 GB GPU)

| Model | Quant | Fits |
|---|---|---|
| 300B | INT4 | ~150 GB weights + headroom for KV |
| 70B | Q8 | Comfortable with room for context |
| 150B MoE | 4-bit | Fits |

### Same ROCm stack as Strix Halo

- `HSA_OVERRIDE_GFX_VERSION` required (check correct version for PRO 400)
- Same HIP backend, same vLLM-ROCm constraints
- Linux preferred; Windows via WSL2

### Sources

- Ryzen AI Max PRO 400 (Tech Insider, Sep 2026): https://tech-insider.org/amd-ryzen-ai-max-pro-400-192gb-unified-memory-2026/
- Framework 192GB Desktop (Medium, 2026): https://medium.com/@mayhemcode/the-new-192gb-mini-pcs-cost-nearly-twice-as-much-their-gpu-barely-changed-aab34807426a
- Gorgon Halo PRO specs (ModelFit): https://modelfit.io/gpu/ryzen-ai-max-plus-395/

---

## Bandwidth reality check

| Platform | Memory | Bandwidth | Relative speed (vs RTX 4090) |
|---|---|---|---|
| RTX 4090 | 24 GB | 1,008 GB/s | 1× (baseline) |
| Strix Halo 128 GB | 96 GB GPU | 256 GB/s | ~0.25× (4× slower) |
| Gorgon Halo 192 GB | 160 GB GPU | 273 GB/s | ~0.27× (3.7× slower) |
| Mac Studio M5 Max | 96 GB | 614 GB/s | ~0.61× (1.6× slower) |
| Mac Studio M5 Ultra | 192 GB | 1,229 GB/s | ~1.22× (faster) |

**Translation:** A 70B model at Q4 takes ~40 GB. It fits on both Strix (96 GB) and 24 GB card is over budget. But it runs 4× slower on Strix. If you're latency-sensitive, it's a tradeoff. If you just need it to run at all, Strix wins.

---

## OS considerations

- **Linux:** Better ROCm support, more stable, preferred for Strix/Gorgon
- **Windows:** Works via WSL2; some ROCm features may be limited
- **macOS:** Not applicable (different unified-memory stack — see `mlx-mac-tuning.md`)

---

## Sources (all)

- Intel Arc local LLM guide (Intel developer): https://www.intel.com/content/www/us/en/developer/articles/technical/run-llms-on-gpus-using-llama-cpp.html
- Intel Arc B580 best for local LLMs (PromptQuorum): https://www.promptquorum.com/prompt-bites/best-intel-arc-gpu-local-llm
- Strix Halo guide (LocalAimaster): https://localaimaster.com/blog/strix-halo-ai-max-395-guide
- Ryzen AI Max+ 395 (AMD Build 2026): https://www.amd.com/en/developer/resources/technical-articles/2026/amd-at-microsoft-build-2026.html
- Ryzen AI Max PRO 400 (Tech Insider, Sep 2026): https://tech-insider.org/amd-ryzen-ai-max-pro-400-192gb-unified-memory-2026/
- Strix Halo buyer's guide (Reddit): https://www.reddit.com/r/StrixHalo/comments/1ufblem/
- 192GB Framework Desktop (Medium): https://medium.com/@mayhemcode/the-new-192gb-mini-pcs-cost-nearly-twice-as-much-their-gpu-barely-changed-aab34807426a
- vLLM alternatives (PremAI, 2026): https://www.premai.io/blog/10-best-vllm-alternatives-for-llm-inference-in-production-2026/
- ROCm + llama.cpp (AMD blog): https://rocm.blogs.amd.com/ecosystems-and-partners/llama-cpp/README.html
