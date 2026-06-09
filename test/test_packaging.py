import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PackagingTest(unittest.TestCase):
  def test_built_wheel_includes_default_app_config(self):
    with tempfile.TemporaryDirectory() as tmp_dir:
      result = subprocess.run(
        ['uv', 'build', '--wheel', '--out-dir', tmp_dir],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
      )
      self.assertEqual(0, result.returncode, result.stdout + result.stderr)

      wheel_path = next(Path(tmp_dir).glob('*.whl'))
      with zipfile.ZipFile(wheel_path) as wheel:
        self.assertIn('app1/res/config.yml', wheel.namelist())


if __name__ == '__main__':
  unittest.main()
