import boto3


class AwsSession:
    def __init__(self, region_name: str):
        self._region_name = region_name
        self.ec2_client = self._get_client('ec2')
        self.cf_client = self._get_client('cloudformation')
        self.ec2_resource = self._get_resource('ec2')

    def get_ec2_client(self):
        return self.ec2_client

    def get_cf_client(self):
        return self.cf_client

    def get_ec2_resource(self):
        return self.ec2_resource

    def _get_client(self, client: str):
        return boto3.client(client, region_name=self._region_name)

    def _get_resource(self, resource: str):
        return boto3.resource(resource, region_name=self._region_name)
