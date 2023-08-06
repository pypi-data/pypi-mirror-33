from .rabbitmq.rmq_producer import CocoRMQProducer
from .kafka.kafka_producer import CocoKafkaProducer
from .redis.redis_producer import CocoRedisProducer
import logging
default_logger = logging.getLogger(__name__)

class CocoProducerManager(object):

    CONSUMER_CLASS = {
        "RMQ": CocoRMQProducer,
        "KAFKA": CocoKafkaProducer,
        "REDIS": CocoRedisProducer
    }


    @staticmethod
    def create_instance(config, logger = default_logger):
        producer = None
        try:
            producer_type = config["MQ_TYPE"]
            producer_class = CocoProducerManager.CONSUMER_CLASS[producer_type]

            sub_config = config[producer_type]
            producer = producer_class(sub_config, logger)
        except Exception as err:
            logger.error(err)

        return producer
