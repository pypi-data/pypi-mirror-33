import json
import logging
import os
from typing import List

from flask import Flask, request
from flask import jsonify

from sidecar.app_configuration_start_policy import AppConfigurationStartPolicy
from sidecar.app_request_info import AppRequestInfo
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_session import AwsSession
from sidecar.aws_status_updater import AwsStatusUpdater
from sidecar.aws_sandbox_start_time_updater import AwsSandboxStartTimeUpdater
from sidecar.const import Const, DateTimeProvider, AppInstanceConfigStatus
from sidecar.file_system import FileSystemService
from sidecar.health_check_monitor import HealthCheckMonitor
from sidecar.kub_api_service import KubApiService
from sidecar.kubernetes_status_updater import KubernetesStatusUpdater
from sidecar.kub_sandbox_start_time_updater import KubSandboxStartTimeUpdater
from sidecar.kub_token_provider import KubTokenProvider
from sidecar.utils import Utils

app = Flask(__name__)
logger = None
_health_check_monitor = None
_app_configuration_start_policy = None
_status_updater = None


def _convert_apps_json_to_app_requests(apps_json: dict()) -> List[AppRequestInfo]:
    # TODO: remove the conditional assignment once all branches are up-to-date with issue #95
    app_requests = [AppRequestInfo(name=app_name,
                                   instances_count=app_value["instances_count"] if isinstance(app_value, dict) else app_value,
                                   app_dependencies=app_value["dependencies"] if isinstance(app_value, dict) else [])
                    for app_name, app_value in apps_json.items()]
    return app_requests


def get_status_updater():
    try:
        with open(Const.get_config_file(), 'r') as conf:
            config_json = json.loads(conf.read())

            provider = config_json["provider"]
            sandbox_id = config_json['sandbox_id']
            apps_json = config_json['apps']
            app_requests = _convert_apps_json_to_app_requests(apps_json=apps_json)
            apps_configuration_end_tracker = AppsConfigurationEndTracker(logger=logger, app_requests=app_requests)
            app_configuration_start_policy = AppConfigurationStartPolicy(apps_configuration_end_tracker, app_requests)
            if provider == "kubernetes":
                kub_token_provider = KubTokenProvider()
                hostname = config_json['kub_api_address']
                kas = KubApiService(hostname=hostname, namespace=sandbox_id, kub_token_provider=kub_token_provider)

                sandbox_start_time_updater = KubSandboxStartTimeUpdater(
                    date_time_provider=DateTimeProvider(),
                    logger=logger,
                    kub_api_service=kas,
                    apps_configuration_end_tracker=apps_configuration_end_tracker)
                return KubernetesStatusUpdater(logger=logger,
                                               kub_api_service=kas,
                                               sandbox_start_time_updater=sandbox_start_time_updater,
                                               apps_configuration_end_tracker=apps_configuration_end_tracker), \
                       app_configuration_start_policy

            if provider == "aws":
                region_name = config_json['region_name']
                aws_session = AwsSession(region_name=region_name)
                sandbox_start_time_updater = AwsSandboxStartTimeUpdater(sandbox_id=sandbox_id, aws_session=aws_session,
                                                                        date_time_provider=DateTimeProvider(),
                                                                        logger=logger,
                                                                        apps_configuration_end_tracker=apps_configuration_end_tracker)
                return AwsStatusUpdater(sandbox_id=sandbox_id,
                                        logger=logger,
                                        apps_configuration_end_tracker=apps_configuration_end_tracker,
                                        sandbox_start_time_updater=sandbox_start_time_updater,
                                        aws_session=aws_session), \
                       app_configuration_start_policy

            raise Exception('unknown provider {}'.format(provider))
    except Exception as exc:
        logger.exception(exc)
        raise exc


@app.route("/")
def hello():
    logger.info("start")
    return "welcome cs18:sidecar-api"


