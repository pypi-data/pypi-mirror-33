import threading
from abc import ABCMeta, abstractmethod
from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.const import AppInstanceConfigStatus
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class IStatusUpdater:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 sandbox_start_time_updater: ISandboxStartTimeUpdater):
        self._logger = logger
        self._apps_configuration_end_tracker = apps_configuration_end_tracker
        self._sandbox_start_time_updater = sandbox_start_time_updater
        self._lock = threading.RLock()

    def update_status(self, name: str, ip_address: str, additional_data: {}, status: str):
        with self._lock:
            # if AppInstanceConfigStatus.is_end_status(status):
            #     # since now "update status" is exposed by the api, need to protect against attempts to set
            #     # app instance's configuration end status after it was already set
            #     current_status = self._do_get_status(name, ip_address=ip_address,
            #                                          additional_data=additional_data)
            #     if AppInstanceConfigStatus.is_end_status(current_status):
            #         self._logger.warning("update configuration end status to '{STATUS}' was called for '{APP_NAME}' "
            #                              "after it is already set to '{CURRENT_STATUS}'"
            #                           .format(STATUS=status, APP_NAME=name, CURRENT_STATUS=current_status))
            #         return

            self._do_update_status(name=name, ip_address=ip_address,
                                   additional_data=additional_data, status=status)
            self._apps_configuration_end_tracker.update_app_instance_config_status(app_name=name,
                                                                                   app_instance_config_status=status)
            self._sandbox_start_time_updater.on_app_instance_configuration_status_updated()

    @abstractmethod
    def _do_update_status(self, name: str, ip_address: str, additional_data: {}, status: str):
        raise NotImplementedError

    @abstractmethod
    def _do_get_status(self, name: str, ip_address: str, additional_data: {}) -> str:
        raise NotImplementedError
