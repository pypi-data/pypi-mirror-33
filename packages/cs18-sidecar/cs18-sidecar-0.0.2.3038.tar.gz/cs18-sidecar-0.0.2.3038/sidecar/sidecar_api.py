import json
import logging
import os
from typing import List

from datetime import datetime
from flask import Flask, request
from flask import jsonify

from sidecar.app_configuration_start_policy import AppConfigurationStartPolicy
from sidecar.app_instance_config_status_event_reporter import AppInstanceConfigStatusEventReporter
from sidecar.app_instance_event_handler import AppInstanceEventHandler
from sidecar.app_instance_events import AppInstanceEvents
from sidecar.app_instance_identifier_creator import IAppInstanceIdentifierCreator
from sidecar.app_request_info import AppRequestInfo
from sidecar.app_status_maintainer import AppStatusMaintainer
from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker
from sidecar.aws_app_instance_identifier_creator import AwsAppInstanceIdentifierCreator
from sidecar.aws_app_instance_service import AwsAppInstanceService
from sidecar.aws_sandbox_start_time_updater import AwsSandboxStartTimeUpdater
from sidecar.aws_sandbox_deployment_end_updater import AwsSandboxDeploymentEndUpdater
from sidecar.aws_session import AwsSession
from sidecar.aws_vpc_service import AwsVpcService
from sidecar.cloud_logger import ICloudLogger, LogEntry
from sidecar.const import Const, DateTimeProvider
from sidecar.file_system import FileSystemService
from sidecar.health_check_monitor import HealthCheckMonitor
from sidecar.kub_api_service import KubApiService
from sidecar.kub_app_instance_identifier_creator import KubAppInstanceIdentifierCreator
from sidecar.kub_app_instance_service import KubAppInstanceService
from sidecar.kub_sandbox_start_time_updater import KubSandboxStartTimeUpdater
from sidecar.kub_sandbox_deployment_end_updater import KubSandboxDeploymentEndUpdater
from sidecar.kub_token_provider import KubTokenProvider
from sidecar.messaging_service import MessagingService, MessagingConnectionProperties
from sidecar.sandbox_deployment_state_tracker import SandboxDeploymentStateTracker
from sidecar.aws_status_maintainer import AWSStatusMaintainer

app = Flask(__name__)
logger = None  # type: logging.Logger
cloud_logger = None  # type: ICloudLogger
_health_check_monitor = None  # type: HealthCheckMonitor
_app_configuration_start_policy = None  # type: AppConfigurationStartPolicy
_app_instance_identifier_creator = None  # type: IAppInstanceIdentifierCreator
_app_instance_event_handler = None  # type: AppInstanceEventHandler



def _load_config():
    with open(Const.get_config_file(), 'r') as conf:
        config_json = json.loads(conf.read())
        return config_json


def _convert_messaging_json_to_connection_props(messaging_json: dict()) -> MessagingConnectionProperties:

    return MessagingConnectionProperties(messaging_json["host"], messaging_json["user"], messaging_json["password"],
                                         messaging_json["queue"], messaging_json["exchange"], messaging_json["routingkey"],
                                         messaging_json["virtualhost"], messaging_json["port"], messaging_json["queuetype"])


def _convert_apps_json_to_app_requests(apps_json: dict()) -> List[AppRequestInfo]:
    # TODO: remove the conditional assignment once all branches are up-to-date with issue #95
    app_requests = [AppRequestInfo(name=app_name,
                                   instances_count=app_value["instances_count"] if isinstance(app_value,
                                                                                              dict) else app_value,
                                   app_dependencies=app_value["dependencies"] if isinstance(app_value, dict) else [])
                    for app_name, app_value in apps_json.items()]
    return app_requests


def _get_apps_environment_variables(config_json: dict) -> dict:
    env = {app_name: app_config["env"] for app_name, app_config in config_json["apps"].items()}
    return env


