import json

from faker import Faker

from fc.cloudtrailsdk.client.tracker import Tracker
from fc.cloudtrailsdk.model.event import DependencyEvent, Event, ExceptionEvent
from fc.cloudtrailsdk.utils.decorators import exception_logger
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

@exception_logger(app_name='test',app_version='1.0')
def test_main():
    a=5/0

if __name__ == '__main__':
    test_main()
    main()

