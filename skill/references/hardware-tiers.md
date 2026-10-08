# Hardware tier universe

Every hardware class users actually run local models on, from 8 GB budget cards to 512 GB Mac Studios and DGX Spark clusters. Each tier includes: what fits, what context is affordable, failure modes, engine-specific fit advice, and the bench to run on that box.

**This file replaces the repo's single-card assumption.** Every number in `references/tables/` was measured on one 24 GB RTX 4090-class card. The tables in this file are tier rules (what changes where), none of these numbers are measurements from this repo. They are compiled from cited sources; verify them on your own box before quoting.

---

## The two numbers that decide everything

For any hardware class: **(1) how much memory the model can address** and **(2) how fast that memory is**. On discrete NVIDIA cards these are VRAM size and bandwidth. On unified-memory systems (Apple Silicon, AMD Strix/Gorgon Halo, Intel Arc iGPU) they're the same pool, model weights, KV cache, compute buffers, and OS all compete for one address space.

---

## Tier 0: 8 GB entry (RTX 4060, Intel Arc B580, Mac mini M6 base)

**What fits:**
| Model class | Quant | Notes |
|---|---|---|
| 7–8B | Q4_K_M | RTX 4060: ~6.5 GiB file, ~6 GiB headroom after fixed cost |
| 3–4B | Q8_0 | Tight but doable; RTX 4060 8 GB, Arc B580 12 GB, M6 Mac 16 GB unified |
| 7B | Q4_K_S | RTX 4060: workable, no headroom for context |

**Failure modes:**
- RTX 4060 8 GB: anything above 8B Q4 is over budget. Context > 8k is a luxury. MCP bloat is lethal, must debloat to 5–7 tools.
- Intel Arc B580 12 GB: no CUDA. Use SYCL or Vulkan backend. 7–14B Q4 quant fits. llama-fit-params works via SYCL/Vulkan (see `engine-backends.md`).
- Mac mini M6 16 GB unified: macOS reserves ~25% → ~12 GB usable. Cosmos 3 Nano (11.9 GiB), Gemma 3 12B (11.1 GiB). 170 GB/s bandwidth → 8B at ~11–22 tok/s. Entry level: chat and email only.

**The constraint at this tier:** every byte counts; harness debloat is survival, not optimisation.

**Sources:** Intel Arc B580 local LLM suitability (PromptQuorum, 2026); Mac mini M6 16 GB/32 GB specs (Apple, 2026); llama.cpp SYCL documentation (Intel).

---

## Tier 1: 12–16 GB consumer (RTX 4070 Ti, RTX 4080, Mac mini M6 24/32 GB)

**What fits:**
| Hardware | Usable memory | What fits |
|---|---|---|
| RTX 4070 Ti 12 GB | ~10 GB | 13–14B Q4_K_M; 7B at higher quants |
| RTX 4080 16 GB | ~14 GB | 17B Q4_K_M (tight); 13B comfortable |
| Mac mini M6 24 GB | ~18 GB | Mistral Small 3 (17.2 GiB), Devstral Small 2 (17.0 GiB) |
| Mac mini M6 32 GB | ~24 GB | Qwen3.5 35B-A3B (23.8 GiB), Qwen3.6 35B-A3B (23.8 GiB), comfortable daily driver at 170 GB/s |

**Context budget:** At 0.033 GiB/1k tokens (q8_0 KV, dense model), 32k context = 1.06 GiB on a 24 GB budget machine. Drop context to buy a quant tier (131k → 65k buys IQ3_M → Q4_K_M on the measured card).

---

## Tier 2: 24 GB sweet spot (RTX 4090)

**This is the repo's measured class.** All `references/tables/` numbers are from this tier. No changes needed here, it's the proven base.

| Property | Value |
|---|---|
| VRAM | 24 GB (24,564 MiB measured) |
| Bandwidth | 1,008 GB/s |
| What fits at 131k ctx | IQ3_M (13.5 GiB file + 7.97 GiB fixed = 21.5 GiB peak, 2.5 GiB free) |
| What fits at 262k ctx | IQ4_XS with q4_0 KV (21.65 GiB); IQ4_XS-MTP does NOT fit (23.83/24.00 GiB) |
| MoE decode | 246–324 t/s |
| Dense 27B decode | ~52–119 t/s |

---

## Tier 3: 32 GB high-end (RTX 5090)

| Property | Value |
|---|---|
| VRAM | 32 GB GDDR7 |
| Bandwidth | 1,792 GB/s |
| What fits | 32B dense at Q4, 27B at Q8 on single card |
| Multi-GPU | Two 5090s = 64 GB → 70B models via tensor parallel |
| Benchmark data | ~365 tok/s on 8B Q4 (vs 200 on 4090, 52 on Strix Halo) |

