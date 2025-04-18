# main.py

from framework.engine.context import ExecutionContext
from workflow.loader import load_workflow

if __name__ == "__main__":
    path = "workflow/definitions/event_driven_architecture.yaml"
    workflow = load_workflow(path)
    context = ExecutionContext(workflow)

    print(f"Trace ID: {context.trace_id}")
    print(f"Starting at: {context.current_step}")
    print("Available steps:", list(context.steps.keys()))
