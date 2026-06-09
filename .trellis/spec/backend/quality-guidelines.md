# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

Quality rules protect config path behavior, Pydantic settings, context access,
and tested runtime boundaries.

---

## Forbidden Patterns

- Do not add compatibility paths for old layouts.
- Do not inspect `sys.argv` inside `load_config_yml()`.
- Do not resolve CLI config paths in the entrypoint.
- Do not access `ContextProxy._instance` outside `ContextProxy`.
- Do not let cleanup methods perform slow maintenance unless named for it.

### Don't: Resolve CLI Config Before Loading

```python
# Don't do this in the entrypoint.
return str(Path(args.config).expanduser().resolve())
```

Use:

```python
return args.config
```

---

## Required Patterns

- `_cli_config_path()` returns the raw user string.
- `load_config_yml()` owns config path resolution.
- Explicit config paths resolve from current working directory.
- Falsey config paths load packaged `app1/res/config.yml`.
- `LogSettings.model_config`: `extra='forbid'`, `populate_by_name=True`.
- `AppSettings.model_config`: `extra='allow'`.
- Settings sources return only `(init_settings,)`; env, dotenv, and secrets do
  not override config.
- Unknown keys under `log` are invalid.
- Unknown top-level keys are allowed but must not be logged at startup.

## Scenario: Configuration Path Loading

### 1. Scope / Trigger

Any change to CLI config parsing, config loading, packaged defaults, or config
path documentation.

### 2. Signatures

- `_cli_config_path() -> str | None`
- `load_config_yml(config_file_path: Optional[str] = None) -> AppSettings`
- CLI option: `--config <path>`

### 3. Contracts

- Entrypoint passes CLI path unchanged.
- `load_config_yml()` ignores `sys.argv`.
- Truthy explicit paths expand `~` and resolve from current working directory.
- Falsey paths load packaged `app1/res/config.yml`.
- No fallback to `src/app1/res/config.yml`.

### 4. Validation & Error Matrix

| Case | Behavior |
|------|----------|
| `--config config/app.yml` | Entrypoint passes `config/app.yml` |
| `load_config_yml('custom.yml')` after `chdir(tmp)` | Loads `<tmp>/custom.yml` |
| `load_config_yml(None)` | Loads packaged default |
| `load_config_yml('')` | Loads packaged default |
| `sys.argv --config missing.yml` with `load_config_yml(None)` | Loads packaged default |
| `load_config_yml('app1/res/config.yml')` from project root | Raises unless exact path exists |

### 5. Good/Base/Bad Cases

- Good: pass raw CLI path to `app_context.init()`.
- Base: empty YAML loads defaults.
- Bad: read CLI args in `load_config_yml()`.
- Bad: search `src/` for compatibility.

### 6. Tests Required

- CLI helper preserves relative path string.
- Explicit relative path loads from current working directory.
- Explicit path is not overridden by CLI args.
- Packaged default is not overridden by CLI args.
- Missing explicit path reports resolved path.
- Historical relative path does not fall back to `src/`.
- Log defaults ignore environment variables.
- Unknown log setting reports configuration error.
- Python field names are accepted for `LogSettings`.

### 7. Wrong vs Correct

#### Wrong

```python
if not config_file_path:
  config_file_path = _read_config_from_sys_argv()
```

#### Correct

```python
if config_file_path:
  config_file_abs_path = Path(config_file_path).expanduser().resolve()
else:
  config_file_abs_path = files('app1').joinpath('res/config.yml')
```

## Testing Requirements

- Path and context changes need success and failure tests.
- Settings changes need validation tests.
- Handler lifecycle changes need cleanup vs maintenance tests.

## Code Review Checklist

- Config path behavior stays in `load_config_yml()`.
- Context access uses public proxy methods.
- Startup logs do not include config objects or arbitrary config sections.
- Specs changed when runtime contracts changed.
