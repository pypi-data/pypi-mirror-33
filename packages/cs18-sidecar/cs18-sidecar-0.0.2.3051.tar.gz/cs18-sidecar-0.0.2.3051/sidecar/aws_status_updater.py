import time
from logging import Logger


from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_session import AwsSession
from sidecar.const import Const
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater
from sidecar.updater import IStatusUpdater


class AwsStatusUpdater(IStatusUpdater):
    def __init__(self, sandbox_id: str, logger: Logger, aws_session: AwsSession,
                 sandbox_start_time_updater: ISandboxStartTimeUpdater,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):
        super().__init__(logger, apps_configuration_end_tracker, sandbox_start_time_updater)
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id

    def _update_app_status(self, ip_address:str, instance_id: str, app_name: str, status: str):
        instance = self._get_existing_instance(ip_address, instance_id, app_name)
        self._logger.info("updating status on instance '{INSTANCE_ID}' when its state is '{STATE}'".format(
            INSTANCE_ID=instance_id, STATE=instance.state["Name"]))
        updated_state = self._create_instance_state(instance=instance, status=status, app_name=app_name)
        instance.create_tags(Tags=[self._create_tag(Const.APP_STATUS_TAG, updated_state)])

    def _get_existing_instance(self, ip_address: str, instance_id: str, app_name: str):
        instance = self._get_instance_by_id(instance_id)
        if instance is None:
            raise Exception("instance for app '{APP_NAME}' not found. ip_address={IP_ADDRESS},instance_id={INSTANCE_ID}"
                            .format(APP_NAME=app_name, IP_ADDRESS=ip_address, INSTANCE_ID=instance_id))
        return instance

    def _do_update_status(self, name: str, ip_address: str, additional_data: {}, status: str):
        instance_id = additional_data['instance-id']
        self._update_app_status(ip_address, instance_id, name, status)

    def _do_get_status(self, name: str, ip_address: str, additional_data: {}) -> str:
        instance_id = additional_data['instance-id']
        instance = self._get_existing_instance(ip_address, instance_id, name)
        app_to_status_map = self._get_apps_status_map(instance)
        return app_to_status_map.get(name, None)

    @staticmethod
    def _create_tag(key, value):
        return {'Key': key, 'Value': value}

    def _create_instance_state(self, instance, status, app_name) -> str:
        app_to_status_map = self._get_apps_status_map(instance)
        app_to_status_map[app_name] = status
        return Const.CSV_TAG_VALUE_SEPARATE.join(["{0}:{1}".format(k, v) for k, v in app_to_status_map.items()])

    @staticmethod
    def _get_apps_status_map(instance):
        instance_tags = AwsStatusUpdater._get_tags(instance)
        apps_status_tag_value = instance_tags.get(Const.APP_STATUS_TAG, None)
        return AwsStatusUpdater._parse_apps_status_tag_value(apps_status_tag_value)

    @staticmethod
    def _parse_apps_status_tag_value(apps_status_value: str) -> {}:
        app_to_status_map = dict()
        if apps_status_value:
            all_statuses = apps_status_value.split(Const.CSV_TAG_VALUE_SEPARATE)
            app_to_status_map = dict(state.split(Const.APP_STATE_KEY_VALUE_SEPARATOR) for state in all_statuses)
        return app_to_status_map

    def _get_instance_by_id(self, instance_id: str):
        ec2 = self.aws_session.get_ec2_resource()
        return ec2.Instance(instance_id)

    def _get_instance_by_ip(self, sandbox_id: str, private_ip_address: str):
        ec2 = self.aws_session.get_ec2_resource()

        filters = [{'Name': 'tag:' + Const.SANDBOX_ID_TAG,
                    'Values': [sandbox_id]},
                   {'Name': 'private-ip-address',
                    'Values': [private_ip_address]}]

        instance = next(iter(list(ec2.instances.filter(Filters=filters))), None)
        start_time = time.time()
        while instance is None:
            instance = next(iter(list(ec2.instances.filter(Filters=filters))), None)
            if instance is None:
                if time.time() - start_time >= 60:
                    raise Exception('Timeout: Waiting for instance with ip {}'.format(private_ip_address))
                time.sleep(5)
        return instance

    @staticmethod
    def _get_tags(resource) -> {}:
        tags = resource.tags
        return dict((tag['Key'], tag['Value']) for tag in tags)