def get_status_updater(config_json, app_instance_event_handler: AppInstanceEventHandler):
    try:
        provider = config_json["provider"]
        sandbox_id = config_json['sandbox_id']
        space_id = config_json['space_id']
        apps_json = config_json['apps']
        app_requests = _convert_apps_json_to_app_requests(apps_json=apps_json)

        messaging_props = _convert_messaging_json_to_connection_props(config_json['messaging'])

        messaging_service = MessagingService(messaging_props, logger)

        app_instance_status_event_reporter = AppInstanceConfigStatusEventReporter(
            app_instance_event_handler=app_instance_event_handler)
        if provider == "kubernetes":
            kub_token_provider = KubTokenProvider()
            hostname = config_json['kub_api_address']
            kas = KubApiService(hostname=hostname, namespace=sandbox_id, kub_token_provider=kub_token_provider)

            app_instance_service = KubAppInstanceService(logger=logger, kub_api_service=kas)
            apps_configuration_end_tracker = AppsConfigurationEndTracker(logger=logger, app_requests=app_requests,
                                                                         app_instance_service=app_instance_service)
            app_configuration_start_policy = AppConfigurationStartPolicy(apps_configuration_end_tracker,
                                                                         app_requests)

            sandbox_start_time_updater = KubSandboxStartTimeUpdater(
                date_time_provider=DateTimeProvider(),
                logger=logger,
                kub_api_service=kas,
                apps_configuration_end_tracker=apps_configuration_end_tracker)

            sandbox_deployment_end_updater = KubSandboxDeploymentEndUpdater(
                kub_api_service=kas)

            sandbox_deployment_state_tracker = SandboxDeploymentStateTracker(
                logger=logger,
                app_requests=app_requests,
                apps_configuration_end_tracker=apps_configuration_end_tracker,
                sandbox_deployment_end_updater=sandbox_deployment_end_updater,
                sandbox_id=sandbox_id,
                messaging_service=messaging_service,
                space_id=space_id)

            app_instance_identifier_creator = KubAppInstanceIdentifierCreator(kub_api_service=kas)
            status_maintainer = AppStatusMaintainer(logger=logger,
                                                    app_instance_service=app_instance_service,
                                                    apps_configuration_end_tracker=apps_configuration_end_tracker,
                                                    sandbox_deployment_state_tracker=sandbox_deployment_state_tracker,
                                                    sandbox_start_time_updater=sandbox_start_time_updater,
                                                    app_instance_status_event_reporter=app_instance_status_event_reporter)
            return status_maintainer, \
                   app_configuration_start_policy, \
                   app_instance_identifier_creator

        if provider == "aws":
            region_name = config_json['region_name']
            aws_session = AwsSession(region_name=region_name)

            aws_status_maintainer = AWSStatusMaintainer(aws_session, sandbox_id=sandbox_id)

            app_instance_service = AwsAppInstanceService(sandbox_id=sandbox_id,
                                                         logger=logger,
                                                         aws_session=aws_session,
                                                         aws_status_maintainer=aws_status_maintainer)
            apps_configuration_end_tracker = AppsConfigurationEndTracker(logger=logger, app_requests=app_requests,
                                                                         app_instance_service=app_instance_service)
            app_configuration_start_policy = AppConfigurationStartPolicy(apps_configuration_end_tracker,
                                                                         app_requests)
            aws_vpc_service = AwsVpcService(sandbox_id=sandbox_id, aws_session=aws_session)
            sandbox_start_time_updater = AwsSandboxStartTimeUpdater(
                sandbox_id=sandbox_id,
                aws_session=aws_session,
                date_time_provider=DateTimeProvider(),
                logger=logger,
                apps_configuration_end_tracker=apps_configuration_end_tracker,
                vpc_service=aws_vpc_service,
                aws_status_maintainer=aws_status_maintainer
            )

            sandbox_deployment_end_updater = AwsSandboxDeploymentEndUpdater(aws_status_maintainer)

            sandbox_deployment_state_tracker = SandboxDeploymentStateTracker(
                logger=logger,
                app_requests=app_requests,
                apps_configuration_end_tracker=apps_configuration_end_tracker,
                sandbox_deployment_end_updater=sandbox_deployment_end_updater,
                sandbox_id=sandbox_id,
                messaging_service=messaging_service,
                space_id=space_id)

            app_instance_identifier_creator = AwsAppInstanceIdentifierCreator()
            status_maintainer = AppStatusMaintainer(logger=logger,
                                                    app_instance_service=app_instance_service,
                                                    apps_configuration_end_tracker=apps_configuration_end_tracker,
                                                    sandbox_deployment_state_tracker=sandbox_deployment_state_tracker,
                                                    sandbox_start_time_updater=sandbox_start_time_updater,
                                                    app_instance_status_event_reporter=app_instance_status_event_reporter)
            return status_maintainer, \
                   app_configuration_start_policy, \
                   app_instance_identifier_creator

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
    logger.info(
        "entered with - app_name: {}, request: {}".format(app_name, request.json))
    # noinspection PyBroadException
    try:
        ip_address = request.remote_addr
        req = request.get_json()
        script_name = req['script']
        additional_data = req.get('additional_data')

        logger.info("start_health_check for app '{}', address: {}, request: {}".format(app_name, ip_address, req))
        app_instance_identifier = _app_instance_identifier_creator.create(app_name=app_name,
                                                                          ip_address=ip_address,
                                                                          additional_data=additional_data)
        logger.info("created identifier for '{APP}' on '{IP}': '{APP_ID}'"
                    .format(APP=app_name, IP=ip_address, APP_ID=app_instance_identifier))
        _health_check_monitor.start(ip_address=ip_address, app_instance_identifier=app_instance_identifier,
                                    script_name=script_name)

        # fail here if validation fails ONLY
        return jsonify(success=True), 202
    except Exception as exc:
        logger.exception(exc)
        return jsonify(success=False, error=str(exc)), 401


