import json

import requests
from requests import Session

from sidecar.kub_token_provider import KubTokenProvider


class KubApiService:
    def __init__(self, hostname: str, namespace: str, kub_token_provider: KubTokenProvider):
        self.namespace = namespace
        self.hostname = hostname
        self.token = kub_token_provider.get_token()

    def get_pod_json(self, ip_address: str) -> {}:
        s = self._get_session()
        s.headers['Content-Type'] = 'application/strategic-merge-patch+json'
        url = '{hostname}/api/v1/namespaces/{namespace}/pods'. \
            format(hostname=self.hostname,
                   namespace=self.namespace)
        res = s.get(url=url, verify=False)
        res.raise_for_status()
        pods_json = res.json()
        pods = pods_json['items']
        pod_json = next(iter([pod for pod in pods if pod['status']['podIP'] == ip_address]))
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
