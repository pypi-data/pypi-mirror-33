import json
from logging import Logger

import urllib3

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.const import Const
from sidecar.kub_api_service import KubApiService
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater
from sidecar.updater import IStatusUpdater


class KubernetesStatusUpdater(IStatusUpdater):
    def __init__(self, logger: Logger, kub_api_service: KubApiService,
                 sandbox_start_time_updater: ISandboxStartTimeUpdater,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):
        super().__init__(logger, apps_configuration_end_tracker, sandbox_start_time_updater)
        self.kub_api_service = kub_api_service

    def _do_update_status(self, name: str, ip_address: str, additional_data: {}, status: str):
        self._disable_secure_warnings()
        self._update_app_status(name, status, ip_address)

    def _do_get_status(self, name: str, ip_address: str, additional_data: {}) -> str:
        self._disable_secure_warnings()
        pod_json = self.kub_api_service.get_pod_json(ip_address=ip_address)
        apps_info_json = self._get_apps_info_json(pod_json)
        return apps_info_json[name]['status'] if name in apps_info_json else None

    def _update_app_status(self, name: str, status: str, ip_address: str):
        pod_json = self.kub_api_service.get_pod_json(ip_address=ip_address)
        apps_info_json = self._get_apps_info_json(pod_json)
        apps_info_json[name]['status'] = status
        annotations = {Const.APPS: json.dumps(apps_info_json)}
        self.kub_api_service.update_pod(self._get_pod_name(pod_json), annotations)

    def _disable_secure_warnings(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @staticmethod
    def _get_pod_name(pod_json) -> str:
        return pod_json['metadata']['name']

    @staticmethod
    def _get_apps_info_json(pod_json) -> {}:
        return json.loads(pod_json['metadata']['annotations'][Const.APPS])
