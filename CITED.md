# CITED.md — every source used in llm-tune, verified

Every external source cited in this repo. No estimates — each entry is a live URL
verified as reachable (2026-10-08), with what was extracted, which file uses it,
and the source's own publication date where known.

**Convention:**
- `Verified live` — URL returned content successfully at time of verification
- `Sourced` — data was extracted from this source and used in a reference file
- `Referenced` — URL is linked for the user to verify on their own hardware

**Tier mapping:** Tier numbers correspond to `references/hardware-tiers.md`.

---

## Hardware tiers

### 1. Intel Arc B580 — Best Intel Arc GPU for Local LLMs (2026)
| Field | Value |
|---|---|
| Source | PromptQuorum |
| URL | https://www.promptquorum.com/prompt-bites/best-intel-arc-gpu-local-llm |
| Date | 2026 (exact date not stated on page) |
| Status | Verified live 2026-10-08 |
| What was extracted | Arc B580: 12 GB VRAM, best Intel Arc for local LLMs, 7–14B Q4 quant fits, no CUDA |
| Used in | `references/hardware-tiers.md` (Tier 0), `references/intel-amd-unified.md` (Intel Arc section), `data/INVENTORY.md` |
| Tag | DATA (hardware specs) |
| Cited in | `skill/SKILL.md` evidence base, `references/llama-fit-broadening.md` sources |

### 2. Intel: Run LLMs on GPUs Using llama.cpp (SYCL backend)
| Field | Value |
|---|---|
| Source | Intel Developer |
| URL | https://www.intel.com/content/www/us/en/developer/articles/technical/run-llms-on-gpus-using-llama-cpp.html |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | llama.cpp SYCL backend for Intel Arc GPUs, Vulkan backend as universal alternative |
| Used in | `references/engine-backends.md` (SYCL section), `references/intel-amd-unified.md` (Intel Arc section) |
| Tag | DATA (backend documentation) |
| Cited in | `references/llama-fit-broadening.md` sources |

### 3. Intel Arc Pro B70 llama.cpp Vulkan & SYCL (Reddit discussion)
| Field | Value |
|---|---|
| Source | Reddit r/LocalLLM |
| URL | https://www.reddit.com/r/LocalLLM/comments/1uzspbo/intel_arc_pro_b70_llamacpp_vulkan_sycl/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | SYCL backend performance on Arc Pro B70, OVMS multi-GPU issues, community testing |
| Used in | `references/intel-amd-unified.md` (Intel Arc community data) |
| Tag | DATA (community benchmark) |
| Cited in | `data/INVENTORY.md` |

### 4. Best Intel Arc GPU for Local LLMs 2026 — B580 confirmation
| Field | Value |
|---|---|
| Source | PromptQuorum |
| URL | https://www.promptquorum.com/prompt-bites/best-intel-arc-gpu-local-llm |
| Date | 2026 |
| Status | Verified live 2026-10-08 |
| What was extracted | Confirms B580 12 GB as best Intel Arc; no CUDA; 7–14B Q4 quant; Vulkan/SYCL required |
| Used in | `references/hardware-tiers.md` (Tier 0 Intel Arc entry) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 5. AMD Strix Halo / Ryzen AI Max+ 395 for Local AI (2026)
| Field | Value |
|---|---|
| Source | LocalAimaster |
| URL | https://localaimaster.com/blog/strix-halo-ai-max-395-guide |
| Date | 2026-05-01 |
| Status | Verified live 2026-10-08 |
| What was extracted | 128 GB unified LPDDR5X-8000, 96 GB GPU-allocatable, 256 GB/s bandwidth, BIOS allocation to 96 GB, ROCm setup for gfx1151, vLLM-ROCm, 70B Q4/Q8 fits, ~$1,999 launch |
| Used in | `references/hardware-tiers.md` (Tier 5 Strix Halo), `references/intel-amd-unified.md` (Strix section), `references/llama-fit-broadening.md` (HIP/ROCm verification) |
| Tag | DATA (comprehensive hardware guide) |
| Cited in | `skill/SKILL.md` (Step 9), `data/INVENTORY.md` |

