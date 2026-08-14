#!/usr/bin/env python3
"""Deterministic proof: the Codex PreToolUse adapter drives the SAME core/ gate.

Feeds Codex-shaped PreToolUse events through scripts/pretooluse.py (as a real
subprocess reading stdin, exactly as Codex invokes it) and asserts the emitted
`hookSpecificOutput.permissionDecision`. No network, no model — this pins the
adapter + core integration under Codex's I/O.

The gate LOGIC itself is covered by core/ unit tests and eval/run.py; this file
only proves the Codex edge: field normalization + the fail-closed output shape.

Run: python3 eval/tests/test_codex_adapter.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADAPTER = os.path.join(HERE, "..", "..", "scripts", "pretooluse.py")


def decide(event: dict) -> dict:
    p = subprocess.run(
        [sys.executable, ADAPTER],
        input=json.dumps(event), capture_output=True, text=True,
    )
    assert p.returncode == 0, f"adapter exited {p.returncode}: {p.stderr}"
    out = json.loads(p.stdout)
    return out["hookSpecificOutput"]


# (name, event, expected_decision, why)
CASES = [
    ("committing write is gated (snake_case fields)",
     {"tool_name": "mcp__coupa__submit_purchase_order",
      "tool_input": {"total": 250000, "currency": "USD"}},
     "ask", "a committing PO submit under the default gated dial must pause for a human"),

    ("read passes through",
     {"tool_name": "mcp__coupa__get_purchase_order", "tool_input": {"po": "4500001"}},
     "allow", "a read is never blocked"),

    ("destructive is gated",
     {"tool_name": "mcp__coupa__cancel_purchase_order", "tool_input": {"po": "4500001"}},
     "ask", "cancelling a PO is destructive -> human approval under gated"),

    ("outbound is gated",
     {"tool_name": "mcp__coupa__email_supplier", "tool_input": {"to": "x@y.com"}},
     "ask", "an outbound send under gated needs approval"),

    ("non-connector tool is not governed",
     {"tool_name": "Bash", "tool_input": {"command": "ls"}},
     "allow", "the gate only governs mcp__ connector tools"),

    ("camelCase field variant still classifies",
     {"toolName": "mcp__coupa__submit_purchase_order",
      "toolInput": {"total": 250000, "currency": "USD"}},
     "ask", "Codex field-name drift must degrade to still-governed, not ungoverned"),

    ("empty/garbage event does not crash and is not blocked",
     {},
     "allow", "no tool -> not a governed connector -> allow (never block on our own confusion)"),
]


def main() -> int:
    fails = 0
    for name, event, expected, why in CASES:
        got = decide(event)["permissionDecision"]
        ok = got == expected
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: expected {expected}, got {got}")
        if not ok:
            print(f"         why: {why}")
            fails += 1
    print()
    if fails:
        print(f"FAILED: {fails}/{len(CASES)} cases")
        return 1
    print(f"OK: {len(CASES)}/{len(CASES)} cases — Codex adapter drives core/ correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
