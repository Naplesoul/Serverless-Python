import random
import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import kafka_errors

from serverless import Request, Response, Evoke
from userland import action

kafka_addr = 'localhost:9092'
partition_cnt = 10


def wrapper():
    consumer = KafkaConsumer(
        action.action_name,
        bootstrap_servers=kafka_addr,
        group_id=action.action_name,
        enable_auto_commit=False,
        key_deserializer=lambda k: json.loads(k.decode()),
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    producer = KafkaProducer(
        bootstrap_servers=[kafka_addr],
        key_serializer=lambda k: json.dumps(k).encode(),
        value_serializer=lambda v: json.dumps(v).encode()
    )

    for msg in consumer:
        req = Request(msg.value['params'], msg.value['path'], msg.value['body'])

        try:
            output = action.action(req)

            if isinstance(output, Evoke):
                topic_next = output.action_name()
                val_next = {
                    'requestUID': msg.value['requestUID'],
                    'returnTopic': msg.value['returnTopic'],
                    'params': output.params(),
                    'path': output.path(),
                    'body': output.body()
                }
            elif isinstance(output, Response):
                topic_next = msg.value['returnTopic']
                val_next = {
                    'requestUID': msg.value['requestUID'],
                    'statusCode': 200,
                    'payload': output.payload()
                }
            else:
                raise RuntimeError("unexpected return value")

        except Exception as e:
            topic_next = msg.value['returnTopic']
            val_next = {
                'requestUID': msg.value['requestUID'],
                'statusCode': 500,
                'payload': repr(e)
            }

        try:
            future = producer.send(
                topic_next,
                value=val_next,
                partition=random.randint(0, partition_cnt - 1)
            )
            future.get(timeout=3)

        except kafka_errors:
            produce_fail()

        consumer.commit()


def produce_fail():
    print("fail to produce")


if __name__ == '__main__':
    wrapper()
