# engine/orchestrator.py

import importlib
import logging
import os

import requests
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from framework.events.cloudevent_kafka_producer import CloudEventKafkaProducer
from telemetry import tracer  # ✅ OpenTelemetry tracer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AgentOrchestrator:
    def __init__(self, context):
        self.context = context
        self.producer = CloudEventKafkaProducer(
            {
                "bootstrap.servers": os.getenv(
                    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
                )
            }
        )

    def execute_step(self, step_name):
        step = self.context.steps[step_name]
        protocol = step.get("protocol", "local")

        logging.info(f"Executing step '{step_name}' using protocol: {protocol}")

        try:
            with tracer.start_as_current_span(f"step:{step_name}") as span:
                span.set_attribute("trace_id", self.context.trace_id)
                span.set_attribute("workflow_id", self.context.workflow_id)
                span.set_attribute("step_name", step_name)
                span.set_attribute("protocol", protocol)

                if protocol == "http":
                    output = self._invoke_http_agent(step)
                elif protocol == "kafka":
                    return self._invoke_kafka_agent(step)
                elif protocol == "local":
                    output = self._invoke_local_agent(step)
                else:
                    raise ValueError(f"Unsupported protocol: {protocol}")

                # Emit step.response event for http/local steps

                event_payload = {
                    "trace_id": self.context.trace_id,
                    "workflow_id": self.context.workflow_id,
                    "step_name": step_name,
                    "payload": {"output": output},
                }

                self.producer.publish(
                    topic="workflow.step.response",
                    event_type="workflow.step.response",
                    payload=event_payload,
                )
                logging.info(
                    f"[Orchestrator] Emitted response event for step '{step_name}'"
                )
                return output
        except Exception as e:
            logging.error(f"Tracing failed: {e}")

    def _invoke_http_agent(self, step):

        input_keys = step.get("input_keys")
        step_input = (
            {
                k: self.context.outputs[k]
                for k in input_keys
                if k in self.context.outputs
            }
            if input_keys
            else self.context.outputs
        )

        payload = {
            "trace_id": self.context.trace_id,
            "workflow_id": self.context.workflow_id,
            "step_name": step["name"],
            "input": step_input,
            "context": {
                "callback_url": f"http://localhost:8000/callback/{step['name']}"
            },
        }

        logging.info(f"[HTTP] Calling {step['endpoint']}")
        res = requests.post(step["endpoint"], json=payload)
        res.raise_for_status()
        output = res.json().get("output", {})
        logging.info(f"[HTTP] Response: {output}")
        return output

    def _invoke_kafka_agent(self, step):
        input_keys = step.get("input_keys")
        step_input = (
            {
                k: self.context.outputs[k]
                for k in input_keys
                if k in self.context.outputs
            }
            if input_keys
            else self.context.outputs
        )

        payload = {
            "trace_id": self.context.trace_id,
            "workflow_id": self.context.workflow_id,
            "step_name": step["name"],
            "payload": {"input": step_input},
            "context": {"reply_topic": step["topic_response"]},
        }

        # Inject trace context into Kafka headers
        carrier = {}
        TraceContextTextMapPropagator().inject(carrier)
        kafka_headers = [(k, v.encode("utf-8")) for k, v in carrier.items()]

        self.producer.publish(
            topic=step["topic_request"],
            event_type=f"workflow.step.{step['name']}.request",
            payload=payload,
            headers=kafka_headers,
        )
        logging.info(
            f"[Kafka] Request for step '{step['name']}' published to {step['topic_request']}"
        )
        return {step["name"]: "pending..."}

    def _invoke_local_agent(self, step):
        name = step["name"]
        logging.info(f"[Local] Executing agent: {name}")

        module_path = step.get("module")
        function_name = step.get("function")

        if not module_path or not function_name:
            raise ValueError(
                f"Step '{name}' missing 'module' or 'function' for local execution"
            )

        try:
            module = importlib.import_module(module_path)
            agent_fn = getattr(module, function_name)
        except Exception as e:
            raise ImportError(
                f"Failed to import local agent '{function_name}' from '{module_path}': {e}"
            )

        input_keys = step.get("input_keys")
        step_input = (
            {
                k: self.context.outputs[k]
                for k in input_keys
                if k in self.context.outputs
            }
            if input_keys
            else self.context.outputs
        )

        output = agent_fn(step_input, step)
        logging.info(f"[Local] Output: {output}")
        return output
