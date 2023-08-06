import boto3
from typing import Dict
from threading import Lock
from ..logs import LogEntry, ICloudLogger
from .stream_writer import CloudWatchStreamWriter


class CloudWatchLogger(ICloudLogger):
    def __init__(self, config: dict):
        region = config["region_name"]
        sandbox = config["sandbox_id"]
        self.logs = boto3.client('logs', region_name=region)
        self.group_name = "/colony/sandboxes/{sandbox}".format(sandbox=sandbox)
        self._stream_writers = dict()  # type: Dict[str, CloudWatchStreamWriter]
        self._lock = Lock()

    def _get_writer(self, log_entry: LogEntry) -> CloudWatchStreamWriter:
        stream_name = "/{0}/{1}/{2}".format(log_entry.app, log_entry.instance, log_entry.topic)
        writer = self._stream_writers.get(stream_name)
        if writer is None:
            with self._lock:
                writer = self._stream_writers.get(stream_name)
                if writer is None:
                    writer = CloudWatchStreamWriter(self.logs, self.group_name, stream_name)
                self._stream_writers[stream_name] = writer
        return writer

    def write(self, log_entry: LogEntry):
        writer = self._get_writer(log_entry)
        writer.write(log_entry.log_events)
