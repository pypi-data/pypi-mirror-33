import json
from abc import abstractmethod, ABCMeta

import requests
import urllib3
from requests import Session

from sidecar.const import Const
from sidecar.kub_api_pod_reader import KubApiPodReader
from sidecar.kub_token_provider import KubTokenProvider


class IKubApiService(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_all_pods_list(self, include_infra: bool = True, include_ended=True, include_terminating: bool = True) -> []:
        raise NotImplementedError

    @abstractmethod
    def try_get_pod_json(self, ip_address: str) -> {}:
        raise NotImplementedError

    @abstractmethod
    def try_get_pod_json_by_container_id(self, container_id: str) -> {}:
        raise NotImplementedError

    @abstractmethod
    def update_namespace(self, annotations: {}):
        raise NotImplementedError

    @abstractmethod
    def update_pod(self, pod_name: str, annotations: {}):
        raise NotImplementedError


class KubApiService(IKubApiService):
    def __init__(self, hostname: str, namespace: str, kub_token_provider: KubTokenProvider):
        super().__init__()
        self.namespace = namespace
        self.hostname = hostname
        self._disable_secure_warnings()
        self.token = kub_token_provider.get_token()

    def get_all_pods_list(self, include_infra: bool = True, include_ended=True, include_terminating: bool = True) -> []:
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/pods'. \
            format(hostname=self.hostname,
                   namespace=self.namespace)
        query_params = {}
        if not include_infra:
            query_params['labelSelector'] = '{app_selector_label}!={sidecar_selector_value}'.format(
                app_selector_label=Const.K8S_SIDECAR_APP_SELECTOR,
                sidecar_selector_value=Const.K8S_SIDECAR_SERVICE)
        res = s.get(url=url, verify=False, params=query_params)
        res.raise_for_status()
        pods_json = res.json()
        pods = pods_json['items']
        live_app_pods = self._filter_pods(pods=pods, include_ended=include_ended,
                                          include_terminating=include_terminating)
        return live_app_pods

    def try_get_pod_json(self, ip_address: str) -> {}:
        # when we're looking for a specific pod, we want to find it no matter in what state it is
        pods = self.get_all_pods_list()
        pod_json = next(iter([pod for pod in pods if KubApiPodReader.safely_get_pod_ip(pod) == ip_address]), None)
        return pod_json

    def try_get_pod_json_by_container_id(self, container_id: str) -> {}:
        # when we're looking for a specific pod, we want to find it no matter in what state it is
        pods = self.get_all_pods_list()
        pod_json = next(iter([pod for pod in pods
                              if container_id in KubApiPodReader.safely_get_container_ids_in_pod(pod=pod)]),
                        None)
        return pod_json

    def update_namespace(self, annotations: {}):
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}'.format(hostname=self.hostname,
                                                                namespace=self.namespace)
        data_json = {
            'metadata': {
                'annotations': annotations
            }
        }

        metadata_json = json.dumps(data_json)
        res = s.patch(url=url, data=metadata_json, verify=False)
        res.raise_for_status()

    def update_pod(self, pod_name: str, annotations: {}):
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/pods/{pod_name}' \
            .format(hostname=self.hostname,
                    namespace=self.namespace,
                    pod_name=pod_name)
        data_json = {
            'metadata': {
                'annotations': annotations
                # 'annotations': {
                #     Const.APPS: json.dumps(apps_info_json)
                # }
            }
        }
        metadata_json = json.dumps(data_json)
        res = s.patch(url=url, data=metadata_json, verify=False)
        res.raise_for_status()

    def _get_session(self) -> Session:
        s = requests.Session()
        s.headers['Authorization'] = 'Bearer ' + self.token
        return s

    @staticmethod
    def _filter_pods(pods: [], include_ended: bool, include_terminating: bool) -> []:
        # filtering out ended pods relies on the assumption that pods' restart policy is Always,
        # meaning that new pods were created instead of the ended ones and the old ones are no longer relevant
        # the terminating pods are filtered out because under this restart policy sometimes the new pod can be created
        # while the old one is still terminating and we don't want to get both of them, but only the "live" one
        return [pod for pod in pods
                if (include_ended or not KubApiPodReader.is_pod_ended(pod)) and
                (include_terminating or not KubApiPodReader.is_pod_terminating(pod))
                ]

    @staticmethod
    def _disable_secure_warnings():
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
