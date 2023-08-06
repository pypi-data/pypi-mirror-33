import os
import signal
import subprocess
from datetime import datetime
from logging import Logger
from typing import List, Dict

from sidecar.app_instance_identifier import IIdentifier
from sidecar.health_check.health_check_executor_logger import HealthCheckExecutorLogger
from sidecar.non_blocking_stream_reader import NonBlockingStreamReader


class HealthCheckExecutor:

    def __init__(self,
                 env_vars: Dict[str, str],
                 app_timeouts: Dict[str, int],
                 executor_logger: HealthCheckExecutorLogger,
                 logger: Logger):
        self._executor_logger = executor_logger
        self._app_timeouts = app_timeouts
        self._env_vars = env_vars
        self._logger = logger

    def start(self,
              identifier: IIdentifier,
              cmd: List[str]) -> bool:

        self._logger.info('enter - identifier: {}, cmd: {}'.format(
            identifier,
            ", ".join(cmd)))

        timeout = self._app_timeouts.get(identifier.name)
        self._executor_logger.log_start(identifier=identifier, cmd=cmd, timeout=timeout)

        env = self._get_env_vars(identifier)

        start = datetime.now()
        timed_out = False
        read_interval = 0.5

        # run healthcheck command in subprocess and redirect its outputs to subprocess' stdout
        # read stdout line by line until subprocess ended or until timeout and send it to cloud logger
        # if timeout occurred kill healthcheck subprocess
        with subprocess.Popen(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              preexec_fn=os.setsid,
                              universal_newlines=True,
                              env=env) as p:
            try:
                stdout_stream_reader = NonBlockingStreamReader(stream=p.stdout, interval=read_interval)
                stderr_stream_reader = NonBlockingStreamReader(stream=p.stderr, interval=read_interval)
                self._logger.info('running command {0}'.format(cmd))

                while True:
                    line = stdout_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier)

                    line = stderr_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier, True)

                    elapsed = datetime.now() - start

                    if elapsed.total_seconds() > timeout:
                        stdout_stream_reader.stop()
                        stderr_stream_reader.stop()
                        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

                    if p.poll() is not None:
                        while True:
                            line = stdout_stream_reader.read_line(read_interval)
                            if line:
                                self._executor_logger.log_line(line, identifier)
                            else:
                                stdout_stream_reader.stop()
                                break

                        while True:
                            line = stderr_stream_reader.read_line(read_interval)
                            if line:
                                self._executor_logger.log_line(line, identifier, True)
                            else:
                                stderr_stream_reader.stop()
                                break
                        break
            except subprocess.TimeoutExpired as ex:
                self._executor_logger.log_timeout(timeout=ex.timeout, identifier=identifier)
                self._kill_process(identifier=identifier, process=p)
                timed_out = True
            finally:
                if timed_out:
                    return False
                process_exit_code = p.returncode
                if process_exit_code == 0:
                    self._executor_logger.log_success(identifier=identifier)
                    return True
                else:
                    self._executor_logger.log_error(identifier=identifier, exit_code=process_exit_code)
                    return False

    def _kill_process(self, identifier, process):
        self._logger.info('enter - identifier: {}, p: {}'.format(identifier, process))
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError as ex:
            self._logger.exception('Could not kill process, pid {} due to {}'.format(
                process.pid,
                str(ex)))

    def _get_env_vars(self, identifier):
        self._logger.info('enter - identifier: {}'.format(identifier))

        # get process environment variables and mix them with user defined application specific environment
        # variables
        app_env = self._env_vars.get(identifier.name)
        return {**os.environ, **({} if app_env is None else app_env)}
