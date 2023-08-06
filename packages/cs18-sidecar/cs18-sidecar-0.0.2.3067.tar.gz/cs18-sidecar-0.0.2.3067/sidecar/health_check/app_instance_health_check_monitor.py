import threading
from logging import Logger

from sidecar.app_instance_identifier import AppInstanceIdentifier, IIdentifier
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.cloud_logger import ICloudLogger
from sidecar.const import AppInstanceConfigStatus
from sidecar.health_check.health_check_executor import HealthCheckExecutor
from sidecar.health_check.health_check_preparer import HealthCheckPreparer

HEALTH_CHECK_TOPIC = "healthcheck"


class AppInstanceHealthCheckMonitor:
    def __init__(self,
                 executor: HealthCheckExecutor,
                 preparer: HealthCheckPreparer,
                 status_maintainer: AppStatusMaintainer,
                 cloud_logger: ICloudLogger,
                 logger: Logger):
        self._status_maintainer = status_maintainer
        self._cloud_logger = cloud_logger
        self._preparer = preparer
        self._executor = executor
        self._logger = logger

    def start(self, address: str, identifier: IIdentifier, script_name: str):
        self._logger.info("entered - identifier: '{}', ip: '{}', script: '{}'".format(
            identifier,
            address,
            script_name))

        thread = threading.Thread(target=self.process_health_check, args=(address, identifier, script_name))
        thread.start()

    def process_health_check(self, ip_address: str, identifier: AppInstanceIdentifier, script_name: str):
        self._logger.info("entered - identifier: '{}', ip: '{}', script: '{}'".format(
            identifier,
            ip_address,
            script_name))

        try:
            status = AppInstanceConfigStatus.PENDING
            self._status_maintainer.update_status(app_instance_identifier=identifier,
                                                  status=status,
                                                  script_name=script_name)

            result = self._execute_health_check_script(identifier=identifier,
                                                       ip_address=ip_address,
                                                       script_name=script_name)

            status = AppInstanceConfigStatus.COMPLETED if result else AppInstanceConfigStatus.ERROR
            self._status_maintainer.update_status(app_instance_identifier=identifier,
                                                  status=status,
                                                  script_name=script_name)
        except Exception as ex:
            self._logger.exception("error - identifier: '{}', ip: '{}', script: '{}'. {}".format(
                identifier,
                ip_address,
                script_name,
                str(ex)))
            raise

    def _execute_health_check_script(self,
                                     identifier,
                                     ip_address: str,
                                     script_name: str) -> bool:
        self._logger.info("entered - identifier: '{}', ip: '{}', script: '{}'".format(
            identifier,
            ip_address,
            script_name))

        cmd = self._preparer.prepare(app_name=identifier.name,
                                     script_name=script_name,
                                     address=ip_address)

        return self._executor.start(identifier=identifier,
                                    cmd=cmd)
