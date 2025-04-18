from fastapi import FastAPI
from node.application_designer import app_designer_node
from pydantic import BaseModel

app = FastAPI()


class AgentInput(BaseModel):
    trace_id: str
    workflow_id: str
    step_name: str
    input: dict
    context: dict


@app.post("/invoke")
async def invoke_agent(payload: AgentInput):
    print(f"[AppDesignerService] Received: {payload.step_name}")
    output = app_designer_node(payload.input, {"params": {}})
    return {"status": "success", "output": output}
