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

## Re-test after flight 6 (16d13ea) and the card rule

Same three prompts, same setup.
- Defect 1 fixed: scenario 3 says the Instruct coder has no thinking mode ("no reasoning budget to cap"); scenario 1
  says the evidence-base sampling is one hybrid thinking model's and does not transfer.
- Residual found: scenario 3 still stated "the Qwen3 card recommends temp 1.0, top_p 0.95..." without being able to
  read the card (the skill's example values, misattributed). Verified the real card: temperature 0.7, top_p 0.8,
  top_k 20, repetition_penalty 1.05. Added to step 7: if the card cannot be read, say so and give the lookup; never
  state a card's values from memory. Re-run of scenario 3: correct values, says it cannot fetch the page, tells the
  user to verify.
- Defect 2 fixed: the MTP line now matches the data (separate allocation that can OOM; no "grows" claim); 20 GB is
  "the common working setting for a 24 GB Mac".
- Defect 3 fixed: all three answers open with stated assumptions and end with the facts still missing.
Verdict: pass. Remaining limits are the documented ones (one hardware class, Mac section unmeasured).
