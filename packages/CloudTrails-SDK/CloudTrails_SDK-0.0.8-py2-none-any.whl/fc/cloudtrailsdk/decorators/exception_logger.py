from functools import wraps

import sys


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
                tracker = configure_tracker()
                exception_event = ExceptionEvent(*sys.exc_info())
                tracker.track_exception(exception_event)
                raise
        return wrapper
    return decorator
