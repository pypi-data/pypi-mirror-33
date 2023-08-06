import os
import json
from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import DependencyEvent, Event, ExceptionEvent
from fc.cloudtrailsdk.utils.functions import configure_tracker


class CustomLogger:
    def __init__(self, app_name="", app_version="", tracker_environment=None):
        self.tracker = configure_tracker(app_name=app_name, app_version=app_version,
                                         tracker_environment=tracker_environment)

    def __call__(self, func): return lambda *args, **kwargs: self.callFunc(func, *args, **kwargs)

    def callFunc(self, func, *args, **kwargs):
        func_name = func.__name__
        r = func(*args, **kwargs)
        custom_event = Event()
        custom_event.Properties.update({
            'Method': func_name,
            'RequestPayload':  json.dumps(args),
            'ResponsePayload': json.dumps(r),
            'ResponseHttpStatus': 200
        })
        custom_event.Properties.update(kwargs)
        self.tracker.track_event(custom_event)
        return r
