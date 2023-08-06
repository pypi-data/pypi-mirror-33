import os
import signal
import _thread
from datetime import datetime
from logging import Logger
import subprocess

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.cloud_logger import ICloudLogger, LogEntry
from sidecar.const import Const, AppInstanceConfigStatus
from sidecar.utils import Utils

HEALTH_CHECK_TOPIC = "healthcheck"


class HealthCheckMonitor:
    def __init__(self, logger: Logger, cloud_logger: ICloudLogger,
                 status_maintainer: AppStatusMaintainer, apps_env: dict=None):
        self.logger = logger
        self.cloud_logger = cloud_logger
        self._status_maintainer = status_maintainer
        self.timeout = Const.HEALTH_CHECK_TIMEOUT
        self.apps_env = {} if apps_env is None else apps_env

    def start(self, ip_address: str, app_instance_identifier: AppInstanceIdentifier, script_name: str):
        self.logger.info("entered '{}'".format(app_instance_identifier.name))
        _thread.start_new_thread(self._process_health_check, (ip_address, app_instance_identifier, script_name))

    def _update_status(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        self._status_maintainer.update_status(app_instance_identifier=app_instance_identifier,
                                              status=status)

    def _process_health_check(self, ip_address: str, app_instance_identifier: AppInstanceIdentifier, script_name: str):
        try:
            self._update_status(app_instance_identifier=app_instance_identifier,
                                status=AppInstanceConfigStatus.PENDING)

            result = self._execute_health_check_script(app=app_instance_identifier,
                                                       ip_address=ip_address,
                                                       script_name=script_name)

            status = AppInstanceConfigStatus.COMPLETED if result else AppInstanceConfigStatus.ERROR
            self._update_status(app_instance_identifier=app_instance_identifier,
                                status=status)
        except Exception as exc:
            self.logger.exception(exc)
            raise

    def _execute_health_check_script(self,
                                     app: AppInstanceIdentifier,
                                     ip_address: str,
                                     script_name: str) -> bool:

        self.logger.info("entered '{}'".format(app.name))
        script_file_path = Const.get_health_check_file(app_name=app.name, script_name=script_name)
        command = ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=ip_address)]

        timestamp = Utils.get_timestamp()
        line = 'health-check started: {0} with command: {1}'.format(timestamp, command)
        log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC, [(datetime.utcnow(), line)])
        self.cloud_logger.write(log_entry)

        # get process environment variables and mix them with user defined application specific environment
        # variables
        app_env = self.apps_env.get(app.name)
        env = {**os.environ, **({} if app_env is None else app_env)}

        # run healthcheck command in subprocess and redirect its outputs to subprocess' stdout
        # read stdout line by line until subprocess ended or until timeout and send it to cloud logger
        # if timeout occurred kill healthcheck subprocess

        start = datetime.now()

        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              preexec_fn=os.setsid,
                              universal_newlines=True,
                              env=env) as p:
            try:
                while True:
                    line = p.stdout.readline()
                    if len(line) == 0 and p.poll() is not None:
                        break

                    log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC, [(datetime.utcnow(), line[:-1])])
                    self.cloud_logger.write(log_entry)

                    elapsed = datetime.now() - start
                    if elapsed.total_seconds() > self.timeout:
                        raise subprocess.TimeoutExpired(cmd=command, timeout=self.timeout)

            except subprocess.TimeoutExpired as ex:
                line = 'health-check: timeout after {} seconds'.format(ex.timeout)
                log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC, [(datetime.utcnow(), line)])
                self.cloud_logger.write(log_entry)
                self._kill_process(p)

            finally:
                if p.returncode == 0:
                    log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC,
                                         [(datetime.utcnow(), 'health-check: done')])
                    self.cloud_logger.write(log_entry)
                    return True
                else:
                    return False

    @staticmethod
    def _kill_process(p: subprocess.Popen):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except ProcessLookupError:
            print('process already killed')
