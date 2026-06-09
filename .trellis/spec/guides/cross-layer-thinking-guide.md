# Cross-Layer Thinking Guide

> **Purpose**: Think through data flow across layers before implementing.

---

## The Problem

This project has no API, frontend, or database layer. Bugs usually happen across
CLI, config, context, logger, and filesystem boundaries.

---

## Before Implementing Cross-Layer Features

### Step 1: Map the Data Flow

```text
CLI --config
-> app1.app1._cli_config_path()
-> common.conf.config.load_config_yml()
-> common.app_context.init()
-> common.log.logger_factory.create_logger()
-> ArchivingTimedRotatingFileHandler
```

### Step 2: Identify Boundaries

| Boundary | Check |
|----------|-------|
| CLI -> loader | Raw path stays raw until loader |
| YAML -> settings | Validation and aliases are explicit |
| settings -> context | Proxies set only after logger succeeds |
| logger -> files | Relative log path is resolved for runtime |
| rotated log -> archive | Source deletion waits for archive validation |

### Step 3: Define Contracts

For each touched boundary, define input, output, errors, and required tests in
the matching backend spec.

---

## Common Cross-Layer Mistakes

### Mistake 1: Implicit Format Assumptions

Assuming CLI paths, resource paths, and log paths resolve from the same base.

### Mistake 2: Scattered Validation

Validating config keys outside Pydantic settings.

### Mistake 3: Leaky Abstractions

Accessing `ContextProxy._instance` or logging full config objects.

---

## Checklist for Cross-Layer Features

Before implementation:

- [ ] Does the entrypoint still pass raw CLI strings?
- [ ] Does the loader still ignore `sys.argv`?
- [ ] Are arbitrary top-level YAML sections excluded from startup logs?
- [ ] Does failed init leave proxies uninitialized?
- [ ] Does archive validation happen before source log deletion?
- [ ] Does packaged config still work from a built wheel?

After implementation:

- [ ] Updated backend specs for changed contracts.
- [ ] Added or updated boundary tests.

---

## When to Create Flow Documentation

Only create extra flow docs if a future feature adds API, database, frontend, or
another runtime boundary.
