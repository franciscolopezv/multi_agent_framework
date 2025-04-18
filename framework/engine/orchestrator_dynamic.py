# orchestrator_dynamic.py

import importlib
import logging

from agent_registry_loader import load_agent_map


class DynamicAgentOrchestrator:
    def __init__(self, context):
        self.context = context
        self.agent_map = load_agent_map()

    def _invoke_local_agent(self, step):
        name = step["name"]
        logging.info(f"[Dynamic] Executing agent: {name}")

        agent_def = self.agent_map.get(name)
        if not agent_def:
            raise ValueError(f"No agent definition found for '{name}'")

        module_path = agent_def["module"]
        function_name = agent_def["function"]

        try:
            module = importlib.import_module(module_path)
            agent_fn = getattr(module, function_name)
        except Exception as e:
            raise ImportError(f"Failed to import agent '{name}': {e}")

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

        output = agent_fn(step_input, agent_def["config"])
        logging.info(f"[Dynamic] Output: {output}")
        return output
