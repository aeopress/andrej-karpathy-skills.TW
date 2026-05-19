# Using this repo with Cursor

The Karpathy-inspired guidelines apply to Cursor via [`.cursor/rules/karpathy-guidelines.mdc`](.cursor/rules/karpathy-guidelines.mdc), committed with `alwaysApply: true`.

## In this repository

Open the folder in Cursor — the rule loads automatically. Confirm under **Settings → Rules** if needed.

## Use in another project

Copy `.cursor/rules/karpathy-guidelines.mdc` into that project's `.cursor/rules/` directory.

If a tool only supports a root instruction file, copy [`CLAUDE.md`](./CLAUDE.md) instead.

## Optional: personal Cursor skill

Symlink or copy [`skills/karpathy-guidelines/SKILL.md`](./skills/karpathy-guidelines/SKILL.md) into `~/.cursor/skills/`.

## Claude Code vs Cursor

- **Claude Code:** see [`README.md`](./README.md) install section. Plugin or `CLAUDE.md`.
- **Cursor:** the committed `.cursor/rules/` file is enough; Cursor does not read `.claude-plugin/` or `CLAUDE.md`.

## For contributors

Keep [`CLAUDE.md`](./CLAUDE.md), [`.cursor/rules/karpathy-guidelines.mdc`](./.cursor/rules/karpathy-guidelines.mdc), and [`skills/karpathy-guidelines/SKILL.md`](./skills/karpathy-guidelines/SKILL.md) in sync (same three reminders).
