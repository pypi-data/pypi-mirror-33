from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import List, Dict

from sidecar.app_instance_identifier import AppInstanceIdentifier


class IAppInstanceService:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_status_if_not_stale(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        raise NotImplementedError

    @abstractmethod
    def get_all_app_instances(self) -> List[AppInstanceIdentifier]:
        raise NotImplementedError

    @abstractmethod
    def get_all_app_instances_statuses(self) -> Dict[AppInstanceIdentifier, str]:
        raise NotImplementedError
