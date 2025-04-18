# agent_registry_api.py

import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.multi_agent_framework
collection = db.agent_registry

app = FastAPI(title="Agent Registry API")


class AgentRegistrationRequest(BaseModel):
    name: str
    execution: str  # "http" or "kafka"
    module: str
    function: str
    prompt: str
    model: str
    config: dict = Field(default_factory=dict)


@app.post("/agents/register")
def register_agent(request: AgentRegistrationRequest):
    agent_id = f"agent_{uuid4().hex[:8]}"

    agent_entry = request.model_dump()
    agent_entry["agent_id"] = agent_id

    try:
        collection.insert_one(agent_entry)
        return {"status": "success", "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
