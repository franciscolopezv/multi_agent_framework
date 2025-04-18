# engine/context.py

class ExecutionContext:
    def __init__(self, workflow: dict):
        self.trace_id = workflow["trace_id"]
        self.workflow_id = workflow["id"]
        self.steps = {step["name"]: step for step in workflow["steps"]}
        self.entry_point = workflow["entry_point"]
        self.current_step = self.entry_point
        self.outputs = {}
        self.metadata = {}

    def update_state(self, step_name, output: dict):
        self.outputs[step_name] = output
        next_step = self.steps[step_name].get("next")
        self.current_step = next_step
        return next_step
