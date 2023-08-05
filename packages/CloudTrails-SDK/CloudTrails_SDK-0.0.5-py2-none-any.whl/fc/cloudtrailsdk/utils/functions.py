import os

from fc.cloudtrailsdk.client.tracker import Tracker


def configure_tracker():
    credentials = {
            'aws_access_key_id': os.environ.get("AWS_ACCESS_KEY_ID"),
            'aws_secret_access_key': os.environ.get("AWS_SECRET_ACCESS_KEY")
        }
    app_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "fc-notify")
    app_version = os.environ.get("APP_VERSION")
    region = os.environ.get("AWS_REGION")
    tracker_environment = os.environ.get("TRACKER_ENVIRONMENT","eCloudTrailsStreamQA")
    tracker = Tracker(
        tracker_environment,
        credentials=credentials,
        region=region,
        app_name=app_name,
        app_version=app_version
    )
    return tracker