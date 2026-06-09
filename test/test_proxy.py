import unittest

try:
  from _path_setup import add_src_to_path
except ModuleNotFoundError:
  from test._path_setup import add_src_to_path

add_src_to_path()

from common.proxy import ContextProxy


class ContextProxyTest(unittest.TestCase):
  def test_proxy_instances_do_not_share_context(self):
    first_proxy = ContextProxy()
    second_proxy = ContextProxy()

    first_proxy.set_instance({'name': 'first'})

    self.assertTrue(first_proxy.is_initialized())
    self.assertFalse(second_proxy.is_initialized())

  def test_get_instance_returns_initialized_context(self):
    proxy = ContextProxy()
    context = {'name': 'context'}

    proxy.set_instance(context)

    self.assertIs(context, proxy.get_instance())

  def test_get_instance_raises_when_context_is_uninitialized(self):
    proxy = ContextProxy()

    with self.assertRaisesRegex(RuntimeError, 'application context has not been initialized'):
      proxy.get_instance()


if __name__ == '__main__':
  unittest.main()
