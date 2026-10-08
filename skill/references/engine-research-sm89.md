# CUDA engine coverage for sm_89 (RTX 4090)

Synthesized from the research dossier collection at `../research/` (12 dossiers, 2026-10-06 through 2026-10-08). Every entry below is sourced from public repos, docs, release notes, model cards, arXiv papers, and community single-card recipes — no installs, no weight downloads, no GPU jobs.

**Relationship to llm-tune's measured data:** llm-tune's measured numbers come from one RTX 4090-class card (24,564 MiB) running llama.cpp b11115 / llama-swap v257, plus Strata and NInfer engine measurements. The data here covers what those engines and their alternatives look like on sm_89 specifically. It is documentation, not measurement — verify on your own box before quoting numbers.

**Why this matters:** sm_89 (Ada Lovelace, AD102, 128 SMs, 24 GB GDDR6X, 1,008 GB/s) is the single most popular consumer compute capability for local LLMs. Every major CUDA inference provider has a different story for sm_89: some run fully, some run partially (Blackwell-only fast paths), some are arch-specific. This file maps those stories.

---

## The sm_89 landscape (summary)

| Engine | sm_89 status | Fast paths available? | Key limitation |
|---|---|---|---|
| llama.cpp (b11115, measured) | Full | CUDA backend fully supported | — |
| Strata (measured) | Full | Expert-cache, int8 KV, KV streaming | — |
| NInfer (measured) | Full | Groupwise-int, state pools | — |
| NInfer 4090 (community) | Native sm_89 target | All | Windows-only headline features (D3D12, DirectStorage) |
| vLLM 0.31.0 | Nominal (CC 7.5+) | Partial | Fast GDN path is Blackwell-only; open 4090 correctness/OOM issues |
| SGLang 0.5.21 | Nominal | Partial | CUDA 13 required (v0.5.20+); verified Qwen hybrid recipes are datacenter/Blackwell |
| TensorRT-LLM 1.3.0 | Full (Ada in support matrix) | Full FP8/INT8/INT4 on Ada | Newest fast kernels are Blackwell; FP8 on Ada is a real path |
| FlashInfer 0.7.0 | Partial | Attention via FA2 yes | GDN/Gated-DeltaNet, fast FMHA/FP4/FP8-MoE, XQA decode are Hopper/Blackwell-only |
| TokenSpeed 0.1.1 | Unverified | No CI on Ada/RTX | No CI on consumer GPUs; only H100/H200 Hopper path and nightly AMD |
| KTransformers 0.7.1 | Partial | CPU expert kernels on any GPU | All Qwen support is MoE; no dense-model offload path |

---

## vLLM on sm_89 (sourced from `../research/vllm.md`)

**Nominally supported** (compute capability 7.5+, docs list T4, RTX20xx, A100, L4, H100, B200). But the fast paths are Blackwell-only:

