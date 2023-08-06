from datetime import datetime
from typing import List, Tuple
from threading import Lock


class CloudWatchStreamWriter(object):

    def __init__(self, logs_client, group_name: str, stream_name: str):
        self.logs_client = logs_client
        self.group_name = group_name
        self.stream_name = stream_name
        self._sequence_token = None
        self._lock = Lock()
        self._init_stream()

    def _init_stream(self):
        try:
            # check if logging group already exist
            log_groups = self.logs_client.describe_log_groups(logGroupNamePrefix=self.group_name)
            if len(log_groups['logGroups']) == 0:
                # if logging group not exists create it and set retention for 30 days
                self.logs_client.create_log_group(logGroupName=self.group_name)
                self.logs_client.put_retention_policy(logGroupName=self.group_name, retentionInDays=30)

            # check if stream already exist
            log_streams = self.logs_client.describe_log_streams(logGroupName=self.group_name,
                                                                logStreamNamePrefix=self.stream_name)
            if len(log_streams['logStreams']) == 0:
                # if not exists create the stream
                response = self.logs_client.create_log_stream(logGroupName=self.group_name,
                                                              logStreamName=self.stream_name)

                log_streams = self.logs_client.describe_log_streams(logGroupName=self.group_name,
                                                                    logStreamNamePrefix=self.stream_name)

            log_stream = log_streams['logStreams'][0]
            self._sequence_token = log_stream.get('uploadSequenceToken') or "0"
        except Exception as ex:
            print(ex)
            raise

    @staticmethod
    def _fix_empty_string(string: str) -> str:
        if len(string) == 0:
            return " "
        return string

    def write(self, log_events: List[Tuple[datetime, str]]):
        """Write log events to AWS CloudWatch Logs service

        Args:
            log_events: list of tuples containing timestamp and log message
        """
        try:
            events = [
                {
                    'timestamp': int(time.timestamp() * 1000),
                    'message': self._fix_empty_string(message)
                } for time, message in log_events]

            with self._lock:
                result = self.logs_client.put_log_events(logGroupName=self.group_name,
                                                         logStreamName=self.stream_name,
                                                         logEvents=events,
                                                         sequenceToken=self._sequence_token)
                if "rejectedLogEventsInfo" in result:
                    raise Exception(result["rejectedLogEventsInfo"])

                self._sequence_token = result['nextSequenceToken']

        except Exception as ex:
            print(ex)
            raise
