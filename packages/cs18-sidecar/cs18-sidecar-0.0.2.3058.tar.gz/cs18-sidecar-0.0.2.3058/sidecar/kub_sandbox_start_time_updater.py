from logging import Logger

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.const import DateTimeProvider, Const
from sidecar.kub_api_service import KubApiService
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class KubSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self,
                 date_time_provider: DateTimeProvider,
                 logger: Logger,
                 kub_api_service: KubApiService,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):
        super(KubSandboxStartTimeUpdater, self).__init__(date_time_provider, logger, apps_configuration_end_tracker)
        self.kub_api_service = kub_api_service
        self.date_time_provider = date_time_provider

    def _on_health_check_done(self):
        annotations = {Const.SANDBOX_START_TIME: str(self.date_time_provider.get_current_time_utc())}
        self.kub_api_service.update_namespace(annotations)