- **GDN (Gated-DeltaNet) prefill:** vLLM auto-selects FlashInfer GDN path on Blackwell ("On supported Blackwell configurations, vLLM automatically selects the FlashInfer path when the GDN backend is set to `auto`"). **On a 4090, vLLM runs GDN through the baseline Triton/Flash-Linear-Attention path only.** FlashInfer Blackwell GDN prefill is PR #3001; vLLM PR #40717.
- **Fast kernel zoo:** FlashMLA, TRTLLM-GEN, CuteDSL BF16 GDN prefill, fused GDN MTP decode — all Blackwell (#55715, #53835, #53864).
- **cuDNN support:** cuDNN FMHA on sm_89 is available but competes with FlashInfer for the same memory.
- **Open 4090 issues:** Search vLLM issues for "sm_89" or "4090" — there are user-reported correctness and OOM issues specific to the 4090 that do not appear on A100/H100. The 4090 has fewer register files per SM than A100/H100, which affects kernel occupancy for some attention variants.
- **Version churn:** v0.30.0 (2026-09-22) → v0.31.0 (2026-10-05) in 13 days, 717 commits. Pin versions.

**Implication for llm-tune:** vLLM tuning advice for sm_89 must control for which attention backend is actually in use. `enable_prefix_caching` and `kv_cache_dtype` behave differently on Triton/FA vs FlashInfer vs cuDNN paths. On a 4090 you get Triton/FA by default — that is the measured path, not FlashInfer.

---

## TensorRT-LLM on sm_89 (sourced from `../research/tensorrt-llm.md`)

**Full Ada Lovelace support** (support matrix, docs 1.1.0rc5): "Ada Lovelace (SM89) — FP32, FP16, BF16, FP8, INT8, INT4." This is the most complete precision stack of any engine for sm_89.

- **Ada-specific release features:** FP8 FMHA on Ada (0.9.0), W4A8 on Ada (0.16), FP8/NVFP4 post-training quantization via ModelOpt.
- **ModelOpt:** companion library for FP8/NVFP4/INT8 SmoothQuant/INT4 AWQ/SVDQuant quantization. Apache 2.0.
- **PyTorch backend only:** since 1.0 line, TensorRT engine backend was removed (1.2 release). PyTorch is the sole execution backend.
- **Version:** v1.3.0rc29 (2026-09-24); main carries 1.4.0rc0. Docs default to 1.3.0rc29; some pages lag at 1.1.0rc5.
- **Windows:** supported (unlike many CUDA engines).

**Implication for llm-tune:** TensorRT-LLM is a serious FP8/INT4 option on sm_89. If a user is running 4090 + TensorRT-LLM, the fit arithmetic is the same (model + KV + compute) but the precision stack is richer than llama.cpp offers. The 4090's 24 GB with FP8 KV cache is a viable 70B-class setup via TRT-LLM.

---

## FlashInfer on sm_89 (sourced from `../research/flashinfer.md`)

**Attention path: yes on sm_89 via FlashAttention-2 (fa2).** Everything else is Hopper/Blackwell:

- **NOT on sm_89:** every GDN/Gated-DeltaNet kernel, fast FMHA, FP4/FP8-MoE backends, XQA decode, `cake_*`/`primTS`/`cutedsl` Blackwell backends.
- **GPU support matrix (README):** Turing SM7.5, Ampere SM8.0/8.6, **Ada SM8.9 (L4, L40, RTX 40 series)**, Hopper SM9.0, Blackwell SM10.0/10.3/11.0/12.0/12.1.
- **"Not all features are supported across all compute capabilities."**
- **Install:** `pip install flashinfer-python` (+ `install-cubin-wheel` for prebuilt arch-specific kernels).
- **Version:** v0.7.0 (2026-09-22), 615 commits. v0.6.18 → v0.7.0 in ~1 month. Breaking API changes each release.
- **Adoption list:** SGLang, vLLM, TensorRT-LLM, TGI, MLC-LLM, LightLLM, lorax, ScaleLLM.

**Implication for llm-tune:** FlashInfer is a library, not an engine. It is consumed by vLLM, SGLang, TensorRT-LLM. On sm_89, only the attention (fa2) path runs; anything that needs GDN falls back to Triton/FA. This explains why vLLM on a 4090 runs GDN through Triton — FlashInfer's GDN kernels are Blackwell-only.

---

## SGLang on sm_89 (sourced from `../research/sglang.md`)

**Nominally supports sm_89, but verified Qwen hybrid recipes are datacenter/Blackwell:**

- **CUDA 13 required:** v0.5.20+ requires CUDA 13 (PyTorch 2.14). v0.5.19 is the last with CUDA 12 lane.
- **Spec decode:** EAGLE/EAGLE3/MTP/UNO/DFlash/DSpark/NGRAM. SGLang ships DFlash2 as `--spec dflash2` (see natpate/ninfer-windows for consumer availability).
- **RadixAttention:** radix tree over token prefixes for cross-request KV reuse. SGLang paper claims up to 6.4x throughput on agentic workloads.
- **Unified Radix Cache:** extends radix tree to hybrid models (FULL KV + SWA windows + MAMBA/GDN state checkpoints on one tree).
- **Version:** v0.5.21 (2026-10-02), biweekly cadence.
- **Versioning:** `transformers_version: 5.8.0.dev0` for Qwen3.8 models — transformers 5.x era compatibility signal.

**Implication for llm-tune:** SGLang on sm_89 is viable but the spec decode ecosystem (DFlash2, EAGLE3, etc.) is primarily documented on datacenter GPUs. Users running 4090 + SGLang need to verify which spec decode methods work on consumer hardware before quoting t/s numbers.

---

## NInfer 4090 community port (sourced from `../research/ninfer-4090-udpsendtofailed.md`)

**This is directly relevant to llm-tune's NInfer measurements.** A community fork specifically targeting sm_89 on RTX 4090:

- **What it is:** from-scratch C++20/CUDA inference engine specialized to one RTX 4090 (`sm_89`, AD102, 128 SMs) running Qwen3.8-27B. Sibling port of `Don-Chad/ninfer-3090` (itself a fork of `Neroued/ninfer`), re-targeted from `sm_86` to native `sm_89`.
- **License:** Apache 2.0 — porting code is license-free.
- **Version:** v1.2.0-rtx4090 (2026-09-09, latest). No release in 4.5 weeks at research time.
- **Blackwell cleanup:** v1.2.0 release notes: "specializes the runtime and operator pipelines for the RTX 4090 (sm_89, AD102)" and **deleted 45+ Blackwell SM120/NVFP4 kernel files** to keep the codebase strictly Ada.
- **Caveat:** headline capacity features (D3D12/WDDM residency eviction, DirectStorage 1.3 disk state cache) are **Windows-only** (if(WIN32) CMake blocks). Linux/Docker build is an open issue.
- **176 stars, 24 forks, 6 open issues** (2026-10-07).

**Implication for llm-tune:** This is community NInfer specifically built for the 4090. It validates that NInfer can run natively on sm_89 — our measurements used llama-swap which may use a different build. If a user is running the 4090 community NInfer port, their numbers may differ from ours due to different compiler flags, kernel selection, and sm_89-specific optimizations.

---

## NInfer Windows port (sourced from `../research/ninfer-windows-natpate.md`)

**Windows 11 x64 port of NInfer (upstream lineage), re-targeted to RTX 5090 (sm_120a, 32 GB):**

- **Spec decode:** v0.7.0 added DFlash2 speculative backend (`--spec dflash2 --draft-tokens 1-15 --lm-head-draft`) — "measured up to ~42% faster decode than MTP on cache-heavy workloads at 131k context (small fixed-budget comparison, not a quality evaluation)."
- **Version:** v0.9.1 (2026-09-29, latest). Nine weeks of active history.
- **Portable:** each release is a portable win64 zip, CUDA 13.1 runtime baseline, built on 13.3 toolchain.
- **v3 artifact format:** model/weight decoupling (v0.8.0).

**Implication for llm-tune:** The DFlash2 vs MTP comparison data (42% faster decode) is a user-reported, unverified measurement — it does not meet our quality bar for inclusion in `references/speculative-mtp.md`. Flag it as "community report, unverified" if referenced. But it demonstrates that parallel-draft speculative decoding (DFlash2) is a real alternative to MTP on consumer hardware.

---

## Speculative decoding alternatives to MTP (sourced from `../research/eagle3-medusa-specforge.md` and `../research/dflash-pard.md`)

llm-tune currently covers MTP (draft-multiple tokens per predict). The research collection reveals a richer speculative decoding landscape on sm_89:

### Draft-model drafters (train a separate small model to draft)

| Method | Draft style | Backers | sm_89 status |
|---|---|---|---|
| **EAGLE-3** | Feature-level draft, autoregressive | Peking U + MS Research + U Waterloo | Community spec via SpecForge; not first-party Qwen3 (EAGLE repo todo: "[ ] Support official EAGLE-3 for Qwen-3") |
| **Medusa** | Parallel decode heads, one-step | Princeton / Together AI / UIUC / CMU | Dormant since 2024-06; superseded by EAGLE-3/DFlash |
| **SpecForge** | Training framework for EAGLE3/DFlash/Domino/DSpark | LMSYS / SGLang team | Active; produces community checkpoints (SpecBundle HF collection) |

### Parallel-draft methods (predict a block of tokens in one forward pass)

| Method | Key insight | Backers | sm_89 status |
|---|---|---|---|
| **DFlash** | Block-diffusion drafter, KV-injection conditioning, per-layer injection. 5L/16-token draft is cheaper and better than EAGLE-3's 1L/8-token. | Z Lab / UC San Diego | Shipped in TensorRT-LLM (`decoding_type: PARD`/`DFlash`) |
| **DFlash 2** | + path selector + two-tap dynamic convolution. "20% more output per verify pass, ~1% latency." | Inco AI | Available via SGLang `--spec dflash2` |
| **PARD** | Target-independent parallel draft (adapt any small AR drafter). One drafter per family. | AMD | ICLR 2026; shipped in TensorRT-LLM |

**Implication for llm-tune:** Step 6 (Speculative/MTP) should note that MTP is one option among many on sm_89. DFlash2 is the most consumer-accessible parallel-draft method (via SGLang `--spec dflash2`). The "MTP only changes speed" finding (finding 2) applies to MTP specifically — DFlash2's block-diffusion approach changes both speed AND verification efficiency (per the natpate community report, 42% faster). This is community-reported, not measured in this repo, and should be flagged as such.

---

## TokenSpeed on sm_89 (sourced from `../research/tokenspeed.md`)

**A newer engine with MIT license and day-0 Qwen3.8/GLM 5.3 flash support — but no CI on consumer GPUs:**

- **What it is:** Python-based inference engine for agentic workloads: "TensorRT-LLM-level performance and vLLM-level usability." C++ scheduler + Python execution plane + pluggable kernel registry (Triton/Gluon/CuteDSL JIT or vendor wrappers for FlashInfer/FlashAttention/TRT-LLM).
- **License:** MIT — the one engine with both an official Qwen3.8 recipe and an unencumbered portable GDN kernel stack.
- **Day-0s shipped:** TML Inkling (2026-07), Kimi K3 (2026-07), Qwen3.8 2.4T (2026-08), Qwen3.8 Flash Next + GLM 5.3 Flash (2026-08).
- **sm_89 status:** **No CI on Ada / RTX consumer GPUs.** Only Hopper/CUDA 12.9 source-install recipe for H100/H200. Nightly AMD ROCm stream in parallel.
- **Backing:** LightSeek Foundation (501(c)(3) nonprofit), with NVIDIA DevTech, AMD Triton, Qwen Inference, Together AI, Mooncake, LongCat, FluentLLM compute support.
- **Version:** v0.1.0 (2026-07-24); v0.1.1 (2026-10-06, latest). ~2,200 stars.

**Implication for llm-tune:** TokenSpeed is architecturally interesting (separate control/execution planes, MIT license, portable GDN) but currently unverified on sm_89 consumer hardware. Do not cite t/s figures. Track its CI for Ada consumer GPU support as a future data source.

---

## KTransformers on sm_89 (sourced from `../research/ktransformers.md`)

**CPU-GPU heterogeneous MoE framework — all Qwen support is MoE, no dense offload path:**

- **Core idea:** attention + shared experts + dense layers on GPU; routed MoE experts persist in CPU DRAM, computed on CPU (no PCIe transfer). SOSP'25 paper.
- **Upstreamed:** CPU kernels upstreamed into SGLang since Oct 2025 (sglang#11425).
- **Qwen coverage (status page):** Qwen3-Coder-Next (Needs smoke), Qwen3.5 (Needs mainline cleanup), Qwen3-30B-A3B (Needs method-specific smoke). **All MoE or MoE-hybrid. No dense-model offload path.**
- **Version:** v0.7.1 (2026-09-15).
- **SFT:** KTransformers × LLaMA-Factory for MoE fine-tuning on consumer hardware. BF16 LoRA on Qwen3-VL-30B, native RAWINT4 Kimi K2.5/K2.6.

**Implication for llm-tune:** KTransformers is relevant only for MoE models on sm_89. Its CPU-expert architecture is a different approach to memory management than what llm-tune measures (GPU VRAM + host RAM). The "no dense offload path" note is important — users running dense 27B models should not use KTransformers expecting it to solve their fit problem.

---

## Qwen3.8-Flash-Next architecture (sourced from `../research/qwen38-flash-next.md`)

**The model Qwen calls "early preview of the architecture used in Qwen4":**

- **Architecture:** multimodal MoE: 125B main model, 6B activated/token, plus 51B n-gram embedding (PLE) and 4B MTP.
- **Fits on sm_89?** **No public single-4090 run exists.** The model does not fit in 24 GB at any published precision (172.78 GiB FP8 per vLLM recipe; 93.7 GB unsloth UD-IQ4_XS GGUF; ~60 GB resident in 4×3090 run). Every consumer run uses multiple cards or 128+ GB unified memory.
- **Engine support:** llama.cpp PR #27742, SGLang PRs #36497/#36585/#37500 + cookbook, KTransformers issue #2179, vLLM recipe. Community runs: tonyd2wild (4×3090), antirez ds4.
- **License:** `qwen-community-1.0` (custom, conditional use) — read before product use. Code (engine PRs) is Apache 2.0.

**Implication for llm-tune:** This model is the architecture future for Qwen coding models but doesn't fit on sm_89 at any published precision. Users on 24 GB cards should use Qwen3.8-27B or Qwen3.5-35B-A3B instead. The 480B-A35B variant fits on 256+ GB Mac Studio (see hardware-tiers.md Tier 7).

---

## Sources and cross-references

All data in this file is synthesized from the research dossier collection:

| Dossier file | Engines/models covered | Used for |
|---|---|---|
| `vllm.md` | vLLM 0.31.0, sm_89 specifics | engine-backends.md, vllm-local.md expansion |
| `tensorrt-llm.md` | TensorRT-LLM 1.3.0, sm_89 support matrix | new engine reference |
| `flashinfer.md` | FlashInfer 0.7.0, sm_89 kernel coverage | engine-backends.md kernel details |
| `sglang.md` | SGLang 0.5.21, sm_89 analysis | new engine reference |
| `tokenspeed.md` | TokenSpeed 0.1.1, sm_89 CI status | engine coverage note |
| `qwen38-flash-next.md` | Qwen3.8-Flash-Next architecture | model management context |
| `qwen-official.md` | Qwen model vendor, architecture timeline | model management context |
| `eagle3-medusa-specforge.md` | EAGLE-3, Medusa, SpecForge drafters | Step 6 speculative alternatives |
| `ktransformers.md` | KTransformers 0.7.1, CPU-GPU MoE | engine comparison note |
| `dflash-pard.md` | DFlash/DFlash2/PARD parallel draft | Step 6 speculative alternatives |
| `ninfer-4090-udpsendtofailed.md` | NInfer native sm_89 community port | engine-backends.md, NInfer context |
| `ninfer-windows-natpate.md` | NInfer Windows port, DFlash2 vs MTP | Windows trapping, speculative data |

---

## Version tracking

| Version | Date | What changed |
|---|---|---|
| 2026-10-08 | Initial | 12 dossier sources synthesized, sm_89 coverage mapped |

---

## How this file relates to the rest of the skill

- **`SKILL.md` Step 9** references this for non-NVIDIA hardware; this file covers non-NVIDIA engines on NVIDIA hardware (vLLM, TRT-LLM, FlashInfer, SGLang on sm_89 specifically)
- **`references/engine-backends.md`** — this file provides the sm_89-specific detail for each engine mentioned there
- **`references/hardware-tiers.md`** — Tier 2 (24 GB RTX 4090) is sm_89; this file tells what engines actually work there
- **`data/INVENTORY.md`** — add new entries for the 12 dossier sources
