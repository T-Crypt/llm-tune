# User journeys: 5 entry-state workflows

Different users arrive at different points. Each state has a specific workflow, hardware considerations, and advice about what to do next. The journeys are ordered from "I have nothing" to "I'm pushing the frontier."

The state definitions map to the hardware tiers in `hardware-tiers.md`:
- State A → Tier 0 (8 GB)
- State B → Tier 1 (16 GB)
- State C → Tier 2–3 (24–32 GB)
- State D → Tier 4+ (32 GB+, cluster)
- State E → Any (adding models to existing setup)
- State F → Tier 0 (unified memory, non-NVIDIA)

---

## State A: "I have no models, I'm just getting started"

**Target hardware:** 8–16 GB consumer tier (Tier 0–1)

1. **Install HF CLI:** `pip install huggingface_hub`
2. **Choose your hardware tier** (link to `hardware-tiers.md` master table)
3. **Pick the simplest entry quant for your tier:**
   - 8 GB: 7–8B Q4_K_M (or 3–4B at Q8 if VRAM tight)
   - 12–16 GB: 13–17B Q4_K_M
   - Mac M6 16 GB: Cosmos 3 Nano or Gemma 3 12B
   - Mac M6 32 GB: Qwen3.5/3.6 35B-A3B (fits at Q4)
   - Strix Halo 128 GB: any 7–14B Q4 to start
4. **Install a serving engine:** Ollama (easiest, auto-backend-detection) or llama.cpp (most tunable)
5. **Run the bench:** `bench/quick_bench.md`, memory accounting first, then prefill/decode, then recall, then quality probe
6. **Start with a simple workload:** chat or single-turn task
7. **Graduate to agent workload** once chat works reliably
8. **Add harnesses incrementally:** start with OpenCode (blend local+cloud), move to Pi/OMP/Claude-local when you need local-only
9. **Key advice for this tier:** Debloat your harness NOW, don't wait until agents start failing. See `debloat.md`.

**Trap:** Jumping to agent workloads before chat works reliably leads to misdiagnosis: is the model bad, the harness bad, or is chat itself broken? Start simple.

---

## State B: "I have models and they are here"

**Target hardware:** 16–32 GB tier (Tier 1–2)

1. **Inventory your models** (template in `model-management.md`)
2. **Run the fit check:** For each model, read engine memory log:
   - `KV buffer size`: how much context fits
   - `compute buffer size`: overhead
   - Peak VRAM per run, actual working set
3. **Run recall at depth:** `bench/needle.py` at 10/50/90%, declared context ≠ usable context (finding 7)
4. **Run the quality probe:** `bench/quality_probe.py` with repeats (finding 19)
5. **Identify the binding constraint:**
   - VRAM exhausted → drop context or quant, see `hardware-tiers.md`
   - Recall at depth fails → KV type or context size issue, see `kv-cache.md`
   - Slow decode → architecture-bound (MoE vs dense) or bandwidth-limited
   - Tool calls failing → harness/tolerance issue, see `harnesses.md`
6. **Tune per the 9-step decision procedure** (`SKILL.md`)
7. **Contribute your data** (CONTRIBUTING.md template), your numbers become the next version

**Trap:** Skipping the recall-at-depth check. Declared context size is not usable context (finding 7). A 131k model can return 400 at 120k depth.

---

## State C: "I have 64k+ context but my agents are barely usable"

**Target hardware:** 24–128 GB tier (Tier 2–5)

1. **Diagnose: is it context size, tool-call reliability, or harness bloat?**
   - Does the agent complete a 64k-context task end-to-end? (If no → not a context issue)
   - Does it complete a 32k task with tools? (If no → tool-call or harness issue)
2. **Apply harness debloat:** Strip MCP servers, compress tool schemas (`debloat.md`)
3. **Switch to local-dedicated harness:** Pi, OMP, or Claude-local with reduced tool set
4. **Tune for the harness:** Different settings per harness (`harnesses.md`)
5. **Verify improvement:** Same task set before/after, quality metric held constant
6. **Consider upgrading:** At 24 GB+ you can run larger models with real context; at 128 GB you can run 70B at Q4 with real context

**What this run validates:** the user went from "64k context inside Unsloth, barely usable local agents" to "overnight tasks, walking away from the desk." The bottleneck was never inference speed (Unsloth Desktop confirms: "for local coding agents, the main bottleneck isn't inference speed, it's context window size and tool-calling"). Proper tuning and harness selection fixed it.

