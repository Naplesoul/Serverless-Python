import random
import json
import sys
import time

from http import HTTPStatus

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import kafka_errors

from serverless import Request, Response, Invoke, ContentType
from userland import action

kafka_addr = "localhost:9092"
partition_cnt = 6

monitor_topic = "action-monitor"
action_name = "default_action"
invoke_actions = []


def wrapper():
    consumer = KafkaConsumer(
        action_name,
        bootstrap_servers=kafka_addr,
        group_id=action_name,
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
        req = Request(msg.value["params"], msg.value["triggerPath"], msg.value["payload"])

        try:
            output = action.action(req)
        except Exception as e:
            output = Response("Failure in action {}: {}.".format(action_name, repr(e)),
                              HTTPStatus.INTERNAL_SERVER_ERROR)

        invoke_next = False
        if isinstance(output, Invoke):
            topic_next = output.invoke_action()

            # legal invocation
            if topic_next in invoke_actions:
                val_next = {
                    "requestUID": msg.value["requestUID"],
                    "returnTopic": msg.value["returnTopic"],
                    "params": output.params(),
                    "triggerPath": output.path(),
                    "payload": output.body()
                }
                invoke_next = True

            # illegal invocation
            else:
                topic_next = msg.value["returnTopic"]
                val_next = {
                    "requestUID": msg.value["requestUID"],
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "contentType": ContentType.MIMEPlain,
                    "payload": "Invoking {} in {} is not allowed.".format(topic_next, action_name)
                }

        elif isinstance(output, Response):
            # respond to gateway
            topic_next = msg.value["returnTopic"]
            val_next = {
                "requestUID": msg.value["requestUID"],
                "statusCode": output.http_status(),
                "contentType": output.content_type(),
                "payload": output.payload()
            }

        else:
            # output type is illegal
            topic_next = msg.value["returnTopic"]
            val_next = {
                "requestUID": msg.value["requestUID"],
                "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                "contentType": ContentType.MIMEPlain,
                "payload": "Illegal return type in action {}.".format(action_name)
            }

        try:
            if invoke_next:
                future_action = producer.send(
                    topic_next,
                    value=val_next,
                    partition=random.randint(0, partition_cnt - 1)
                )
                future_monitor = producer.send(
                    monitor_topic,
                    value={
                        "time": int(time.time()),
                        "action": topic_next
                    }
                )

                future_action.get(timeout=3)
                future_monitor.get(timeout=3)

            else:
                future = producer.send(
                    topic_next,
                    value=val_next
                )
                future.get(timeout=3)

        except kafka_errors:
            print("Producer send timeout")

        consumer.commit()


if __name__ == "__main__":
    args = len(sys.argv)
    if args < 3:
        print("Missing arguments.")
        exit(-1)

    kafka_addr = sys.argv[1]
    action_name = sys.argv[2]
    invoke_actions = sys.argv[3:]

    print("kafka server:", kafka_addr)
    print("action name:", action_name)
    print("invoke actions:", invoke_actions)
    random.seed()
    wrapper()
