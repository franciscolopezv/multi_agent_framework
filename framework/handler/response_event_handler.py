# response_event_handler.py

import json
import logging
import os

from pymongo import MongoClient

from framework.engine.context import ExecutionContext
from framework.engine.orchestrator import AgentOrchestrator
from framework.events.cloudevent_kafka_producer import CloudEventKafkaProducer

# MongoDB config
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["multi_agent_framework"]
collection = db["workflows"]

# Kafka config for publishing final outputs
kafka_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
}
producer = CloudEventKafkaProducer(kafka_config)


# Handler function for CloudEventConsumer
def handle_response_event(event):

    logging.info(f"[Handler] Raw event data: {json.dumps(event, indent=2)}")

    trace_id = event.get("trace_id")
    data = event.get("data", {})
    step_name = event.get("step_name")
    output = data.get("output")

    if not trace_id or not step_name or not output:
        logging.error("[Handler] Invalid event structure")
        return

    # Fetch existing workflow state
    workflow_record = collection.find_one({"trace_id": trace_id})
    if not workflow_record:
        logging.error(f"[Handler] No workflow found for trace_id: {trace_id}")
        return

    # Rebuild execution context
    context = ExecutionContext(workflow_record["workflow"])
    context.outputs = workflow_record.get("outputs", {})
    context.current_step = step_name

    # Inject new output from event
    context.outputs[step_name] = output

    # Continue execution from next step
    orchestrator = AgentOrchestrator(context)
    next_step = context.update_state(step_name, output)

    if next_step and next_step != "end":
        orchestrator.execute_step(next_step)

        # Update MongoDB state
        collection.update_one(
            {"trace_id": trace_id},
            {
                "$set": {
                    "outputs": context.outputs,
                    "current_step": context.current_step,
                }
            },
        )
    else:
        # Workflow complete
        collection.update_one(
            {"trace_id": trace_id},
            {
                "$set": {
                    "outputs": context.outputs,
                    "current_step": "end",
                    "status": "completed",
                }
            },
        )

        # Publish final result
        producer.publish(
            topic="workflow.output",
            event_type="workflow.output",
            payload={
                "trace_id": trace_id,
                "workflow_id": context.workflow_id,
                "step_name": "end",
                "status": "completed",
                "payload": {"outputs": context.outputs},
            },
        )

        logging.info(f"[Handler] Workflow {trace_id} completed and result published.")
