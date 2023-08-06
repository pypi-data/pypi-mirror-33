# -*- coding: utf-8 -*-

import redis
import json
import pika
from ..base_producer import CocoBaseProducer
from .common import createBlockingConnection


class CocoRMQProducer(CocoBaseProducer):

    def __init__(self, conf, logger = None):
        self._exchange_name = conf['EXCHANGE_NAME']
        self._queue_name = conf['QUEUE_NAME']
        self._connection = None
        self._channel = None
        super().__init__(conf, logger)


    def connect(self):
        self._connection, self._channel = createBlockingConnection(self._config)


    def send(self, data):
      self._channel.basic_publish(exchange=self._exchange_name, 
                      routing_key=self._queue_name, 
                      body=data, 
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))


    def close(self):
        self._connection.close()


