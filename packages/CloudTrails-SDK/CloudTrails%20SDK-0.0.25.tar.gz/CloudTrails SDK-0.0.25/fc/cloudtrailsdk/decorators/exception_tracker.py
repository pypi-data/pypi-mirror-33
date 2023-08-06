import logging
import traceback
from functools import wraps
import sys
from fc.cloudtrailsdk.model.event import ExceptionEvent
from fc.cloudtrailsdk.utils.functions import configure_tracker

logger = logging.getLogger(__name__)


def exception_logger(*params_args, **params_kwargs):
    def decorator(f, *f_args, **f_kwargs):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                response = f(*args, **kwargs)
                return response
            except Exception as e:
                try:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    app_name = params_kwargs.get("app_name", "")
                    app_version = params_kwargs.get("app_version", "")
                    tracker_environment = params_kwargs.get("tracker_environment", None)
                    tracker = configure_tracker(app_name=app_name, app_version=app_version,
                                                tracker_environment=tracker_environment)

                    exception_event = ExceptionEvent(exc_value.__str__(), exc_type.__name__, traceback.format_exc())
                    tracker.track_exception(exception_event)
                    logger.error(e.message)
                except Exception as e:
                    logger.error(e.message)



        return wrapper

    return decorator
