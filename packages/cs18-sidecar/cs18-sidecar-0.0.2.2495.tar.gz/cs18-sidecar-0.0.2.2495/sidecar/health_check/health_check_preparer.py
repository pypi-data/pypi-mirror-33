import os

import time
from logging import Logger
from typing import List, Dict

from sidecar.app_instance_identifier import IIdentifier
from sidecar.const import Const


class HealthCheckPreparer:
    def __init__(self,
                 logger: Logger,
                 default_ports: Dict[str, List[str]] = None):
        self._default_ports = default_ports
        self._logger = logger

    def prepare(self, identifier, script_name: str, address: str):
        identifier = identifier  # type: IIdentifier
        self._logger.info('enter - identifier: {}, script: {}, address: {}'.format(
            identifier,
            script_name,
            address))

        if self._default_ports:
            default_health_check_ports_to_test = self._default_ports.get(identifier.name)
            if len(default_health_check_ports_to_test) > 0:
                app_dir = Const.get_app_folder(app_name=identifier.name)
                if not os.path.exists(app_dir):
                    os.makedirs(app_dir)
                return self._create_default_health_check_script(default_health_check_ports_to_test,
                                                                address,
                                                                identifier.name)

        script_file_path = Const.get_health_check_file(app_name=identifier.name, script_name=script_name)
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
        with open(script_file_path, "w+") as default_health_check_file:
            default_health_check_file.writelines(lines)
        os.chmod(script_file_path, 0o777)
        return ['{script_file_path} {ip_address}'.format(
            script_file_path=script_file_path,
            ip_address=address)]