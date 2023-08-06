import time
from logging import Logger
from typing import List, Dict

from sidecar.const import Const
from sidecar.file_system import FileSystemService


class HealthCheckPreparer:
    def __init__(self,
                 file_system: FileSystemService,
                 logger: Logger,
                 default_ports: Dict[str, List[str]] = None):
        self._file_system = file_system
        self._default_ports = default_ports
        self._logger = logger

    def prepare(self, app_name: str, script_name: str, address: str):
        self._logger.info('enter - app_name: {}, script: {}, address: {}'.format(
            app_name,
            script_name,
            address))

        if self._default_ports:
            default_ports = self._default_ports.get(app_name)
            if len(default_ports) > 0:
                app_dir = Const.get_app_folder(app_name=app_name)
                self._file_system.create_folder(app_dir)
                return self._create_default_health_check_script(default_ports=default_ports,
                                                                address=address,
                                                                app_name=app_name)

        script_file_path = Const.get_health_check_file(app_name=app_name, script_name=script_name)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=address)]

    def _create_default_health_check_script(self,
                                            default_ports: List[str],
                                            app_name: str,
                                            address: str):
        self._logger.info('enter - app: {}, ports: {}, address: {}'.format(
            app_name,
            ", ".join([str(default_port) for default_port in default_ports]),
            address))

        script_file_path = Const.get_health_check_file(app_name=app_name,
                                                       script_name="default-{0}-hc-{1}.sh".
                                                       format(app_name, str(time.time())))
        lines = list()

        lines.append('#!/bin/bash\n')
        lines.append('ip=$1\n')
        for port_to_test in default_ports:
            lines.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), address))
            lines.append(
                'until bash -c "</dev/tcp/$ip/{0}"; [[ "$?" -eq "0" ]];\n'.format(str(port_to_test)))
            lines.append('   do sleep 5;\n')
            lines.append(
                "echo 'Testing connectivity to port: {0} on private ip {1}'\n".format(str(port_to_test), address))
            lines.append('done;\n')
            lines.append("echo 'tested port {0}'\n".format(str(port_to_test)))
        self._file_system.write_lines_to_file(path=script_file_path, lines=lines, chmod=0o777)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=address)]