# Engine backend-specific fit advice

Every backend users actually run local models on, with backend-specific fit arithmetic, commands, and traps. The core arithmetic (file size + KV + compute + context) is universal — only the memory accounting differs.

**The core fit formula (all backends):**
```
peak_memory ≈ model_file + KV_cache + compute_buffers + mmproj + draft_context + OS_overhead
```

Where:
- **KV_cache** = `0.033 GiB per 1k tokens × context_length` (dense model, q8_0 KV; varies by architecture and KV type)
- **compute_buffers** = ~2.85 GiB on the measured card (single measurement, unverified; engine reports the authoritative number)
- **mmproj** = ~0.87 GiB (loaded)
- **draft_context** = separate allocation, can OOM when target fits (MTP)
- **OS_overhead** = 0.5–2 GiB depending on OS and compositor

---

## llama.cpp CUDA (NVIDIA GPUs)

**Memory accounting:** Discrete VRAM. Model + KV + compute must all fit in GPU memory. Windows silently spills overflow to system RAM (slow).

**Fit verification:**
```bash
# Engine's own log lines (authoritative):
# "CUDA0 model file ... GiB", "CUDA0 KV buffer size ... MiB",
# "CUDA0 compute buffer size ... MiB"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

**Common flags (measured on b11115 / llama-swap v257):**
```
-ngl 99 -ub 1024 --ctx-size <N> -fa on -ctk q8_0 -ctv q8_0 --parallel 1
--spec-type draft-mtp --spec-draft-n-max <N> --jinja --reasoning on --reasoning-budget <N>
```

**Traps:**
- `--fit` and `-ngl` are mutually exclusive: `common_fit_params` aborts when `-ngl` is already set
- Auto-fit probes VRAM and adjusts context/offload automatically — but it cannot override user-set `-ngl`
- Windows: "Prefer No Sysmem Fallback" makes OOM fail loudly instead of hanging; default silently spills to system RAM
- `--n-cpu-moe` is the correct overflow lever, never `-ngl` for MoE entries

---

## llama.cpp SYCL (Intel Arc GPUs)

**Memory accounting:** Unified memory — iGPU shares system RAM. Model + KV + compute all from one pool. No separate VRAM budget.

**Key difference from CUDA:** No VRAM ceiling; the constraint is total system RAM minus OS. The fit arithmetic is the same but the budget is larger and less predictable.

**Commands:**
```bash
# Use Vulkan or SYCL backend (SYCL for Intel Arc specifically):
./llama-server -ngl 99 -ub 1024 --ctx-size <N> -fa on -ctk q8_0 -ctv q8_0
# or with SYCL:
./llama-server --backend sycl -ngl 99 -ub 1024 --ctx-size <N> ...
```

**Traps:**
- System RAM is the budget, not VRAM — check total RAM, not GPU specs
- iGPU allocation in BIOS controls how much of unified memory the GPU can address (BIOS setting, varies by OEM)
- Memory pressure from other processes is more impactful (shared pool)
- llama-fit-params works via SYCL backend — same probing arithmetic, different target

**Sources:** Intel Arc local LLM guide (Intel developer, 2026); llama.cpp SYCL documentation; Intel Arc Pro B70 discussion (GitHub, 2026).

---

## llama.cpp Vulkan (universal: Intel, AMD, Apple)

**Memory accounting:** Same as backend-specific GPU memory. Vulkan is the most portable backend.

**Commands:**
```bash
./llama-server --backend vulkan -ngl 99 -ub 1024 --ctx-size <N> ...
```

**Traps:**
- Less mature memory profiling than CUDA — `KV buffer size` log line may differ from CUDA builds
- Use llama-fit-params to verify fit, don't trust arithmetic alone
- Universal backend means cross-platform consistency but potentially slower than native CUDA/HIP

---

## llama.cpp HIP/ROCm (AMD GPUs: RX 7900, Strix Halo iGPU, Gorgon Halo iGPU)

**Memory accounting:** GPU-allocated unified memory. On Strix Halo: 96 GB GPU-allocatable out of 128 GB total. On Gorgon Halo: 160 GB out of 192 GB.

**Commands:**
```bash
# Set GPU architecture version (REQUIRED for ROCm):
export HSA_OVERRIDE_GFX_VERSION=11.5.1   # Strix Halo (RDNA 3.5)
# For Ryzen AI Max PRO 400 (Gorgon Halo), check ROCm compatibility for the correct version
./llama-server -ngl 99 -ub 1024 --ctx-size <N> ...
```

**Traps:**
- `HSA_OVERRIDE_GFX_VERSION` is required; wrong version = fail or suboptimal
- Linux has better ROCm support; Windows works via WSL2
- Bandwidth is the bottleneck (Strix 256 GB/s vs RTX 4090 1,008 GB/s) — models that fit run 4–7× slower
- Same fit arithmetic as CUDA; llama-fit-params works via HIP backend

**Sources:** Strix Halo local LLM guide (LocalAimaster, May 2026); Strix Halo review (Micro Center); Ryzen AI Max PRO 400 (Tech Insider, Sep 2026).

---

## MLX/Metal (Apple Silicon: all M-series, Mac Mini/MacBook/Studio/Max)

**Memory accounting:** Unified memory pool. macOS reserves ~25% for system (fraction varies: ~2/3 at ≤36 GB, ~3/4 at >36 GB — community sources disagree; read the actual value).

**The wired limit is the budget:**
```bash
# Check current limit:
sysctl iogpu.wired_limit_mb
# Check MLX's view:
python -c "import mlx.core as mx; print(mx.metal.device_info())"
# → max_recommended_working_set_size, memory_size
```

**Raising the limit (in steps, close other apps):**
```bash
sudo sysctl iogpu.wired_limit_mb=<MB>  # keep strictly under total RAM (~85–90% max)
# Resets on reboot; /etc/sysctl.conf persistence is community-reported, unverified
```

**Fit verification:**
```bash
python bench/mlx_quant_search.py   # estimate, then real load to confirm
```

**Common quants (mlx-community, verified via HF API):**
| Model | Weight size | Fits 24 GB Mac (default ~16 GB)? | Fits at 20 GB limit? |
|---|---|---|---|
| mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit | 16.0 GiB | No (needs raised limit) | Tight (~4 GB left for KV) |

**Traps:**
- Weights are NOT the working set — KV and overhead compete for same pool
- A quant that fits on paper can fail on load
- MLX quants come from `mlx-community` org; multi-file (sharded) downloads
- No separate VRAM — model + KV + compute all from unified pool

**Sources:** MLX docs (ml-explore.github.io); headroom issue #13 (GitHub); MLX-LM guide (PromptQuorum, 2026); Apple Silicon LLM guide (canitrun.dev, 2026).

---

## Ollama (universal wrapper)

**Memory accounting:** Wraps llama.cpp. Same fit arithmetic underneath but fewer tuning knobs exposed.

**Commands:**
```bash
ollama pull <model>       # handles download + caching internally
ollama run <model>        # auto-detects backend
```

**Use case:** Simplest entry point for new users. For tuning, treat as llama.cpp underneath — same fit arithmetic, but less control over offload, KV type, and prefill settings.

**Traps:**
- Backend detection is hidden — verify which backend it selected
- Tuning knobs are limited; for serious tuning switch to llama.cpp directly
- Model format is GGUF internally

---

## vLLM (NVIDIA, AMD ROCm, cluster serving)

**Memory accounting:** Different from llama.cpp — fit is about batch capacity + KV pool, not just model fit. PagedAttention manages KV in pages, continuous batching handles request scheduling.

**sm_89 (RTX 4090) specifics:** `references/engine-research-sm89.md` maps which vLLM backends actually run on sm_89 (Triton/FA yes, FlashInfer GDN Blackwell-only), open 4090 correctness/OOM issues, and version churn risks. On a 4090 you get Triton/FA by default — not FlashInfer.

**vLLM fit arithmetic:**
```
total_memory ≈ model_weights + KV_pool (dynamic) + compute_buffers + batching_overhead
KV_pool = num_kv_heads × head_dim × num_layers × context_length × bytes_per_element
```

**Commands:**
```bash
# Serve a model:
vllm serve <model> --max-model-len <N> --kv-cache-dtype fp16
# Tensor parallel across GPUs:
vllm serve <model> --tensor-parallel-size 2 --max-model-len <N>
# Multi-model on one endpoint:
vllm serve <model1> --port 8000
vllm serve <model2> --port 8001
# Load balance with nginx or vLLM Router in front
```

**Key flag mappings from llama.cpp to vLLM:**
| llama.cpp | vLLM | Why |
|---|---|---|
| `--ctx-size` | `max_model_len` | Client context cap must match served window |
| `-fa on` | `enable_prefix_caching` | Prefix caching changes results; must be controlled in A/B |
| `-ctk q8_0` | `kv_cache_dtype` (fp16/fp8/int8/fp8_e4m3) | KV quantization is a real lever |
| `-ub 1024` | `max_num_batched_tokens` | Batching changes the math |
| `--parallel 1` | `--tensor-parallel-size` | Multi-GPU parallelism |
| `--n-cpu-moe` | N/A | vLLM handles MoE routing internally |

**Traps:**
- `--fit`/`-ngl` conflicts don't apply (vLLM doesn't use them)
- KV quantization quality beyond needle recall is unmeasured in vLLM
- Engine defaults differ per version — pin versions
- `--max-model-len` must match client context cap or requests get clipped/400'd
- Multi-endpoint deployment: one model per endpoint (simple) vs multi-model behind one endpoint (requires routing logic)

**Multi-endpoint patterns:**
1. **One model per endpoint:** isolated, easy to tune each independently
2. **Multi-model behind one endpoint:** vLLM serves multiple models on one port; client selects per request
3. **Load balanced endpoints:** nginx or vLLM Router in front of multiple vLLM instances; data parallel for throughput

**Sources:** vLLM docs (docs.vllm.ai); DGX Spark vLLM clustering (NVIDIA build, MindStudio, vLLM blog Jun 2026); vLLM production deployment (Spheron, 2026); multi-model serving (vLLM discussions #239).

---

## Backend comparison: fit arithmetic transfer

What transfers between backends:
- The fit formula: model_file + KV + compute + context + overhead
- The method: read engine's own buffer log, verify with real load
- The quality checks: recall at depth, quality held constant, repeat runs
- The traps: load ≠ runtime fit, Windows spill, version pinning

What does NOT transfer:
- Specific GiB/MiB numbers (memory accounting differs per backend)
- Flag names (CUDA flags ≠ SYCL flags ≠ HIP flags ≠ Metal flags)
- Bandwidth characteristics (VRAM ≠ unified ≠ network)
- TPS figures (measured on one architecture only)
