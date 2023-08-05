import os

from fc.cloudtrailsdk.client.tracker import Tracker


def configure_tracker():
    app_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "fc-notify")
    app_version = os.environ.get("APP_VERSION")
    region = os.environ.get("AWS_REGION")
    tracker_environment = os.environ.get("TRACKER_ENVIRONMENT","eCloudTrailsStreamQA")
    tracker = Tracker(
        tracker_environment,
        region=region,
        app_name=app_name,
        app_version=app_version
    )
    return tracker