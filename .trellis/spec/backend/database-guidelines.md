# Database Guidelines

> Database patterns and conventions for this project.

---

## Overview

This project has no database layer.

No ORM, query builder, migrations, schema files, connection pool, repository
layer, or database runtime contract exists.

---

## Query Patterns

No query patterns exist.

If database access is added later:

- Add the dependency to `pyproject.toml`.
- Add typed settings in `src/common/conf/config.py`.
- Initialize outside `app1.app1`.
- Add tests for validation, missing credentials, failed init, and cleanup.

---

## Migrations

No migrations exist.

If migrations are introduced, document:

- command signatures
- directory layout
- revision naming
- rollback policy
- required tests

---

## Naming Conventions

No table, column, index, or constraint naming conventions exist yet.

Do not invent database naming rules before adding an actual database
implementation.

---

## Common Mistakes

- Treating top-level YAML keys such as `database` as active runtime config.
- Assuming `AppSettings(extra='allow')` means unknown sections are consumed.
- Logging full config mappings after adding connection-like data.
