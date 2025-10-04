# py-uv-config-log-example

[English](./README.md) | [简体中文](./README_CN.md)

Use [uv](https://www.google.com/search?q=https.docs.astral.sh/uv/) to manage dependencies, read configuration from a YAML file using [PyYAML](https://pyyaml.org/), customize [logging](https://docs.python.org/3/library/logging.html) to generate logs, and use [APScheduler](https://apscheduler.readthedocs.io/) and [py7zr](https://py7zr.readthedocs.io/) to periodically compress and archive logs.

# Usage in PyCharm

- In the Project view, right-click the `src` directory and select `Mark Directory as` -> `Sources Root`. This allows for direct imports of modules located under `src`.
- If running as a module, set the 'Module name' to `app1.app1` and the 'Working directory' to the project's root directory.

# Command

```shell
# Create a virtual environment in the current directory
uv venv
# Activate the virtual environment (Windows)
.venv\Scripts\activate.bat
# Deactivate the virtual environment (Windows)
.venv\Scripts\deactivate.bat

# Install the project in the current directory in editable mode
uv pip install -e .
# Execute the 'app1.app1' module as a script within the uv-managed environment
uv run python -m app1.app1
```

# Packaging EXE

**Initial Build**:

- `-F` Single-file executable, `-D` Single-directory executable
- `-n` Specifies the name of the exe file
- `--add-data` Adds resource files
- `-p` Add the specified path to the module search path (sys.path)

```shell
pyinstaller -n app1 -D --add-data "src/app1/res;res" -p src src/app1/app1.py
```

**Build Using a .spec File**:

- `--noconfirm` No need to confirm whether to overwrite the last built file

```shell
pyinstaller app1.spec --noconfirm
```

**Run the EXE**:

```shell
app1.exe --config _internal\res\config.yml
```
