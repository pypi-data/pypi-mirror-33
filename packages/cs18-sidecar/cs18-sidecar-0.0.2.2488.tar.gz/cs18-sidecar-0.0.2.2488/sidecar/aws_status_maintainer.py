from enum import Enum
from logging import Logger

from sidecar.const import Const
from sidecar.aws_session import AwsSession
from sidecar.utils import Utils


class AWSStatusMaintainer:
    table_data = {}

    class INSTANCE_STATE(Enum):
        START_DEPLOYMENT = 1
        RUNNING = 2

    class APP_STATE(Enum):
        NOT_STARTED = 1
        STARTED = 2
        PASSED_HEALTH_CHECK = 3
        FAILED_HEALTH_CHECK = 4

    default_Table_Name = 'colony-sandboxes-datatable'

    default_table_atributes = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'AttributeType': 'S',
        }
    ]

    defualt_table_Schema = [
        {
            'AttributeName': Const.SANDBOX_ID_TAG,
            'KeyType': 'HASH',
        }
    ]

    def __init__(self, awssessionservice: AwsSession, sandbox_id: str, logger: Logger):
        self.dynamo_resource = awssessionservice.get_dynamo_resource()
        self.sandboxid = sandbox_id
        self._logger = logger
        self.table_name = self.default_Table_Name

        table = self.dynamo_resource.Table(self.default_Table_Name)

        try:
            Utils.wait_for(func=lambda:  self._set_table_data(table, sandbox_id) is not None,
                           interval_sec=1,
                           max_retries=5,
                           error='No sandbox data available')
        except Exception:
            self.logger.exception("Failed to get sandbox data from dynamodb after 5 times")
            return

    def _set_table_data(self, table, sandbox_id):

        response = table.get_item(
            Key={
                Const.SANDBOX_ID_TAG: sandbox_id
            }
        )

        if "Item" in response:
            self.table_data = response["Item"]
            self._logger.info("dynamo table response for sandbox {id} is {data}".format(id=sandbox_id, data=response))
            return "Item"

        return None

    def update_app_instance_status(self, instance_logical_id, instance_id, app_name, status_tag, status):

        table = self.dynamo_resource.Table(self.default_Table_Name)
        if instance_id not in self.table_data["apps"][instance_logical_id]["instances"]:
            self.table_data["apps"][instance_logical_id]["instances"][instance_id] = \
                {
                    "apps": {}
                }

        self.table_data["apps"][instance_logical_id]["instances"][instance_id]["apps"][app_name] = {status_tag: status}

        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set " + "apps" + " = :r",
            ExpressionAttributeValues={
                ':r': self.table_data["apps"]
            },
            ReturnValues="UPDATED_NEW"
        )
        self._logger.info("update_app_instance_status response for sandbox_id: {sandbox_id} app_name: {app} instance_id: {instance_id} is {data}"
                          .format(sandbox_id=self.sandboxid, app=app_name, instance_id= instance_id, data=response))

    def update_sandbox_end_status(self, sandbox_deployment_end_status: str):
        table = self.dynamo_resource.Table(self.default_Table_Name)

        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set #f = :r",
            ExpressionAttributeValues={
                ':r': sandbox_deployment_end_status
            },
            ExpressionAttributeNames={
                "#f": Const.SANDBOX_DEPLOYMENT_END_STATUS
            },
            ReturnValues="UPDATED_NEW"
        )
        self._logger.info("update_sandbox_end_status for sandbox_id: {sandbox_id} status: {status} is {data}"
                          .format(sandbox_id=self.sandboxid, status=sandbox_deployment_end_status, data=response))

    def update_sandbox_start_status(self, sandbox_start_time):
        table = self.dynamo_resource.Table(self.default_Table_Name)

        response = table.update_item(
            Key={
                Const.SANDBOX_ID_TAG: self.sandboxid
            },
            UpdateExpression="set #f = :r",
            ExpressionAttributeValues={
                ':r': str(sandbox_start_time)
            },
            ExpressionAttributeNames={
                "#f": Const.SANDBOX_START_TIME
            },
            ReturnValues="UPDATED_NEW"
        )

        self._logger.info("update_sandbox_start_status for sandbox_id: {sandbox_id} status: {status} is {data}"
                          .format(sandbox_id=self.sandboxid, status=sandbox_start_time, data=response))

    def getAllappNamesForInstance(self, logical_id: str):
        return self.table_data["spec"]["expected_apps"][logical_id]["apps"]

    def getAllappStatusForInstance(self, logical_id: str, instance_id: str):
        logical_instance = self.table_data["apps"][logical_id]["instances"]
        if instance_id in logical_instance:
            return logical_instance[instance_id]["apps"]
        else:
            return {}



