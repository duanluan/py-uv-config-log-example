import argparse
import time

from common import app_context
from common.app_context import log


def _cli_config_path():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--config', type=str)
  args, _ = parser.parse_known_args()
  if not args.config:
    return None
  return args.config


def main():
  # Initialize the app context, loading config and setting up the logger.
  # 初始化应用上下文，加载配置并设置日志记录器。
  app_context.init(_cli_config_path(), "app1")

  try:
    # Log startup state without dumping configuration values.
    # 记录启动状态，不输出配置内容。
    log.info('Application started; configuration loaded.')

    # Main loop to keep the application running for background tasks.
    # 主循环使应用保持运行以执行后台任务。
    count = 0
    while True:
      count += 1
      log.info(f"This is a continuous log message, count: {count}")
      # 0.5-second interval, as logs will be split at least every second
      # 0.5 秒间隔，因为日志最短会每秒拆分一次
      time.sleep(0.5)
  except Exception:
    # Log any unexpected exceptions in the main loop.
    # 记录主循环中的任何意外异常。
    log.exception('An unexpected error occurred in the main loop.')
    raise
  finally:
    app_context.clear()


if __name__ == '__main__':
  main()
