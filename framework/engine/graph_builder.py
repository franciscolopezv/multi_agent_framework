# engine/graph_builder.py
from langgraph.graph import END, StateGraph

# Placeholder type for execution state
type AgentState = dict[str, str]


def build_state_machine(workflow: dict, registry: dict) -> StateGraph:
    """
    Builds a LangGraph-like state machine from the workflow config.
    Each step must be registered in the registry as a node function.
    """
    builder = StateGraph(AgentState)
    steps = workflow["steps"]
    entry = workflow["entry_point"]

    for step in steps:
        name = step["name"]
        node_fn = registry.get(name)
        if node_fn is None:
            raise ValueError(f"Step '{name}' is not registered.")
        builder.add_node(name, node_fn)

    builder.set_entry_point(entry)

#tito


    for step in steps:
        name = step["name"]
        next_step = step.get("next")
        if next_step:
            if next_step == "end":
                builder.add_edge(name, END)
            else:
                builder.add_edge(name, next_step)

    return builder.compile()
