from __future__ import absolute_import, unicode_literals

import datetime
import logging

import boto3
import sys

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
            track_event.TimeStamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            track_event.Dimensions.update({
                "dApplication": self.app_name,
                "dApplicationVersion": self.app_version
            })
            success = False
            max_tries = 3
            data = track_event.to_json()
            if (sys.version_info > (3, 0)):
                data = bytes(data.encode('utf-8'))
            else:
                data = bytes(data)
            record = {
                'Data': data
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
                    logger.info('error{}'.format(e.message))
                    logger.info('Retrying...')
                    continue

            return success

        except Exception as e:
            logger.info('error{}'.format(e.message))
            # logger.exception(e.message, *e.args)
            return False
