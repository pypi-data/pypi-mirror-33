from sidecar.aws_vpc_service import AwsVpcService
from sidecar.const import Const
from sidecar.sandbox_deployment_end_updater import ISandboxDeploymentEndUpdater


class AwsSandboxDeploymentEndUpdater(ISandboxDeploymentEndUpdater):
    def __init__(self, vpc_service: AwsVpcService):
        super(AwsSandboxDeploymentEndUpdater, self).__init__()
        self._vpc_service = vpc_service

    def _set_deployment_end_details(self, deployment_end_status: str):
        self._vpc_service.update_tags_on_vpc({Const.SANDBOX_DEPLOYMENT_END_STATUS: deployment_end_status})
