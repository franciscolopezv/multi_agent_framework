# workflow_output_logger.py

import json
import logging
import os

from confluent_kafka import Consumer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

kafka_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"),
    "group.id": "workflow-output-logger",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(kafka_config)
consumer.subscribe(["workflow.output"])

logging.info("[OutputLogger] Listening to workflow.output...")

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
                f"[OutputLogger] Raw event data: {json.dumps(event, indent=2)}"
            )
            trace_id = event.get("trace_id")
            outputs = event.get("data", {}).get("outputs", {})
            logging.info(f"[OutputLogger] Final output for trace_id {trace_id}:")
            for key, value in outputs.items():
                logging.info(f"  {key}: {value[:100]}...")
        except Exception as e:
            logging.error(f"Failed to parse message: {e}")

except KeyboardInterrupt:
    logging.info("[OutputLogger] Shutting down...")
    consumer.close()
