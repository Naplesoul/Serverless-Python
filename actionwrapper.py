import random
import json
import sys
import time
import logging
import importlib

from http import HTTPStatus
from kafka import KafkaProducer, KafkaConsumer
from serverless import Request, Response, Invoke, ContentType

from userland import action

kafka_addr = "localhost:9092"
partition_cnt = 6

monitor_topic = "action-monitor"
action_name = "default_TOPIC"
invoke_actions = []

logger = logging.getLogger("logger")

consumer = None
producer = None


def wrapper(msg):
    req = Request(msg.value["params"], msg.value["triggerPath"], msg.value["payload"])

    try:
        logger.info("Invoking user action...")
        output = action.action(req)
        logger.info("User action returned.")
    except Exception as e:
        logger.error("Caught an exception in user action, err: {}".format(repr(e)))
        output = Response("Failure in action {}: {}.".format(action_name, repr(e)),
                          http_status=HTTPStatus.INTERNAL_SERVER_ERROR)

    invoke_next = False
    if isinstance(output, Invoke):
        # legal invocation
        invoke_action = output.invoke_action()
        if invoke_action in invoke_actions:
            invoke_next = True
            topic_next = "{}_TOPIC".format(invoke_action)
            val_next = {
                "requestUID": msg.value["requestUID"],
                "returnTopic": msg.value["returnTopic"],
                "params": output.params(),
                "triggerPath": output.path(),
                "payload": output.body()
            }

        # illegal invocation
        else:
            topic_next = msg.value["returnTopic"]
            val_next = {
                "requestUID": msg.value["requestUID"],
                "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
                "contentType": ContentType.MIMEPlain.value,
                "payload": "Invoking {} in {} is not allowed.".format(invoke_action, action_name)
            }

    elif isinstance(output, Response):
        # respond to gateway
        topic_next = msg.value["returnTopic"]
        val_next = {
            "requestUID": msg.value["requestUID"],
            "statusCode": int(output.http_status()),
            "contentType": output.content_type().value,
            "payload": output.payload()
        }

    else:
        # output type is illegal
        topic_next = msg.value["returnTopic"]
        val_next = {
            "requestUID": msg.value["requestUID"],
            "statusCode": int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "contentType": ContentType.MIMEPlain.value,
            "payload": "Illegal return type in action {}.".format(action_name)
        }

    logger.info("Produce message\ttopic={}\tvalue={}.".format(topic_next, val_next))
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
                    "time": int(time.time()*1000),
                    "action": invoke_next
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

    except Exception as e:
        logger.error("Producer send fail, err: {}.".format(repr(e)))
        return

    consumer.commit()


def poll():
    cur_msg = None
    try:
        for new_msg in consumer:
            cur_msg = new_msg
            wrapper(new_msg)

    except KeyboardInterrupt:
        logger.info("Receive SIGINT, reloading user script...")
        importlib.reload(action)

        if cur_msg is not None:
            wrapper(cur_msg)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("./userland/action.log", encoding="UTF-8")
    ft = logging.Formatter(fmt="%(asctime)s %(filename)s %(levelname)s %(message)s",
                           datefmt="%Y/%m/%d %X")
    fh.setFormatter(ft)
    logger.addHandler(fh)

    args = len(sys.argv)
    if args < 3:
        logger.error("Missing arguments.")
        exit(-1)

    kafka_addr = sys.argv[1]
    action_name = sys.argv[2]
    invoke_actions = sys.argv[3:]

    logger.info("Set kafka server: {}.".format(kafka_addr))
    logger.info("Set action name: {}.".format(action_name))
    logger.info("Set invoke actions: {}.".format(invoke_actions))

    random.seed()
    consumer = KafkaConsumer(
        "{}_TOPIC".format(action_name),
        bootstrap_servers=kafka_addr,
        group_id=action_name,
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    producer = KafkaProducer(
        bootstrap_servers=[kafka_addr],
        value_serializer=lambda v: json.dumps(v).encode()
    )

    while True:
        poll()
