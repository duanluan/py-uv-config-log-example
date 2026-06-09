import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

try:
  from _path_setup import add_src_to_path
except ModuleNotFoundError:
  from test._path_setup import add_src_to_path

add_src_to_path()

from common import app_context
import app1.app1 as app_module


class AppEntrypointTest(unittest.TestCase):
  def tearDown(self):
    app_context.clear()

  def test_cli_config_path_preserves_user_supplied_relative_path(self):
    old_argv = sys.argv[:]
    sys.argv = ['app1', '--config', 'config/app.yml']
    try:
      self.assertEqual('config/app.yml', app_module._cli_config_path())
    finally:
      sys.argv = old_argv

  def test_main_passes_none_to_context_init_without_cli_config(self):
    old_argv = sys.argv[:]
    old_log = app_module.log
    sys.argv = ['app1']
    app_module.log = MagicMock()
    try:
      with patch.object(app_module.app_context, 'init') as init:
        with patch.object(app_module.app_context, 'clear'):
          with patch.object(app_module.time, 'sleep', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
              app_module.main()
      init.assert_called_once_with(None, 'app1')
    finally:
      sys.argv = old_argv
      app_module.log = old_log

  def test_main_passes_cli_config_path_to_context_init(self):
    old_argv = sys.argv[:]
    old_log = app_module.log
    sys.argv = ['app1', '--config', 'config/app.yml']
    app_module.log = MagicMock()
    try:
      with patch.object(app_module.app_context, 'init') as init:
        with patch.object(app_module.app_context, 'clear'):
          with patch.object(app_module.time, 'sleep', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
              app_module.main()
      init.assert_called_once_with('config/app.yml', 'app1')
    finally:
      sys.argv = old_argv
      app_module.log = old_log

  def test_main_honors_cli_config_argument_over_packaged_default(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_path = Path(tmp_dir)
      cli_config_file = tmp_path / 'cli.yml'
      cli_config_file.write_text(
        f"""
log:
  path: {tmp_path / 'cli_logs'}
  file: app
  compress-schedule-cron: ''
""".strip(),
        encoding='utf-8',
      )

      old_argv = sys.argv[:]
      old_sleep = app_module.time.sleep
      sys.argv = ['app1', '--config', str(cli_config_file)]
      app_module.time.sleep = lambda seconds: (_ for _ in ()).throw(KeyboardInterrupt())
      try:
        with self.assertRaises(KeyboardInterrupt):
          app_module.main()
      finally:
        sys.argv = old_argv
        app_module.time.sleep = old_sleep

      self.assertTrue((tmp_path / 'cli_logs' / 'app.log').is_file())

  def test_main_does_not_log_full_configuration(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_path = Path(tmp_dir)
      cli_config_file = tmp_path / 'cli.yml'
      cli_config_file.write_text(
        f"""
log:
  path: {tmp_path / 'logs'}
  file: app
  compress-schedule-cron: ''
custom:
  secret-token: do-not-log
""".strip(),
        encoding='utf-8',
      )

      old_argv = sys.argv[:]
      old_sleep = app_module.time.sleep
      sys.argv = ['app1', '--config', str(cli_config_file)]
      app_module.time.sleep = lambda seconds: (_ for _ in ()).throw(KeyboardInterrupt())
      try:
        with self.assertRaises(KeyboardInterrupt):
          app_module.main()
      finally:
        sys.argv = old_argv
        app_module.time.sleep = old_sleep

      log_text = (tmp_path / 'logs' / 'app.log').read_text(encoding='utf-8')
      self.assertIn('Application started; configuration loaded.', log_text)
      self.assertNotIn('do-not-log', log_text)
      self.assertNotIn('secret-token', log_text)
      self.assertNotIn('AppSettings', log_text)

  def test_main_reraises_unexpected_loop_exception(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_path = Path(tmp_dir)
      cli_config_file = tmp_path / 'cli.yml'
      cli_config_file.write_text(
        f"""
log:
  path: {tmp_path / 'logs'}
  file: app
  compress-schedule-cron: ''
""".strip(),
        encoding='utf-8',
      )

      old_argv = sys.argv[:]
      old_sleep = app_module.time.sleep
      sys.argv = ['app1', '--config', str(cli_config_file)]
      app_module.time.sleep = lambda seconds: (_ for _ in ()).throw(ValueError('boom'))
      try:
        with self.assertRaisesRegex(ValueError, 'boom'):
          app_module.main()
      finally:
        sys.argv = old_argv
        app_module.time.sleep = old_sleep


if __name__ == '__main__':
  unittest.main()
