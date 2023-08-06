from ..base_consumer import CocoBaseConsumer
from kafka import KafkaConsumer

class CocoKafkaConsumer(CocoBaseConsumer):
    def __init__(self, conf, worker, logger = None):
    	self._consumer = None
    	super().__init__(conf, worker, logger)
        
    def connect(self):
        username = self._config.get("USERNAME", None)
        password = self._config.get("PASSWORD", None)

        if username and password:
            self._consumer = KafkaConsumer(bootstrap_servers=self._config['BOOTSTRAP_SERVERS'],
                                           group_id=self._config['GROUP_ID'],
                                           security_protocol = "SASL_PLAINTEXT",
                                           sasl_mechanism = 'PLAIN',
                                           sasl_plain_username = username,
                                           sasl_plain_password = password,
                                           consumer_timeout_ms=1000,
                                           auto_offset_reset='earliest'
                                           )
        else:
            self._consumer = KafkaConsumer(bootstrap_servers=self._config['BOOTSTRAP_SERVERS'],
                                           group_id=self._config['GROUP_ID'],
                                           consumer_timeout_ms=1000,
                                           auto_offset_reset='earliest')

        self._consumer.subscribe(self._config['TOPIC'])

        while True:
            for message in self._consumer:
            	try:
                    self._logger.debug(message.value)
                    self._worker.process(message.value)
            	except Exception as err:
            		self._logger.error(err)
