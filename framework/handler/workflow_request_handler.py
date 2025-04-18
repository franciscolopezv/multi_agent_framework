# workflow_request_handler.py

import json
import logging
import os
from datetime import datetime
from uuid import uuid4

from pymongo import MongoClient

from framework.engine.context import ExecutionContext
from framework.engine.orchestrator import AgentOrchestrator

# MongoDB config
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["multi_agent_framework"]
collection = db["workflows"]


# Entry point handler for workflow.request events
def handle_workflow_request(event):
    logging.info(f"[WorkflowHandler] Raw event data: {json.dumps(event, indent=2)}")
    data = event.get("data", {})
    workflow = data.get("workflow")
    input_text = data.get("input")

    if not workflow or not input_text:
        logging.error("[WorkflowHandler] Invalid request structure")
        return

    trace_id = str(uuid4())
    workflow["trace_id"] = trace_id

    context = ExecutionContext(workflow)
    context.outputs["input"] = input_text

    # Persist workflow in DB
    collection.insert_one(
        {
            "trace_id": trace_id,
            "workflow": workflow,
            "outputs": context.outputs,
            "current_step": context.current_step,
            "created_at": datetime.utcnow(),
            "status": "started",
        }
    )

    logging.info(f"[WorkflowHandler] New workflow started: {trace_id}")

    # Trigger first step
    orchestrator = AgentOrchestrator(context)
    orchestrator.execute_step(context.current_step)

    # Update state after first execution
    collection.update_one(
        {"trace_id": trace_id},
        {"$set": {"outputs": context.outputs, "current_step": context.current_step}},
    )
