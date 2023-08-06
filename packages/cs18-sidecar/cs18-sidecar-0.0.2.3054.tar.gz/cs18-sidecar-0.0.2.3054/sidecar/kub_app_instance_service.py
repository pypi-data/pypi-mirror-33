import json
from logging import Logger
from typing import List, Dict

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.const import Const
from sidecar.kub_api_pod_reader import KubApiPodReader
from sidecar.kub_api_service import KubApiService
from sidecar.app_instance_service import IAppInstanceService


class KubAppInstanceService(IAppInstanceService):
    def __init__(self, logger: Logger, kub_api_service: KubApiService):
        super().__init__(logger)
        self.kub_api_service = kub_api_service

    def update_status_if_not_stale(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        self._update_app_status(app_instance_identifier, status)

    def _update_app_status(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        name = app_instance_identifier.name
        container_id = app_instance_identifier.infra_id
        pod_json = self.kub_api_service.try_get_pod_json_by_container_id(container_id=container_id)
        # should update status only for a "live" instance
        if not self._is_pod_live_in_sandbox(pod_json):
            raise Exception("cannot update '{APP_NAME}' status to '{STATUS}' since the app instance is no longer a "
                            "part of the sandbox. infra id: {INFRA_ID}"
                            .format(APP_NAME=name, STATUS=status, INFRA_ID=container_id))
        apps_info_json = KubApiPodReader.get_apps_info_json(pod_json)
        apps_info_json[name]['status'] = status
        annotations = {Const.APPS: json.dumps(apps_info_json)}
        self.kub_api_service.update_pod(KubApiPodReader.get_pod_name(pod_json), annotations)

    def get_all_app_instances(self) -> List[AppInstanceIdentifier]:
        all_pods = self._get_all_live_app_pods_in_sandbox()
        app_instance_identifiers = [app_instance_identifier
                                    for pod_json in all_pods
                                    for app_instance_identifier in self._create_app_instance_identifiers(pod_json)]
        return app_instance_identifiers

    def get_all_app_instances_statuses(self) -> Dict[AppInstanceIdentifier, str]:
        result = {}
        all_pods = self._get_all_live_app_pods_in_sandbox()
        for pod_json in all_pods:
            apps_info_json = KubApiPodReader.get_apps_info_json(pod_json)
            app_instance_identifiers = self._create_identifiers_from_pod_apps_info(pod_json, apps_info_json)
            for app_instance_identifier in app_instance_identifiers:
                result[app_instance_identifier] = apps_info_json[app_instance_identifier.name]['status']

        return result

    def _get_all_live_app_pods_in_sandbox(self):
        return self.kub_api_service.get_all_pods_list(include_infra=False, include_ended=False,
                                                      include_terminating=False)

    def _create_app_instance_identifiers(self, pod_json: dict()) -> List[AppInstanceIdentifier]:
        apps_info_json = KubApiPodReader.get_apps_info_json(pod_json)
        return self._create_identifiers_from_pod_apps_info(pod_json, apps_info_json)

    @staticmethod
    def _create_identifiers_from_pod_apps_info(pod_json: dict(), apps_info_json: dict()) \
            -> List[AppInstanceIdentifier]:
        identifiers = []
        for app_name in apps_info_json:
            container_id = KubApiPodReader.safely_get_container_id_for_app(app_name, pod_json)
            # handling the possibility that container id is not available in the pod (maybe when pod in pending phase)
            if container_id:
                identifiers.append(AppInstanceIdentifier(name=app_name,infra_id=container_id))
        return identifiers

    @staticmethod
    def _is_pod_live_in_sandbox(pod_json) -> bool:
        return True if pod_json and \
                       not KubApiPodReader.is_pod_ended(pod_json) and \
                       not KubApiPodReader.is_pod_terminating(pod_json) else False
