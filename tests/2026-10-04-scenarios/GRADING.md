# Scenario test 1 - 2026-10-04

Skill at commit 229f265, installed as a project skill in a scratch dir; claude-local on Strata (Qwen3.8-Flash-Next
IQ2_XS, 512K), read-only tools (Bash/Edit/Write/WebFetch disallowed), one fresh session per prompt. Graded by the
orchestrator (Claude Opus) against the skill's own rules.

| Check | 1: RTX 3060 12 GB, 27B dense agent | 2: 4090, Q4_K_XL crashes mid-request | 3: M3 24 GB, MLX 30B-A3B |
|---|---|---|---|
| Skill used, evidence cited | yes | yes | yes |
| No transfer of 4090 numbers | yes (estimate labelled) | n/a (same class) | yes |
| Core diagnosis | right | right (runtime fit, T3 152k crash) | right (needs raised limit) |
| Bench handed over | yes | yes | yes, Mac unmeasured stated |
| Intake asked first | answered, then asked | answered, then asked | answered, then asked |

Defects (fixed in flight 6):
1. Sampling over-generalised: step 7's numbers are one thinking model's vendor spec; the answers applied them to a
   non-thinking Instruct coder model and said "keep thinking on" for it.
2. Overclaims: "the MTP draft context grows during generation" (not in the data); "20 GB is the commonly reported
   setting for exactly this model" (the source supports 20 GB for a 24 GB Mac, not for this model).
3. Intake rule unrealistic when the user already gave most details; allow answer-with-stated-assumptions.
Verdict: pass with fixes.
