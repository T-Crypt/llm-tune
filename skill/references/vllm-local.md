# vLLM for local serving (2–3 endpoints on a network)

Tuning for vLLM when serving models locally at scale, multiple endpoints, multi-model behind one port, or load-balanced across machines.

---

## How vLLM differs from llama.cpp tuning

vLLM is a production serving engine, not an inference engine. Fit arithmetic is about batch capacity + KV pool, not model fit alone.

| Dimension | llama.cpp | vLLM |
|---|---|---|
| Fit metric | model + KV + compute in VRAM | batch capacity + KV pool + per-token memory |
| KV management | contiguous buffer | PagedAttention (pages) |
| Request scheduling | one request at a time | continuous batching |
| Multi-GPU | tensor parallel via flags | `--tensor-parallel-size` |
| Prefix caching | engine-specific flag | `enable_prefix_caching` |
| KV quantization | `-ctk q8_0` | `kv_cache_dtype` (fp16, fp8, int8, fp8_e4m3) |
| Context cap | `--ctx-size` | `max_model_len` |
| ubatch | `-ub 1024` | `max_num_batched_tokens` |

---

## Fit arithmetic for vLLM

```
total_memory ≈ model_weights + KV_pool + compute_buffers + batching_overhead

KV_pool ≈ num_kv_heads × head_dim × num_layers × context_length × bytes_per_element
```

Same fundamental math as llama.cpp (KV is still the big consumer), but the engine manages allocation dynamically via PagedAttention rather than a contiguous buffer.

**Verification:** Run a load test with concurrent requests and watch memory: the KV pool will fluctuate with batch size, unlike llama.cpp's static allocation.

---

## Deployment patterns

### Pattern 1: One model per endpoint (simplest)

```bash
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --max-model-len 32768 \
  --kv-cache-dtype fp16
```

- Easy to tune each independently
- Good for: distinct models for different roles (coding vs chat vs research)

### Pattern 2: Multi-model behind one endpoint

```bash
# Serve multiple models on different ports
vllm serve coding-model --port 8001
vllm serve chat-model --port 8002

# Proxy with routing (nginx or custom)
# Client selects per request via header or path
```

- Good for: mixed workloads on a single network endpoint
- Requires: routing logic (vLLM Server or custom proxy)

### Pattern 3: Load balanced endpoints

```bash
# Multiple vLLM instances serving the same model
vllm serve model --port 8000 --tensor-parallel-size 2
vllm serve model --port 8001 --tensor-parallel-size 2

# Load balancer in front
nginx → 8000, 8001
```

- Good for: throughput, redundancy
- Data parallel across instances

### Pattern 4: Cluster serving (DGX Spark, multi-node)

```bash
# Per NVIDIA DGX Spark documentation:
# sparkrun for one-command launch/manage/stop
# vLLM tensor-parallel across nodes via ConnectX-7 RDMA
```

- Good for: models >200B, multi-tenant serving
- Per-node advice from this skill still applies

---

## Key flag mappings (llama.cpp → vLLM)

| llama.cpp | vLLM | Notes |
|---|---|---|
| `--ctx-size N` | `max_model_len N` | Client context cap must match served window |
| `-fa on` | `enable_prefix_caching` | Changes results; control in A/B |
| `-ctk q8_0` | `kv_cache_dtype fp8/int8` | KV quantization is a real lever |
| `-ub 1024` | `max_num_batched_tokens` | Batching changes the math |
| `--parallel 1` | `--tensor-parallel-size N` | Multi-GPU parallelism |
| `--n-cpu-moe` | N/A | vLLM handles MoE routing internally |

---

## Traps specific to vLLM

1. **`--max-model-len` ≠ client context cap.** A client cap larger than the served window overfills the server (400 or silent clipping, same trap as llama.cpp, finding 28).
2. **KV quantization quality beyond needle recall is unmeasured.** vLLM's FP8/int8 KV is a real lever, but quality at depth is not benchmarked in this repo.
3. **Engine defaults differ per version.** Pin vLLM versions; `--max-model-len` defaults and KV management have changed between versions.
4. **Prefix caching changes results.** If `enable_prefix_caching` is on, A/B test results are unreliable unless you control for it.
5. **Batching changes memory.** Unlike llama.cpp's static allocation, vLLM KV pool fluctuates with concurrent request count. Measure at your expected concurrency.
6. **Multi-model routing adds latency.** Pattern 2 adds proxy overhead; measure end-to-end latency, not per-model throughput alone.
7. **MLX ≠ vLLM on Mac.** vLLM on AMD ROCm (Apple Silicon via MLX is MLX territory, not vLLM). Don't mix engine advice.

---

## What transfers from llama.cpp to vLLM

- **Fit formula:** model + KV + compute is still the budget equation
- **Quality verification:** hold quality constant, recall at depth, repeat runs
- **Traps:** `--max-model-len`/context cap mismatch, version pinning
- **Method:** bench before and after, same prompt set, quality held constant

**What doesn't transfer:**
- Flag names (completely different CLI)
- t/s figures (different scheduling, different batching)
- `--n-cpu-moe` / `--ngl` / MTP flags (not applicable)
- Memory numbers (different allocation strategy)

---

## Multi-user serving measurement methodology

Multi-user / concurrent serving is **unmeasured** in this repo. To measure it yourself:

1. Run X concurrent requests with Y model at Z context
2. Measure t/s degradation vs single-request baseline
3. Measure quality score per request (same task set)
4. Vary X (concurrency) and Z (context) systematically
5. Hold the task set constant: the task determines what degrades

**Template:** `bench/quick_bench.md` is single-user; create a parallel variant for concurrency testing.

---

## Sources

- vLLM docs: https://docs.vllm.ai/en/stable/cli/serve/
- vLLM on DGX Spark (2026-06-01): https://vllm.ai/blog/2026-06-01-vllm-dgx-spark
- NVIDIA DGX Spark vLLM: https://build.nvidia.com/spark/vllm/multi-node
- MindStudio cluster guide: https://www.mindstudio.ai/blog/how-to-cluster-dgx-spark-vllm
- vLLM production deployment (2026): https://www.spheron.network/blog/vllm-production-deployment-2026/
- Multi-model serving (vLLM discussions #239): https://github.com/vllm-project/vllm/discussions/239
