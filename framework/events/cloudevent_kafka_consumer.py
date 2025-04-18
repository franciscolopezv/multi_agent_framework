# cloudevent_kafka_consumer.py

import json
import logging

from confluent_kafka import Consumer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CloudEventKafkaConsumer:
    def __init__(self, kafka_config, topic, handler_fn, group_id="workflow-core"):
        self.topic = topic
        self.handler_fn = handler_fn
        self.consumer = Consumer(
            {**kafka_config, "group.id": group_id, "auto.offset.reset": "earliest"}
        )
        self.consumer.subscribe([self.topic])

    def listen(self):
        logging.info(f"[CloudEventConsumer] Listening on topic: {self.topic}")
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logging.error(f"Kafka error: {msg.error()}")
                    continue

                try:
                    event = json.loads(msg.value().decode("utf-8"))
                    logging.info(
                        f"[CloudEventConsumer] Raw event data: {json.dumps(event, indent=2)}"
                    )
                    logging.info(
                        f"[CloudEventConsumer] Received event: {event.get('type')} for trace_id: {event.get('trace_id')}"
                    )
                    self.handler_fn(event)
                except Exception as e:
                    logging.error(f"Failed to process message: {e}")

        finally:
            self.consumer.close()
