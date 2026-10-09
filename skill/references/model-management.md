# Model management

How to download, inventory, and safely delete models across all engines and platforms.

---

## The download workflow (universal)

```bash
# 0. The HF CLI (hf) is optional but recommended for big quants: it transfers
#    large files over xet (fast, deduped) and works on Windows/Linux/Mac.
#    Models can be downloaded without it (browser, the HF HTTP API, ollama pull).
#    Check whether it is already installed, install only if you want it:
command -v hf && hf --version || pip install -U huggingface_hub

# 1. For GGUF models (llama.cpp)
hf download <org>/<model> --include "*.gguf" --local-dir ./models/<name>

# 2. For safetensors (MLX, PyTorch)
hf download <org>/<model> --local-dir ./models/<name>

# 3. For MLX quants specifically (mlx-community org)
hf download mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit --local-dir ./models/qwen3-coder-30b

# 4. List available quants for a model
hf api huggingface.co/api/models?author=mlx-community&search=Qwen3-Coder&limit=50

# 5. Check a model's file sizes (before downloading)
hf api huggingface.co/api/models/<org>/<model>/tree/main | jq '.[].size'
```

Note: `skill/bench/mlx_quant_search.py` talks to the Hugging Face HTTP API
directly and needs no `hf` CLI installed.

---

## Engine-specific download approaches

| Engine | Model format | Download approach | Key gotcha |
|---|---|---|---|
| llama.cpp | GGUF | HF download, single file | MTP tensors are part of the GGUF; check file size vs `vram-fit.md` table |
| MLX | safetensors | HF download, multi-file (sharded) | `mlx-community` org; check safetensors sum via HF API; use `bench/mlx_quant_search.py` for fit estimate |
| Ollama | GGUF (internal) | `ollama pull <name>` | Handles download + caching internally; simplest entry point |
| vLLM | multiple | HF download or model cache | Use `--model <path>` to local HF cache; avoids re-download on each serve |

---

## Model inventory template

Track each model in your collection. This is the template for `CONTRIBUTING.md` submissions and `data/INVENTORY.md` updates:

```yaml
# model inventory entry
- model: <name-or-organizer/model>
  path: ./models/<name>/model.gguf
  file_size_gib: <float>
  quant: <q4_k_m|q8_0|iq4_xs|...>
  mtp_tensors: yes|no
  registered_context_k: <number>

  # Runtime measurements
  peak_vram_mib: <integer>        # peak VRAM during run
  engine: <llama.cpp|strata|ninfer|...>
  engine_version: <build>
  backend: <cuda|sycl|vulkan|hip|metal>
  host_ram_peak_mib: <integer>    # if applicable
  status: working | OOM | partial | untested

  # Hardware
  tested_on_tier: <tier-number-from-hardware-tiers.md>
  hardware: <RTX 4090|Strix Halo 128GB|...>

  # Notes
  notes: <any observations>
```

---

## Model deletion safety

**Before deleting ANY model or file, validate with operator** (see `safety.md`).

### Deletion workflow:

1. **Validate with operator**, state what will be removed and kept
2. **Check for other instances:**
   ```bash
   # Check for duplicates
   find / -name "MODEL.gguf" 2>/dev/null
   # Check HF cache
   ls ~/.cache/huggingface/hub/models--<org>--<model>/snapshots/
   # Check if running
   pgrep -f "llama.*<model>" || echo "not running"
   ```
3. **Interactive delete only:** `rm -ri <file>` (never `rm -rf` for model files)
4. **Stop any running server** before deleting the file
5. **After deletion:** update inventory
6. **Verify:** check disk space freed, confirm server no longer references file

### HF cache cleanup:

```bash
# List cached models by size
du -sh ~/.cache/huggingface/hub/ | sort -rh | head -20

# Remove specific cached model (HF CLI)
hf delete-cache <org>/<model>

# Safe verification before deleting
ls -la ~/.cache/huggingface/hub/models--<org>--<model>/snapshots/
```

---

## Unsloth Desktop as a model management option

Unsloth Desktop provides a convenient model management layer:
- Built-in model hub: search/download/run GGUFs, MLX, safetensors
- Connects Claude Code, Codex, Hermes, OpenCode to local models via `unsloth start`
- The skill references it as a convenient option, not the primary path (HF CLI is primary)

**Sources:** Unsloth Desktop docs (unsloth.ai/docs/desktop).

---

## Sources

- HuggingFace Hub CLI docs: https://huggingface.co/docs/huggingface_hub/en/guides/cli
- Unsloth Desktop: https://unsloth.ai/docs/desktop
- Qwen3-Coder-30B-A3B-4bit size verification (HF API, 2026): `state/evals/2026-09-25/gain-research.md`
