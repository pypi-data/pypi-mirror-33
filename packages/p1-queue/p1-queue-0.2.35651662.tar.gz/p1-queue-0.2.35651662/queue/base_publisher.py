# -*- coding: utf-8 -*-

from __future__ import absolute_import
import logging
import pika
import json

LOGGER = logging.getLogger(__name__)


class BasePublisher(object):
    APP_ID = None

    EXCHANGE = ''
    EXCHANGE_TYPE = 'topic'
    ROUTING_KEY = ''

    _instances = None

    def __new__(cls, amqp_url):
        if cls is BasePublisher:
            raise Exception(
                "Can't directly use the BasePublisher class. Please extend it.")

        if cls._instances is None:
            cls._instances = {}

        instance = cls._instances.get(amqp_url)

        if instance is None:
            instance = super(BasePublisher, cls).__new__(cls)
            instance._url = amqp_url
            instance.connect()

            cls._instances[amqp_url] = instance

        return instance

    def connect(self):
        LOGGER.info('Connecting to %s', self._url)

        self._connection = pika.BlockingConnection(
            pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()

        LOGGER.info('Connected to %s', self._url)

        self.setup_exchange(self.EXCHANGE, self.EXCHANGE_TYPE)

    def publish(self, body, raise_exception=False):
        message = json.dumps(body)

        LOGGER.info('Publishing message %s', message)

        if not self._channel.basic_publish(self.EXCHANGE, self.ROUTING_KEY, message,
                                           pika.BasicProperties(app_id=self.APP_ID, delivery_mode=2)):
            LOGGER.warning('Message not published')

            if raise_exception:
                raise Exception('Message not published')

            return False

        LOGGER.info('Message published')
        return True

    def close(self):
        LOGGER.info('Closing channel')
        self._channel.close()
        LOGGER.info('Channel closed')

        LOGGER.info('Closing connection')
        self._connection.close()
        LOGGER.info('Connection closed')

    def setup_exchange(self, exchange_name, exchange_type):
        LOGGER.info('Declaring exchange %s', exchange_name)

        self._channel.exchange_declare(
            exchange=exchange_name, exchange_type=exchange_type)

        LOGGER.info('Exchange declared')
