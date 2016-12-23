# Reference: kafka-python package API example
import logging
import time
from kafka import SimpleProducer, KafkaClient
from kafka.common import LeaderNotAvailableError

logger = logging.getLogger('django')

kafka_client = KafkaClient("54.89.85.133","9092")
producer = SimpleProducer(kafka_client)

def start_connection():
    global kafka_client
    global producer
    kafka_client = KafkaClient("54.89.85.133", "9092")
    producer = SimpleProducer(kafka_client)

def print_response(response=None):
    if response:
        print('Error: {0}'.format(response[0].error) + 'Offset: {0}'.format(response[0].offset))


def send_message(msg, topic):
    topic = topic.encode('utf-8')
    msg = msg.encode('utf-8')
    # At most send twice
    try:
        print("1st attempt " + topic)
        print_response(producer.send_messages(topic, msg))

    except LeaderNotAvailableError:
        print("1st attempt failed to send message to " + topic + ":" + msg)
        time.sleep(1)
        print_response(producer.send_messages(topic, msg))


def close_connection():
    logger.info('Closing kafka connection')
    kafka_client.close()


