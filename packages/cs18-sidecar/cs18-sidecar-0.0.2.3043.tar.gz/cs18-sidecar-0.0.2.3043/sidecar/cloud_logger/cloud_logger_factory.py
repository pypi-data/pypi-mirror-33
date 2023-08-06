import importlib
import pkgutil
from inspect import getmembers, isclass, isabstract
from .. import cloud_logger
from . import ICloudLogger, DummyLogger


class CloudLoggerFactory(object):
    def __init__(self, config: dict):
        self.config = config
        self.logger = None
        provider = config["provider"]
        for path, pkg_name, is_package in pkgutil.iter_modules(cloud_logger.__path__):
            if is_package and pkg_name == provider:
                pkg = importlib.import_module(".{}".format(pkg_name), package=cloud_logger.__name__)
                classes = getmembers(pkg, lambda m: isclass(m) and not isabstract(m) and issubclass(m, ICloudLogger))
                if len(classes) > 0:
                    self.logger = classes[0][1]
                break

    def create_instance(self):
        if self.logger is not None:
            return self.logger(self.config)
        else:
            return DummyLogger(self.config)
