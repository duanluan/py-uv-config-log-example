from importlib.resources import files
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, ValidationError, field_validator

import yaml

VALID_LOG_LEVELS = {
  'notset',
  'debug',
  'info',
  'warn',
  'warning',
  'error',
  'fatal',
  'critical',
}


class LogSettings(BaseSettings):
  """
  Represents the logging configuration settings for the application.
  表示应用程序的日志配置设置
  """
  model_config = ConfigDict(extra='forbid', populate_by_name=True)

  @classmethod
  def settings_customise_sources(
    cls,
    settings_cls,
    init_settings,
    env_settings,
    dotenv_settings,
    file_secret_settings,
  ):
    return (init_settings,)

  path: str = "./logs"
  file: str = "app"
  level: str = "info"
  fmt: str = "%(asctime)s %(levelname)s %(module)s.py, line %(lineno)d - %(message)s"
  when: str = "midnight"
  # Use an alias to allow kebab-case in the YAML file (e.g., 'bak-count').
  # 使用别名以允许在 YAML 文件中使用 kebab-case (例如, 'bak-count')。
  bak_count: int = Field(alias="bak-count", default=30)
  compress_level: int = Field(alias="compress-level", default=9, ge=0, le=9)
  compress_suffix: str = Field(alias="compress-suffix", default=".7z")
  compress_schedule_cron: str = Field(alias="compress-schedule-cron", default="0 1 * * *")
  # Archive retention count. If smaller than bak_count, effective retention is raised to bak_count to avoid repeated recompression.
  # 压缩归档保留数量。若小于 bak_count，为避免重复压缩，实际保留数会提升到 bak_count。
  compress_bak_count: int = Field(alias="compress-bak-count", default=90)

  @field_validator('level', mode='before')
  @classmethod
  def normalize_level(cls, value):
    """
    Normalize log level names and reject unknown values.
    规范化日志级别名称，并拒绝未知值。
    """
    if value is None:
      return 'info'
    if not isinstance(value, str):
      raise ValueError(f"level must be a string, got {type(value).__name__}")

    level = value.strip().lower()
    if level not in VALID_LOG_LEVELS:
      supported = ', '.join(sorted(VALID_LOG_LEVELS))
      raise ValueError(f"Unsupported log level '{value}'. Supported values: {supported}")
    return level

  @field_validator('compress_suffix', mode='before')
  @classmethod
  def normalize_compress_suffix(cls, value):
    """
    Accept both 'zip' and '.zip' styles, normalize to '.zip' / '.7z'.
    同时接受 'zip' 和 '.zip' 写法，统一规范为 '.zip' / '.7z'。
    """
    if value is None:
      return '.7z'
    if not isinstance(value, str):
      raise ValueError(f"compress-suffix must be a string, got {type(value).__name__}")

    suffix = value.strip().lower()
    if not suffix:
      return '.7z'
    if not suffix.startswith('.'):
      suffix = f'.{suffix}'
    return suffix

  @field_validator('compress_schedule_cron', mode='before')
  @classmethod
  def normalize_compress_schedule_cron(cls, value):
    """
    Normalize cron string and keep empty value as "disabled scheduler".
    规范化 cron 字符串，并保留空值用于“禁用定时压缩”。
    """
    if value is None:
      return ''
    if not isinstance(value, str):
      raise ValueError(
        f"compress-schedule-cron must be a string, got {type(value).__name__}"
      )
    return value.strip()


class AppSettings(BaseSettings):
  """
  Defines the main application settings, aggregating other settings models.
  定义主应用程序设置，聚合其他设置模型。
  """
  # By setting model_config, we allow extra fields that are not explicitly defined in the model. This enables loading of any top-level keys from the config.yml file, such as 'log' and other custom sections (e.g., 'database').
  # 通过设置 model_config，我们允许模型中未明确定义的额外字段。这使得可以从 config.yml 文件加载任何顶级键，例如 'log' 和其他自定义部分 (例如, 'database')。
  model_config = ConfigDict(extra='allow')

  @classmethod
  def settings_customise_sources(
    cls,
    settings_cls,
    init_settings,
    env_settings,
    dotenv_settings,
    file_secret_settings,
  ):
    return (init_settings,)

  # Use default_factory to avoid shared mutable defaults in model field definitions.
  # 使用 default_factory 避免模型字段默认值的共享实例问题。
  log: LogSettings = Field(default_factory=LogSettings)


