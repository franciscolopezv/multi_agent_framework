# kafka_expert_agent_service.py

import json
import logging
import os
import uuid
from datetime import datetime

from confluent_kafka import Consumer, Producer
from node.kafka_expert import kafka_node

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Environment setup
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REQUEST_TOPIC = "workflow.step.kafka.request"
RESPONSE_TOPIC = "workflow.step.response"

# Kafka consumer
consumer = Consumer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": "kafka-agent",
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe([REQUEST_TOPIC])

# Kafka producer
producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})


def build_response_event(event, output):
    return {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "/kafka-agent",
        "type": "workflow.step.response",
        "time": datetime.utcnow().isoformat() + "Z",
        "datacontenttype": "application/json",
        "trace_id": event.get("trace_id"),
        "workflow_id": event.get("workflow_id"),
        "step_name": event.get("step_name"),
        "data": {"output": output},
    }


logging.info(f"[KafkaExpertAgent] Listening on topic: {REQUEST_TOPIC}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logging.error(f"Kafka error: {msg.error()}")
            continue

        try:
            event = json.loads(msg.value().decode("utf-8"))
            logging.info(
                f"[KafkaExpertAgent] Received event for trace_id={event.get('trace_id')}"
            )
            step_input = event.get("input", {})
            result = kafka_node(step_input, {"params": {}})
            output_event = build_response_event(event, result)
            producer.produce(RESPONSE_TOPIC, json.dumps(output_event).encode("utf-8"))
            producer.flush()
            logging.info(
                f"[KafkaExpertAgent] Response sent for trace_id={event.get('trace_id')}"
            )
        except Exception as e:
            logging.error(f"[KafkaExpertAgent] Failed to process message: {e}")

except KeyboardInterrupt:
    logging.info("[KafkaExpertAgent] Shutting down...")
    consumer.close()
