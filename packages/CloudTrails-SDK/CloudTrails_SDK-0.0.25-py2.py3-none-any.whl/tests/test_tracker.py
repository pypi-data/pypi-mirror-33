import json
from faker import Faker
from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import DependencyEvent, Event, ExceptionEvent
from fc.cloudtrailsdk.utils.functions import send_custom_logger, send_exception_logger
from tests.conftest import customer_kwargs

__author__ = 'Yaisel Hurtado <hurta2yaisel@gmail.com>'
__date__ = '15/06/18'

fake = Faker()


class TestTracker(object):
    pass


def main():
    try:
        credentials = {
            'aws_access_key_id': "AKIAJRTLLEJZH4IHID7Q",
            'aws_secret_access_key': "nnJgGu8BUMBoDTjNmNBhe1jqk9FFWJhdpGbIkfsj"
        }
        tracker = Tracker(
            "eCloudTrailsStreamQA",
            credentials=credentials,
            region='us-east-1',
            app_name=fake.name(),
            app_version=fake.building_number()
        )
        customer = customer_kwargs()
        tracker.dimensions.update({
            'Customer': customer['name']
        })

        custom_event = Event()
        custom_event.Properties.update({
            'Method': 'Register',
            'RequestPayload': json.dumps(customer_kwargs()),
            'ResponsePayload': json.dumps({"status": "ok"}),
            'ResponseHttpStatus': 200
        })
        tracker.track_event(custom_event)

        print("Tracked Event")

        dependency_event = DependencyEvent("webhook01", 3000)
        tracker.track_dependency(dependency_event)
        print("Tracked Dependency")

        exception_event = ExceptionEvent(
            "Mensaje de error", "Tipo de Excepcion", "El stacktrace"
        )
        tracker.track_exception(exception_event)
        print("Tracked Exception")
        print("Done!")
    except Exception as e:
        print("Error: %s" % e)


# @exception_logger()
# @custom_logger(app_name="test_custom")
def test_exception_logger(a, b, url="http://localhost"):
    try:
        a = 5 / 0
    except Exception as e:
        send_exception_logger(app_name="test_custom_function", **{'pepes': 5})
    # send_custom_logger(app_name="test_custom_function",data={'pepes': 5})
    print("success")


if __name__ == '__main__':
    test_exception_logger(1, 2)
    # main()
