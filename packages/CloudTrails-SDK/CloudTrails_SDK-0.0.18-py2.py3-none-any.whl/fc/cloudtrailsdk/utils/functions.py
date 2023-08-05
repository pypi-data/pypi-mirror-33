import json
import os

import sys
import traceback

from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import Event, ExceptionEvent, DependencyEvent


def configure_tracker(app_name="", app_version="", tracker_environment=None):
    region = os.environ.get("AWS_REGION")
    tracker_environment = os.environ.get("TRACKER_ENVIRONMENT",
                                         "eCloudTrailsStreamQA") if tracker_environment is None else tracker_environment
    tracker = Tracker(
        tracker_environment,
        region=region,
        app_name=app_name,
        app_version=app_version
    )
    return tracker


def send_custom_logger(app_name="", app_version="", tracker_environment=None, **properties):
    tracker = configure_tracker(app_name=app_name, app_version=app_version,
                                tracker_environment=tracker_environment)
    custom_event = Event()
    custom_event.Properties.update(properties)
    return tracker.track_event(custom_event)


def send_exception_logger(app_name="", app_version="", tracker_environment=None, **properties):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tracker = configure_tracker(app_name=app_name, app_version=app_version,
                                tracker_environment=tracker_environment)
    exception_event = ExceptionEvent(exc_value.__str__(), exc_type.__name__, traceback.format_exc())
    tracker.track_exception(exception_event)


def send_dependency_logger(dependency_name, dependency_duration):
    tracker = configure_tracker()
    dependency_event = DependencyEvent(dependency_name, dependency_duration)
    tracker.track_dependency(dependency_event)
