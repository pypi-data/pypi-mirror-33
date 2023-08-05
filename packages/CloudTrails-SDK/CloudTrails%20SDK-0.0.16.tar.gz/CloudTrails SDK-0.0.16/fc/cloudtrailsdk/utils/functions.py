import json
import os

import sys
import traceback

from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import Event, ExceptionEvent, DependencyEvent


def configure_tracker():
    app_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "fc-notify")
    app_version = os.environ.get("APP_VERSION")
    region = os.environ.get("AWS_REGION")
    tracker_environment = os.environ.get("TRACKER_ENVIRONMENT", "eCloudTrailsStreamQA")
    tracker = Tracker(
        tracker_environment,
        region=region,
        app_name=app_name,
        app_version=app_version
    )
    return tracker


def send_custom_logger(data=None, method=""):
    tracker = configure_tracker()
    custom_event = Event()
    custom_event.Properties.update(data)
    return tracker.track_event(custom_event)

def send_exception_logger():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tracker = configure_tracker()
    exception_event = ExceptionEvent(exc_value.__str__(), exc_type.__name__, traceback.format_exc())
    tracker.track_exception(exception_event)

def send_dependency_logger(dependency_name, dependency_duration):
    tracker = configure_tracker()
    dependency_event = DependencyEvent(dependency_name, dependency_duration)
    tracker.track_dependency(dependency_event)
