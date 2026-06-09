# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

This is a Python `src/` layout app. Runtime scope is YAML config loading,
global app context, and rotating archived logs.

There is no API server, frontend, or database layer.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Runtime layout, resources, tests | Active |
| [Database Guidelines](./database-guidelines.md) | No database layer; rules if one is added | Active |
| [Error Handling](./error-handling.md) | Exceptions, cleanup, context lifecycle | Active |
| [Quality Guidelines](./quality-guidelines.md) | Config paths, settings, review checks | Active |
| [Logging Guidelines](./logging-guidelines.md) | Logger setup, log config, archival | Active |

---

## How to Fill These Guidelines

Keep rules short and executable:

1. Preserve Trellis headings.
2. Document real code contracts only.
3. Include config keys, signatures, errors, and tests.
4. Put implementation rules in backend specs.
5. Put thinking triggers in guides.

---

**Language**: All documentation should be written in **English**.
