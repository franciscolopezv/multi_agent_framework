# workflow/loader.py
import uuid

import yaml


def load_workflow(path: str):
    with open(path, 'r') as f:
        raw = yaml.safe_load(f)

    workflow = raw.get("workflow")
    if not workflow:
        raise ValueError("Missing 'workflow' definition.")

    workflow["trace_id"] = str(uuid.uuid4())
    return workflow
