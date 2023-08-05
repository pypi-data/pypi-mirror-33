import traceback
from functools import wraps

import sys

from fc.cloudtrailsdk.execptions import ExceptionTracker
from fc.cloudtrailsdk.model.event import ExceptionEvent
from fc.cloudtrailsdk.utils.functions import configure_tracker


def exception_logger(*params_args, **params_kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            try:
                response = f(*args, **kwargs)
                return response
            except Exception as e:
                exc_type, exc_value, exc_traceback= sys.exc_info()
                tracker = configure_tracker()
                exception_event = ExceptionEvent(exc_value.__str__(), exc_type.__name__, traceback.format_exc())
                tracker.track_exception(exception_event)
                raise ExceptionTracker(e)
        return wrapper
    return decorator
