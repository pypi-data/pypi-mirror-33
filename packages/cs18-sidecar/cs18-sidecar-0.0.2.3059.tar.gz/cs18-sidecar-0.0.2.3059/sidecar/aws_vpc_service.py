from sidecar.aws_session import AwsSession
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const


class AwsVpcService():
    def __init__(self, sandbox_id: str, aws_session: AwsSession) -> None:
        super().__init__()
        self.aws_session = aws_session
        self.sandbox_id = sandbox_id
        self._ec2_client = self.aws_session.get_ec2_client()
        self._ec2_resource = self.aws_session.get_ec2_resource()

    def update_tags_on_vpc(self, tags: {}):
        tags_list = [AwsTagHelper.create_tag(tag_name, tag_value) for tag_name, tag_value in tags.items()]
        vpc = self._get_vpc()
        self._ec2_client.create_tags(
            Resources=[vpc.id],
            Tags=tags_list
        )

    def _get_vpc(self):
        filters = [{'Name': 'tag:' + Const.SANDBOX_ID_TAG,
                    'Values': [self.sandbox_id]}]

        vpcs = list(self._ec2_resource.vpcs.filter(Filters=filters))

        if not vpcs:
            return None

        if len(vpcs) > 1:
            raise ValueError('Too many vpcs for the sandbox')

        return vpcs[0]
