from __future__ import absolute_import, unicode_literals

import datetime
import logging

import boto3

__author__ = 'Yaisel Hurtado <hurta2yaisel@gmail.com>'
__date__ = '15/06/18'

logger = logging.getLogger(__name__)


class Tracker(object):
    def __init__(
            self, stream_name, credentials=None, region=None,
            app_name=None, app_version=None
    ):
        if not credentials:
            credentials = {}

        self.firehose_client = boto3.client(
            'firehose',
            region_name=region,
            aws_access_key_id=credentials.get('aws_access_key_id', None),
            aws_secret_access_key=credentials.get('aws_secret_access_key', None)
        )

        self.delivery_stream_name = stream_name
        self.dimensions = {}
        self.app_name = app_name
        self.app_version = app_version

    def track_event(self, track_event):
        return self.__internal_track_event(track_event)

    def track_exception(self, exception_event):
        return self.__internal_track_event(exception_event)

    def track_dependency(self, dependency_event):
        return self.__internal_track_event(dependency_event)

    def __internal_track_event(self, track_event):
        try:
            track_event.Dimensions.update(self.dimensions)
            track_event.TimeStamp = str(datetime.datetime.utcnow())
            track_event.Dimensions.update({
                "dApplication": self.app_name,
                "dApplicationVersion": self.app_version
            })

            success = False
            max_tries = 3

            record = {
                'Data': bytes(track_event.to_json())
            }

            while not success and max_tries > 0:
                try:
                    response = self.firehose_client.put_record(
                        DeliveryStreamName=self.delivery_stream_name,
                        Record=record
                    )
                    success = True if response else False

                except Exception as e:
                    max_tries -= 1
                    logger.exception(e.message, *e.args)
                    logger.info('Retrying...')
                    continue

            return success

        except Exception as e:
            logger.exception(e.message, *e.args)
            return False
