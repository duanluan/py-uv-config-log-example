# py-uv-config-log-example

[English](./README.md) | [简体中文](./README_CN.md)

[uv](https://docs.astral.sh/uv/) 管理依赖，使用 [PyYAML](https://pyyaml.org/) 从 yml 读取配置，自定义 [logging](https://docs.python.org/3/library/logging.html) 生成日志，使用 [APScheduler](https://apscheduler.readthedocs.io/) 和 [py7zr](https://py7zr.readthedocs.io/) 定时压缩归档日志。

# 命令

```shell
# 当前目录创建虚拟环境
uv venv
# 激活虚拟环境（Windows）
.venv\Scripts\activate.bat
# 退出虚拟环境（Windows）
.venv\Scripts\deactivate.bat

# 安装依赖
uv pip install -e .

# 启动
uv run -m src.main.setup
```

# 打包

**首次构建**：

* `-F`单文件，`-D`单目录
* `-n`exe 文件名
* `--add-data`添加资源文件

```bash
pyinstaller -D src/main/setup.py -n main --add-data "res;res"
```

**通过 .spec 文件构建**：

* `--noconfirm`无需确认是否覆盖上次构建的文件

```bash
pyinstaller main.spec --noconfirm
```
