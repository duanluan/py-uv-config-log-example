# py-uv-config-log-example

[English](./README.md) | [简体中文](./README_CN.md)

Use [uv](https://www.google.com/search?q=https.docs.astral.sh/uv/) to manage dependencies, read configuration from a YAML file using [PyYAML](https://pyyaml.org/), customize [logging](https://docs.python.org/3/library/logging.html) to generate logs, and use [APScheduler](https://apscheduler.readthedocs.io/) and [py7zr](https://py7zr.readthedocs.io/) to periodically compress and archive logs.

# Command

```shell
# Create a virtual environment in the current directory
uv venv
# Activate the virtual environment (Windows)
.venv\Scripts\activate.bat
# Deactivate the virtual environment (Windows)
.venv\Scripts\deactivate.bat

# Install dependencies
uv pip install -e .

# Start the application
uv run -m src.main.setup
```

# Packaging EXE

**Initial Build**:

  * `-F` Single-file executable, `-D` Single-directory executable
  * `-n` Specifies the name of the exe file
  * `--add-data` Adds resource files

<!-- end list -->

```bash
pyinstaller -D src/main/setup.py -n main --add-data "res;res"
```

**Build Using a .spec File**:

  * `--noconfirm` No need to confirm whether to overwrite the last built file

<!-- end list -->

```bash
pyinstaller main.spec --noconfirm
```
