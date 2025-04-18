# run_workflow_poc.py

import os

import networkx as nx
from graphviz import Digraph

from framework.engine.context import ExecutionContext
from framework.engine.graph_builder import build_state_machine
from framework.engine.orchestrator import AgentOrchestrator
from workflow.loader import load_workflow

if __name__ == "__main__":
    workflow_path = "workflow/definitions/event_driven_architecture.yaml"

    print("[PoC] Loading workflow...")
    workflow = load_workflow(workflow_path)
    context = ExecutionContext(workflow)

    # Initialize the state with user input
    user_input = "Design a Kafka-based Java system"
    context.outputs["input"] = user_input

    print(f"[PoC] Initialized context with trace ID: {context.trace_id}")

    orchestrator = AgentOrchestrator(context)

    # Wrap each step into a callable node for the graph
    def wrapped_node(step_name):
        def node(state: dict[str, str]) -> dict[str, str]:
            orchestrator.context.outputs = state
            return orchestrator.execute_step(step_name)

        return node

    # Build the graph using wrapped nodes
    step_registry = {
        step["name"]: wrapped_node(step["name"]) for step in workflow["steps"]
    }

    graph = build_state_machine(workflow, step_registry)

    # Visualize the graph structure (DOT + PNG)
    graph_path = "workflow/graph"
    os.makedirs(graph_path, exist_ok=True)

    dot_path = os.path.join(graph_path, "workflow_graph.dot")
    png_path = os.path.join(graph_path, "workflow_graph.png")

    # Optional: render to PNG using graphviz
    viz = Digraph(comment="Workflow Graph")
    viz.graph_attr["rankdir"] = "LR"
    for node in graph.get_graph().nodes:
        viz.node(node)
    for edge in graph.get_graph().edges:
        source, target = edge[0], edge[1]
        viz.edge(source, target)

    viz.render(dot_path.replace(".dot", ""), format="png", cleanup=True)
    print(f"[PoC] Workflow graph visualized at: {png_path}")

    print("[PoC] Executing LangGraph state machine with orchestrator integration...")

    result = graph.invoke(context.outputs)

    print("[PoC] Final Outputs:")
    for key, val in result.items():
        print(f"- {key}: {val}")
