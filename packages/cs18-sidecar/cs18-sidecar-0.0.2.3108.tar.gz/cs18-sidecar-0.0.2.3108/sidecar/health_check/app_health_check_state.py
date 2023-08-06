import threading
from logging import Logger
from typing import List, Dict

from blinker import Signal

from sidecar.const import AppNetworkStatus


class AppHealthCheckState:
    on_apps_deployment_complete = Signal()

    def __init__(self, app_names: List[str], logger: Logger):
        self._lock = threading.RLock()
        self._logger = logger
        self._app_states = {app_name: AppNetworkStatus.PENDING for app_name in app_names}  # type: Dict[str, str]

    def set_app_state(self, app_name: str, status: str):
        self._logger.info("entered - app_name: '{}', status: '{}'".format(
            app_name,
            status))

        with self._lock:
            self._app_states[app_name] = status

            all_apps_complete = all(AppNetworkStatus.is_end_status(status)
                                    for status
                                    in self._app_states.values())

        if all_apps_complete:
            self.on_apps_deployment_complete.send(self)

    def all_complete_with_success(self) -> bool:
        self._logger.info("entered")

        with self._lock:
            return all(status == AppNetworkStatus.COMPLETED
                       for status
                       in self._app_states.values())

    def get_apps_state(self, app_names: List[str]) -> Dict[str, str]:
        self._logger.info("entered - app_names: '{}'".format(
            ", ".join(app_names)))

        with self._lock:
            return {k: v for k, v in self._app_states.items() if k in app_names}
