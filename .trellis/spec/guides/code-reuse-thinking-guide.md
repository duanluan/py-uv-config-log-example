# Code Reuse Thinking Guide

> **Purpose**: Stop and think before creating new code - does it already exist?

---

## The Problem

Duplicate runtime rules cause config, context, and logging behavior to drift.

---

## Before Writing New Code

### Step 1: Search First

```bash
rg "load_config_yml|_cli_config_path|ContextProxy"
rg "bak-count|compress-bak-count|_run_archival_tasks|_has_archive"
rg "package-data|app1/res/config.yml|importlib.resources"
```

### Step 2: Ask These Questions

| Question | If Yes... |
|----------|-----------|
| Does the behavior already exist? | Use or extend it |
| Is a config key already modeled? | Update the existing Pydantic model |
| Is a logger rule already tested? | Add to existing logger tests |
| Is this only test path setup? | Keep it in `test/_path_setup.py` |

---

## Common Duplication Patterns

### Pattern 1: Copy-Paste Functions

Do not duplicate config path, archive validation, or context proxy logic.

### Pattern 2: Similar Components

Not applicable today; no frontend component layer exists.

### Pattern 3: Repeated Constants

Do not repeat log key names, archive suffixes, or level names without searching.

---

## When to Abstract

Abstract only when two or more callers need the same nontrivial runtime logic.

---

## After Batch Modifications

Search for old names, old config keys, and stale tests before finishing.

---

## Gotcha: Asymmetric Mechanisms Producing Same Output

If package resources move, update both runtime loading and packaging metadata.
Wheel tests must prove `app1/res/config.yml` is included.

---

## Checklist Before Commit

- [ ] Searched for existing behavior.
- [ ] Kept runtime rules in one module.
- [ ] Updated backend specs for contract changes.
- [ ] Ran relevant tests.
