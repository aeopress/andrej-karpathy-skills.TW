# Karpathy-Inspired Claude Code Guidelines

A small `CLAUDE.md` that complements Claude Code's built-in guidance, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

English | [繁體中文（台灣）](./README.zh-TW.md)

## Status (May 2026)

Claude Code's system prompt (Opus 4.7 / Sonnet 4.6 era) now includes most of the generic "don't over-engineer / make surgical changes / don't add speculative features" guidance that earlier versions of this skill provided. **This version intentionally keeps only what the system prompt still does not cover, and reframes the "leverage" point as a user-side prompting guide.**

The earlier full-rules version lives in [`archived/v1/`](./archived/v1/) for reference.

## What the assistant gets

Three reminders, copied verbatim from [`CLAUDE.md`](./CLAUDE.md):

1. **Stop when confused** — if a request is ambiguous, name what is unclear and ask; do not pick an interpretation silently.
2. **Every changed line should trace to the request** — re-read your diff before reporting done; if a line does not serve the user's stated goal, remove it.
3. **Loop on declarative goals** — when a verifiable end state exists, drive toward it autonomously.

That is the entire instruction file. The other pitfalls Karpathy named (overcomplication, drive-by refactors, speculative features, dead-code creep, removing comments the model "doesn't like") are already addressed by Claude Code's default system prompt; duplicating them only dilutes signal.

## What the user does — the actual leverage

Karpathy's strongest observation is **a user-side discipline**, not something the assistant self-enforces:

> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go."

To unlock this in your own workflow:

### Convert imperative → declarative

| Imperative (weak leverage) | Declarative (strong leverage) |
|---|---|
| "Add input validation" | "Write failing tests for these invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces the bug, then make it pass — other tests must still pass" |
| "Make it faster" | "Reduce p95 latency under this load to <X ms; benchmark with `scripts/bench.sh`" |
| "Refactor X" | "Refactor X without changing observable behavior; existing tests must still pass" |

### Give the assistant the means to verify

Together with the goal, hand it the verification tool: a test command, a benchmark script, a lint command, a browser MCP for visual checks. Then leave it to iterate.

### When to use which

- **Declarative**: features with observable outcomes, bug fixes, performance work, refactors with test coverage.
- **Imperative**: exploratory edits, UI tweaks, prose, anything where "done" is subjective.

### Explicit reframing: `/dec` (bundled with the plugin)

`/dec <request>` asks the assistant to convert the request into success criteria + verification command + non-goals **without implementing anything**. You confirm, then it executes. Use when you want the declarative discipline applied to a single prompt without changing how you write the rest.

```
/dec fix the login flicker on first load
```

Returns success criteria (e.g. "Playwright screenshot diff < 2px across 10 runs"), verification command, and explicit non-goals. If the task is too subjective or too small, it replies "not applicable — just do it" instead of forcing a conversion.

## Install

**Option A: Claude Code plugin**

From within Claude Code:

```
/plugin marketplace add yelban/andrej-karpathy-skills.TW
/plugin install andrej-karpathy-skills@karpathy-skills
```

**Option B: `CLAUDE.md` per-project**

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/yelban/andrej-karpathy-skills.TW/main/CLAUDE.md
```

## Using with Cursor

The repository includes [`.cursor/rules/karpathy-guidelines.mdc`](.cursor/rules/karpathy-guidelines.mdc) with `alwaysApply: true`. See [`CURSOR.md`](./CURSOR.md) for setup details and how it differs from the Claude Code install.

## Why this version is shorter

Cross-reference between [the four original principles](./archived/v1/CLAUDE.md) and the current Claude Code system prompt (Opus 4.7):

| Original principle | Already in system prompt? |
|---|---|
| Simplicity First (no speculative features, no abstractions for single-use code) | Yes — "Don't add features, refactor, or introduce abstractions beyond what the task requires" |
| Simplicity First (no error handling for impossible scenarios) | Yes — "Don't add error handling, fallbacks, or validation for scenarios that can't happen" |
| Surgical Changes (don't refactor adjacent code) | Yes — "A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper" |
| Surgical Changes (match existing style, don't reformat) | Yes — "Match the scope of your actions to what was actually requested" |
| Think Before Coding (state assumptions, surface tradeoffs) | Partial — system prompt covers exploratory replies; this skill adds "stop when confused" |
| Goal-Driven Execution (loop until verified) | Partial — system prompt covers self-verification; this skill adds the user-side declarative framing |

The three reminders that remain are the ones the system prompt does not cover or under-emphasizes.

For the full line-by-line diff between v1 and v2 — every removed sub-rule mapped to its system-prompt replacement, plus the rationale for the rewrites — see [`archived/v1/NOTE.md`](./archived/v1/NOTE.md#detailed-v1--v2-diff-for-claudemd).

## Relationship to upstream

This repository is a Traditional Chinese (Taiwan) localization fork of [`forrestchang/andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills), updated for the Claude Code Opus 4.7 era. Plugin / marketplace names intentionally match upstream; the README is bilingual (English + 繁體中文).

## License

MIT
