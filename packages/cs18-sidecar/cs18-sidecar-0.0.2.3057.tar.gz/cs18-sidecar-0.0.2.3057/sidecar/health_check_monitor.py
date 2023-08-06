import os
import signal
import _thread
from logging import Logger
import subprocess

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.const import Const, AppInstanceConfigStatus
from sidecar.file_system import FileSystemService
from sidecar.utils import Utils


class HealthCheckMonitor:
    def __init__(self, logger: Logger, file_service: FileSystemService,
                 status_maintainer: AppStatusMaintainer):
        self._file_service = file_service
        self.logger = logger
        self._status_maintainer = status_maintainer
        self.timeout = Const.HEALTH_CHECK_TIMEOUT

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

            result = self._execute_health_check_script(app_name=app_instance_identifier.name,
                                                       ip_address=ip_address,
                                                       script_name=script_name)

            status = AppInstanceConfigStatus.COMPLETED if result else AppInstanceConfigStatus.ERROR
            self._update_status(app_instance_identifier=app_instance_identifier,
                                status=status)
        except Exception as exc:
            self.logger.exception(exc)
            raise

    def _execute_health_check_script(self,
                                     app_name: str,
                                     ip_address: str,
                                     script_name: str) -> bool:

        self.logger.info("entered '{}'".format(app_name))
        script_file_path = Const.get_health_check_file(app_name=app_name, script_name=script_name)
        command = ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=ip_address)]

        app_folder = Const.get_app_folder(app_name=app_name)
        if not self._file_service.exists(app_folder):
            self._file_service.create_folders(app_folder)

        with open(Const.get_app_log_file(app_name=app_name), 'ab', 0) as output_file:
            timestamp = Utils.get_timestamp()
            output_file.write('health-check started: {0} with command: {1}\n'.format(timestamp, command).encode())

            with subprocess.Popen(command,
                                  stdout=output_file,
                                  stderr=output_file,
                                  shell=True,
                                  preexec_fn=os.setsid) as p:
                try:
                    p.communicate(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    output_file.write('health-check: timeout after {} seconds\n'.format(self.timeout).encode())
                finally:
                    if p.returncode:
                        output_file.write('health-check: error, script exit with "{}"\n'.format(p.returncode).encode())
                        self._kill_process(p)
                    else:
                        if p.returncode == 0:
                            output_file.write('health-check: done\n'.encode())
                            return True
                        else:
                            self._kill_process(p)
                            return False

    @staticmethod
    def _kill_process(p: subprocess.Popen):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except ProcessLookupError:
            print('process already killed')
