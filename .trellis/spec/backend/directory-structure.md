# Directory Structure

> How backend code is organized in this project.

---

## Overview

`app1` owns the entrypoint and packaged resources. `common` owns reusable
runtime infrastructure: config, context, proxy, and logging.

---

## Directory Layout

```text
src/
|-- app1/
|   |-- app1.py
|   `-- res/config.yml
`-- common/
    |-- app_context.py
    |-- proxy.py
    |-- conf/config.py
    `-- log/logger_factory.py

test/
|-- _path_setup.py
`-- test_*.py
```

---

## Module Organization

- `src/app1/app1.py`: parse CLI, init context, run loop, clear context.
- `src/app1/res/config.yml`: packaged default config.
- `src/common/conf/config.py`: Pydantic settings and YAML loader.
- `src/common/app_context.py`: assemble config/logger and expose proxies.
- `src/common/proxy.py`: `ContextProxy` only.
- `src/common/log/logger_factory.py`: logger factory, rotation, archival.
- `test/_path_setup.py`: test-only `src` path setup.
- Do not put runtime code in `build/`, `dist/`, or `*.egg-info/`.
- Do not mutate `sys.path` in runtime modules.

---

## Naming Conventions

- Modules use lowercase snake case.
- Private helpers use a leading underscore: `_cli_config_path()`, `_namer()`,
  `_run_archival_tasks()`.
- YAML log keys use kebab case: `bak-count`, `compress-level`,
  `compress-suffix`, `compress-schedule-cron`, `compress-bak-count`.
- Python settings fields use snake case with Pydantic aliases.
- Rotated logs use `app_YYMMDD.log` or `app_YYMMDD_HHMMSS.log`.
- Archives use the same base name plus `.7z` or `.zip`.

---

## Examples

- Packaged resource contract: `[tool.setuptools.package-data] app1 = ["res/*.yml"]`.
- Default config loader: `files('app1').joinpath('res/config.yml')`.
- Required tests: packaged default loads, empty path loads default, wheel
  includes `app1/res/config.yml`, explicit historical path does not fall back to
  `src/app1/res/config.yml`.
