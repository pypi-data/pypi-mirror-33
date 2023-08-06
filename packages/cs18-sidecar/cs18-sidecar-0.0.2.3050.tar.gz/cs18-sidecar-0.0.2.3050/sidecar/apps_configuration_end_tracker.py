import json
import threading
from logging import Logger
from typing import Dict, List

from sidecar.app_request_info import AppRequestInfo
from sidecar.const import AppInstanceConfigStatus


class AppConfigurationEndStatus:
    NONE = "none"
    COMPLETED = "completed"
    ERROR = "error"
    ABORTED = "aborted"

    def __init__(self, status: str, is_final: bool):
        self.status = status
        self.is_final = is_final


class AppRecord:
    def __init__(self, app_name: str, expected_instances_count: int):
        self.app_name = app_name
        self.expected_instances_count = expected_instances_count
        self.instance_config_end_statuses = []

    def update_instance_config_end_status(self, config_end_status: str):
        self.instance_config_end_statuses.append(config_end_status)

    def app_configuration_ended(self) -> bool:
        return self.expected_instances_count - len(self.instance_config_end_statuses) == 0

    def get_current_config_end_status(self) -> AppConfigurationEndStatus:
        is_final = self.app_configuration_ended()

        current_config_end_statuses = self.instance_config_end_statuses
        if not current_config_end_statuses:
            return AppConfigurationEndStatus(AppConfigurationEndStatus.NONE, is_final)

        if any(status == AppInstanceConfigStatus.ERROR for status in current_config_end_statuses):
            return AppConfigurationEndStatus(AppConfigurationEndStatus.ERROR, is_final)

        if any(status == AppInstanceConfigStatus.ABORTED for status in current_config_end_statuses):
            return AppConfigurationEndStatus(AppConfigurationEndStatus.ABORTED, is_final)

        if all(status == AppInstanceConfigStatus.COMPLETED for status in current_config_end_statuses):
            return AppConfigurationEndStatus(AppConfigurationEndStatus.COMPLETED, is_final)

        raise Exception("could not calculate app configuration end status from: {}"
                        .format(",".join(current_config_end_statuses)))


class AppsConfigurationEndTracker:
    def __init__(self, logger: Logger, app_requests: List[AppRequestInfo]):
        self._logger = logger
        self._lock = threading.RLock()
        self._app_records = self._build_app_records(app_requests)

    def update_app_instance_config_status(self, app_name: str, app_instance_config_status: str):
        with self._lock:
            # protection against app instances being restarted and reconfigured after sandbox deployment already ended
            if self.all_apps_configuration_ended():
                self._logger.info("attempt to update app instance configuration status for '{APP_NAME}' to '{STATUS}'"
                                  " after all apps ended configuration - doing nothing"
                                  .format(APP_NAME=app_name, STATUS=app_instance_config_status))
                return

            if not AppInstanceConfigStatus.is_end_status(app_instance_config_status):
                return

            app_record = self._app_records[app_name]
            app_record.update_instance_config_end_status(app_instance_config_status)
            self._logger.info("configuration ended for instance of '{APP_NAME}' app with status '{STATUS}'.\n"
                              "app records: {APP_RECORDS}"
                              .format(APP_NAME=app_name, STATUS=app_instance_config_status,
                                      APP_RECORDS=json.dumps(self._app_records, default=lambda x: x.__dict__,
                                                             indent=2)))

    def all_apps_configuration_ended(self) -> bool:
        with self._lock:
            return all(record.app_configuration_ended() for record in self._app_records.values())

    def all_apps_configuration_ended_with_status(self, required_app_status: str) -> bool:
        with self._lock:
            return all(self._is_app_configuration_ended_with_status(record, required_app_status)
                       for record in self._app_records.values())

    def get_app_configuration_statuses(self, *app_names: str) -> Dict[str, AppConfigurationEndStatus]:
        with self._lock:
            app_records = [self._app_records[app_name] for app_name in app_names]
            app_statuses = {record.app_name: record.get_current_config_end_status() for record in app_records}
            return app_statuses

    @staticmethod
    def _build_app_records(app_requests: List[AppRequestInfo]) -> Dict[str, AppRecord]:
        app_records = {app_request.name: AppRecord(app_name=app_request.name,
                                                   expected_instances_count=app_request.instances_count)
                       for app_request in app_requests}
        return app_records

    @staticmethod
    def _is_app_configuration_ended_with_status(record: AppRecord, required_app_status: str) -> bool:
        configuration_end_status = record.get_current_config_end_status()
        return configuration_end_status.is_final and configuration_end_status.status == required_app_status
