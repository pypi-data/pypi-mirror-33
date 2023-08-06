from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_identifier_creator import IAppInstanceIdentifierCreator
from sidecar.kub_api_pod_reader import KubApiPodReader
from sidecar.kub_api_service import KubApiService


class KubAppInstanceIdentifierCreator(IAppInstanceIdentifierCreator):
    def __init__(self, kub_api_service: KubApiService) -> None:
        super().__init__()
        self._kub_api_service = kub_api_service

    def create(self, app_name: str, ip_address: str, additional_data: {}) -> AppInstanceIdentifier:
        # TODO: change ip address to pod name/id (or specify it in additional_data) and use it to find the pod because:
        #       a. consistent with aws
        #       b. don't want to have to handle the situation where ip is not available on the pod (maybe can happen
        #          in some pod phases, like 'pending'), which will cause the pod not to be found
        pod_json = self._kub_api_service.try_get_pod_json(ip_address=ip_address)
        if not pod_json:
            raise Exception("pod with address '{ADDRESS}' not found".format(ADDRESS=ip_address))
        # container id is enough as infra identifier because it is supposed to be unique (across space and time),
        # meaning that even if there are multiple instances of the same app on different pods -
        # they should have different container ids
        container_id = KubApiPodReader.safely_get_container_id_for_app(app_name=app_name, pod=pod_json)
        if not container_id:
            raise Exception("container id for app '{APP}' not found on pod with address '{ADDRESS}'"
                            .format(APP=app_name, ADDRESS=ip_address))
        return AppInstanceIdentifier(name=app_name, infra_id=container_id)