@app.route('/application/<app_name>/<instance_id>/logs/<topic>', methods=['POST'])
def write_log(app_name: str, instance_id: str, topic: str):
    try:
        events = [(datetime.fromtimestamp(item["date"]), item["line"]) for item in request.json]
        log_entry = LogEntry(app_name, instance_id, topic, events)
        cloud_logger.write(log_entry)

        return jsonify(success=True), 200
    except Exception as exc:
        logger.exception(
            "writing log error, entered with - app_name: {}, instance_id: {}, topic: {}, request: {}, error: {}".format(
                app_name, instance_id, topic,
                request.json, exc))
        return jsonify(success=False, error=str(exc)), 401


@app.route('/application/<string:app_name>/<string:instance_id>/event', methods=['POST'])
def report_app_instance_event(app_name: str, instance_id: str):
    logger.info(
        "entered with - app_name: {}, instance_id: {}, request: {}".format(app_name, instance_id, request.json))
    try:
        data_json = request.get_json()
        event = data_json['event']
        if event not in AppInstanceEvents.ALL:
            error_message = "'{EVENT}' is not one of the known event types".format(EVENT=event)
            return jsonify(success=False, error=error_message), 400

        app_instance_identifier = _app_instance_identifier_creator.create_from_instance_id(app_name=app_name,
                                                                                           instance_id=instance_id)
        _app_instance_event_handler.report_event(app_instance_identifier=app_instance_identifier,
                                                 app_instance_event=event)
        return jsonify(success=True), 200
    except Exception as exc:
        logger.exception(exc)
        return str(exc), 500


@app.route("/application/<string:app_name>/config-start-status", methods=['GET'])
def get_application_configuration_start_status(app_name: str):
    logger.info(
        "entered with - app_name: {}, request: {}".format(app_name, request.json))
    try:
        start_status = _app_configuration_start_policy.get_app_configuration_start_status(app_name)
        return start_status, 200
    except Exception as exc:
        logger.exception(exc)
        return str(exc), 500

def run():
    global _health_check_monitor
    global logger
    global cloud_logger
    global _app_configuration_start_policy
    global _app_instance_identifier_creator
    global _app_instance_event_handler
    # logger definitions
    logger = logging.getLogger('sidecar-api')
    hdlr = logging.FileHandler(Const.get_log_file())
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s -> %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    try:
        config_json = _load_config()

        from sidecar.cloud_logger import CloudLoggerFactory
        cloud_logger_factory = CloudLoggerFactory(config_json)
        cloud_logger = cloud_logger_factory.create_instance()

        _app_instance_event_handler = AppInstanceEventHandler(cloud_logger=cloud_logger,
                                                              date_time_provider=DateTimeProvider())

        apps_env = _get_apps_environment_variables(config_json)

        status_maintainer, _app_configuration_start_policy, _app_instance_identifier_creator = \
            get_status_updater(config_json, _app_instance_event_handler)

        _health_check_monitor = HealthCheckMonitor(logger=logger,
                                                   cloud_logger=cloud_logger,
                                                   status_maintainer=status_maintainer,
                                                   apps_env=apps_env)
    except Exception as exc:
        logger.exception(exc)
        raise exc

    # server startstatus_updater
    app.run(host='0.0.0.0', port=4000)


def configure_debug():
    # create log folder: ~/sidecar
    api_log_folder = os.path.dirname(Const.get_log_file())
    file_system = FileSystemService()
    if not file_system.exists(api_log_folder):
        file_system.create_folders(api_log_folder)

    # setup the config file
    # apps_json = {
    #     "myApp": 1
    # }
    apps_json = {
        "demoapp-server": {
            "instances_count": 1,
            "dependencies": [],
             "env":{"WELCOME_STRING": "Welcome to Quali Colony!", "PORT": "3001"},
        }
    }

    messaging_json ={
        "host": "wombat.rmq.cloudamqp.com",
        "user": "rhpjvtoj",
        "password": "M7dZ2D5hWkIEOLPj6poiB4fF1t9cmNIf",
        "queue": "sidecar_queue",
        "exchange": "",
        "routingkey": "sidecar_queue",
        "virtualhost": "rhpjvtoj",
        "port": 5672,
        "queuetype": "fanout"
    }

    config_file_content = {
        "env":"",
        "provider": "aws",
        "sandbox_id": "d229c185-39d5-4d8b-9c4c-1eb4c5d5678a",  # can set it to an existing sandbox
        # "kub_api_address": "https://35.197.122.51",
        "region_name": "eu-west-2",
        "space_id": "84a26312-90d3-4e3e-a0ea-136778623573",
        "apps": apps_json,
        "messaging": messaging_json
    }
    with open(Const.get_config_file(), "w") as conf_file:
        conf_file.write(json.dumps(config_file_content))


if __name__ == "__main__":
    #configure_debug()
    run()
