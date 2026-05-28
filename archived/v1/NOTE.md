# Archived: v1 (original four-principles version)

This directory contains the original four-principles version of the Karpathy guidelines, archived on 2026-05-19.

## Why archived

By Claude Code Opus 4.7 (May 2026), the default system prompt covers most of the original four principles:

- **Simplicity First** → covered by system prompt
- **Surgical Changes** → covered by system prompt
- **Think Before Coding** → partially covered
- **Goal-Driven Execution** → partially covered

Keeping the full four principles in `CLAUDE.md` duplicated the system prompt, diluted signal, and risked false triggers on non-code tasks (writing, docs).

See the project [`README.md`](../../README.md) for the side-by-side comparison and the three reminders that replaced this version.

## Detailed v1 → v2 diff for `CLAUDE.md`

The v1 file was 66 lines; the v2 file is 21 lines (~68% reduction). Below is the line-by-line accounting of what was removed and why.

### Overall structural changes

| Section | v1 | v2 | Reason |
|---|---|---|---|
| Opening framing | "Merge with project-specific instructions" + "**Tradeoff:** caution over speed; for trivial tasks, use judgment" | "Notes that complement Claude Code's built-in guidance. Apply to code work; for non-code tasks (writing, docs, design), use judgment." | "Caution over speed" had a large false-trigger surface (the LLM cannot reliably classify "trivial"). Rescoped to task type (code vs. non-code), which is a judgment the LLM can actually make. |
| Body | 4 principles × 4–7 sub-rules each | 3 reminders | ~70% of the sub-rules are already in the Opus 4.7 system prompt verbatim or near-verbatim. |
| Closing | "These guidelines are working if: fewer unnecessary changes / fewer rewrites / clarifying questions come first" | "This file intentionally omits generic coding hygiene... see `archived/v1/CLAUDE.md` and `README.md` for the rationale." | The v1 closing was a user-facing success metric the LLM cannot self-check. The v2 closing is a meta-instruction that tells the LLM why the file is short, preventing it from over-extrapolating from a sparse prompt. |

### Fully removed: Principle 2 "Simplicity First"

Every sub-rule maps to an existing line in the Opus 4.7 system prompt:

| v1 sub-rule | Already in system prompt |
|---|---|
| "No features beyond what was asked" | "Don't add features, refactor, or introduce abstractions beyond what the task requires" |
| "No abstractions for single-use code" | "Three similar lines is better than a premature abstraction" |
| "No 'flexibility' or 'configurability' that wasn't requested" | "Don't design for hypothetical future requirements" |
| "No error handling for impossible scenarios" | "Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries" |
| "If you write 200 lines and it could be 50, rewrite it" + senior-engineer test | Implied by the above; "No half-finished implementations either" |

**Why removed wholesale:** 100% duplication of system prompt content. Restating diluted signal without adding any.

### Mostly removed: Principle 3 "Surgical Changes" (1 line kept)

| v1 sub-rule | Status | Reason |
|---|---|---|
| "Don't 'improve' adjacent code" | Removed | System prompt: "A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper" |
| "Don't refactor things that aren't broken" | Removed | System prompt: "Match the scope of your actions to what was actually requested" |
| "Match existing style" | Removed | Implied by scope-matching above |
| "Don't remove pre-existing dead code unless asked" | Removed | System prompt handles this more precisely: "Avoid backwards-compatibility hacks like renaming unused _vars... If you are certain that something is unused, you can delete it completely" |
| "Remove imports/variables/functions YOUR changes made unused" | Removed | Same as above |
| **"Every changed line should trace directly to the user's request"** | **Kept (renamed)** | System prompt has no self-check mantra; this single line is the working definition of "surgical" and is verifiable during diff review. |

### Mostly removed: Principle 1 "Think Before Coding" (1 line kept)

| v1 sub-rule | Status | Reason |
|---|---|---|
| "State your assumptions explicitly" | Removed | System prompt: "For exploratory questions, respond in 2-3 sentences with a recommendation and the main tradeoff. Present it as something the user can redirect" |
| "If multiple interpretations exist, present them" | Removed | Covered by the same line above (multi-interpretation surfacing is implicit in "the main tradeoff") |
| "If a simpler approach exists, push back" | Removed | "Push back when warranted" is already in the broader system prompt framing around exploratory replies |
| **"If something is unclear, stop. Name what's confusing. Ask."** | **Kept (renamed to "Stop when confused")** | System prompt has no explicit "stop and ask" instruction. This is genuinely additive. |

### Rewritten (not pure removal): Principle 4 "Goal-Driven Execution"

**v1 (removed):**
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"
- Multi-step plan format: `1. [Step] → verify: [check]`

**v2:** "Loop on declarative goals" + "if the request is imperative but a clear success criterion exists, propose the declarative version first."

