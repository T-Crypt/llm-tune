# Harness-specific tuning

Tuning advice differs by harness. This is not optional — the same model settings produce different results in different harnesses because each harness processes tool calls, manages context, and handles errors differently.

**Source:** [Infralovers 2026-07-14](https://www.infralovers.com/blog/2026-07-14-local-model-ai-coding-tools-benchmark/) — verified, same model across 4 harnesses (Pi, OpenCode, Claude Code, Copilot). Key finding (author's paraphrase): the leanest tools need the most hand-holding while the most structured harness produces the most autonomous results, at real-time cost. Claude Code measured at ~40 min total with 11+ minutes in planning; precise wall-clock times for the other three harnesses were not measured (the author explicitly states this gap), so any comparison is directional.

---

## The core principle

The leanest harnesses (Pi, OpenCode) need the most hand-holding on local models. The most structured harness (Claude Code) gives the most autonomous results but takes ~40 min on a coding task (11+ min in planning; timing of other harnesses not measured by the source, comparison is directional). **Tuning advice MUST differ by harness.**

| Harness | Profile | Context handling | Tuning priority |
|---|---|---|---|
| **Pi** | Local-only, leanest CLI | Compacts ~28k tokens, strict tool validation | Tool-call reliability > context > speed |
| **OMP** (Oh My Pi) | Local-only, rapid prototyping | Similar to Pi | Speed > quality > context |
| **Claude-local** | Local-only, reduced skills, 7 tools | Reduced tool set = less bloat | Quality > context > speed |
| **OpenCode** | Blend local+cloud, full skill set | Compacts ~28–32k tokens gracefully | Balanced — debloat for local-only sessions |
| **Claude Code** (local mode) | Max autonomy, plan+sub-agents | Plan burn-in ~11 min, total ~40 min on local model | Context size + quality > speed |

---

## Pi — tightest budget, hardest work

**Profile:** The leanest local harness. Designed for local-only operation. Minimal overhead but demands precise model behavior.

**Tuning advice:**
- Tool-call reliability is the #1 priority — Pi rejected ALL `write` calls without `path` argument. Budget for retrying sloppy tool calls.
- Keep models small enough that tool-call accuracy matters most.
- Reduce context to 2–4k for headroom (every GiB counts at this tier).
- Accept manual nudges — this harness needs them by design.
- No MTP/draft context benefit (Pi uses cloud model in user's setup but can use local).

**Verification:** Run a tool-call-heavy task set. If the model completes tool calls correctly 0/16 → 16/16 with parser tolerance change alone, the model is fine — the harness was the issue.

---

## OMP (Oh My Pi) — fast prototyping

**Profile:** Local-only, rapid iteration. Similar constraints to Pi but more focused on speed.

**Tuning advice:**
- Speed > quality > context (in that order).
- Same Pi-like tool-call strictness — budget for retries.
- Good for quick experiments, not for deep reasoning tasks.
- Same debloat rules as Pi (see `debloat.md`).

---

## Claude-local — quality-first local

**Profile:** Dedicated local harness for local models. Reduced skills (7 tools) = less bloat. Designed for users running entirely local.

**Tuning advice:**
- Quality settings first, context second — these users value accuracy over speed.
- Fewer tools to bloat (7 tool set), so debloat is already partially done.
- Strict validation catches model errors early — trust the harness.
- This is what the user runs for local-only work.

**Verification:** The harness itself validates tool calls — focus tuning on model quality settings and context size.

---

## OpenCode — balanced, watch for local bloat

**Profile:** Blend of local and cloud. Full skill set loaded into local model = context bloat risk when running local-only sessions.

**Tuning advice:**
- Balanced settings generally work.
- **EXPLICITLY debloat when running local-only sessions.** Full skill set in a local model is wasteful.
- OpenCode's tool surfaces are lean (low context overhead) — good for local models.
- When cloud-connected, less critical. When local, strip cloud-only skills.

---

## Claude Code (local mode) — max autonomy, pay in time

**Profile:** Most autonomous local harness. Plan mode + sub-agents. The same autonomy that makes it powerful also makes it slow on local models (~40 min on a coding task — Infralovers measured Claude Code at roughly 40 minutes total, with 11+ minutes in planning before any code was written; the Infralovers author did not measure precise wall-clock times for the other three harnesses, so treat the comparison as directional, not precise).

**Tuning advice:**
- Larger context windows matter more (plan burn-in is fixed cost).
- Quality settings critical — the autonomy means errors compound over many steps.
- Point at local endpoint via env vars:
  ```
  ANTHROPIC_BASE_URL=<local>
  ANTHROPIC_AUTH_TOKEN=<token>
  ANTHROPIC_DEFAULT_SONNET_MODEL=<local-model>
  ```
- Same autonomy, no cloud dependency.

**Context trap:** At 32k window, ~60% of context budget can go to tool definitions (Infralovers measured this for GitHub Copilot, not Claude Code — Claude Code's overhead is plan-mode time, not tool-definition tokens: 11+ minutes of the 40-minute run were planning). For context-bounded users on any harness, tool-definition overhead matters — see `debloat.md` for the compression data and per-tier tool limits.

---

## Universal harness rules (all harnesses)

1. **Harness/parser tolerance is a tunable:** tolerant tool-call parsing turned 5/16 failures into 0/16 without touching the model (`ninfer-toolcall` measurement).
2. **Client context cap = served window:** a hardcoded 262144 in the client overfills a 131k server (finding 28).
3. **Single-turn evals mislead:** a model that passes single-turn can fail multi-turn in a specific harness (finding 18).
4. **Think-about-the-tool-call, not the-model:** most harness issues are parser/tolerance/context, not model quality.

---

## Quick reference: which harness for which user

| User situation | Recommended harness | Why |
|---|---|---|
| "I just want it to work, I'm new" | Pi or OMP | Simplest setup, local-only |
| "I want local-only, I care about quality" | Claude-local | Built for local, reduced bloat |
| "I want local + cloud blend" | OpenCode | Flexible, good local support |
| "I want maximum autonomy locally" | Claude Code local | Most capable, slowest on local models |
| "My model keeps failing tool calls" | Check parser tolerance FIRST | 5/16 → 0/16 with tolerance alone |
| "My context fills up instantly" | Check harness context usage | 60% tool definitions at 32k in CC |

---

## Sources

- Infralovers — 4 harnesses benchmark (2026-07-14): https://www.infralovers.com/blog/2026-07-14-local-model-ai-coding-tools-benchmark/
- NInfer tool-call strict vs tolerant (2026-10-03): `state/evals/2026-10-03/ninfer-toolcall/`
- MODEL-ROLES context cap finding (2026-09-25): `projects/active/MODEL-ROLES-2026-09-25.md`
