from functools import wraps

import sys

import os

from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import ExceptionEvent


def exception_logger(*params_args, **params_kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            try:
                response = f(*args, **kwargs)
                return response
            except Exception as e:
                aws_access_key_id = params_kwargs.get('ct_aws_access_key_id',
                                                      os.environ.get("CT_AWS_ACCESS_KEY_ID", "AKIAJRTLLEJZH4IHID7Q"))
                aws_secret_access_key = params_kwargs.get('ct_aws_secret_access_key',
                                                          os.environ.get("CT_AWS_SECRET_ACCESS_KEY",
                                                                         "nnJgGu8BUMBoDTjNmNBhe1jqk9FFWJhdpGbIkfsj"))
                aws_region = params_kwargs.get('ct_aws_region', os.environ.get("CT_AWS_REGION", "us-east-1"))

                credentials = {
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                }

                tracker = Tracker(
                    "eCloudTrailsStreamQA",
                    credentials=credentials,
                    region=aws_region,
                    app_name=params_kwargs.get('app_name'),
                    app_version=params_kwargs.get('app_version')
                )

                exception_event = ExceptionEvent(*sys.exc_info())
                tracker.track_exception(exception_event)

        return wrapper

    return decorator
