# Release review, 2026-10-08

Full repo pass before the public announcement: README, banner, skill files,
references, tables, data, contributing, templates, tests, and structure.

## What changed in this pass

- README rewritten: banner, install and use instructions, scope section,
  repository layout, contributing. The stale "Local until tested; nothing is
  released" status line is gone.
- Banner added under `assets/` (SVG source, PNG render). The design is the
  measured VRAM budget bar from the 131k fit table: model file, KV cache,
  compute buffers, mmproj, MTP draft, headroom. The green tick in the bottom
  ruler is the needle-at-depth bench.
- Internal build plans and the pre-release review moved from the repo root to
  `docs/dev/`, with a README explaining their provenance.
- Repo-wide typographic cleanup outside `tests/`: 566 em dashes removed, "not
  just X" formulas rewritten as direct statements, ALL-CAPS emphasis lowered,
  "Key insight" and "transformation story" labels replaced with plain claims.
  The frozen scenario records in `tests/` keep their original punctuation;
  they are run records, not docs.
- `CHANGELOG.md` started; `tests/README.md` marks the scenario files as
  frozen records; CI workflow added (bench scripts compile check, plus a
  warning-only em-dash report).
- `data/INVENTORY.md` reframed for public readers: citations point at the
  private measurement repo as provenance, the tabulated numbers live here.
  Header hardware corrected: 31 GB RAM host, was 64 GB. Verified against the
  machine (`free -h` reports 31 GiB) and against every "31 GB box" figure in
  the evidence.
- Privacy: removed the author's lab-specific rules from
  `skill/references/safety.md` (the one-public-service topology and the
  internal VM numbering) and the same items from `docs/dev/`. The
  `ai.ttindall.com` recipe citations stay: that site is public and they are
  real provenance.
- `skill/references/harnesses.md`: one caveat was stated three times; now
  once. Splices and caps fixed.
- `CONTRIBUTING.md` and the issue template: cleaned, filler removed.

## Verification

- `py_compile` passes on all three bench scripts.
- Sweep results: zero em dashes outside `tests/`; zero "not just / not only";
  no private host names, VM ids, IPs, or local paths anywhere (docs/dev
  sanitized too); remaining `ai.ttindall.com` references are intentional
  public citations.
- Scenario records in `tests/` untouched.

## Recommendations before the announcement

1. **Publish the repo before posting.** The announcement links to
   github.com/T-Crypt/llm-tune; if it is private at post time, the link 404s.
   It resolved 200 during this pass, so this is just "keep it that way".
2. **The skill frontmatter description is the trigger surface.** It is clean
   now; if it changes again, keep it free of dashes and formulas. It is what
   Claude reads when deciding to load the skill.
3. **One decision left to the author: the `ai.ttindall.com` citations.** They
   are public links and real provenance, but they tie the GitHub identity
   (T-Crypt) to the blog identity. If that is unwanted, replace them with
   "the author's recipe site" phrasing and lose the working links.
4. **Channel:** r/LocalLLaMA is the primary audience. The bench, the fit
   traps, and the hardware tiers are exactly what that community argues
   about. Cross-post options: r/ClaudeAI (the skill angle), r/LocalLLM or
   r/ollama (the bench scripts). One post, not five; Reddit punishes
   identical cross-posts.
5. **Post shape:** data-first. The bullets in the README's "What the
   measurements show" section are the post. State the one-machine scope up
   front; it is the most credible sentence in the whole repo.
6. **Expect the first question to be "does it work with Ollama / LM Studio /
   Windows?"** The honest answer is SKILL.md section 5: method and traps
   transfer, numbers do not, and the per-backend files are sourced rather
   than measured. Answer with that section.
7. **After the post:** the first external measurement on a different hardware
   class is the milestone that turns the one-machine caveat into a
   two-machine evidence base. The Measurement Report issue template exists
   for exactly that.

## Addendum: merge with the parallel README rewrite (2026-10-08, post-review)

While this review was in progress, a second agent (opencode/Ling 3.0 Flash VL)
pushed its own README rewrite (477ee36) to origin. The rebase merged the two:

- Kept from this review's version: the banner, the no-slop discipline (the
  remote version had ~20 em dashes, marketing voice, a "Trap of the day"
  section, and the stale "Flight 6 / Local until tested" status line), the
  status fix, the Why section, the measurement bullets' numbers, scope.
- Adopted from the remote version: the 9-step decision table (de-slopped; one
  claim corrected: the HTTP 400 at depth is an error, not silent), per-agent
  install instructions, the format-compatible agent list (reworded from
  "confirmed compatible" to loadable-by-format, which is what format support
  actually shows), the evidence-honesty gap table, the purpose-grouped
  layout, and the CITED.md row (50 source entries, verified live 2026-10-08;
  count checked against the file).
- Cut: "Trap of the day" (engagement gimmick; the traps live in SKILL.md
  section 4), the marketing one-liner, "Flight 6" jargon.

## Not done, deliberately

- `tests/` scenario answers keep their generated punctuation; frozen records.
- `docs/dev/` keeps its planning voice; it is labeled as internal notes.
- No badges or shields on the README; they read as template decoration and
  add nothing the status line does not already say.