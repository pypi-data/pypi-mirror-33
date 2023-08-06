from logging import Logger
from typing import List

from sidecar.app_configuration_start_policy import AppConfigurationStartPolicy
from sidecar.app_instance_config_status_event_reporter import AppInstanceConfigStatusEventReporter
from sidecar.app_instance_service import IAppInstanceService
from sidecar.app_request_info import AppRequestInfo
from sidecar.app_services.app_service import AzureAppService
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.azure.azure_app_instance_identifier_creator import AzureAppInstanceIdentifierCreator
from sidecar.azure.azure_app_instance_service import AzureAppInstanceService
from sidecar.azure.azure_clients import AzureClientsManager, AzureCredentialsProvider
from sidecar.azure.azure_cosmos_service import AzureCosmosService
from sidecar.azure.azure_sandbox_deployment_end_updater import AzureSandboxDeploymentEndUpdater
from sidecar.azure.azure_sandbox_start_time_updater import AzureSandboxStartTimeUpdater
from sidecar.azure.azure_status_maintainer import AzureStatusMaintainer
from sidecar.const import DateTimeProvider
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.messaging_service import MessagingService
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater
from sidecar.sandbox_deployment_state_tracker import SandboxDeploymentStateTracker


class AzureSidecarApiInitializer:
    def __init__(self,
                 sandbox_id: str,
                 space_id: str,
                 app_requests: List[AppRequestInfo],
                 messaging_service: MessagingService,
                 app_instance_status_event_reporter: AppInstanceConfigStatusEventReporter,
                 app_health_check_state: AppHealthCheckState,
                 logger: Logger,
                 config_json: dict) -> None:
        super().__init__()
        self._app_health_check_state = app_health_check_state
        self._sandbox_id = sandbox_id
        self._space_id = space_id
        self._app_requests = app_requests
        self._messaging_service = messaging_service
        self._app_instance_status_event_reporter = app_instance_status_event_reporter
        self._logger = logger
        self._config_json = config_json

    def initialize(self):
        app_instance_identifier_creator = AzureAppInstanceIdentifierCreator(logger=self._logger)

        azure_credentials_provider = self._create_credentials_provider()
        azure_clients_manager = AzureClientsManager(credentials_provider=azure_credentials_provider)
        azure_cosmos_service = AzureCosmosService(clients_manager=azure_clients_manager)
        azure_status_maintainer = AzureStatusMaintainer(cosmos_service=azure_cosmos_service,
                                                        sandbox_id=self._sandbox_id)
        azure_app_instance_service = AzureAppInstanceService(logger=self._logger,
                                                             sandbox_id=self._sandbox_id,
                                                             clients_manager=azure_clients_manager,
                                                             status_maintainer=azure_status_maintainer)

        azure_sandbox_deployment_end_updater = AzureSandboxDeploymentEndUpdater(
            status_maintainer=azure_status_maintainer)

        apps_configuration_end_tracker = self._create_apps_configuration_end_tracker(
            app_instance_service=azure_app_instance_service)

        start_time_updater = AzureSandboxStartTimeUpdater(
            app_health_check_state=self._app_health_check_state,
            date_time_provider=DateTimeProvider(),
            logger=self._logger,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            status_maintainer=azure_status_maintainer)

        app_status_maintainer, \
        app_configuration_start_policy, \
        sandbox_deployment_state_tracker = self._create_cp_agnostic_components(
            app_instance_service=azure_app_instance_service,
            sandbox_deployment_end_updater=azure_sandbox_deployment_end_updater,
            apps_configuration_end_tracker=apps_configuration_end_tracker)

        app_service = AzureAppService(logger=self._logger)

        return app_status_maintainer, \
               app_configuration_start_policy, \
               app_instance_identifier_creator, \
               apps_configuration_end_tracker, \
               app_service, \
               sandbox_deployment_state_tracker, \
               start_time_updater


    def _create_apps_configuration_end_tracker(self, app_instance_service: IAppInstanceService):
        return AppsConfigurationEndTracker(logger=self._logger,
                                           app_requests=self._app_requests,
                                           app_instance_service=app_instance_service)

    def _create_cp_agnostic_components(self, app_instance_service: IAppInstanceService,
                                       sandbox_deployment_end_updater: ISandboxDeploymentEndUpdater,
                                       apps_configuration_end_tracker: AppsConfigurationEndTracker):
        sandbox_deployment_state_tracker = SandboxDeploymentStateTracker(
            logger=self._logger,
            app_requests=self._app_requests,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            sandbox_deployment_end_updater=sandbox_deployment_end_updater,
            sandbox_id=self._sandbox_id,
            messaging_service=self._messaging_service,
            space_id=self._space_id)

        app_status_maintainer = AppStatusMaintainer(
            logger=self._logger,
            app_instance_service=app_instance_service,
            apps_configuration_end_tracker=apps_configuration_end_tracker,
            sandbox_deployment_state_tracker=sandbox_deployment_state_tracker,
            app_instance_status_event_reporter=self._app_instance_status_event_reporter)

        app_configuration_start_policy = AppConfigurationStartPolicy(
            app_health_check_state=self._app_health_check_state,
            apps_config_end_tracker=apps_configuration_end_tracker,
            app_requests=self._app_requests)

        return app_status_maintainer, app_configuration_start_policy, sandbox_deployment_state_tracker

    def _create_credentials_provider(self):
        return AzureCredentialsProvider(
            management_resource_group=self._config_json['management_resource_group'],
            subscription_id=self._config_json['subscription_id'],
            application_id=self._config_json['application_id'],
            application_secret=self._config_json['application_secret'],
            tenant_id=self._config_json['tenant_id'])
