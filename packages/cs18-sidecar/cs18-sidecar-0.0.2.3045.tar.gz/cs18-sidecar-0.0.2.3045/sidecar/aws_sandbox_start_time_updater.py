from logging import Logger

import _thread

import requests

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_session import AwsSession
from sidecar.const import Const, DateTimeProvider
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class AwsSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self, sandbox_id: str, aws_session: AwsSession, date_time_provider: DateTimeProvider, logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker):
        super(AwsSandboxStartTimeUpdater, self).__init__(date_time_provider, logger, apps_configuration_end_tracker)
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id
        self._date_time_provider = date_time_provider
        self._logger = logger
        self._ec2client = self.aws_session.get_ec2_client()
        self._cfclient = self.aws_session.get_cf_client()
        self._ec2 = self.aws_session.get_ec2_resource()

    def on_health_check_done(self):
        _thread.start_new_thread(self._wait_for_stack_complete, ())

    def _wait_for_stack_complete(self):
        waiter = self._cfclient.get_waiter('stack_create_complete')
        stack_name = self._get_stack_name(self.sandbox_id)

        self._logger.info('waiting for stack_create_complete state')
        waiter.wait(StackName=stack_name)
        self._logger.info('stack completed!')
        self._update_sidecar_start_time()

    def _update_sidecar_start_time(self):
        #sidecar_instance_id = self._get_side_car_instance_id()
        vpc = self._get_vpc()
        self._ec2client.create_tags(
            Resources=[vpc.id],
            Tags=[self._create_tag(Const.SANDBOX_START_TIME,
                                   str(self._date_time_provider.get_current_time_utc()))]
        )

    @staticmethod
    def _update_stack(self, stack_name: str):
        stack = self._cf.Stack(stack_name)
        stack.update(
            UsePreviousTemplate=True,
            Tags=[self._create_tag(Const.SANDBOX_START_TIME, str(self._date_time_provider.get_current_time_utc()))])

    def _get_vpc(self):
        filters = [{'Name': 'tag:' + Const.SANDBOX_ID_TAG,
                    'Values': [self.sandbox_id]}]

        vpcs = list(self._ec2.vpcs.filter(Filters=filters))

        if not vpcs:
            return None

        if len(vpcs) > 1:
            raise ValueError('Too many vpcs for the sandbox')

        return vpcs[0]

    @staticmethod
    def _get_side_car_instance_id():
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        return response.text

    @staticmethod
    def _get_stack_name(sandbox_id: str):
        return 'sandbox-{0}'.format(sandbox_id)

    @staticmethod
    def _create_tag(key, value):
        return {'Key': key, 'Value': value}
