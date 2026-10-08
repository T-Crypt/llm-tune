# Harness debloat & MCP compression

Every tool in a harness's MCP server set consumes context tokens. On a 24 GB card with a 131k context window, those tokens cost GB of KV cache. On an 8 GB card, they're the difference between fitting and not fitting.

**Source:** [Atlassian mcp-compressor (2026-03-29)](https://www.atlassian.com/blog/development/mcp-compression-preventing-tool-bloat-in-ai-agents) — 94-tool GitHub MCP server compressed from 17,600 to 500 tokens.

---

## Why this matters for local models specifically

> "A cloud-hosted model with 128k context can absorb verbose tool descriptions from three or four MCP servers and still have room for the task. A local model with an 8–32GB VRAM context window has no such luxury."
> — [Dev.to: MCP bloat hits local models harder](https://dev.to/shenao_yu_e15c14815264a44/mcp-tool-bloat-hits-local-models-harder-a-constraint-worth-talking-about-oon)

At 0.033 GiB per 1k tokens (q8_0 KV, dense model):
| Tokens | KV cost (dense) | On 8 GB card | On 24 GB card |
|---|---|---|---|
| 17,600 (full) | 0.58 GiB | Lethal — competes with model | Painful but survivable |
| 3,900 (low compression) | 0.13 GiB | Significant | Manageable |
| 500 (max compression) | 0.017 GiB | Negligible | Negligible |

---

## The compression levels (Atlassian data, GitHub MCP server, 94 tools)

| Compression level | Tokens | Reduction |
|---|---|---|
| Full (no compression) | 17,600 | baseline |
| Low | 3,900 | 78% |
| Moderate | 3,300 | 81% |
| Strong | 2,200 | 87% |
| Max | 500 | 97% |

---

## Per-tier tool count limits

| VRAM tier | Max tools | Rationale |
|---|---|---|
| 8 GB (RTX 4060, base M6, Arc B580) | 5–7 tools | Every token counts; harness debloat is survival |
| 16 GB (RTX 4070 Ti, M6 24/32 GB) | 10–12 tools | Room for moderate bloat; compress everything |
| 24 GB+ (RTX 4090 and above) | 15–20 tools | Debloat is good practice, not survival-critical |
| Unlimited (server/cluster) | 20+ | More room for tools, they still cost context |

---

## What to keep vs strip vs compress

### Keep (tools the agent calls directly in core workflow):
- grep, file-read, file-write, shell, websearch
- Any tool the agent calls in >20% of tasks
- Any tool the agent cannot work without (e.g., `write_file` for code generation)

### Strip (tools called <5% of the time):
- Jira, Confluence, GitHub issues (if not the primary workflow)
- Any MCP server the agent rarely invokes
- Tools called via other tools (MCP-in-MCP chains)

### Compress (everything else):
- Use mcp-compressor at `brief` level (78% reduction, reasonable discoverability)
- Use `moderate` for tools the agent calls regularly but whose schemas are verbose
- Use `strong` for rarely-used tools you might still need

---

## mcp-compressor usage

```bash
# Install
npm install -g @atlassian/mcp-compressor

# Compress a server config at different levels
mcp-compressor compress --level brief    # 78% reduction, good discoverability
mcp-compressor compress --level moderate # 81% reduction
mcp-compressor compress --level strong  # 87% reduction
mcp-compressor compress --level max     # 97% reduction, minimal discoverability
```

---

## Local-only harness tool sets (recommended)

When running local models, use a dedicated local harness with a stripped tool set. The user's Pi/OMP/Claude-local configs (7 tools each) are the correct pattern.

### Recommended local-only tool set (7 tools):
1. `grep` — search codebase
2. `file-read` — read files
3. `file-write` — write/modify files
4. `shell` — run commands
5. `websearch` — research (when connected)
6. `bash` — shell operations
7. `mcp-fetch` — fetch URLs

### What Claude-local strips (and why it works):
Claude-local ships with 7 tools vs Claude Code's 30+. This is not a limitation — it's the correct local-only configuration. Fewer tools = less bloat = better tool-call reliability on smaller models.

---

## Harness debloat rules by tier

### When VRAM < 16 GB:
1. Run a dedicated local harness with ONLY 5–7 tools
2. Don't load cloud-skills into a local model
3. Compress all remaining MCP servers at `brief` level minimum
4. Strip any server called <5% of the time
5. **This is survival, not optimization** — on 8 GB, tool-call overhead can push a model over budget

### When VRAM 16–24 GB:
1. Maximum 10–12 tools
2. Strip MCP servers called <5% of the time
3. Use mcp-compressor at `moderate` level on remaining servers
4. Verify: tool-call reliability ≥ your quality bar (use `--tolerant-tool-calls` as a test)

### When VRAM > 24 GB:
1. Debloat is good practice but not survival-critical
2. More room for tools, but they still cost context
3. Focus on quality settings first; debloat is a secondary optimization

---

## Verification

1. Measure tool-call success rate before and after debloat (same model, same task, harness-only change)
2. Check recall at depth — debloat should not reduce task completion
3. Measure KV usage before/after (engine log: "KV buffer size" before and after stripping tools)
4. Run the same task set before/after, quality metric held constant

---

## Sources

- Atlassian mcp-compressor (2026-03-29): https://www.atlassian.com/blog/development/mcp-compression-preventing-tool-bloat-in-ai-agents
- Dev.to: MCP bloat hits local models harder: https://dev.to/shenao_yu_e15c14815264a44/mcp-tool-bloat-hits-local-models-harder-a-constraint-worth-talking-about-oon
- Infralovers harness benchmark (2026-07-14): https://www.infralovers.com/blog/2026-07-14-local-model-ai-coding-tools-benchmark/
- NInfer toolcall strict vs tolerant (2026-10-03): `state/evals/2026-10-03/ninfer-toolcall/`