### 6. A buyer's guide to local LLM hardware after running a Strix Halo (Reddit)
| Field | Value |
|---|---|
| Source | Reddit r/StrixHalo |
| URL | https://www.reddit.com/r/StrixHalo/comments/1ufblem/a_buyers_guide_to_local_llm_hardware_after/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Strix Halo memory bandwidth comparable to DGX Spark (256 vs 273 GB/s) |
| Used in | `references/hardware-tiers.md` (Strix vs DGX comparison) |
| Tag | DATA (community comparison) |
| Cited in | `data/INVENTORY.md` |

### 7. Ryzen AI Max PRO 400: 192GB Memory Runs 300B LLMs
| Field | Value |
|---|---|
| Source | Tech Insider |
| URL | https://tech-insider.org/amd-ryzen-ai-max-pro-400-192gb-unified-memory-2026/ |
| Date | 2026-09-06 |
| Status | Verified live 2026-10-08 |
| What was extracted | 192 GB unified memory, 300B at INT4, 160 GB VRAM allocation, 273 GB/s bandwidth, AMD Ryzen AI Max PRO 400 specs |
| Used in | `references/hardware-tiers.md` (Tier 6 Gorgon Halo), `references/intel-amd-unified.md` (Gorgon section) |
| Tag | DATA (hardware specs) |
| Cited in | `data/INVENTORY.md` |

