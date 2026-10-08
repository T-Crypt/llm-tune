# Safety: validate-with-operator protocol & model deletion safety

This section covers two safety concerns: (1) the "validate with operator" command for irreversible actions, and (2) safe model/file deletion procedures.

---

## Part 1: Validate with operator

**The rule:** Before any irreversible action — deleting data, rotating credentials, destroying guests, exposing a service, force-pushing, modifying a running system — the skill MUST pause and ask the operator.

### The safety command:

> **"Validate with operator before proceeding: [describe exactly what will happen]."**

### What "validate with operator" means in practice:

1. **State exactly what will be removed or changed** — name the files, models, configs, or systems
2. **State what will be kept** — what stays untouched
3. **Confirm this isn't the only instance** — backup? another machine? another deploy?
4. **Wait for explicit approval** — silence is not consent; proceed only after the operator says go
5. **After completion** — verify the expected state, report what changed

### Common irreversible actions that require validation:

| Action | What to validate | What to check before |
|---|---|---|
| Deleting a model file | Exact file path, size, purpose | Is there a backup? Is it on another machine? |
| Deleting a quant | Quant name, model it belongs to, file size | Is this the only copy? Any references? |
| Deleting a harness config | Which harness, what settings | Can it be recreated? Is it version controlled? |
| Rotating a credential | Which service, impact on running systems | Is there a rollout plan? Rolling restart? |
| Exposing a service | Which service, port, URL | Is this the one public service (jellyfin)? |
| Force-pushing | Branch, what will be overwritten | Is there a backup branch? |
| Destroying a guest/VM | VM ID, name, data on disk | Snapshot? Backup? Other guests depend on it? |
| Restarting a service | Which service, downtime window | Graceful shutdown? Connection drain? |
| Reverting a commit | Which commit, what will change | Is this safe to revert? Tests passing? |

### The command in the skill flow:

When the decision procedure reaches an irreversible step, stop and use the validation command before proceeding. This applies to:
- Step 1 (Fit): if a user asks to delete a model that's currently running
- Step 4 (Offload/MoE): if a user asks to force-offload that risks a crash
- Any user request to remove models, configs, or data

---

## Part 2: Model & file deletion safety

### When a user asks to remove a model, quant, or HF download:

1. **Validate with operator** (see above)
2. State exactly what will be removed and what will be kept
3. Confirm this isn't the only instance:
   - Check for backups: `find / -name "MODEL.gguf" 2>/dev/null`
   - Check Hugging Face cache: `~/.cache/huggingface/hub/` — is it downloaded elsewhere?
   - Check if other machines use it (network share, NAS)
4. Use **interactive deletion** for files: `rm -ri <file>` (prompts per file)
5. **Never use `rm -rf` for model files** — always confirm each deletion
6. After deletion: update the model inventory (see `model-management.md`)
7. Verify: check that disk space was freed, check that no running server references the deleted file

### Safe model deletion workflow:

```bash
# 1. Identify the model
ls -lh ./models/<name>/

# 2. Check if it's running
pgrep -f "llama.*<name>" || echo "not running"

# 3. Check for copies elsewhere
find / -name "<filename>.gguf" 2>/dev/null | head -5

# 4. Check Hugging Face cache
du -sh ~/.cache/huggingface/hub/models--<org>--<model>/

# 5. Interactive deletion (ALWAYS use -ri)
rm -ri ./models/<name>/<file>.gguf

# 6. Verify deletion
ls -lh ./models/<name>/ 2>/dev/null || echo "deleted successfully"

# 7. Update inventory
# (edit data/INVENTORY.md or model-management.md)
```

### HF cache cleanup (safe):

```bash
# List cached models with sizes
du -sh ~/.cache/huggingface/hub/ | sort -rh | head -20

# Remove a specific cached model (HF CLI handles this)
hf delete-cache <org>/<model>

# Safe: verify before deleting
ls -la ~/.cache/huggingface/hub/models--<org>--<model>/snapshots/
```

---

## Part 3: What NEVER to do

| NEVER | Why |
|---|---|
| `rm -rf` on model files | Too destructive; use `rm -ri` and confirm |
| Delete the only copy of a model | Check backups and other machines first |
| Delete while a server is running | Stop the server first; verify it's stopped |
| Delete HF cache without checking duplicates | Multiple machines may share the cache |
| Rotate credentials without validation | May break running services |
| Expose a new service publicly | Only jellyfin.ttindall.com + apex is public |
| Touch VM 250 (kali) | OFF LIMITS — never |

---

## Part 4: Safety in the decision procedure

When the 9-step decision procedure reaches an irreversible step, insert the validation command. Specifically:

- **Before Step 1 (Fit):** If user wants to delete a model to free space → validate which model, confirm no other instances, interactive delete
- **Before Step 4 (Offload/MoE):** If user wants to force-offload to CPU → warn that it trades speed for headroom, confirm they want to proceed
- **Before any model deletion:** Full validation protocol (Part 2)
- **Before any config change to a running system:** Validate with operator

---

## Sources

- Safety protocols from AGENTS.md (homelab rules)
- Model management practices from hf_hub documentation
- Operational safety from state/incidents.md (embedding daemon, container OOM)