@app.route("/application/<string:app_name>/health-check", methods=['POST'])
def start_health_check(app_name: str):
    logger.info("start")
    # noinspection PyBroadException
    try:
        ip_address = request.remote_addr
        req = request.get_json()
        script_name = req['script']
        additional_data = req.get('additional_data')

        logger.info("start_health_check for app '{}', request: {}, address: {}".format(app_name, req, ip_address))
        _health_check_monitor.start(ip_address=ip_address, app_name=app_name, script_name=script_name,
                                    additional_data=additional_data)

        # fail here if validation fails ONLY
        return jsonify(success=True), 202
    except Exception as exc:
        logger.exception(exc)
        return jsonify(success=False, error=str(exc)), 401


@app.route("/application/<string:app_name>/log", methods=['GET'])
def get_application_log(app_name: str):
    logger.info("start")
    # noinspection PyBroadException
    try:
        log = Utils.read_log(app_name=app_name)
        return jsonify(success=True, log=log), 200
    except FileNotFoundError as exc:
        logger.exception(exc)
        return jsonify(success=False, error="log for app {} was not found".format(app_name)), 400
    except Exception as exc:
        logger.exception(exc)
        return jsonify(success=False, error=str(exc)), 401


@app.route("/application/<string:app_name>/config-start-status", methods=['GET'])
def get_application_configuration_start_status(app_name: str):
    logger.info("start")
    try:
        start_status = _app_configuration_start_policy.get_app_configuration_start_status(app_name)
        return start_status, 200
    except Exception as exc:
        logger.exception(exc)
        return str(exc), 500


@app.route("/application/<string:app_name>/config-end-status", methods=['POST'])
def set_application_configuration_end_status(app_name: str):
    logger.info("start")
    try:
        ip_address = request.remote_addr
        data_json = request.get_json()
        status = data_json['status']
        additional_data = data_json.get('additional_data')

        if not AppInstanceConfigStatus.is_end_status(status):
            error_message = "'{STATUS}' is not one of the allowed configuration end statuses".format(STATUS=status)
            return jsonify(success=False, error=error_message), 400
        _status_updater.update_status(name=app_name, ip_address=ip_address, additional_data=additional_data,
                                      status=status)

        return jsonify(success=True), 200
    except Exception as exc:
        logger.exception(exc)
        return jsonify(success=False, error=str(exc)), 500


def run():
    global _health_check_monitor
    global logger
    global _app_configuration_start_policy
    global _status_updater
    # logger definitions
    logger = logging.getLogger('sidecar-api')
    hdlr = logging.FileHandler(Const.get_log_file())
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s -> %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    _status_updater, _app_configuration_start_policy = get_status_updater()
    _health_check_monitor = HealthCheckMonitor(updater=_status_updater, logger=logger,
                                               file_service=FileSystemService())
    # server startstatus_updater
    app.run(host='0.0.0.0', port=4000)


def configure_debug():
    # create log folder: ~/sidecar
    api_log_folder = os.path.dirname(Const.get_log_file())
    file_system = FileSystemService()
    if not file_system.exists(api_log_folder):
        file_system.create_folders(api_log_folder)

    # setup the config file
    apps_json = {
        "myApp": 1
    }
    # apps_json = {
    #     "myApp": {
    #         "instances_count": 1,
    #         "dependencies": ["app2"]
    #     },
    #     "app2":{
    #         "instances_count": 1,
    #         "dependencies": []
    #     }
    # }
    config_file_content = {
        "provider": "aws",
        "sandbox_id": "17011808-85AD-4D83-9AAB-4E21442BFF97",  # can set it to an existing sandbox
        # "kub_api_address": "https://35.197.122.51",
        "region_name": "eu-west-2",
        "apps": apps_json
    }
    with open(Const.get_config_file(), "w") as conf_file:
        conf_file.write(json.dumps(config_file_content))


if __name__ == "__main__":
    # configure_debug()
    run()
