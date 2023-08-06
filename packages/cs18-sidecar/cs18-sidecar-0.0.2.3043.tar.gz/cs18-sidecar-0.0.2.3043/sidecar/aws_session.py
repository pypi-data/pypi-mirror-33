import boto3
from botocore.config import Config


class AwsSession:
    def __init__(self, region_name: str):
        config_dict = {'connect_timeout': 5, 'read_timeout': 15, 'max_pool_connections': 100,
                       'retries': {'max_attempts': 0}}
        self._config = Config(**config_dict)
        self._region_name = region_name
        self.ec2_client = self._get_client('ec2', self._config)
        self.cf_client = self._get_client('cloudformation', self._config)
        self.ec2_resource = self._get_resource('ec2', self._config)
        self._autoscalling_client = self._get_client('autoscaling', self._config)

    def get_ec2_client(self):
        return self.ec2_client

    def get_cf_client(self):
        return self.cf_client

    def get_ec2_resource(self):
        return self.ec2_resource

    def get_autoscaling_client(self):
        return self._autoscalling_client

    def _get_client(self, client: str, config: Config):
        return boto3.client(client, region_name=self._region_name, config=config)

    def _get_resource(self, resource: str, config: Config):
        return boto3.resource(resource, region_name=self._region_name, config=config)

    def get_dynamo_resource(self):
        return boto3.resource('dynamodb', region_name=self._region_name, config=self._config)
