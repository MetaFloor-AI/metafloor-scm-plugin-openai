# Changelog

All notable changes to the MetaFloor Supply Chain plugin for OpenAI Codex CLI.

## [0.1.0] - 2026-08-17
### Added
- **Initial OpenAI Codex CLI release.** A standalone, Codex-native supply-chain plugin: 72 skills
  (55 vendor systems across 15 categories + 16 end-to-end business workflows + a gating/judgment skill),
  4 independent review agents (`agents/*.md` + `agents/openai.yaml`), and a SessionStart hook that injects
  compact supply-chain safety guidance.
- **Safety as judgment, not enforcement.** The session-start guidance has the model classify each connector
  action (read / write / destructive / outbound) and pause consequential ones for explicit human approval.
  Actual gating of a tool call is handled by **Codex's own MCP approval flow** — documented honestly in the
  README ("Safety, honestly") and ARCHITECTURE.
- **Reference policy engine** under `core/` + `config/` + `eval/` (stdlib, unit-tested): action classification
  and an autonomy dial, kept as a portable, tested reference.

### Notes
- On OpenAI Codex, `PreToolUse` hooks fire for the shell tool only — MCP connector tool calls do not trigger
  a hook, and only a `deny` decision takes effect. A plugin-level deterministic gate over connector writes is
  therefore not possible on Codex today; the reference policy engine is **not** wired as live enforcement.
  Configure Codex's own approval policy on your connectors to enforce the posture a workflow recommends.
