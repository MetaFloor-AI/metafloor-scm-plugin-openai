# Architecture - metafloor-scm-plugin-openai

> System structure and safety posture. Update only when these change.

## Overview
An OpenAI Codex CLI plugin that adds supply-chain capability on top of Codex, which owns the runtime,
agent loop, tools/MCP connections, permissions, and execution. The plugin contributes **expertise**
(how enterprise systems work + how supply-chain decisions are made) and **judgment** (how to classify
a connector action and when to pause for human approval). It owns **no** tools, connectors, or
integration layer, and it does **not** enforce a control over your tool calls — that keeps it portable,
and it means enforcement is Codex's job, not the plugin's (see Safety posture).

## Components
- **Platform expertise skills** — `skills/platforms/<category>/<vendor>/SKILL.md`. Prose operator knowledge
  for one vendor system (object/state model, the vocabulary that bites, the read/write/destructive matrix,
  gotchas as causal chains, edge states, recovery, guardrails; deep material in `references/`). 15 categories.
  No tool names.
- **Business-workflow skills** — `skills/business-workflows/<name>/SKILL.md`. One end-to-end supply-chain
  decision each: the operating method (the computation with thresholds), a worked example with numbers, and
  a failure→recovery playbook. Each recommends a per-workflow autonomy posture (advisory). Defers each vendor
  HOW by name to the matching expertise skill.
- **Gating skill** — `skills/gating/supply-chain-gating/` — the cross-cutting judgment: classify each action
  (read / write / destructive / outbound), when to stop for a human, and how to present a consequential action
  for approval. Advisory, not an enforced control.
- **Specialist agents** — `agents/*.md` (+ `agents/openai.yaml` interface) — independent subagents the main
  agent delegates to for a fresh, uncontaminated context: `decision-reviewer`, `scope-auditor`,
  `genealogy-tracer`, `cross-system-reconciler`. Fully tool-enabled; analysis-only by prompt. They advise; the
  human approves.
- **Session-start guidance** — `hooks.json` (SessionStart) → `scripts/session_context.sh` emits a compact
  safety brief so the model reasons in read/write/destructive terms and pauses consequential actions for
  approval from the first turn.
- **Reference policy engine** — `core/` + `config/` + `eval/` (stdlib, unit-tested): action classification, an
  autonomy dial, and scenario/lint tests. Kept as a portable, tested reference; **not wired as live
  enforcement** on Codex (see Safety posture).

## Safety posture (read this)
The safety value here is **operator judgment**, injected at session start — not a technical control that
blocks a tool call. On OpenAI Codex:
- `PreToolUse` hooks fire for the **shell tool only**; **MCP connector tool calls do not trigger a hook**, and
  only a `deny` decision has any effect. So a plugin-level deterministic gate over connector writes is **not
  possible** on Codex today.
- The actual gate on a connector call is **Codex's own MCP approval flow** — configure `approval_policy` and
  per-connector `approval_mode` to match the posture a workflow recommends (observe / suggest / gated /
  bounded-auto / auto).
- The plugin therefore ships the judgment (classification + when-to-stop) and defers enforcement to Codex.

## Data flow
```
SessionStart -> scripts/session_context.sh injects the safety brief (advisory context)
Model reasons with the skills; before a consequential connector action it classifies it and
  presents What / preview / rollback / provenance for approval
Codex's own MCP approval flow prompts the human on the actual tool call
```

## Integrations
None owned by the plugin. It ships no MCP server, connector, adapter, or orchestrator. The customer brings
their real connectors and configures Codex's approval policy on them. The plugin provides the judgment.
