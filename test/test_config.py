import tempfile
import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch

try:
  from _path_setup import add_src_to_path
except ModuleNotFoundError:
  from test._path_setup import add_src_to_path

add_src_to_path()

from common.conf.config import LogSettings, load_config_yml


class ConfigTest(unittest.TestCase):
  def test_default_config_path_loads_packaged_app_config(self):
    settings = load_config_yml(None)

    self.assertEqual('app1', settings.log.file)

  def test_empty_config_path_loads_packaged_app_config(self):
    settings = load_config_yml('')

    self.assertEqual('app1', settings.log.file)

  def test_log_defaults_ignore_environment_variables(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text('custom:\n  key: value\n', encoding='utf-8')

      with patch.dict('os.environ', {'LOG_PATH': 'env_logs'}):
        settings = load_config_yml(str(config_file))

      self.assertEqual('./logs', settings.log.path)

  def test_explicit_config_path_is_not_overridden_by_cli_argument(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      explicit_config_file = Path(tmp_dir) / 'explicit.yml'
      cli_config_file = Path(tmp_dir) / 'cli.yml'
      explicit_config_file.write_text('log:\n  path: explicit_logs\n', encoding='utf-8')
      cli_config_file.write_text('log:\n  path: cli_logs\n', encoding='utf-8')

      old_argv = sys.argv[:]
      sys.argv = ['test', '--config', str(cli_config_file)]
      try:
        settings = load_config_yml(str(explicit_config_file))
      finally:
        sys.argv = old_argv

      self.assertEqual('explicit_logs', settings.log.path)

  def test_default_config_path_is_not_overridden_by_cli_argument(self):
    old_argv = sys.argv[:]
    sys.argv = ['test', '--config', 'missing.yml']
    try:
      settings = load_config_yml(None)
    finally:
      sys.argv = old_argv

    self.assertEqual('app1', settings.log.file)

  def test_explicit_relative_config_path_loads_from_current_working_directory(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'custom.yml'
      config_file.write_text('log:\n  path: cwd_logs\n', encoding='utf-8')

      old_cwd = Path.cwd()
      try:
        os.chdir(tmp_dir)
        settings = load_config_yml('custom.yml')
      finally:
        os.chdir(old_cwd)

      self.assertEqual('cwd_logs', settings.log.path)

  def test_missing_relative_config_path_reports_config_file_path(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      old_cwd = Path.cwd()
      try:
        os.chdir(tmp_dir)
        missing_config_path = Path('missing.yml').resolve()
        with self.assertRaisesRegex(
          FileNotFoundError,
          f'Configuration file not found at: {missing_config_path}',
        ):
          load_config_yml('missing.yml')
      finally:
        os.chdir(old_cwd)

  def test_explicit_relative_config_path_does_not_fallback_to_src_directory(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      old_cwd = Path.cwd()
      try:
        os.chdir(Path(__file__).resolve().parents[1])
        missing_config_path = Path('app1/res/config.yml').resolve()
        with self.assertRaisesRegex(
          FileNotFoundError,
          f'Configuration file not found at: {missing_config_path}',
        ):
          load_config_yml('app1/res/config.yml')
      finally:
        os.chdir(old_cwd)

  def test_invalid_compress_suffix_reports_configuration_error(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text('log:\n  compress-suffix: 123\n', encoding='utf-8')

      with self.assertRaisesRegex(ValueError, 'Invalid configuration'):
        load_config_yml(str(config_file))

  def test_invalid_log_level_reports_configuration_error(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text('log:\n  level: verbose\n', encoding='utf-8')

      with self.assertRaisesRegex(ValueError, 'Invalid configuration'):
        load_config_yml(str(config_file))

  def test_unknown_log_setting_reports_configuration_error(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text('log:\n  fiel: app\n', encoding='utf-8')

      with self.assertRaisesRegex(ValueError, 'Invalid configuration'):
        load_config_yml(str(config_file))

  def test_log_settings_accept_python_field_names(self):
    settings = LogSettings(
      bak_count=5,
      compress_level=3,
      compress_suffix='zip',
      compress_schedule_cron='',
      compress_bak_count=8,
    )

    self.assertEqual(5, settings.bak_count)
    self.assertEqual(3, settings.compress_level)
    self.assertEqual('.zip', settings.compress_suffix)
    self.assertEqual('', settings.compress_schedule_cron)
    self.assertEqual(8, settings.compress_bak_count)

  def test_log_settings_allow_negative_retention_counts(self):
    settings = LogSettings(
      bak_count=-1,
      compress_bak_count=-1,
    )

    self.assertEqual(-1, settings.bak_count)
    self.assertEqual(-1, settings.compress_bak_count)


if __name__ == '__main__':
  unittest.main()
