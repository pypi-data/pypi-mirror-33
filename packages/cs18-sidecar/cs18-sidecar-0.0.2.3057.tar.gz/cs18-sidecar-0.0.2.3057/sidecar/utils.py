import os
import sys

import time

import datetime

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
