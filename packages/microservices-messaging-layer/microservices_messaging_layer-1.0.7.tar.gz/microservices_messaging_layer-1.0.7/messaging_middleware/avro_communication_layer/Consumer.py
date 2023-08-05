import threading
from confluent_kafka import TopicPartition
import confluent_kafka
import logging


class Consumer():

    def __init__(self, **kwargs):
        self.bootstrap_servers = kwargs.pop('bootstrap_servers', None)
        self.consumer_topic = kwargs.pop('consumer_topic', None)
        print(self.bootstrap_servers,self.consumer_topic)
        self.consumer = confluent_kafka.Consumer({'bootstrap.servers': self.bootstrap_servers,
                                                  'group.id': 'grouip', 'session.timeout.ms': 6000,
                                                  'enable.auto.commit': False,
                                                  'default.topic.config': {'auto.offset.reset': 'latest'}

                                                  })

        self.consumer.assign(list(map(lambda p: TopicPartition(self.consumer_topic, p), range(0, 3))))
        logging.basicConfig(
            format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
            level=logging.INFO
        )
        logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

    def stop(self):
        self.consumer.close()

    def run(self):
        pass
