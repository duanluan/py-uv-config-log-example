# Logging Guidelines

> How logging is done in this project.

---

## Overview

Use Python `logging`. Create app loggers through `create_logger()`. Each logger
writes to stdout and `ArchivingTimedRotatingFileHandler`; propagation is false.

---

## Log Levels

- Accepted: `notset`, `debug`, `info`, `warn`, `warning`, `error`, `fatal`,
  `critical`.
- Unknown levels are errors, not `info` fallbacks.
- `LogSettings` rejects non-string levels.

---

## Structured Logging

- `log.fmt` is passed to `logging.Formatter`.
- Default format:
  `%(asctime)s %(levelname)s %(module)s.py, line %(lineno)d - %(message)s`.
- File handler encoding is UTF-8.

---

## What to Log

- Startup: `Application started; configuration loaded.`
- Progress counters or operational status in long-running loops.
- Unexpected loop exceptions with stack traces, then re-raise.

---

## What NOT to Log

- Do not log `AppSettings` at startup.
- Do not log full config mappings.
- Do not log arbitrary top-level config sections.

---

## Scenario: Rotated Log Archival

### 1. Scope / Trigger

Any change to logger factory, log config validation, rollover naming,
compression, scheduler, or retention.

### 2. Signatures

- `create_logger(logger_name, log_file_path='app.log', level='info', ...)`
- `ArchivingTimedRotatingFileHandler`
- `_namer(name)`
- `_has_archive(log_file_path)`
- `_run_archival_tasks()`
- Config keys: `bak-count`, `compress-level`, `compress-suffix`,
  `compress-schedule-cron`, `compress-bak-count`

### 3. Contracts

- Build new handlers before removing old handlers.
- Restore old logger state if handler swap fails.
- Close old handlers only after successful swap.
- `compress-level` is `0..9`.
- `compress-suffix` normalizes `zip`/`.zip`/`7z`/`.7z`; only `.zip` and `.7z`
  are supported.
- Empty `compress-schedule-cron` disables scheduler; non-empty must parse as
  crontab.
- Rotated logs match `app_YYMMDD.log` or `app_YYMMDD_HHMMSS.log`.
- Archive validity requires the exact rotated log basename as a member.
- `.zip` validation uses `ZipFile.namelist()`.
- `.7z` validation uses `SevenZipFile.getnames()`.
- Delete rotated logs only after `_has_archive(log_file_path)` is true.
- Create archives through temp file, validate, then replace.
- `close()` stops scheduler and closes resources only.
- If `compress-bak-count < bak-count` and both are positive, keep at least
  `bak-count` archives.

### Review Rule: `bak-count <= 0` Archive Retention

When `bak-count <= 0`, keep rotated logs and compressed archives. Do not let
`compress-bak-count` delete archives in this state.

### 4. Validation & Error Matrix

| Case | Behavior |
|------|----------|
| Unknown level | `ValueError` |
| Unsupported suffix | `ValueError` |
| Empty or wrong-member archive | Not valid |
| Matching basename in archive | Valid |
| Archive creation fails | Keep source log and warn to stderr |
| `bak-count <= 0` | Keep logs and archives |
| `compress-bak-count <= 0` | Keep archives |
| `close()` with old archives | No archival maintenance |

### 5. Good/Base/Bad Cases

- Good: `app_260101.zip` contains `app_260101.log`.
- Good: `app_260101.7z` contains `app_260101.log`.
- Bad: archive contains `logs/app_260101.log`.
- Bad: delete source log before archive validation.
- Bad: run compression from `close()`.

### 6. Tests Required

- Unknown log level is rejected.
- Invalid level and suffix report configuration errors.
- Negative retention counts are accepted.
- Empty cron disables scheduler and rollover compresses.
- Rollover uses custom names and matching archives.
- Empty archive and wrong-member archive are invalid.
- `.zip` and `.7z` require matching basename members.
- Broken archive repairs before source log cleanup.
- `bak-count <= 0` keeps logs and archives and avoids repeated recompression.
- `compress-bak-count <= 0` keeps archives.
- Archive retention is raised to log retention when needed.
- `close()` does not run archival maintenance.

### 7. Wrong vs Correct

#### Wrong

Treat `zipfile.is_zipfile(path)` alone as archive validity.

#### Correct

Open the archive and require the exact rotated log basename in the member list.
