from abc import abstractmethod, ABCMeta

from sidecar.app_instance_identifier import AppInstanceIdentifier


class IAppInstanceIdentifierCreator:
    __metaclass__ = ABCMeta

    def __init__(self) -> None:
        pass

    @abstractmethod
    def create(self, app_name: str, ip_address: str, additional_data: {}) -> AppInstanceIdentifier:
        raise NotImplementedError


