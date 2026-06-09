import logging
import tempfile
import unittest
from pathlib import Path

try:
  from _path_setup import add_src_to_path
except ModuleNotFoundError:
  from test._path_setup import add_src_to_path

add_src_to_path()

from common import app_context


class AppContextTest(unittest.TestCase):
  def tearDown(self):
    app_context.clear()
    for logger_name in ['app_context_test', 'app_context_test_next']:
      logger = logging.getLogger(logger_name)
      for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

  def test_failed_reinit_clears_previous_context(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir) / 'logs'
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text(
        f"""
log:
  path: {log_dir}
  file: app
  compress-schedule-cron: ''
""".strip(),
        encoding='utf-8',
      )

      app_context.init(str(config_file), 'app_context_test')
      self.assertTrue(app_context.is_initialized())

      with self.assertRaises(FileNotFoundError):
        app_context.init(str(Path(tmp_dir) / 'missing.yml'), 'app_context_test')

      self.assertFalse(app_context.is_initialized())

  def test_successful_reinit_closes_previous_logger(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      first_config_file = self._write_config(tmp_dir, 'first')
      second_config_file = self._write_config(tmp_dir, 'second')

      app_context.init(str(first_config_file), 'app_context_test')
      first_logger = logging.getLogger('app_context_test')
      self.assertGreater(len(first_logger.handlers), 0)

      app_context.init(str(second_config_file), 'app_context_test_next')

      self.assertEqual([], first_logger.handlers)

  def test_resolves_log_path_for_runtime_use(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      config_file = Path(tmp_dir) / 'config.yml'
      config_file.write_text(
        """
log:
  path: logs
  file: app
  compress-schedule-cron: ''
""".strip(),
        encoding='utf-8',
      )

      app_context.init(str(config_file), 'app_context_test')

      self.assertTrue(Path(app_context.log_path).is_absolute())
      self.assertEqual((Path.cwd() / 'logs').resolve(), Path(app_context.log_path))

  def _write_config(self, tmp_dir, name):
    config_file = Path(tmp_dir) / f'{name}.yml'
    config_file.write_text(
      f"""
log:
  path: {Path(tmp_dir) / name}
  file: app
  compress-schedule-cron: ''
""".strip(),
      encoding='utf-8',
    )
    return config_file


if __name__ == '__main__':
  unittest.main()
