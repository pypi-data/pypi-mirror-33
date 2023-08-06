from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Optional

from sidecar.aws_session import AwsSession
from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const, get_app_selector
from sidecar.kub_api_service import IKubApiService
from sidecar.utils import Utils


class StaleAppException(Exception):
    pass


class AppService:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_network_status(self, app_name: str, status: str):
        raise NotImplementedError

    @abstractmethod
    def get_private_dns_name_by_app_name(self, app_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        raise NotImplementedError


class AzureAppService(AppService):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def update_network_status(self, app_name: str, status: str):
        pass

    def get_private_dns_name_by_app_name(self, app_name: str) -> str:
        pass

    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        pass


class K8sAppService(AppService):
    def __init__(self, api: IKubApiService, sandbox_id: str, logger: Logger):
        super().__init__(logger)
        self.sandbox_id = sandbox_id
        self.api = api

    def get_private_dns_name_by_app_name(self, app_name: str) -> str:
        self._logger.info("entered - app_name: '{}'".format(
            app_name))

        service = self._get_service_by_app_name(app_name=app_name)
        return "{}.{}".format(service['metadata']['name'], self.sandbox_id)

    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        self._logger.info("entered - app_name: '{}', infra_id: '{}', address_read_timeout: '{}'".format(
            app_name,
            infra_id,
            address_read_timeout))

        return Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_app_name(app_name=app_name),
                                        timeout=address_read_timeout,
                                        logger=self._logger,
                                        logger_msg="trying to get public dns for app '{}'.".format(app_name))

    def _get_public_dns_name_by_app_name(self, app_name: str) -> Optional[str]:
        self._logger.info("entered - app_name: '{}'".format(
            app_name))

        service = self._get_service_by_app_name(app_name=app_name)

        if service["spec"]["type"] != "LoadBalancer":
            return None

        if "status" not in service:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status' yet.".format(app_name=app_name))

        if "loadBalancer" not in service["status"]:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status.loadBalancer' yet.".format(app_name=app_name))

        load_balancer = service["status"]['loadBalancer']
        if "ingress" not in load_balancer:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress' yet.".format(
                    app_name=app_name))

        ingress = next(iter(load_balancer['ingress']), None)
        if ingress and "ip" not in ingress and "hostname" not in ingress:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress.ip' or 'status.loadBalancer.ingress.hostname' yet.".format(
                    app_name=app_name))

        return ingress['ip'] if "ip" in ingress else ingress['hostname']

    def update_network_status(self, app_name: str, status: str):
        self._logger.info("entered - app_name: '{}', status: {}".format(
            app_name,
            status))

        # TODO: rethink it !!! not so good to mark both services when only one got checked
        app_services = [service for service in self.api.get_all_services()
                        if service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]

        for app_service in app_services:
            annotations = app_service['metadata']['annotations']
            if app_service['metadata']['annotations'] is None or Const.HEALTH_CHECK_STATUS not in annotations:  # backward compatibility
                annotations = {Const.HEALTH_CHECK_STATUS: status}
            else:
                annotations[Const.HEALTH_CHECK_STATUS] = status
            self.api.update_service(name=app_service['metadata']['name'],
                                    annotations=annotations)

    def _get_service_by_app_name(self, app_name: str) -> dict:
        self._logger.info("entered - app_name: '{}'".format(
            app_name))

        services = self.api.get_all_services()
        service = next(
            iter([service for service in services if
                  service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]),
            None)
        if service is None:
            raise StaleAppException(
                "Cannot get '{app_name}' since the service exposing it does not exists.".format(
                    app_name=app_name))

        return service


class AWSAppService(AppService):
    def __init__(self, session: AwsSession, sandbox_id: str, logger: Logger):
        super().__init__(logger)
        self.sandbox_id = sandbox_id
        self.session = session

    def update_network_status(self, app_name: str, status: str):
        self._logger.info("entered - app_name: '{}', status: {}".format(
            app_name,
            status))

        table, item = Utils.retry_on_exception(
            func=lambda: self._get_table(sandbox_id=self.sandbox_id),
            logger=self._logger,
            logger_msg="cannot get public dns for app '{}'.".format(app_name))

        if 'logical-apps' not in item:  # backward compatibility
            item["logical-apps"] = {**{app_name: {Const.HEALTH_CHECK_STATUS: status}}}
        else:
            item["logical-apps"][app_name][Const.HEALTH_CHECK_STATUS] = status

        response = table.update_item(
            Key={Const.SANDBOX_ID_TAG: self.sandbox_id},
            UpdateExpression='set #col = :r',
            ExpressionAttributeValues={':r': item["logical-apps"]},
            ExpressionAttributeNames={"#col": "logical-apps"},
            ReturnValues="UPDATED_NEW"
        )
        self._logger.info("ended - app_name: '{}', status: {}, response: {}".format(
            app_name,
            status,
            response))

    def _get_table(self, sandbox_id: str):
        self._logger.info("entered - sandbox_id: '{}'".format(
            sandbox_id))

        table = self.session.get_dynamo_resource().Table(AWSStatusMaintainer.default_table_name)
        item = table.get_item(Key={Const.SANDBOX_ID_TAG: sandbox_id})
        if "Item" not in item:
            raise Exception("dynamodb table is not ready yet")
        return table, item["Item"]

    def get_private_dns_name_by_app_name(self, app_name: str) -> str:
        self._logger.info("entered - app_name: '{}'".format(
            app_name))

        return "{}.{}.sandbox.com".format(app_name, self.sandbox_id)

    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        self._logger.info("entered - app_name: '{}', infra_id: '{}', address_read_timeout: '{}'".format(
            app_name,
            infra_id,
            address_read_timeout))

        return Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_instance_id(instance_id=infra_id),
                                        timeout=address_read_timeout,
                                        logger=self._logger,
                                        logger_msg="trying to get public dns for app '{}'.".format(app_name))

    def _get_public_dns_name_by_instance_id(self, instance_id: str):
        self._logger.info("entered - instance_id: '{}'".format(
            instance_id))

        instance = self.session.get_ec2_resource().Instance(instance_id)
        dns_name = AwsTagHelper.safely_get_tag(resource=instance,
                                               tag_name=Const.EXTERNAL_ELB_DNS_NAME,
                                               logger=self._logger)

        return dns_name if dns_name is not None else instance.public_ip_address