def find_project_root(marker_file: str = 'pyproject.toml') -> Path:
  """
  Searches upwards from the current file's directory to find the project root.
  从当前文件所在目录向上搜索以查找项目根目录。
  :param marker_file: The name of the file to look for to identify the root. Defaults to 'pyproject.toml'. 用于识别根目录的文件名。默认为 'pyproject.toml'。
  :return: A Path object representing the project's root directory. 代表项目根目录的 Path 对象。
  :raises FileNotFoundError: If the project root cannot be determined by traversing up from the current file path. 如果从当前文件路径向上遍历无法确定项目根目录。
  """
  current_path = Path(__file__).resolve()
  # The loop should terminate when we reach the filesystem root, where  current_path.parent is the same as current_path.
  # 当我们到达文件系统根目录时，循环应该终止，此时 current_path.parent 与 current_path 相同。
  while current_path.parent != current_path:
    if (current_path / marker_file).is_file():
      return current_path
    current_path = current_path.parent
  # A final check in case the script is run from the project root itself.
  # 最后检查一下，以防脚本本身就是从项目根目录运行的。
  if (current_path / marker_file).is_file():
    return current_path
  raise FileNotFoundError(f"Project root with '{marker_file}' not found.")


def load_config_yml(config_file_path: Optional[str] = None) -> AppSettings:
  """
  Loads a YAML configuration file and parses it into an AppSettings object. Explicit relative paths are resolved from the current working directory. If no path is provided, the packaged app config is loaded.
  加载 YAML 配置文件并将其解析为 AppSettings 对象。显式传入的相对路径按当前工作目录解析。如果没有提供路径，则加载打包的应用配置。

  :param config_file_path: Explicit path to the config file. Relative paths are resolved from the current working directory. 配置文件的显式路径。相对路径按当前工作目录解析。
  :return: An AppSettings object populated with the loaded configuration. 一个填充了已加载配置的 AppSettings 对象。
  :raises FileNotFoundError: If the configuration file cannot be found at the determined path. 如果在确定的路径下找不到配置文件。
  :raises Exception: If there is an error reading or parsing the YAML file. 如果读取或解析 YAML 文件时出错。
  """
  # Determine the absolute path of the configuration file.
  # 确定配置文件的绝对路径。
  if config_file_path:
    config_file_abs_path = Path(config_file_path).expanduser().resolve()
  else:
    config_file_abs_path = files('app1').joinpath('res/config.yml')

  try:
    # Read and parse the YAML configuration file.
    # 读取并解析 YAML 配置文件。
    with config_file_abs_path.open('r', encoding='utf-8') as file_path:
      # Use yaml.safe_load for security against arbitrary code execution.
      # 使用 yaml.safe_load 以防止任意代码执行，增强安全性。
      full_config = yaml.safe_load(file_path)
      if full_config is None:
        full_config = {}
  except FileNotFoundError as e:
    raise FileNotFoundError(f"Configuration file not found at: {config_file_abs_path}") from e
  except yaml.YAMLError as e:
    raise ValueError(f"Invalid YAML syntax in: {config_file_abs_path}. {e}") from e
  except OSError as e:
    raise RuntimeError(f"Failed to read configuration file: {config_file_abs_path}. {e}") from e

  if not isinstance(full_config, dict):
    raise ValueError(
      f"Configuration root must be a mapping (YAML object), got: {type(full_config).__name__}."
    )

  try:
    return AppSettings.model_validate(full_config)
  except ValidationError as e:
    raise ValueError(f"Invalid configuration at {config_file_abs_path}: {e}") from e
