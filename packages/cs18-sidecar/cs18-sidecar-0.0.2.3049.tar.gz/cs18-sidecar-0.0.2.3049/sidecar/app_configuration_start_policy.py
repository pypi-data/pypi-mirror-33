from typing import List, Dict

from sidecar.app_request_info import AppRequestInfo
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus


class AppConfigurationStartStatus:
    START = "start"
    WAIT = "wait"
    ABORT = "abort"


class AppConfigurationStartPolicy:
    def __init__(self, apps_config_end_tracker: AppsConfigurationEndTracker, app_requests: List[AppRequestInfo]):
        self._apps_config_end_tracker = apps_config_end_tracker
        self._app_dependencies = self._build_app_dependencies(app_requests)

    def get_app_configuration_start_status(self, app_name: str) -> str:
        app_dependency_names = self._app_dependencies[app_name]
        if not app_dependency_names:
            return AppConfigurationStartStatus.START

        # not waiting for dependencies if the sandbox is already deployed (i.e. all apps finished configuration)
        # because then apps availability is managed by the sandbox (load balancers)
        # this logic will have to be re-considered when sandbox upgrade is implemented
        if self._apps_config_end_tracker.all_apps_configuration_ended():
            return AppConfigurationStartStatus.START

        app_dependency_statuses = self._apps_config_end_tracker.get_app_configuration_statuses(*app_dependency_names)
        if any(config_end_status.status == AppConfigurationEndStatus.ERROR or
               config_end_status.status == AppConfigurationEndStatus.ABORTED
               for config_end_status in app_dependency_statuses.values()):
            return AppConfigurationStartStatus.ABORT

        if all(config_end_status.status == AppConfigurationEndStatus.COMPLETED and config_end_status.is_final
               for config_end_status in app_dependency_statuses.values()):
            return AppConfigurationStartStatus.START

        return AppConfigurationStartStatus.WAIT

    @staticmethod
    def _build_app_dependencies(app_requests: List[AppRequestInfo]) -> Dict[str, List[str]]:
        _app_dependencies = {app_request.name: list(app_request.app_dependencies) for app_request in app_requests}
        return _app_dependencies