**Three reasons for the rewrite:**

1. **TDD hardcode is harmful in non-testable contexts.** The v1 examples were all "write a test first." UI tweaks, config edits, and prose work have no test to write. The v1 framing pushed the LLM to invent verification criteria where none belonged.

2. **Role inversion of Karpathy's actual point.** Karpathy's original line is: "Don't tell it what to do, **give it** success criteria and watch it go." The success criterion is something the **user** provides, not something the LLM defines for itself. The v1 wording placed the burden on the LLM, contradicting the source observation.

3. **Plan-and-verify format was over-prescriptive.** The system prompt already handles "state a brief plan for multi-step tasks." The v1 `1. [Step] → verify: [check]` format was a lock-in that constrained the LLM in cases that did not need a structured plan.

The v2 rewrite reframes the LLM's role as **converter and executor** ("when you see an imperative request with an obvious criterion, propose converting it first; when the user has already given you a verifiable end state, drive toward it autonomously"), which matches the collaboration model Karpathy described.

### One-line summary

Of the 45 lines removed, roughly 35 were direct duplicates of Opus 4.7 system prompt content, and roughly 10 were example hardcodes (TDD framing) that misfired on non-code work. The 3 reminders that remain are the ones the system prompt genuinely does not cover or under-emphasizes.

## Contents

- `README.md` / `README.zh.md` — original READMEs (English + simplified Chinese)
- `CLAUDE.md` — original four-principles CLAUDE.md
- `CURSOR.md` — original Cursor setup notes
- `EXAMPLES.md` — 500 lines of good-vs-bad code examples
- `SKILL.md` — original skill file (from `skills/karpathy-guidelines/`)
- `cursor-rule.mdc` — original Cursor rule (from `.cursor/rules/`)

## Appendix: Observed Opus 4.7 system prompt (2026-05-28)

> **Full snapshot:** [`../observed-system-prompts/2026-05-28-opus-4.7-cli.md`](../observed-system-prompts/2026-05-28-opus-4.7-cli.md) reproduces the entire prose system prompt (from "You are Claude Code..." through `# Context management`), explains how the built-in prompt is structurally separable from CLAUDE.md injection in the session the model receives, and includes a per-quote cross-reference. This appendix retains only the excerpts directly relevant to v1's four principles, plus the "what is NOT in the prompt" notes that justify the three v2 rules we kept.

Below are the verbatim passages from Claude Code's Opus 4.7 system prompt that the v1 → v2 deletion argument relies on. They were observed in a live Claude Code CLI session on 2026-05-28 and are quoted here so any reader can verify the mapping in the [README's `Which v1 rules ended up where` table](../../README.md#which-v1-rules-ended-up-where) without re-running an observation themselves.

**Caveats:**
- Claude Code's system prompt is injected at runtime; Anthropic does not publish it. Wording may change in future CLI / model updates.
- These are the passages directly relevant to v1's four principles. The full system prompt contains many other sections (tool use, environment, language, hooks, etc.) that are reproduced in the full snapshot linked above.
- To verify this snapshot against your own session, start `claude` in any directory and inspect the system prompt via the CLI's debug / dump facilities, or by asking the model to repeat its instructions verbatim. Differences are expected over time.

### Section: `# Doing tasks`

> Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper. Don't design for hypothetical future requirements. Three similar lines is better than a premature abstraction. No half-finished implementations either.

> Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.

> For exploratory questions ("what could we do about X?", "how should we approach this?", "what do you think?"), respond in 2-3 sentences with a recommendation and the main tradeoff. Present it as something the user can redirect, not a decided plan. Don't implement until the user agrees.

> Avoid backwards-compatibility hacks like renaming unused _vars, re-exporting types, adding // removed comments for removed code, etc. If you are certain that something is unused, you can delete it completely.

### Section: `# Executing actions with care`

> Match the scope of your actions to what was actually requested.

### What is NOT in the observed system prompt

These are claims v2 does **not** make — they are documented here to forestall over-reading the deletion argument:

- **"Stop and ask when confused"** as an explicit instruction — no such line. v2 keeps `## Stop when confused` precisely because the system prompt does not cover it.
- **"Every changed line should trace to the user's request"** as a diff self-check — no such line. v2 keeps this as its own reminder.
- **"Drive toward declarative success criteria autonomously"** — no equivalent. This is Karpathy's contribution; v2 keeps it under `## Loop on declarative goals`.
- **"State a brief plan for multi-step tasks"** — not observed in the 2026-05-28 snapshot. The v1 multi-step plan template was dropped on **design judgment** (the system prompt's general guidance was deemed sufficient), not on verbatim overlap.
- **TDD-first phrasing** — not observed. v1's "write a test that reproduces the bug, then make it pass" examples were dropped because they hard-code testable contexts onto every task, not because the system prompt replaces them.
