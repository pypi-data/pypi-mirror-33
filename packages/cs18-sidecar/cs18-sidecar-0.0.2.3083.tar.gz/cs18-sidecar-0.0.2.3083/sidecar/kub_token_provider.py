from sidecar.const import Const


class KubTokenProvider:
    def get_token(self):
        with open(Const.get_kubernetes_token_file_path(), 'r') as pod_token_file:
            return pod_token_file.read().replace('\n', '')
