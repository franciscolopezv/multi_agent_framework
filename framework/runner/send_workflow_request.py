# send_workflow_request.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import uuid

from framework.events.cloudevent_kafka_producer import CloudEventKafkaProducer

# Kafka producer config
kafka_config = {"bootstrap.servers": "localhost:29092"}
producer = CloudEventKafkaProducer(kafka_config)

# Sample workflow definition
workflow_def = {
    "id": "event-driven-001",
    "name": "event_driven_architecture",
    "entry_point": "app_designer",
    "steps": [
        {
            "name": "app_designer",
            "next": "terraform",
            "protocol": "http",
            "endpoint": "http://app_designer_agent:8001/invoke",
            "input_keys": ["input"],
        },
        {
            "name": "terraform",
            "next": "kafka",
            "protocol": "kafka",
            "topic_request": "workflow.step.terraform.request",
            "topic_response": "workflow.step.response",
            "input_keys": ["design"],
        },
        {
            "name": "kafka",
            "next": "end",
            "protocol": "kafka",
            "topic_request": "workflow.step.kafka.request",
            "topic_response": "workflow.step.response",
            "input_keys": ["design"],
        },
    ],
}

# Build request event
workflow_input = {
    "payload": {
        "workflow": workflow_def,
        "input": "Design a Python e-commerce platform for a pharmacy",
    }
}

producer.publish(
    topic="workflow.request", event_type="workflow.request", payload=workflow_input
)

print("✅ Workflow request sent to Kafka")
