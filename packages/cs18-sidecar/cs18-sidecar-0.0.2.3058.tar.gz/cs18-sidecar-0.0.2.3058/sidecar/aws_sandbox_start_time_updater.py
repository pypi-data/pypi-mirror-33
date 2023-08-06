import _thread
from logging import Logger

import requests

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_session import AwsSession
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.aws_vpc_service import AwsVpcService
from sidecar.const import Const, DateTimeProvider
from sidecar.sandbox_start_time_updater import ISandboxStartTimeUpdater


class AwsSandboxStartTimeUpdater(ISandboxStartTimeUpdater):
    def __init__(self, sandbox_id: str, aws_session: AwsSession, date_time_provider: DateTimeProvider, logger: Logger,
                 apps_configuration_end_tracker: AppsConfigurationEndTracker, vpc_service: AwsVpcService):
        super(AwsSandboxStartTimeUpdater, self).__init__(date_time_provider, logger, apps_configuration_end_tracker)
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id
        self._date_time_provider = date_time_provider
        self._logger = logger
        self._vpc_service = vpc_service
        self._cfclient = self.aws_session.get_cf_client()

    def _on_health_check_done(self):
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
        self._vpc_service.update_tags_on_vpc({Const.SANDBOX_START_TIME: str(self._date_time_provider.get_current_time_utc())})

    @staticmethod
    def _update_stack(self, stack_name: str):
        stack = self._cf.Stack(stack_name)
        stack.update(
            UsePreviousTemplate=True,
            Tags=[AwsTagHelper.create_tag(Const.SANDBOX_START_TIME,
                                          str(self._date_time_provider.get_current_time_utc()))])

    @staticmethod
    def _get_side_car_instance_id():
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        return response.text

    @staticmethod
    def _get_stack_name(sandbox_id: str):
        return 'sandbox-{0}'.format(sandbox_id)
