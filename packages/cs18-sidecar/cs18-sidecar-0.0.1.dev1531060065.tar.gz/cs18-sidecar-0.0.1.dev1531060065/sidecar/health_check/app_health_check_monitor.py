import threading
from logging import Logger

from sidecar.app_instance_identifier import AppIdentifier
from sidecar.app_services.app_service import AppService
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus
from sidecar.const import AppNetworkStatus
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.health_check.health_check_executor import HealthCheckExecutor
from sidecar.health_check.health_check_preparer import HealthCheckPreparer


class AppHealthCheckMonitor:
    def __init__(self,
                 executor: HealthCheckExecutor,
                 preparer: HealthCheckPreparer,
                 app_health_check_state: AppHealthCheckState,
                 app_service: AppService,
                 app_timeouts: dict(),
                 apps_configuration_end_tracker: AppsConfigurationEndTracker,
                 logger: Logger):
        self._apps_configuration_end_tracker = apps_configuration_end_tracker
        self._app_health_check_state = app_health_check_state
        self._app_timeouts = app_timeouts
        self._preparer = preparer
        self._executor = executor
        self._app_service = app_service
        self._logger = logger
        self._lock = threading.RLock()

    def start(self, identifier: AppIdentifier, infra_id: str, script_name: str):
        self._logger.info("entered - identifier: '{}', infra_id: '{}', script_name: '{}'".format(
            identifier,
            infra_id,
            script_name))

        try:
            app_configuration_status = self._get_app_configuration_status(identifier)
            if app_configuration_status \
                    and app_configuration_status.is_ended_with_status(AppConfigurationEndStatus.COMPLETED):
                self._start(identifier=identifier, infra_id=infra_id, script_name=script_name)
            else:
                self._logger.info("skipping network health-check. identifier: '{}', status: '{}'".format(
                    identifier,
                    app_configuration_status))
        except Exception as ex:
            self._logger.exception("error - identifier: '{}', script_name: '{}'. {}".format(
                identifier,
                script_name,
                str(ex)))
            raise

    def _get_app_configuration_status(self, identifier: AppIdentifier):
        self._logger.info("entered - identifier: '{}'".format(
            identifier))

        app_configuration_statuses = self._apps_configuration_end_tracker\
            .get_app_configuration_statuses(identifier.name)
        if len(app_configuration_statuses) != 1:
            raise Exception("Status for app '{}' was no found".format(identifier.name))
        return app_configuration_statuses[identifier.name]

    def _start(self, identifier: AppIdentifier, infra_id: str, script_name: str):
        self._logger.info("entered - identifier: '{}', infra_id: '{}', script_name: '{}'".format(
            identifier,
            infra_id,
            script_name))

        private_dns_check = self._test_private_network(identifier, script_name)

        if private_dns_check:
            self._test_public_network(identifier, infra_id, script_name)
        else:
            self._update_status(app_name=identifier.name, status=AppNetworkStatus.ERROR)

    def _test_public_network(self, identifier, infra_id, script_name):
        self._logger.info("entered - identifier: '{}', infra_id: '{}', script_name: '{}'".format(
            identifier,
            infra_id,
            script_name))

        timeout = self._app_timeouts.get(identifier.name)
        public_dns_name = self._app_service.get_public_dns_name_by_app_name(app_name=identifier.name,
                                                                            infra_id=infra_id,
                                                                            address_read_timeout=timeout)
        public_dns_check = True
        if public_dns_name is not None:
            self._update_status(app_name=identifier.name, status=AppNetworkStatus.TESTING_PUBLIC_NETWORK)

            public_dns_check = self._health_check_dns_names(identifier=identifier,
                                                            script_name=script_name,
                                                            dns_name=public_dns_name)
        status = AppNetworkStatus.COMPLETED if public_dns_check else AppNetworkStatus.ERROR
        self._update_status(app_name=identifier.name, status=status)

    def _test_private_network(self, identifier: AppIdentifier, script_name: str) -> bool:
        self._logger.info("entered - identifier: '{}', script_name: '{}'".format(
            identifier,
            script_name))

        private_dns_name = self._app_service.get_private_dns_name_by_app_name(app_name=identifier.name)

        private_dns_check = True  # TODO: REMOVE IF => Bug 1234: support Azure in private / public health checks
        if private_dns_name:
            self._update_status(app_name=identifier.name, status=AppNetworkStatus.TESTING_PRIVATE_NETWORK)
            private_dns_check = self._health_check_dns_names(identifier=identifier,
                                                             script_name=script_name,
                                                             dns_name=private_dns_name)
        return private_dns_check

    def _update_status(self, app_name: str, status: str):
        self._logger.info("entered - app_name: '{}', status: '{}'".format(
            app_name,
            status))

        with self._lock:
            self._app_service.update_network_status(app_name=app_name, status=status)
            self._app_health_check_state.set_app_state(app_name=app_name, status=status)

    def _health_check_dns_names(self,
                                identifier: AppIdentifier,
                                script_name: str,
                                dns_name: str) -> bool:
        self._logger.info("entered - identifier: '{}', script_name: '{}', dns_name: '{}'".format(
            identifier,
            script_name,
            dns_name))

        cmd = self._preparer.prepare(app_name=identifier.name,
                                     script_name=script_name,
                                     address=dns_name)

        return self._executor.start(identifier=identifier, cmd=cmd)
