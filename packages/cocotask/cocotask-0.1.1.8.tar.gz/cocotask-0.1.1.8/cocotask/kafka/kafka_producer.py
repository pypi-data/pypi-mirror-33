# -*- coding: utf-8 -*-

import json
from ..base_producer import CocoBaseProducer
from kafka import KafkaProducer

class CocoKafkaProducer(CocoBaseProducer):

    def __init__(self, conf, logger = None):
        self._producer = None
        super().__init__(conf, logger)

    def connect(self):
      username = self._config.get("USERNAME", None)
      password = self._config.get("PASSWORD", None)

      if username and password:
        self._producer = KafkaProducer(bootstrap_servers=self._config['BOOTSTRAP_SERVERS'],
                                       security_protocol = "SASL_PLAINTEXT",
                                       sasl_mechanism = 'PLAIN',
                                       sasl_plain_username = username,
                                       sasl_plain_password = password
                                       )
      else:
        self._producer = KafkaProducer(bootstrap_servers=self._config['BOOTSTRAP_SERVERS'])


    def send(self, data):
      databytes = data
      if isinstance(databytes, str):
        databytes = databytes.encode()

      self._producer.send(self._config['TOPIC'], databytes)

    def close(self):
        self._producer.close()


