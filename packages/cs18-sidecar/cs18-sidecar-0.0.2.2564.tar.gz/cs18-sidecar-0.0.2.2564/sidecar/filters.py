import logging
import os
import platform
import socket


class LoggingFilter(logging.Filter):
    def __init__(self, config_json):
        logging.Filter.__init__(self)
        self.config_json = config_json

    def filter(self, record: logging.LogRecord):
        record.__dict__['colony.application'] = 'sidecar'
        record.__dict__['colony.branch'] = os.getenv('branch', "none")
        record.__dict__['colony.environment'] = self.config_json['environment']
        record.__dict__['colony.hostname'] = self._get_hostname()
        record.__dict__['colony.level'] = record.levelname
        record.__dict__['colony.sandbox_id'] = self.config_json['sandbox_id']
        record.__dict__['colony.threadId'] = record.thread
        record.logger = '{0} {1}'.format(record.filename, record.funcName)
        return record

    @staticmethod
    def _get_hostname():
        n1 = platform.node()
        n2 = socket.gethostname()
        n3 = os.getenv("COMPUTERNAME")
        if n1 == n2 == n3:
            return n1
        elif n1 == n2:
            return n1
        elif n1 == n3:
            return n1
        elif n2 == n3:
            return n2
        else:
            return "local-pc"
