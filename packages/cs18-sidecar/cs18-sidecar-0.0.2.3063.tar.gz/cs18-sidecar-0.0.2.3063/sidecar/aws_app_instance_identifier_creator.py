from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_instance_identifier_creator import IAppInstanceIdentifierCreator


class AwsAppInstanceIdentifierCreator(IAppInstanceIdentifierCreator):
    def __init__(self) -> None:
        super().__init__()

    def create(self, app_name: str, ip_address: str, additional_data: {}) -> AppInstanceIdentifier:
        return AppInstanceIdentifier(name=app_name, infra_id=additional_data['instance-id'])
