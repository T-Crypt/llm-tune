# LOCAL.md: the local model's command frontier

Optional additional setup for users running local models alongside cloud models in a
multi-harness environment. This is **not** a required skill step, it is an available
function, like the `nexus-sub` agent pattern in OpenCode. The operator chooses whether
to adopt it.

**Relationship to llm-tune's measured data**: llm-tune's numbers come from one RTX 4090-class
card running llama.cpp b11115 / llama-swap v257 plus Strata and NInfer measurements. The
LOCAL.md pattern is documented from the operator's tested recipes at `https://ai.ttindall.com/recipes/`
and from the architecture of the loopback router described in those recipes. No measurements
here, this is a setup pattern, not tuning data. Verify on your own hardware.

---

## The problem

Local models have tight context windows (4K–8K tokens for most quantized models).
A massive `AGENTS.md` (10K–15K+ tokens) would choke a local model. But you can't just
shrink `AGENTS.md` because cloud models need the full version. You also can't drop a local
model into a massive project expecting it to work with a 15K+ `AGENTS.md`.

**The tension**:
- `AGENTS.md` = global command frontier, can be huge (30K), used by cloud models → **keep as-is**
- `LOCAL.md` = local model frontier, sized for ~4096 tokens → **new, additive**
- Cloud model requests → `AGENTS.md` / `CLAUDE.md` unchanged
- Local model requests → `LOCAL.md` (the local model's frontier only)

Nothing is lost. `LOCAL.md` is a subset of `AGENTS.md`, never a parallel divergence.
It contains only what a local model needs to function for the tasks the operator assigns it.

---

## The chunk function

A procedure to create `LOCAL.md` from `AGENTS.md` of any size. It is a one-time setup;
re-run it when `AGENTS.md` changes significantly. Invoke it as:

```
/chunk-md AGENTS.md
```

or equivalently (same function, shorter name):

```
/local-md
```

Both forms produce the same output: a `LOCAL.md` sized for local-model context windows.

### Input → output

| Input size | Action | Output |
|---|---|---|
| AGENTS.md ≤ 4096 tokens | Too small for a local model, lacks guidance. Flag it. LOCAL.md should EXPAND guidance to reach ~4096, not trim further. | LOCAL.md = AGENTS.md + recommended expansions |
| AGENTS.md 4K–8K tokens | In the sweet spot. Chunk to ≤4096 by removing cloud-model-specific sections. | LOCAL.md = essential subset |
| AGENTS.md 8K–16K tokens | Chunk aggressively to ≤4096. Prioritize: safety, tool guidance, model-specific notes. | LOCAL.md = essential subset (flag what was lost) |
| AGENTS.md 16K+ tokens | Chunk hard to ≤4096. Flag all removed sections in a `## What was trimmed` section at the bottom of LOCAL.md so the operator knows what's missing. | LOCAL.md = essential subset + trim log |

### What LOCAL.md should contain (4096-token budget)

Priority order for what to keep (highest to lowest):

1. **Safety and validation protocols**, validate-with-operator rules, model deletion safety, privacy gates
2. **Tool guidance for local models**, which tools local models should use, tool-call reliability tips, debloated tool set (5-7 tools, no MCP)
3. **Model-specific notes**, quant-fit guidance, context window limits, reasoning budget caps per role
4. **Harness routing**, which harness runs local models, how it connects to the local model endpoint
5. **Essential project structure**, only the paths and files a local model needs to know about
6. **Quality criteria**, how to verify the local model's work (the non-negotiable checks)

### What LOCAL.md should NOT contain

- Cloud-model-specific instructions (Anthropic API details, cloud-only tooling)
- MCP server configurations (local models should run debloated, no MCP)
- Large project background that cloud models need but local models don't
- Anything that would bloat the context window beyond ~4096 tokens

### Output: the trim log

When chunking reduces LOCAL.md significantly, append a section listing what was removed:

```markdown
## What was trimmed from AGENTS.md (not lost: AGENTS.md remains intact)

- [Section name]: Removed because [reason]. Find it in AGENTS.md Section X.
- [Section name]: Removed because [reason]. Find it in AGENTS.md Section Y.
```

This guarantees nothing is lost, the operator can always find the full version in AGENTS.md.

---

## Harness routing

The loopback router (tested recipe at `https://ai.ttindall.com/recipes/claude-code-local-subagents/`)
is the mechanism that directs local model requests to LOCAL.md and cloud model requests to
AGENTS.md/CLAUDE.md.

### How it works

```text
Claude Code  →  loopback proxy  →  llama-swap (local roles: agent, coder, review, fast, thinker)
                                     ↕
Claude Code  →  Anthropic API  →  cloud model (uses AGENTS.md / CLAUDE.md normally)
```

1. Local role names (`agent`, `coder`, `review`, `fast`, `thinker` and similar) → forwarded to llama-swap → LOCAL.md context
2. All other model names (cloud models) → forwarded to Anthropic API → AGENTS.md / CLAUDE.md context
3. Auth headers stripped for local requests, preserved for cloud requests

### Setup (one-time)

1. Create `LOCAL.md` using the chunk function above
2. Configure the harness (Claude Code subagents, OpenCode, etc.) to point local role names at `LOCAL.md`
3. Run the loopback proxy: `python3 claude_router.py --port <router-port> --llama <llama-url>`
4. Verify: send a local request → should serve from LOCAL.md; send a cloud request → should serve from AGENTS.md

### The kill switch

Unset `ANTHROPIC_BASE_URL` (or equivalent) → Claude Code falls back to the Anthropic API directly,
local subagents error out. This is the safety mechanism, local model routing is opt-in, not forced.

---

## Sizing guidance

| Local model context | Recommended LOCAL.md size | Notes |
|---|---|---|
| 2K–4K (small quant, 7B–9B) | ≤2048 tokens | Aggressive trimming. Only safety + tool guidance + 1-2 role definitions. |
| 4K–8K (mid quant, 13B–30B) | ≤4096 tokens (recommended) | Standard LOCAL.md. All priority sections. |
| 8K–16K (large quant, 30B–70B) | ≤8192 tokens | More context allows including harness-specific notes. |
| 32K+ (Qwen3.8-27B at 256K, etc.) | ≤16384 tokens | Can include most of AGENTS.md with cloud sections removed. |

**General rule**: LOCAL.md should be sized for the smallest context window in the local model
roster. If one role runs at 2K context, LOCAL.md must fit in 2K (with overhead for the model's
own system prompt).

---

## When to re-run the chunk function

Re-run `/chunk-md` (or `/local-md`, same function) when:

- `AGENTS.md` is updated with new sections that affect local model operation
- The local model harness changes (new tools, new harness, different endpoint)
- The operator assigns new task categories to local models (new role definitions needed)
- The LOCAL.md trim log grows beyond ~200 tokens (sign of significant drift)

Do NOT re-run for minor AGENTS.md changes (typo fixes, reordering). Re-run for content changes
that affect what a local model needs to know.

---

## The alternative view: why this might be a bad idea

**Concern**: Two files to maintain creates staleness risk.
**Mitigation**: LOCAL.md is explicitly a SUBSET of AGENTS.md. It should never contain anything
AGENTS.md doesn't also contain. If it does, the operator is maintaining two conflicting command
frontiers, that's a user error, not a design flaw. The trim log provides the safety net.

**Concern**: The loopback router adds complexity.
**Mitigation**: The router is already tested and documented (two tested recipes on the site).
LOCAL.md doesn't add complexity to the router, it just changes what the router serves for local roles.

**Concern**: Local models can't follow complex guidance anyway, so a smaller file doesn't help.
**Mitigation**: Partially true, but the issue isn't comprehension, it's context exhaustion.
A local model that runs out of context mid-task fails regardless of guidance quality. LOCAL.md
keeps the guidance within the budget that actually fits.

---

## Relationship to the rest of the skill

- **SKILL.md Step 9**: LOCAL.md is the local model's harness configuration; Step 9 covers
  harness setup generally
- **`references/debloat.md`**, LOCAL.md is the debloated command file for local models;
  debloat principles apply (minimal tools, no MCP, low context)
- **`references/harnesses.md`**, LOCAL.md is configured per-harness; the harness-specific
  tuning in that file determines which harnesses run local models
- **`references/engine-backends.md`**, LOCAL.md doesn't affect engine fit arithmetic;
  it's a context-level routing decision
- **Website recipes**: the loopback router recipe and role-based recipes at
  `ai.ttindall.com/recipes/` are the tested implementations this pattern draws from

---

## Version tracking

| Version | Date | What changed |
|---|---|---|
| 2026-10-08 | Initial | LOCAL.md pattern documented from operator's tested recipes; chunk function spec defined; sizing guidance added |
