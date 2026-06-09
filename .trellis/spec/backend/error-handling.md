# Error Handling

> How errors are handled in this project.

---

## Overview

Errors are handled at runtime boundaries: config loading, app context init,
logger setup, main loop, and log archival internals.

No API response format exists.

---

## Error Types

| Case | Exception or behavior |
|------|-----------------------|
| Missing explicit config | `FileNotFoundError("Configuration file not found at: <path>")` |
| Invalid YAML | `ValueError("Invalid YAML syntax in: <path>. ...")` |
| Unreadable config | `RuntimeError("Failed to read configuration file: <path>. ...")` |
| YAML root not mapping | `ValueError("Configuration root must be a mapping ...")` |
| Settings validation failure | `ValueError("Invalid configuration at <path>: ...")` |
| Uninitialized proxy access | `RuntimeError("The application context has not been initialized...")` |
| Logger setup failure in context init | `RuntimeError("Failed to set up the logging system: ...")` |
| Unknown logger level | `ValueError("Unsupported log level ...")` |
| Unsupported archive suffix | `ValueError("Unsupported compress_suffix ...")` |
| Invalid compression level | `ValueError("compress_level must be within [0, 9] ...")` |
| Invalid cron | `ValueError("Invalid compress_schedule_cron ...")` |
| APScheduler missing with cron | `RuntimeError("APScheduler is required ...")` |
| py7zr missing for `.7z` archival | Warn once to stderr and skip compression |

---

## Error Handling Patterns

- `load_config_yml()` wraps file, YAML, and Pydantic failures with path-aware
  messages.
- `app_context.init()` clears partial or previous context on failure.
- Inject `config` and `log` only after logger setup succeeds.
- `app_context.clear()` is best effort and always clears proxies and `log_path`.
- Main loop exceptions are logged with stack trace and re-raised.
- Handler internals warn to stderr, not through the same logger.

Correct context init order:

```python
loaded_config = load_config_yml(config_file_path)
clear()
created_logger = create_logger(...)
config.set_instance(loaded_config)
log.set_instance(created_logger)
```

---

## API Error Responses

Not applicable. This project has no API server.

---

## Common Mistakes

- Leaving old `config` or `log` initialized after failed reinit.
- Wrapping missing explicit config paths in generic exceptions.
- Letting CLI args override explicit `load_config_yml()` arguments.
- Assuming environment variables override YAML/default settings.
- Logging archival warnings through the failing logger.

Required tests: failed reinit clears context, successful reinit closes old
handlers, uninitialized proxy raises, missing config reports path, main loop
re-raises, startup logs exclude config values.
