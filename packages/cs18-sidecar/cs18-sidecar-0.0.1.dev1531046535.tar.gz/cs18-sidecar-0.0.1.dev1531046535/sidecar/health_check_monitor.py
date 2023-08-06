import os
import signal
import _thread
from datetime import datetime
import time
from logging import Logger
import subprocess

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.cloud_logger import ICloudLogger, LogEntry
from sidecar.const import Const, AppInstanceConfigStatus
from sidecar.non_blocking_stream_reader import NonBlockingStreamReader
from sidecar.utils import Utils

HEALTH_CHECK_TOPIC = "healthcheck"


class HealthCheckMonitor:
    def __init__(self, logger: Logger,
                 cloud_logger: ICloudLogger,
                 status_maintainer: AppStatusMaintainer,
                 apps_timeout: dict,
                 default_health_check_ports_to_test: dict = None,
                 apps_env: dict = None):
        self.default_health_check_ports_to_test = default_health_check_ports_to_test
        self.logger = logger
        self.cloud_logger = cloud_logger
        self._status_maintainer = status_maintainer
        self.apps_env = {} if apps_env is None else apps_env
        self._apps_timeout = apps_timeout

    def start(self, ip_address: str, app_instance_identifier: AppInstanceIdentifier, script_name: str):
        self.logger.info("entered '{}'".format(app_instance_identifier.name))
        _thread.start_new_thread(self._process_health_check, (ip_address, app_instance_identifier, script_name))

    def _update_status(self, app_instance_identifier: AppInstanceIdentifier, status: str):
        self._status_maintainer.update_status(app_instance_identifier=app_instance_identifier,
                                              status=status)

    def _process_health_check(self, ip_address: str, app_instance_identifier: AppInstanceIdentifier, script_name: str):
        try:
            self.logger.info("entered '{}'".format("_process_health_check"))
            self._update_status(app_instance_identifier=app_instance_identifier,
                                status=AppInstanceConfigStatus.PENDING)

            result = self._execute_health_check_script(app=app_instance_identifier,
                                                       ip_address=ip_address,
                                                       script_name=script_name)

            status = AppInstanceConfigStatus.COMPLETED if result else AppInstanceConfigStatus.ERROR
            self._update_status(app_instance_identifier=app_instance_identifier,
                                status=status)
        except Exception as exc:
            self.logger.exception("Failed to _process_health_check for ip '{0}' exception {1}".format(ip_address, str(exc)))
            raise

    @staticmethod
    def create_default_health_check_script(default_health_check_ports_to_test, ip_address, app_name):
        script_file_path = Const.get_health_check_file(app_name=app_name,
                                                       script_name="default-{0}-hc-{1}.sh".
                                                       format(app_name, str(time.time())))
        default_healthcheck_file_content = list()

        default_healthcheck_file_content.append('#!/bin/bash\n')
        default_healthcheck_file_content.append('ip=$1\n')
        for port_to_test in default_health_check_ports_to_test:
            default_healthcheck_file_content.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), ip_address))
            default_healthcheck_file_content.append(
                'until bash -c "</dev/tcp/$ip/{0}"; [[ "$?" -eq "0" ]];\n'.format(str(port_to_test)))
            default_healthcheck_file_content.append('   do sleep 5;\n')
            default_healthcheck_file_content.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), ip_address))
            default_healthcheck_file_content.append('done;\n')
            default_healthcheck_file_content.append("echo 'tested port {0}'\n".format(str(port_to_test)))
        with open(script_file_path, "w+") as default_healthcheck_file:
            default_healthcheck_file.writelines(default_healthcheck_file_content)
        os.chmod(script_file_path, 0o777)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=ip_address)]

    def log_line(self, line: str, app: AppInstanceIdentifier, error=False):
        log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC,
                             [(datetime.utcnow(), line)])
        self._write_to_cloud_logger(log_entry)
        if error:
            self.logger.error(line)
        else:
            self.logger.info(line)

    def _execute_health_check_script(self,
                                     app: AppInstanceIdentifier,
                                     ip_address: str,
                                     script_name: str) -> bool:

        self.logger.info("entered '{}'".format(app.name))
        script_file_path = Const.get_health_check_file(app_name=app.name, script_name=script_name)
        command = ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=ip_address)]

        # get process environment variables and mix them with user defined application specific environment
        # variables
        app_env = self.apps_env.get(app.name)
        env = {**os.environ, **({} if app_env is None else app_env)}

        # run default healthcheck script instead if exists

        if self.default_health_check_ports_to_test:
            default_health_check_ports_to_test = self.default_health_check_ports_to_test.get(app.name)
            if len(default_health_check_ports_to_test) > 0:
                app_dir = Const.get_app_folder(app_name=app.name)
                if not os.path.exists(app_dir):
                    os.makedirs(app_dir)
                self.logger.info("creating default health check script")
                command = HealthCheckMonitor.create_default_health_check_script(default_health_check_ports_to_test,
                                                                                ip_address,
                                                                                app.name)

        timestamp = Utils.get_timestamp()
        line = 'health-check started: {0} with command: {1}'.format(timestamp, command)
        log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC, [(datetime.utcnow(), line)])
        self._write_to_cloud_logger(log_entry)
        self.logger.info(log_entry.get_as_string())

        # run healthcheck command in subprocess and redirect its outputs to subprocess' stdout
        # read stdout line by line until subprocess ended or until timeout and send it to cloud logger
        # if timeout occurred kill healthcheck subprocess

        start = datetime.now()
        timeout = self._apps_timeout.get(app.name)
        self.logger.info('the timeout for app {0} is {1}'.format(app.name, timeout))
        self.logger.info('the ip for app {0} is {1}'.format(app.name, ip_address))

        timed_out = False

        read_interval = 0.5

        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              preexec_fn=os.setsid,
                              universal_newlines=True,
                              env=env) as p:
            try:
                stdout_stream_reader = NonBlockingStreamReader(stream=p.stdout, interval=read_interval)
                stderr_stream_reader = NonBlockingStreamReader(stream=p.stderr, interval=read_interval)
                self.logger.info('running command {0}'.format(command))

                while True:
                    line = stdout_stream_reader.read_line(read_interval)
                    if line:
                        self.log_line(line, app)
                    line = stderr_stream_reader.read_line(read_interval)
                    if line:
                        self.log_line(line, app, True)
                    elapsed = datetime.now() - start
                    if elapsed.total_seconds() > timeout:
                        stdout_stream_reader.stop()
                        stderr_stream_reader.stop()
                        raise subprocess.TimeoutExpired(cmd=command, timeout=timeout)
                    if p.poll() is not None:
                        while True:
                            line = stdout_stream_reader.read_line(read_interval)
                            if line:
                                self.log_line(line, app)
                            else:
                                stdout_stream_reader.stop()
                                break

                        while True:
                            line = stderr_stream_reader.read_line(read_interval)
                            if line:
                                self.log_line(line, app, True)
                            else:
                                stderr_stream_reader.stop()
                                break
                        break

            except subprocess.TimeoutExpired as ex:
                line = 'health-check: timed out for app {0} after {1} seconds'.format(app.name, ex.timeout)
                log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC, [(datetime.utcnow(), line)])
                self.logger.info(log_entry.get_as_string())
                self._write_to_cloud_logger(log_entry)
                timed_out = True
                self._kill_process(p, logger=self.logger)

            finally:
                if timed_out:
                    return False
                process_exit_code = p.returncode
                if process_exit_code == 0:
                    log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC,
                                         [(datetime.utcnow(), 'health-check: done')])
                    self._write_to_cloud_logger(log_entry)
                    self.logger.info('Healthcheck succeeded for app {0}'.format(app.name))
                    return True
                else:
                    log_entry = LogEntry(app.name, app.infra_id, HEALTH_CHECK_TOPIC,
                                         [(datetime.utcnow(), 'health-check: failed with error {0}'.format(process_exit_code))])
                    self._write_to_cloud_logger(log_entry)
                    self.logger.info('Healthcheck failed for app {0} with error {1}'.format(app.name, process_exit_code))
                    return False

    @staticmethod
    def _kill_process(p: subprocess.Popen, logger: Logger):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except ProcessLookupError:
            logger.exception('Could not kill process, pid: ' + p.pid)

    def _write_to_cloud_logger(self, log_entry: LogEntry):
        try:
            self.cloud_logger.write(log_entry)
        except Exception:
            self.logger.exception("Failed to register log entry " + log_entry.get_as_string())

