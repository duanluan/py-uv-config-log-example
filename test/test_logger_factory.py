import logging
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

import py7zr

try:
  from _path_setup import add_src_to_path
except ModuleNotFoundError:
  from test._path_setup import add_src_to_path

add_src_to_path()

from common.log.logger_factory import ArchivingTimedRotatingFileHandler, _namer, create_logger


class ArchivingTimedRotatingFileHandlerTest(unittest.TestCase):
  def tearDown(self):
    logger = logging.getLogger('direct_handler_test')
    for handler in list(logger.handlers):
      logger.removeHandler(handler)
      handler.close()

  def test_namer_normalizes_minute_and_hour_rollover_names(self):
    self.assertEqual(
      'app_260608_180300.log',
      Path(_namer('app.log.2026-06-08_18-03')).name,
    )
    self.assertEqual(
      'app_260608_180000.log',
      Path(_namer('app.log.2026-06-08_18')).name,
    )

  def test_parent_backup_count_is_disabled_for_custom_retention(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      handler = ArchivingTimedRotatingFileHandler(
        filename=str(Path(tmp_dir) / 'app.log'),
        backupCount=3,
        compress_backup_count=3,
      )

      try:
        self.assertEqual(3, handler.real_backup_count)
        self.assertEqual(0, handler.backupCount)
      finally:
        handler.close()

  def test_direct_handler_casts_retention_counts_to_int(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      handler = ArchivingTimedRotatingFileHandler(
        filename=str(Path(tmp_dir) / 'app.log'),
        backupCount='-1',
        compress_backup_count='-1',
      )

      try:
        self.assertEqual(-1, handler.real_backup_count)
        self.assertEqual(-1, handler.compress_backup_count)
      finally:
        handler.close()

  def test_close_does_not_run_archival_tasks(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      for archive_name in [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
        'app_260104.7z',
      ]:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=2,
        compress_backup_count=2,
      )

      handler.close()

      archive_names = sorted(path.name for path in log_dir.glob('*.7z'))
      self.assertEqual(
        ['app_260101.7z', 'app_260102.7z', 'app_260103.7z', 'app_260104.7z'],
        archive_names,
      )

  def test_archival_task_cleans_old_archives_when_no_rotated_logs_exist(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      for archive_name in [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
        'app_260104.7z',
      ]:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=2,
        compress_backup_count=2,
      )

      try:
        handler._run_archival_tasks()

        archive_names = sorted(path.name for path in log_dir.glob('*.7z'))
        self.assertEqual(['app_260103.7z', 'app_260104.7z'], archive_names)
      finally:
        handler.close()

  def test_backup_count_zero_keeps_logs_and_archives(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_names = [
        'app_260101.log',
        'app_260102.log',
        'app_260103.log',
        'app_260104.log',
      ]
      archive_names = [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
        'app_260104.7z',
      ]
      for log_name in log_names:
        (log_dir / log_name).write_text('rotated log', encoding='utf-8')
      for archive_name in archive_names:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=0,
        compress_backup_count=2,
      )

      try:
        handler._run_archival_tasks()

        remaining_log_names = sorted(path.name for path in log_dir.glob('app_*.log'))
        remaining_archive_names = sorted(path.name for path in log_dir.glob('*.7z'))
        self.assertEqual(log_names, remaining_log_names)
        self.assertEqual(archive_names, remaining_archive_names)
      finally:
        handler.close()

  def test_negative_backup_count_keeps_logs_and_archives(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_names = [
        'app_260101.log',
        'app_260102.log',
      ]
      archive_names = [
        'app_260101.7z',
        'app_260102.7z',
      ]
      for log_name in log_names:
        (log_dir / log_name).write_text('rotated log', encoding='utf-8')
      for archive_name in archive_names:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=-1,
        compress_backup_count=1,
      )

      try:
        handler._run_archival_tasks()

        self.assertEqual(log_names, sorted(path.name for path in log_dir.glob('app_*.log')))
        self.assertEqual(archive_names, sorted(path.name for path in log_dir.glob('*.7z')))
      finally:
        handler.close()

  def test_backup_count_zero_does_not_recompress_old_logs(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_names = [
        'app_260101.log',
        'app_260102.log',
        'app_260103.log',
      ]
      for log_name in log_names:
        (log_dir / log_name).write_text('rotated log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=0,
        compress_backup_count=1,
        compress_suffix='.zip',
      )

      compressed_logs = []
      original_compress_with_zip = handler._compress_with_zip

      def count_compression(log_file_path, archive_file_path):
        compressed_logs.append(Path(log_file_path).name)
        original_compress_with_zip(log_file_path, archive_file_path)

      try:
        handler._compress_with_zip = count_compression
        handler._run_archival_tasks()
        compressed_logs.clear()

        handler._run_archival_tasks()

        self.assertEqual([], compressed_logs)
      finally:
        handler.close()

  def test_archive_retention_is_raised_to_log_retention_when_logs_are_limited(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      for archive_name in [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
        'app_260104.7z',
      ]:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=3,
        compress_backup_count=2,
      )

      try:
        handler._run_archival_tasks()

        archive_names = sorted(path.name for path in log_dir.glob('*.7z'))
        self.assertEqual(['app_260102.7z', 'app_260103.7z', 'app_260104.7z'], archive_names)
      finally:
        handler.close()

  def test_compress_backup_count_zero_keeps_all_archives(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      expected_archive_names = [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
        'app_260104.7z',
      ]
      for archive_name in expected_archive_names:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=3,
        compress_backup_count=0,
      )

      try:
        handler._run_archival_tasks()

        archive_names = sorted(path.name for path in log_dir.glob('*.7z'))
        self.assertEqual(expected_archive_names, archive_names)
      finally:
        handler.close()

  def test_negative_compress_backup_count_keeps_all_archives(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      expected_archive_names = [
        'app_260101.7z',
        'app_260102.7z',
        'app_260103.7z',
      ]
      for archive_name in expected_archive_names:
        (log_dir / archive_name).write_text('archived log', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=-1,
      )

      try:
        handler._run_archival_tasks()

        self.assertEqual(expected_archive_names, sorted(path.name for path in log_dir.glob('*.7z')))
      finally:
        handler.close()

  def test_empty_zip_archive_does_not_count_as_archived_log(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_file = log_dir / 'app_260101.log'
      archive_file = log_dir / 'app_260101.zip'
      log_file.write_text('original log content', encoding='utf-8')
      with zipfile.ZipFile(archive_file, mode='w'):
        pass

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=1,
        compress_suffix='.zip',
      )

      try:
        self.assertFalse(handler._has_archive(str(log_file)))
      finally:
        handler.close()

  def test_zip_archive_with_different_member_does_not_count_as_archived_log(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_file = log_dir / 'app_260101.log'
      archive_file = log_dir / 'app_260101.zip'
      log_file.write_text('original log content', encoding='utf-8')
      with zipfile.ZipFile(archive_file, mode='w') as archive:
        archive.writestr('another.log', 'other log content')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=1,
        compress_suffix='.zip',
      )

      try:
        self.assertFalse(handler._has_archive(str(log_file)))
      finally:
        handler.close()

  def test_zip_archive_with_matching_member_allows_old_log_cleanup(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      old_log_file = log_dir / 'app_260101.log'
      new_log_file = log_dir / 'app_260102.log'
      old_log_file.write_text('old log content', encoding='utf-8')
      new_log_file.write_text('new log content', encoding='utf-8')
      for log_file in [old_log_file, new_log_file]:
        with zipfile.ZipFile(log_file.with_suffix('.zip'), mode='w') as archive:
          archive.write(log_file, arcname=log_file.name)

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=2,
        compress_suffix='.zip',
      )

      try:
        handler._run_archival_tasks()

        self.assertFalse(old_log_file.exists())
        self.assertTrue(new_log_file.exists())
      finally:
        handler.close()

  def test_7z_archive_must_contain_matching_log_member(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_file = log_dir / 'app_260101.log'
      matching_archive_file = log_dir / 'app_260101.7z'
      wrong_archive_file = log_dir / 'app_260102.7z'
      other_file = log_dir / 'another.log'
      log_file.write_text('original log content', encoding='utf-8')
      other_file.write_text('other log content', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=1,
        compress_suffix='.7z',
      )
      try:
        handler._compress_with_7z(str(log_file), str(matching_archive_file))
        handler._compress_with_7z(str(other_file), str(wrong_archive_file))

        self.assertTrue(handler._has_archive(str(log_file)))
        self.assertFalse(handler._has_archive(str(log_dir / 'app_260102.log')))
      finally:
        handler.close()

  def test_7z_compress_level_zero_creates_copy_archive_with_matching_member(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_file = log_dir / 'app_260101.log'
      archive_file = log_dir / 'app_260101.7z'
      log_file.write_text('original log content', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=1,
        compress_suffix='.7z',
        compress_level=0,
      )
      try:
        handler._compress_with_7z(str(log_file), str(archive_file))

        self.assertTrue(handler._has_archive(str(log_file)))
        with py7zr.SevenZipFile(archive_file, mode='r') as archive:
          self.assertEqual([log_file.name], archive.getnames())
      finally:
        handler.close()

  def test_zip_compress_level_zero_creates_stored_archive_with_matching_member(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      log_file = log_dir / 'app_260101.log'
      archive_file = log_dir / 'app_260101.zip'
      log_file.write_text('original log content', encoding='utf-8')

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=1,
        compress_suffix='.zip',
        compress_level=0,
      )
      try:
        handler._compress_with_zip(str(log_file), str(archive_file))

        self.assertTrue(handler._has_archive(str(log_file)))
        with zipfile.ZipFile(archive_file) as archive:
          self.assertEqual([log_file.name], archive.namelist())
          self.assertEqual(zipfile.ZIP_STORED, archive.getinfo(log_file.name).compress_type)
      finally:
        handler.close()

  def test_direct_handler_rollover_uses_custom_names_and_compresses_logs(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      logger = logging.getLogger('direct_handler_test')
      logger.setLevel(logging.INFO)
      logger.propagate = False
      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        when='S',
        backupCount=2,
        compress_suffix='.zip',
        compress_schedule_cron='',
      )
      logger.addHandler(handler)

      logger.info('first log line')
      time.sleep(1.1)
      logger.info('second log line')
      logger.removeHandler(handler)
      handler.close()

      rotated_logs = sorted(path.name for path in log_dir.glob('app_*.log'))
      archive_names = sorted(path.name for path in log_dir.glob('app_*.zip'))
      self.assertEqual(1, len(rotated_logs))
      self.assertEqual([rotated_logs[0].replace('.log', '.zip')], archive_names)
      self.assertNotIn('app.log.', ''.join(path.name for path in log_dir.iterdir()))

      with zipfile.ZipFile(log_dir / archive_names[0]) as archive:
        self.assertEqual([rotated_logs[0]], archive.namelist())

  def test_repairs_broken_archive_before_retention_deletes_log(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      log_dir = Path(tmp_dir)
      old_log_file = log_dir / 'app_260101.log'
      old_archive_file = log_dir / 'app_260101.zip'
      new_log_file = log_dir / 'app_260102.log'
      new_archive_file = log_dir / 'app_260102.zip'
      old_log_file.write_text('original log content', encoding='utf-8')
      old_archive_file.write_text('not a zip archive', encoding='utf-8')
      new_log_file.write_text('new log content', encoding='utf-8')
      with zipfile.ZipFile(new_archive_file, mode='w') as archive:
        archive.write(new_log_file, arcname=new_log_file.name)

      handler = ArchivingTimedRotatingFileHandler(
        filename=str(log_dir / 'app.log'),
        backupCount=1,
        compress_backup_count=2,
        compress_suffix='.zip',
      )

      try:
        handler._run_archival_tasks()

        self.assertTrue(zipfile.is_zipfile(old_archive_file))
        with zipfile.ZipFile(old_archive_file) as archive:
          self.assertEqual('original log content', archive.read(old_log_file.name).decode('utf-8'))
      finally:
        handler.close()

  def test_create_logger_rejects_unknown_level(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      with self.assertRaisesRegex(ValueError, 'Unsupported log level'):
        create_logger('invalid_level_test', log_file_path=str(Path(tmp_dir) / 'app.log'), level='verbose')


if __name__ == '__main__':
  unittest.main()