**vLLM path:** PagedAttention, tensor-parallel across 2× 5090 for 70B at Q4. Same fit arithmetic, but KV pool is engine-managed.

**Sources:** RTX 5090 specs (NVIDIA); VRAM requirements guide (VRLA Tech, 2026); RTX 5090 multi-GPU strategies (Reddit r/LocalLLaMA, 2026).

---

## Tier 4: 48 GB professional (RTX 6000 Ada, RX 7900 XTX)

| Hardware | VRAM | Bandwidth | What it runs |
|---|---|---|---|
| RTX 6000 Ada | 48 GB | 696 GB/s | Dense 27B at Q8, 30B A3B at Q8 |
| RX 7900 XTX | 24 GB discrete | 960 GB/s (HBM) | Same as 24 GB tier but faster; ROCm via HIP |

**Key:** 48 GB means what 24 GB needed q4_0 KV for, runs at q8_0 here. KV at q8_0 for 131k = 4.25 GiB → 48 GB buys dense 30B + long context + headroom.

---

## Tier 5: 64–128 GB unified (Mac Studio M5 Max 128 GB, Strix Halo 128 GB, Mac mini M5 Pro 64 GB)

### Apple Silicon (unified memory: the 75% rule applies)

| Hardware | Total RAM | Usable for GPU | Bandwidth | What fits |
|---|---|---|---|---|
| Mac mini M5 Pro 64 GB | 64 GB | ~48 GB | 307 GB/s | Qwen2.5 72B (47.0 GiB), serious local AI |
| Mac Studio M5 Max 128 GB | 128 GB | ~96 GB | 614 GB/s | GPT-OSS 120B (71.9 GiB), Llama 4.5 Scout (69.4 GiB) |
| Mac Studio M5 Ultra 256 GB | 256 GB | ~192 GB | 1,229 GB/s | DeepSeek V4-Flash (173 GB) at tight fit |
| Mac Studio M5 Ultra 512 GB | 512 GB | ~384 GB | 1,229 GB/s | Qwen3-Coder 480B-A35B (292 GB), MiniMax M3 428B (264 GB) |

**The 75% rule:** macOS reserves ~25% of unified memory for system. A 128 GB Mac has ~96 GB for model + KV. Buy one tier above your model size because context eats GB on top.

**Bandwidth matters more than capacity for speed:** M5 Pro at 307 GB/s beats M6 at 170 GB/s even with more RAM.

**Sources:** Mac local LLM buying guide (LLM Configurator, Sep 2026); Mac Studio LLM guide (ModelFit, 2026); Apple Silicon LLM guide (canitrun.dev, 2026).

### AMD Strix Halo (unified memory: separate VRAM budget)

| Property | Value |
|---|---|
| Total unified memory | 128 GB LPDDR5X-8000 |
| GPU-allocatable | 96 GB |
| Bandwidth | 256 GB/s |
| What fits | 70B Q4 (~40 GB) with long context, 70B Q8 (~75 GB) |
| Price | ~$1,999 launch |
| BIOS setting | Raise iGPU allocation to 96 GB (128 GB system) |

**vs RTX 4090:** Strix Halo bandwidth is ~1/4 of 4090 (256 vs 1008 GB/s), so models that DO fit run 4–7× slower. But models that DON'T fit on 24 GB DO fit on 128 GB unified. The trade is capacity vs speed.

**vLLM-ROCm:** Available but bandwidth-bound. Same constraint as llama.cpp.

**Sources:** Strix Halo guide (LocalAimaster, May 2026); Strix Halo deep dive (Reddit r/StrixHalo, 2026); Ryzen AI Max+ 395 specs (AMD).

---

## Tier 6: 192–256 GB unified (Gorgon Halo 192 GB, Mac Studio M5 Ultra 256 GB)

### Gorgon Halo PRO 495 (AMD Ryzen AI Max PRO 400)

| Property | Value |
|---|---|
| Total unified memory | 192 GB LPDDR5X-8533 |
| GPU-allocatable | 160 GB |
| Bandwidth | 273 GB/s |
| What fits | 300B at INT4 (~150 GB weights + 42 GB headroom), 150 GB headroom for KV |
| Price | $3,449+ (coming) |
| Compute | 131 TOPS combined AI compute |

**Same ROCm stack as Strix Halo.** HSA_OVERRIDE_GFX_VERSION required.

### Mac Studio M5 Ultra 256 GB

Same as tier 5 but at frontier scale. 192 GB usable, 1,229 GB/s bandwidth.

---