**Why the journeys exist:** most users are one tuning decision away from a working setup. The skill makes that decision explicit and measurable.

---

## State D: "I'm advanced, I want to squeeze every bit"

**Target hardware:** 32 GB+ tier, cluster users (Tier 4+)

1. **Engine A/B** (same model, same harness, different engine, r12 methodology from `MODEL-ROLES-2026-09-25.md`)
2. **KV quant A/B** (q4_0 vs int8, recall held, r13 methodology)
3. **Speculative depth sweep** (d2/d3/d4/d5 per workload, 3 runs each, ninfer-sweep1 methodology)
4. **Prefill chunk A/B** (alternating arms, depth-held, strata-ctx methodology)
5. **Engine version A/B** (PR #646 methodology, alternating arms, strata-pr646)
6. **Cluster-specific (if applicable):**
   - vLLM tensor-parallel A/B
   - Data-parallel load testing
   - Endpoint routing comparison
7. **Contribute to tier tables:** Your advanced data fills gaps for other hardware tiers

**Methodology rule:** Each A/B must hold quality constant. A speed gain without a quality metric is not a result (verification section in `SKILL.md`).

---

## State E: "I'm adding models to my existing setup"

**Target hardware:** Any tier (applies to all users who already have a working system)

This is different from State B (which assumes the user is building up from scratch). State E assumes:
- They already have a working harness
- They already have one or more models running
- They want to add more without breaking what works

1. **Don't break what works**: your current config is validated; don't change it while adding
2. **Add one model at a time**: install, test, then add the next
3. **Benchmark new models against existing ones** with the SAME harness and SAME task set
4. **Check fit first**: run `bench/quick_bench.md` or engine memory log BEFORE committing to a new model
5. **Update your inventory** (see `model-management.md`) after each addition
6. **Watch for resource conflicts**: one model on the GPU at a time (verification section). A run was spoiled by a background session loading a model mid-sweep.
7. **Contribute data**: multi-model setups are undermeasured in this repo

**Trap:** Adding multiple models simultaneously makes it impossible to isolate what broke. Add one at a time, test it, then add the next.

---

## State F: "I'm on Intel/AMD unified memory, not NVIDIA"

**Target hardware:** Intel Arc, Strix Halo, Gorgon Halo, any APU (Tier 0–6, non-NVIDIA)

1. **Understand unified memory:** No VRAM split, model + KV + compute all from one pool
2. **Choose your backend:**
   - Intel Arc → llama.cpp SYCL or Vulkan (no CUDA available)
   - AMD Strix/Gorgon → llama.cpp HIP/ROCm (`HSA_OVERRIDE_GFX_VERSION=11.5.1` for Strix)
   - Universal → Vulkan (most portable)
3. **Run llama-fit-params:** Same arithmetic, different backend. It WILL work, verified on Intel Arc Pro B70, Strix Halo, Gorgon Halo community reports. See `llama-fit-broadening.md`.
4. **BIOS allocation:** On Strix Halo, raise iGPU allocation to 96 GB (128 GB system) or 160 GB (192 GB Gorgon) in BIOS before fitting models
5. **Bandwidth reality:** Strix Halo 256 GB/s vs RTX 4090 1,008 GB/s, models that fit run 4–7× slower. But models that DON'T fit on a 24 GB card DO fit on 128 GB unified. The trade is capacity vs speed.
6. **vLLM-ROCm:** Available but bandwidth-bound. Same constraint as llama.cpp.
7. **OS matters:** Linux has better ROCm support; Windows works via WSL2. macOS not applicable here (different unified-memory stack).

**What this means for the skill:** tuning advice must account for bandwidth, not capacity alone. A Strix Halo user has 5× more memory than a 24 GB card user but 4× less bandwidth. The right quant and context size are different.

---

## Journey quick-reference

| User says | State | First step |
|---|---|---|
| "I want to try local AI" | A | Install HF CLI, pick a 7–8B Q4_K_M, run the bench |
| "I have a model, how do I tune it?" | B | Inventory it, read engine memory log, run recall at depth |
| "My agents are broken despite big context" | C | Debloat harness, switch to local-dedicated harness, tune per harness |
| "I want to squeeze more" | D | Engine A/B, KV quant A/B, speculative sweep, hold quality constant |
| "I want to add another model" | E | One at a time, same harness, same task set, update inventory |
| "I have an AMD/Intel Mac/PC" | F | Choose backend, run llama-fit-params, account for bandwidth |
