---
description: Show and verify the tamper-evident audit log of gated/executed actions.
---

Show what the harness has gated or executed this session, and verify the log hasn't been altered.

Run:
`python3 "<plugin_dir>/scripts/scm_audit.py"`

Then summarize for the user: the recent actions (what, decision, and why it was allowed/asked/denied),
and whether the hash chain verified. If the chain is BROKEN, treat it as a security event — say which
entry failed and that the log was altered after the fact; do not gloss over it.

> **Path resolution:** `<plugin_dir>` is this plugin's install directory; run the helper with your Python 3 interpreter (`python3`, or `python` on Windows). Python 3 is required for the safety gate to run.
