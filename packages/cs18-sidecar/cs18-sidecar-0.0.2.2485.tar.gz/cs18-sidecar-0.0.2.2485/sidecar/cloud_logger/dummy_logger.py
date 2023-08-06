import os
from sidecar.const import Const
from . import ICloudLogger, LogEntry


class DummyLogger(ICloudLogger):
    def __init__(self, config: dict):
        apps = config.get("apps")
        for app_name in apps:
            app_folder = Const.get_app_folder(app_name)
            if not os.path.exists(app_folder):
                os.mkdir(app_folder)

    def write(self, log_entry: LogEntry):
        app_folder = Const.get_app_folder(log_entry.app)

        filename = "{0}/{1}.{2}.log".format(app_folder, log_entry.instance.replace("docker://", ""), log_entry.topic)
        lines = [line + "\n" for time, line in log_entry.log_events]
        with open(filename, "at") as stream:
            stream.writelines(lines)
