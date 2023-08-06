# -*- coding: utf-8 -*-

import redis
import json
from ..base_producer import CocoBaseProducer

class CocoRedisProducer(CocoBaseProducer):

    def __init__(self, conf, logger = None):
        self._client = None
        self._host = conf['SERVER']
        self._port = int(conf['PORT'])
        self._db = conf.get("DB", 7)
        self._queue = conf.get("QUEUE")
        self._password = conf.get("PASSWORD", None)
        super().__init__(conf, logger)


    def connect(self):
        self._client = redis.Redis(host = self._host, 
                                   port = self._port, 
                                   decode_responses = True, 
                                   db = self._db,
                                   password = self._password)
        self._client.ping()


    def send(self, data):
        self._client.lpush(self._queue, data)


    def close(self):
        pass


