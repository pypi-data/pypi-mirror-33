# -*- coding: utf-8 -*-

import redis
import json
from ..base_consumer import CocoBaseConsumer

class CocoRedisConsumer(CocoBaseConsumer):

    def __init__(self, conf, worker, logger = None):
        self._client = None
        self._host = conf['SERVER']
        self._port = int(conf['PORT'])
        self._db = conf.get("DB", 7)
        self._queue = conf.get("QUEUE")
        self._password = conf.get("PASSWORD", None)
        super().__init__(conf, worker, logger)


    def connect(self):
        self._client = redis.Redis(host = self._host, 
                                   port = self._port, 
                                   decode_responses = True, 
                                   db = self._db,
                                   password = self._password)
        self._client.ping()

        while True:
          value = self._client.blpop(self._queue, 0)[1]
          self._worker.process(value)
