# terraform_agent_service.py

import json
import logging
import os
import uuid
from datetime import datetime

from confluent_kafka import Consumer, Producer
from node.terraform_generator import terraform_node
from opentelemetry.context import attach, detach
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from telemetry import tracer  # ✅ OpenTelemetry tracer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REQUEST_TOPIC = "workflow.step.terraform.request"
RESPONSE_TOPIC = "workflow.step.response"

consumer = Consumer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": "terraform-agent",
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe([REQUEST_TOPIC])

producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})


def build_response_event(event, output):
    return {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "/terraform-agent",
        "type": "workflow.step.response",
        "time": datetime.utcnow().isoformat() + "Z",
        "datacontenttype": "application/json",
        "trace_id": event.get("trace_id"),
        "workflow_id": event.get("workflow_id"),
        "step_name": event.get("step_name"),
        "data": {"output": output},
    }


logging.info(f"[TerraformAgent] Listening on topic: {REQUEST_TOPIC}")

with tracer.start_as_current_span("startup-test"):
    logging.info("🔥 Simple test span triggered at startup")

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
                f"[TerraformAgent] Received event for trace_id={event.get('trace_id')}"
            )

            # Extract trace context from Kafka headers
            kafka_headers = msg.headers() or []
            carrier = {k: v.decode("utf-8") for k, v in kafka_headers}
            ctx = TraceContextTextMapPropagator().extract(carrier)
            token = attach(ctx)

            with tracer.start_as_current_span("terraform-agent") as span:
                span.set_attribute("trace_id", event.get("trace_id"))
                span.set_attribute("workflow_id", event.get("workflow_id"))
                span.set_attribute("step_name", event.get("step_name"))

                step_input = event.get("input", {})
                result = terraform_node(step_input, {"params": {}})
                output_event = build_response_event(event, result)

                producer.produce(
                    RESPONSE_TOPIC, json.dumps(output_event).encode("utf-8")
                )
                producer.flush()
                logging.info(
                    f"[TerraformAgent] Response sent for trace_id={event.get('trace_id')}"
                )

            detach(token)

        except Exception as e:
            logging.error(f"[TerraformAgent] Failed to process message: {e}")

except KeyboardInterrupt:
    logging.info("[TerraformAgent] Shutting down...")
    consumer.close()
