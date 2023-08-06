import pika

def createBlockingConnection(config):
	credentials = pika.PlainCredentials(config['USERNAME'], config['PASSWORD'])
	parameters = pika.ConnectionParameters(config['SERVER_ADDRESS'],
	                                   config['SERVER_PORT'],
	                                   config.get("VIRTUAL_HOST", "/"),
	                                   credentials)
	connection = pika.BlockingConnection(parameters)
	channel = connection.channel()

	channel.exchange_declare(exchange=config['EXCHANGE_NAME'],
	                     exchange_type=config['EXCHANGE_TYPE'])
	channel.queue_declare(queue=config['QUEUE_NAME'], durable=True)

	return connection, channel
