# cloudevent_kafka_producer.py

import json
import uuid
from datetime import datetime

from confluent_kafka import Producer


class CloudEventKafkaProducer:
    def __init__(self, kafka_config):
        self.producer = Producer(kafka_config)

    def _build_cloudevent(self, topic: str, type_: str, data: dict) -> dict:
        return {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "source": f"/framework/{type_}",
            "type": type_,
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "trace_id": data.get("trace_id"),
            "workflow_id": data.get("workflow_id"),
            "step_name": data.get("step_name"),
            "data": data.get("payload"),
        }

    def publish(self, topic: str, event_type: str, payload: dict, headers: list = None):
        event = self._build_cloudevent(topic, event_type, payload)
        message = json.dumps(event).encode("utf-8")
        self.producer.produce(topic, message, headers=headers)
        self.producer.flush()
        print(f"[CloudEvent] Published to {topic} with event type {event_type}")