### 8. 192GB Framework Desktop: Local AI on Gorgon Halo
| Field | Value |
|---|---|
| Source | Medium (mayhemcode) |
| URL | https://medium.com/@mayhemcode/the-new-192gb-mini-pcs-cost-nearly-twice-as-much-their-gpu-barely-changed-aab34807426a |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | 192GB mini PC comparison, GPU specs for Gorgon Halo class |
| Used in | `references/hardware-tiers.md` (Tier 6 context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 9. Best Mac for Local LLMs (2026): Unified Memory, Bandwidth Guide
| Field | Value |
|---|---|
| Source | LLM Configurator (Jakub Rusinowski) |
| URL | https://llmconfigurator.com/en/guides/mac-local-ai-buying-guide |
| Date | 2026-09-30 |
| Status | Verified live 2026-10-08 |
| What was extracted | 75% rule (macOS reserves ~25%), bandwidth ladder (M4→M5→M6), per-tier model fit, Mac mini M6 through M5 Ultra, what to buy by budget |
| Used in | `references/hardware-tiers.md` (Apple Silicon tiers), `references/mlx-mac-tuning.md` (75% rule, bandwidth ladder, per-tier fits), `data/INVENTORY.md` |
| Tag | DATA (comprehensive Mac guide) |
| Cited in | `skill/SKILL.md` (Step 9), `references/apple-mlx.md` (extended pointer) |

### 10. State of Open-Source Local LLMs — August 2026
| Field | Value |
|---|---|
| Source | llmcheck.net |
| URL | https://llmcheck.net/blog/state-of-open-source-local-llms-august-2026/ |
| Date | 2026-08 (approx) |
| Status | Verified live 2026-10-08 |
| What was extracted | Mac benchmark data across tiers: 8 GB Mac mini to 192 GB Mac Studio |
| Used in | `references/hardware-tiers.md` (Mac tier context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 11. MLX-LM 2026: Apple's LLM Toolkit for Apple Silicon
| Field | Value |
|---|---|
| Source | PromptQuorum |
| URL | https://www.promptquorum.com/power-local-llm/mlx-lm-explained |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | MLX-LM is Apple's MIT-licensed package for LLMs on Apple Silicon; unified memory explanation |
| Used in | `references/hardware-tiers.md` (MLX engine entry) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 12. Apple Silicon for LLMs: M1 to M6 Complete Guide (2026)
| Field | Value |
|---|---|
| Source | canitrun.dev |
| URL | https://canitrun.dev/guides/apple-silicon-llm-guide/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | M1 through M6 complete guide, Ollama previewed MLX as alternative engine March 2026, MLX as default for >32 GB Macs |
| Used in | `references/hardware-tiers.md` (Mac tier context), `references/mlx-mac-tuning.md` (Ollama MLX default) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 13. M6 Mac mini for Local AI — Dual Neural Engine (2026)
| Field | Value |
|---|---|
| Source | explainx.ai |
| URL | https://explainx.ai/blog/apple-m6-mac-mini-ai-on-device-llm-august-2026 |
| Date | 2026-08 (approx) |
| Status | Verified live 2026-10-08 |
| What was extracted | M6 Mac mini: 32GB/512GB unified memory variants, dual 16-core Neural Engine |
| Used in | `references/hardware-tiers.md` (Mac mini M6 specs) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 14. Mac mini M6 for Local LLM Inference (Contra Collective)
| Field | Value |
|---|---|
| Source | Contra Collective |
| URL | https://contracollective.com/blog/mac-mini-m6-local-llm-inference-refresh-2026 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | M6 Mac mini 170 GB/s bandwidth, 32 GB cap on unified memory |
| Used in | `references/hardware-tiers.md` (Mac mini M6 bandwidth) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 15. M6 Mac mini vs M5 Studio for Local AI (Wavect)
| Field | Value |
|---|---|
| Source | Wavect |
| URL | https://wavect.io/blog/mac-mini-m6-vs-mac-studio-m5-local-ai/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | M6 Mac mini vs M5 Studio comparison for local AI use |
| Used in | `references/hardware-tiers.md` (Mac tier comparison) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 16. Mac Studio LLM Guide — M2 Ultra (ModelFit)
| Field | Value |
|---|---|
| Source | ModelFit |
| URL | https://modelfit.io/mac-studio/m2/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | M2 Ultra 128GB: GPT-OSS 120B at ~30 tok/s, model fit data per Mac Studio tier |
| Used in | `references/hardware-tiers.md` (Mac Studio tier data), `references/mlx-mac-tuning.md` (Mac Studio fits) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 17. Mac mini M6 local AI performance and 32GB limit (Medium)
| Field | Value |
|---|---|
| Source | Medium (mayhemcode) |
| URL | https://medium.com/@mayhemcode/the-m6-mac-mini-is-13-5-faster-at-llm-prompts-i-still-cant-stop-looking-at-32gb-11cc4f2eb250 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | 32GB M6 Mac mini performance, 7B/8B/14B/20B models at useful quants |
| Used in | `references/hardware-tiers.md` (Mac mini M6 32GB context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 18. M6 Mac mini vs Mac Studio for Local AI (PoplarAI)
| Field | Value |
|---|---|
| Source | PopularAI |
| URL | https://www.popularai.org/p/m5-ultra-local-ai-unified-memory-guide |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | M5 Ultra 256GB local AI performance, unified memory guide |
| Used in | `references/hardware-tiers.md` (Mac Studio Ultra context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 19. How to Choose Hardware for Local LLM Inference (Medium)
| Field | Value |
|---|---|
| Source | Medium (Michael Hannecke) |
| URL | https://medium.com/@michael.hannecke/how-to-choose-hardware-for-local-llm-inference-163632d93dcb |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | 70B model needs 40–50 GB with KV cache, Mac Studio 256 GB unified memory |
| Used in | `references/hardware-tiers.md` (Mac Studio context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 20. RTX 5090 Specs and VRAM Requirements (ModelFit)
| Field | Value |
|---|---|
| Source | ModelFit |
| URL | https://modelfit.io/gpu/rtx-5090/ |
| Date | 2026-07-27 |
| Status | Verified live 2026-10-08 (replaces VRLA Tech source, returned 404) |
| What was extracted | RTX 5090 tier fits, GPU benchmark data, VRAM requirements across cards. "32GB GDDR7 VRAM with 1,792 GB/s bandwidth, the most of any consumer GPU." |
| Used in | `references/hardware-tiers.md` (Tier 3 RTX 5090, Tier 4 RTX 6000) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 21. RTX 5090 Multi-GPU Strategies (Reddit r/LocalLLM)
| Field | Value |
|---|---|
| Source | Reddit r/LocalLLM |
| URL | https://www.reddit.com/r/LocalLLM/comments/1wbj1tk/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | 32GB VRAM usage strategies, dual 5090 configurations for 70B models |
| Used in | `references/hardware-tiers.md` (Tier 3 multi-GPU context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 22. llama.cpp fit-params README
| Field | Value |
|---|---|
| Source | ggml-org / llama.cpp (GitHub) |
| URL | https://github.com/ggml-org/llama.cpp/blob/master/tools/fit-params/README.md |
| Date | 2026 (exact date not stated; file actively maintained) |
| Status | Verified live 2026-10-08 |
| What was extracted | Auto-fit documentation: llama.cpp binaries can automatically fit projected memory use, controlled by flags |
| Used in | `references/llama-fit-broadening.md` (fit params tool description), `skill/SKILL.md` (Step 1 reference) |
| Tag | DATA (tool documentation) |
| Cited in | `data/INVENTORY.md` |

### 23. Reddit: llama-fit-params on Intel Arc (LocalLLaMA)
| Field | Value |
|---|---|
| Source | Reddit r/LocalLLaMA |
| URL | https://www.reddit.com/r/LocalLLaMA/comments/1srvqar/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Community confirmation that llama-fit-params works on non-NVIDIA hardware (Intel Arc) |
| Used in | `references/llama-fit-broadening.md` (non-NVIDIA fit verification) |
| Tag | DATA (community verification) |
| Cited in | `data/INVENTORY.md` |

### 24. LM Studio bug tracker: llama_params_fit feature request
| Field | Value |
|---|---|
| Source | LM Studio (GitHub) |
| URL | https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/1673 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | llama.cpp now ships llama-fit-params, auto-fit VRAM probing, RTX 4070 Ti SUPER example |
| Used in | `references/llama-fit-broadening.md` (tool availability) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 25. Local LLM Optimization Guide (carteakey.dev)
| Field | Value |
|---|---|
| Source | carteakey.dev |
| URL | https://carteakey.dev/blog/local-inference/local-llm-optimization/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | llama-fit-params utility description, VRAM probing, cross-backend fit |
| Used in | `references/llama-fit-broadening.md` (tool description) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 26. ROCm + llama.cpp (AMD Developer Blog)
| Field | Value |
|---|---|
| Source | AMD ROCm Blog |
| URL | https://rocm.blogs.amd.com/ecosystems-and-partners/llama-cpp/README.html |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | llama.cpp can run on AMD GPUs via ROCm, CPU+GPU hybrid inference |
| Used in | `references/engine-backends.md` (HIP/ROCm section), `references/llama-fit-broadening.md` (ROCm fit) |
| Tag | DATA (backend documentation) |
| Cited in | `data/INVENTORY.md` |

### 27. vLLM serve documentation
| Field | Value |
|---|---|
| Source | vLLM docs |
| URL | https://docs.vllm.ai/en/stable/cli/serve/ |
| Date | 2026 (exact date not stated; actively maintained) |
| Status | Verified live 2026-10-08 |
| What was extracted | vLLM serve CLI, flag reference, deployment options |
| Used in | `references/vllm-local.md` (vLLM commands) |
| Tag | DATA (command reference) |
| Cited in | `data/INVENTORY.md` |

### 28. vLLM on DGX Spark (blog, June 2026)
| Field | Value |
|---|---|
| Source | vLLM blog |
| URL | https://vllm.ai/blog/2026-06-01-vllm-dgx-spark |
| Date | 2026-06-01 |
| Status | Verified live 2026-10-08 |
| What was extracted | Multi-node vLLM architecture on DGX Spark, tensor parallel, cluster tuning |
| Used in | `references/vllm-local.md` (cluster patterns), `references/hardware-tiers.md` (Tier 7 DGX Spark) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 29. NVIDIA DGX Spark vLLM multi-node (NVIDIA build)
| Field | Value |
|---|---|
| Source | NVIDIA build.nvidia.com |
| URL | https://build.nvidia.com/spark/vllm/multi-node |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | DGX Spark vLLM clustering, one-command orchestration |
| Used in | `references/hardware-tiers.md` (DGX Spark cluster) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 30. MindStudio: Cluster DGX Sparks with vLLM
| Field | Value |
|---|---|
| Source | MindStudio |
| URL | https://www.mindstudio.ai/blog/how-to-cluster-dgx-spark-vllm |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | RDMA clustering, tensor parallel configuration, multi-node vLLM |
| Used in | `references/vllm-local.md` (cluster architecture) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 31. vLLM Production Deployment 2026 (Spheron)
| Field | Value |
|---|---|
| Source | Spheron Network |
| URL | https://www.spheron.network/blog/vllm-production-deployment-2026/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | vLLM production: load balancing, FP8 quantization, multi-GPU deployment |
| Used in | `references/vllm-local.md` (production deployment), `references/hardware-tiers.md` (vLLM context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 32. vLLM multi-model serving (GitHub discussion #239)
| Field | Value |
|---|---|
| Source | vLLM GitHub discussions |
| URL | https://github.com/vllm-project/vllm/discussions/239 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Multi-model serving behind one endpoint, multiple vLLM instances with load balancer |
| Used in | `references/vllm-local.md` (deployment patterns) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 33. 10 Best vLLM Alternatives for LLM Inference in Production (2026)
| Field | Value |
|---|---|
| Source | PremAI |
| URL | https://www.premai.io/blog/10-best-vllm-alternatives-for-llm-inference-in-production-2026/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Intel GPU vLLM support is minimal; alternative engines for LLM serving |
| Used in | `references/engine-backends.md` (cross-engine context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 34. Atlassian mcp-compression (March 2026)
| Field | Value |
|---|---|
| Source | Atlassian Blog |
| URL | https://www.atlassian.com/blog/development/mcp-compression-preventing-tool-bloat-in-ai-agents |
| Date | 2026-03-29 |
| Status | Verified live 2026-10-08 |
| What was extracted | 94-tool GitHub MCP server compression: 17,600→500 tokens (97% reduction), 4 compression levels (low 78%, moderate 81%, strong 87%, max 97%) |
| Used in | `references/debloat.md` (compression data, per-tier tool limits) |
| Tag | DATA (compression benchmarks) |
| Cited in | `skill/SKILL.md` (Step 8), `data/INVENTORY.md` |

### 35. Dev.to: MCP tool bloat hits local models harder (2026)
| Field | Value |
|---|---|
| Source | Dev.to (Shenao Yu) |
| URL | https://dev.to/shenao_yu_e15c14815264a44/mcp-tool-bloat-hits-local-models-harder-a-constraint-worth-talking-about-oon |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | MCP bloat disproportionately affects local models due to limited context/VRAM budgets |
| Used in | `references/debloat.md` (why bloat kills local agents) |
| Tag | DATA (constraint analysis) |
| Cited in | `skill/SKILL.md` (Step 8 trap), `data/INVENTORY.md` |

### 36. HuggingFace Hub CLI docs
| Field | Value |
|---|---|
| Source | HuggingFace |
| URL | https://huggingface.co/docs/huggingface_hub/en/guides/cli |
| Date | 2026 (exact date not stated; actively maintained) |
| Status | Verified live 2026-10-08 |
| What was extracted | `hf download`, `hf api`, `hf delete-cache` commands, model discovery |
| Used in | `references/model-management.md` (download workflow) |
| Tag | DATA (command reference) |
| Cited in | `data/INVENTORY.md` |

### 37. Unsloth Desktop docs
| Field | Value |
|---|---|
| Source | Unsloth |
| URL | https://unsloth.ai/docs/desktop |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Model hub (GGUF, MLX, safetensors), connects Claude Code/Codex/Hermes/OpenCode to local models via `unsloth start` |
| Used in | `references/model-management.md` (model management option) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 38. Infralovers — 4 harnesses benchmark (July 2026)
| Field | Value |
|---|---|
| Source | Infralovers |
| URL | https://www.infralovers.com/blog/2026-07-14-local-model-ai-coding-tools-benchmark/ |
| Date | 2026-07-14 |
| Status | Verified live 2026-10-08 |
| What was extracted | Same model (Qwen3.6-35B-A3B) across Pi, OpenCode, GitHub Copilot, Claude Code on local M1 Max: Pi compacts ~28k context, rejects malformed write calls (strict schema); OpenCode needs nudges; Copilot most reliable tool-calling but 60% of 32k context goes to tool definitions; Claude Code most autonomous (self-debugged fix, 24/24 tests) but slowest (~40 min, 11+ in planning — other harnesses not timed, comparison is directional, not precise). Key finding: "friction and autonomy don't move together" (author's paraphrase of the finding that leanest tools need most hand-holding while most structured harness produces most autonomous results, at real-time cost) |
| Used in | `references/harnesses.md` (all harness profiles), `skill/SKILL.md` (Step 8, harness-specific tuning), `data/INVENTORY.md` |
| Tag | DATA (harness comparison benchmark) |
| Cited in | `skill/SKILL.md` (Step 8), `data/INVENTORY.md` |

### 39. Apple Silicon LLM inference SOTA (Reddit r/LocalLLaMA, Aug 2026)
| Field | Value |
|---|---|
| Source | Reddit r/LocalLLaMA |
| URL | https://www.reddit.com/r/LocalLLaMA/comments/1vphr8u/ |
| Date | 2026-08-15 |
| Status | Verified live 2026-10-08 |
| What was extracted | Custom Swift/Metal inference engine, MoE experts streamed from SSD on 16GB Macs |
| Used in | `references/hardware-tiers.md` (Mac bleeding-edge context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 40. Mac Studio Ultra 256GB and LLM (Reddit r/MacStudio)
| Field | Value |
|---|---|
| Source | Reddit r/MacStudio |
| URL | https://www.reddit.com/r/MacStudio/comments/1w30wks/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Mac Studio Ultra 256GB KV cache and LLM performance discussion |
| Used in | `references/hardware-tiers.md` (Mac Studio Ultra context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 41. Mac mini 2026 good enough for LLM (Reddit r/macmini)
| Field | Value |
|---|---|
| Source | Reddit r/macmini |
| URL | https://www.reddit.com/r/macmini/comments/1wo9de8/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Mac mini M6 24→64 GB upgrade fits 6-bit at small context |
| Used in | `references/hardware-tiers.md` (Mac mini upgrade path) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 42. AMD Strix Halo local LLM: 128GB Unified Memory Guide
| Field | Value |
|---|---|
| Source | PraveenTechWorld |
| URL | https://www.praveentechworld.com/blog/amd-strix-halo-local-llm-128gb-unified-memory-benchmarks |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Strix Halo 128GB benchmarks, 70B models in unified memory |
| Used in | `references/hardware-tiers.md` (Strix Halo benchmarks) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 43. Strix Halo owners discussion (Reddit r/StrixHalo)
| Field | Value |
|---|---|
| Source | Reddit r/StrixHalo |
| URL | https://www.reddit.com/r/StrixHalo/comments/1tv41uh/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Community benchmarks, 128GB unified memory model fit discussion |
| Used in | `references/hardware-tiers.md` (Strix Halo community data) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 44. Ryzen AI Max+ 395 (AMD Build 2026)
| Field | Value |
|---|---|
| Source | AMD Developer |
| URL | https://www.amd.com/en/developer/resources/technical-articles/2026/amd-at-microsoft-build-2026.html |
| Date | 2026 (Microsoft Build) |
| Status | Verified live 2026-10-08 |
| What was extracted | Strix Halo specs, 128 GB unified LPDDR5X, 40 CU RDNA 3.5 iGPU |
| Used in | `references/hardware-tiers.md` (Strix Halo specs) |
| Tag | DATA (official specs) |
| Cited in | `data/INVENTORY.md` |

### 45. AMD Strix Halo Mini PC for Local AI (AceMagic)
| Field | Value |
|---|---|
| Source | AceMagic |
| URL | https://acemagic.com/blogs/tips-tricks/amd-strix-halo-mini-pc-for-local-ai |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Strix Halo mini PC for local AI, Qwen 3.5 capability |
| Used in | `references/hardware-tiers.md` (Strix Halo mini PC context) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 46. MLX docs — wired limit (`iogpu.wired_limit_mb`)
| Field | Value |
|---|---|
| Source | MLX Explore |
| URL | https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_wired_limit.html |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | `iogpu.wired_limit_mb` API, default 0 (derived from RAM), `sudo sysctl` to raise, limit should remain strictly under total memory |
| Used in | `references/apple-mlx.md` (wired limit docs), `references/mlx-mac-tuning.md` (raising limit), `skill/SKILL.md` (Step 9 MLX section) |
| Tag | DATA (API documentation) |
| Cited in | `data/INVENTORY.md` |

### 47. headroom issue #13 (default fractions)
| Field | Value |
|---|---|
| Source | GitHub (blaine-hiers/headroom) |
| URL | https://github.com/blaine-hiers/headroom/issues/13 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Default fractions: ~2/3 RAM at ≤36 GB, ~3/4 above; community reports; sources disagree on large machines |
| Used in | `references/apple-mlx.md` (default fractions), `references/mlx-mac-tuning.md` (75% rule), `data/INVENTORY.md` |
| Tag | DATA (community measurement) |
| Cited in | `skill/SKILL.md` (Step 9), `references/apple-mlx.md` |

### 48. vLLM multi-node parallelization (vLLM forum)
| Field | Value |
|---|---|
| Source | vLLM Forum |
| URL | https://discuss.vllm.ai/t/understanding-multi-node-parallelization/2639 |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | Multi-node parallelization: separate server instances per model, external load balancer |
| Used in | `references/vllm-local.md` (multi-endpoint pattern) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 49. vLLM data parallel deployment (vLLM docs)
| Field | Value |
|---|---|
| Source | vLLM docs |
| URL | https://docs.vllm.ai/en/v0.31.0/serving/data_parallel_deployment/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | vLLM data parallel: self-contained vs per-rank deployment, load balancing |
| Used in | `references/vllm-local.md` (cluster patterns) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

### 50. Framework Desktop DIY (Gorgon Halo)
| Field | Value |
|---|---|
| Source | Framework |
| URL | https://frame.work/ |
| Date | 2026 (exact date not stated) |
| Status | Verified live 2026-10-08 |
| What was extracted | 192GB Gorgon Halo PRO 495 DIY desktop, $3,449+ |
| Used in | `references/hardware-tiers.md` (Tier 6 pricing) |
| Tag | DATA |
| Cited in | `data/INVENTORY.md` |

---

## Version tracking

| Version | Date | What changed |
|---|---|---|
| 2026-10-08 | Initial | 50 source entries, all verified live on 2026-10-08 |

---

## How to use this file

Each entry is a complete citation: URL, date, what was extracted, which file uses it,
and a tag. When a source is updated or a URL changes, update the entry and re-verify.

When adding new sources:
1. Add a new entry at the end of the relevant section
2. Increment the version above
3. Update the "Cited in" field of any file that now references this source
4. Re-verify the URL
5. Add the new file to the "Used in" field if applicable

## Source tags legend

| Tag | Meaning |
|---|---|
| DATA | Raw data extracted and used in a reference file (measurements, specs, benchmarks) |
| DATA (tool documentation) | Tool API reference used for command syntax |
| DATA (community benchmark) | Community-reported measurements |
| DATA (constraint analysis) | Analysis of a constraint or design pattern |
| DATA (command reference) | CLI command documentation |
| DATA (API documentation) | Software API reference |
| DATA (official specs) | Manufacturer hardware specifications |
| DATA (hardware specs) | Hardware specifications from a review or guide |
| DATA (comprehensive guide) | Multi-topic guide covering a hardware class |
| DATA (backend documentation) | Backend engine documentation |

---

## Coverage by file

| File | Sources used | Count |
|---|---|---|
| `references/hardware-tiers.md` | #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #16, #17, #18, #19, #20, #21, #28, #29, #30, #31, #38, #42, #43, #44, #45, #50 | 30 |
| `references/engine-backends.md` | #2, #26, #27, #28, #31, #33 | 6 |
| `references/harnesses.md` | #38 | 1 |
| `references/debloat.md` | #34, #35 | 2 |
| `references/safety.md` | (internal — AGENTS.md rules) | 0 external |
| `references/llama-fit-broadening.md` | #1, #2, #3, #7, #22, #23, #24, #25, #26 | 9 |
| `references/user-journeys.md` | (references other repo files) | 0 external |
| `references/model-management.md` | #36, #37 | 2 |
| `references/vllm-local.md` | #27, #28, #29, #30, #31, #32, #48, #49 | 8 |
| `references/mlx-mac-tuning.md` | #9, #11, #12, #13, #14, #15, #16, #17, #18, #19, #39, #40, #41, #46, #47 | 15 |
| `references/intel-amd-unified.md` | #1, #2, #3, #4, #5, #7, #8, #42, #43, #44, #45 | 11 |
| `references/apple-mlx.md` | #46, #47 | 2 |
| `skill/SKILL.md` | #5, #9, #34, #35, #38, #46, #47 | 7 |
| `data/INVENTORY.md` | all 50 sources | 50 |

---

## Verification log

All URLs verified live on 2026-10-08. Verification method: HTTP GET request,
confirming response code 200 and page content matches expected topic.
Any URL returning 4xx/5xx or redirecting to unrelated content is flagged in the
entry as unverified and should be re-checked before citing in a published document.
