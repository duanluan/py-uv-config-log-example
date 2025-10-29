# py-uv-config-log-example

[English](./README.md) | [简体中文](./README_CN.md)

[uv](https://docs.astral.sh/uv/) 管理依赖，使用 [PyYAML](https://pyyaml.org/) 从 yml 读取配置，自定义 [logging](https://docs.python.org/3/library/logging.html) 生成日志，使用 [APScheduler](https://apscheduler.readthedocs.io/) 和 [py7zr](https://py7zr.readthedocs.io/) 定时压缩归档日志。

# 在 PyCharm 中使用

- 在项目视图中右键`src`目录，选择`将目标标记为` -> `源代码根目录`，以支持在代码中直接使用`src`下的模块。
- 如果使用`module`方式运行，修改形参为`app1.app1`，工作目录为项目目录。

# 命令

```shell
# 当前目录创建虚拟环境
uv venv

# --- 激活虚拟环境 ---
# Windows
.venv\Scripts\activate.bat
# Linux / MacOS
source .venv/bin/activate

# --- 退出虚拟环境 ---
# Windows
.venv\Scripts\deactivate.bat
# Linux / MacOS
deactivate

# 以可编辑模式安装当前目录下的项目
uv pip install -e .
# 在 uv 虚拟环境中，以脚本方式运行 app1.app1 模块
uv run python -m app1.app1
```

# 打包

**首次构建**：

- `-F`单文件，`-D`单目录
- `-n`exe 文件名
- `--add-data`添加资源文件
- `-p`添加指定路径到模块搜索路径（sys.path）

```shell
pyinstaller -n app1 -D --add-data "src/app1/res;res" -p src src/app1/app1.py
```

**通过 .spec 文件构建**：

- `--noconfirm`无需确认是否覆盖上次构建的文件

```bash
pyinstaller app1.spec --noconfirm
```

**运行 EXE**：

```shell
app1.exe --config _internal\res\config.yml
```
