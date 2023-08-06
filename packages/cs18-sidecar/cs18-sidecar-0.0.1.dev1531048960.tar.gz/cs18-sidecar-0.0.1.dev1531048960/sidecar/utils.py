import os
import sys

import time

import datetime
from logging import Logger

from sidecar.const import Const


class Utils:
    @staticmethod
    def stop_on_debug():
        while not sys.gettrace():
            time.sleep(0.5)

    @staticmethod
    def read_log(app_name: str) -> str:
        file_path = Const.get_app_log_file(app_name)
        with open(file_path, 'r') as application_log:
            return application_log.read()

    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def wait_for(func, interval_sec: int = 10, max_retries: int = 10, error: str = "", silent: bool = False):
        current_retry = 0
        while current_retry < max_retries:
            try:
                if func():
                    return
                else:
                    if not silent:
                        print('re-try {} out of {}'.format(current_retry, max_retries))
                    time.sleep(interval_sec)
                    current_retry += 1
                    if current_retry >= max_retries:
                        raise Exception('max retries for wait_for is exhausted with message: {}'.format(error))
            except Exception as e:
                raise Exception('wait_for function exited due to an exception: {}'.format(e))

    @staticmethod
    def retry_on_exception(func,
                           logger: Logger = None,
                           logger_msg: str = "",
                           interval: int = 1,
                           timeout: int = 10):
        remains = timeout / interval
        while True:
            try:
                return func()
            except Exception as e:
                if remains == 0:
                    raise e
                else:
                    if logger:
                        logger.info("{} ({} remaining attempts)".format(logger_msg, remains))
                remains -= 1
                time.sleep(interval)