## Tier 7: 512 GB+ frontier (Mac Studio M5 Ultra 512 GB, 5× DGX Spark, 3× RTX 6000, H100/H200 class)

### Multi-box clusters

| Cluster | Total memory | Architecture | Use case |
|---|---|---|---|
| 5× DGX Spark | 320 GB (64 GB each, GB10 GPU) | ConnectX-7 RDMA, tensor-parallel vLLM, sparkrun one-command | Models >200B, multi-tenant serving |
| 3× RTX 6000 | 144 GB total (48 GB each) | vLLM or llama.cpp distributed | 70B+ across nodes, 27B at Q8 per node |
| 5× Mac Studio Max | 1,280 GB unified (256 GB each) | Thunderbolt 5 + RDMA (Apple claims 3× inference of one, unbenchmarked) | Frontier Mac network |
| H100/H200 class | 80–141 GB per GPU | vLLM data parallel, PagedAttention | Data center-class local serving |

**Cluster tuning is about load balancing and KV distribution, not per-node tuning.** The per-node advice from this skill still applies. The cluster adds resource orchestration (vLLM tensor-parallel, nginx/vLLM Router load balancing).

**Sources:** DGX Spark vLLM clustering (NVIDIA build, MindStudio, vLLM blog Jun 2026); vLLM production deployment (Spheron, 2026); multi-model serving (vLLM discussions, 2026).

---

## Engine-specific fit arithmetic per tier

| Engine | Memory accounting | Fit arithmetic | Tier notes |
|---|---|---|---|
| llama.cpp CUDA | Discrete VRAM | File + KV + compute + mmproj + draft | Tier 2 base (measured) |
| llama.cpp SYCL | Unified (iGPU shares system RAM) | Same math, no separate VRAM budget | Intel Arc; model + KV + compute all from one pool |
| llama.cpp Vulkan | Universal | Same math | Works on Intel, AMD, Apple; less mature profiling |
| llama.cpp HIP/ROCm | GPU-allocated unified memory | Same math, different allocation shape | AMD Strix/Gorgon: VRAM = GPU-allocatable pool (96/160 GB) |
| MLX/Metal | Unified, macOS reserves 25% | Wired limit is the budget; model + KV must fit in 75% of RAM | All Mac tiers; `bench/mlx_quant_search.py` for estimates |
| Ollama | Wraps llama.cpp | Same as llama.cpp underneath | Fewer tuning knobs; simplest entry point |
| vLLM | Batch capacity + KV pool | Different: PagedAttention, continuous batching | Cluster serving; 2–3 endpoints on a network (see `vllm-local.md`) |

**See also:** `engine-backends.md` for backend-specific commands, traps, and fit verification per engine.

---

## The hardware upgrade decision

"Should I upgrade my GPU, my Mac, or add nodes?" is a tuning decision:
- **Bottleneck is VRAM** → upgrade (smaller tier jump: 24→32 GB card, or 128→256 GB Mac)
- **Bottleneck is bandwidth** → different platform (Strix Halo 256 GB/s vs RTX 4090 1,008 GB/s; Mac Studio 1,229 GB/s)
- **Bottleneck is context** → unified memory platform (Mac Studio, Gorgon Halo)
- **Compare against renting first** (LLM Configurator advice for 512 GB Mac Studio)

---

## Tier quick-reference: what to tell each user

| User says | Tier | First advice |
|---|---|---|
| "I have a budget PC / an old laptop" | 0 | Hugest compression, smallest model, debloat harness NOW |
| "I have a Mac mini M6" | 0 (16 GB) / 1 (24–32 GB) | Check wired limit; 16 GB = ~12 GB usable; use MLX |
| "I have an RTX 4070 / 4080" | 1 | Context vs quant is the lever; 32k ctx ≈ 1 GiB KV |
| "I have an RTX 4090" | 2 | This repo's measured base; run `bench/quick_bench.md` |
| "I have an RTX 5090" | 3 | 32B dense Q4; tensor parallel 2× for 70B |
| "I have an Apple Silicon Mac" | 0–7 (depends on model) | Check `iogpu.wired_limit_mb`; 75% rule; see `mlx-mac-tuning.md` |
| "I have a Strix Halo / Gorgon Halo" | 5–6 | ROCm/HIP backend; BIOS GPU allocation; 256/273 GB/s is slow but big fits |
| "I have an Intel Arc" | 0 | SYCL or Vulkan backend; no CUDA; 12 GB VRAM on B580 |
| "I run vLLM on a network" | 3–7 | `vllm-local.md`; batch capacity + KV pool, not model fit alone |
| "I have a server / DGX cluster" | 7 | Tensor parallel, data parallel, load balancing; per-node advice still applies |
