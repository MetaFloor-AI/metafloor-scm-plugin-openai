#!/usr/bin/env python3
"""PreToolUse entrypoint for the supply-chain plugin (Codex CLI).

Codex invokes this on every MCP tool call (matched by the plugin-root hooks.json
`mcp__.*`). It reads the hook event from stdin, normalizes it into the shape
`core.hook` expects, asks for an allow | ask | deny decision, and writes the
decision JSON to stdout (exit 0). ALL the logic — and the fail-closed behaviour —
lives in `core/`; this file is only the host adapter.

Layout: this lives at `<plugin>/scripts/pretooluse.py`, with `core/`, `config/`,
and `skills/` at the plugin root. When Codex installs this plugin (marketplace
source "./"), it snapshots the plugin, so the same relative layout holds inside
the install cache.
"""
import json
import os
import sys


def _repo_root() -> str:
    """Plugin root = one level up from this script (scripts/ -> plugin root).

    That root holds core/ + config/ + skills/.
    """
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(scripts_dir)


def _normalize(event: dict) -> dict:
    """Map Codex's PreToolUse payload onto the keys core.hook reads.

    Tolerant of field-name variants across Codex versions (snake_case matches the
    shared output contract; camelCase / nested forms are accepted too) so a schema
    drift degrades to a still-governed call rather than an ungoverned one.
    """
    def pick(*keys):
        for k in keys:
            v = event.get(k)
            if v is not None:
                return v
        return None

    tool_name = pick("tool_name", "toolName", "tool")
    if isinstance(tool_name, dict):  # e.g. {"tool": {"name": ...}}
        tool_name = tool_name.get("name")

    tool_input = pick("tool_input", "toolInput", "arguments", "input", "params")
    if not isinstance(tool_input, dict):
        tool_input = {}

    cwd = pick("cwd", "workspace", "workingDirectory") or os.getcwd()

    return {"tool_name": tool_name, "tool_input": tool_input, "cwd": cwd}


def main() -> None:
    try:
        raw = json.load(sys.stdin)
        if not isinstance(raw, dict):
            raw = {}
    except Exception:
        raw = {}

    root = _repo_root()
    sys.path.insert(0, root)
    from core import hook  # noqa: E402  (import after root is on sys.path)

    out = hook.evaluate(_normalize(raw), root)
    sys.stdout.write(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
