# Changelog

All notable changes to the MetaFloor Supply Chain plugin for OpenAI Codex CLI.

## [0.1.0] - 2026-08-14
### Added
- **Initial OpenAI Codex CLI release.** A standalone, Codex-native supply-chain plugin: 72 skills
  (55 vendor systems across 15 categories + 16 end-to-end business workflows + a gating reference),
  4 independent review agents (`agents/*.md` + `agents/openai.yaml`), 5 operator commands
  (`commands/scm-*.md`), and a deterministic PreToolUse policy gate with an autonomy dial.
- **Host layer** — plugin-root `hooks.json` (SessionStart context + PreToolUse `mcp__.*` → the shared
  `core.hook`), self-locating `scripts/pretooluse.sh`/`.py` (fails **closed** with no Python interpreter),
  `.codex-plugin/plugin.json` manifest, and `.agents/plugins/marketplace.json`.
- **Safety harness** (`core/`, stdlib, unit-tested): connector-tool classification, autonomy-dial
  resolution, allow/ask/deny gate, session blast-radius tracking, hash-chained audit. Fails closed on an
  unknown op of a mapped app; governs only `mcp__*` connector tools.
- **Eval** — P0 gate-safety scenarios (`eval/run.py`, 100% safe, over-gate budget 0), skill/registry lint,
  105 harness unit tests, and a 7/7 deterministic Codex adapter proof.

> This repository is the OpenAI-only build of the MetaFloor supply-chain plugin. It reuses the
> host-agnostic `core/`, `skills/`, and `config/`; only the host layer (manifest, hooks, agents, commands)
> is Codex-native.
