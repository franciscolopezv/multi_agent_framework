# event_runner.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from framework.events.cloudevent_kafka_consumer import CloudEventKafkaConsumer
from framework.handler.response_event_handler import handle_response_event
from framework.handler.workflow_request_handler import handle_workflow_request

kafka_config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
}

if __name__ == "__main__":
    import threading

    # One consumer for new workflow requests
    request_listener = CloudEventKafkaConsumer(
        kafka_config=kafka_config,
        topic="workflow.request",
        handler_fn=handle_workflow_request,
        group_id="workflow-request-listener",
    )

    # One consumer for step responses
    response_listener = CloudEventKafkaConsumer(
        kafka_config=kafka_config,
        topic="workflow.step.response",
        handler_fn=handle_response_event,
        group_id="workflow-response-listener",
    )

    # Run them in parallel threads
    threading.Thread(target=request_listener.listen, daemon=True).start()
    threading.Thread(target=response_listener.listen, daemon=True).start()

    print("[EventRunner] Event-driven orchestrator is running. Press Ctrl+C to exit.")
    try:
        while True:
            pass  # keep main thread alive
    except KeyboardInterrupt:
        print("[EventRunner] Shutting down...")
