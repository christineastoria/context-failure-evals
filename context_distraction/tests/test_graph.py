"""Test script for graph-based research agent evaluation."""

from langsmith import aevaluate
from dotenv import load_dotenv

from context_distraction.graph import graph
from context_distraction.resources.test_tasks import TEST_TASKS
from context_distraction.resources.validation_utils import extract_answers_json, extract_tool_calls_from_message
from context_distraction.tests.setup_datasets import setup_datasets, build_reference_outputs
from context_distraction.tests.evaluators import (
    recall_accuracy_evaluator_graph,
    tool_call_completeness_evaluator,
    tool_call_efficiency_evaluator,
)

load_dotenv()


async def run_graph_agent(inputs: dict) -> dict:
    """Run graph agent and extract outputs using streaming to capture trajectory."""
    query = inputs["query"]
    trajectory = []
    final_response = ""
    
    # Set recursion limit to prevent infinite loops
    config = {"recursion_limit": 100}
    
    # Stream to capture tool calls and final state
    final_state = {}
    all_messages = []
    
    async for chunk in graph.astream(
        {"messages": [("user", query)]},
        config=config,
        subgraphs=True,
        stream_mode="updates",
    ):
        # chunk is a tuple: (namespace, data) or just data dict
        if isinstance(chunk, tuple) and len(chunk) >= 2:
            namespace, data = chunk
            ns_str = ":".join(str(n) for n in namespace) if namespace else "root"
        elif isinstance(chunk, dict):
            data = chunk
            ns_str = "root"
        else:
            continue
        
        # Extract messages from various keys that might contain them
        if isinstance(data, dict):
            for key in ['tools', 'model', 'supervisor_messages', 'reseacher_messages']:
                if key in data:
                    if isinstance(data[key], dict) and 'messages' in data[key]:
                        msgs = data[key]['messages']
                    elif isinstance(data[key], list):
                        msgs = data[key]
                    else:
                        continue
                    
                    all_messages.extend(msgs)
                    
                    # Extract tool calls from messages
                    for msg in msgs:
                        tool_calls = extract_tool_calls_from_message(msg)
                        for tc in tool_calls:
                            if tc not in trajectory:  # Avoid duplicates
                                trajectory.append(tc)
            
            # Update final state
            final_state.update(data)
    
    # Extract final response from final_report key or last message
    final_response = final_state.get("final_report", "")
    if not final_response:
        for msg in reversed(all_messages):
            if isinstance(msg, dict) and msg.get("content"):
                final_response = msg["content"]
                break
            elif hasattr(msg, 'content') and msg.content:
                final_response = msg.content
                break
    
    return {"final_response": final_response, "trajectory": trajectory}


async def run_experiment(dataset_name: str):
    """
    Run evaluation experiment for graph agent using LangSmith.
    
    Args:
        dataset_name: Name of the LangSmith dataset to evaluate against
    
    Returns:
        The experiment result from LangSmith aevaluate
    """
    return await aevaluate(
        lambda inputs: run_graph_agent(inputs),
        data=dataset_name,
        evaluators=[
            recall_accuracy_evaluator_graph,
            tool_call_completeness_evaluator,
            tool_call_efficiency_evaluator,
        ],
        experiment_prefix="context-distraction-graph-agent",
        metadata={"agent_type": "graph", "model": "gpt-4o-mini"},
        max_concurrency=1,
    )


async def run_local_test():
    """
    Run a local test with streaming output for debugging.
    Always uses test case 1 (index 0).
    """
    task = TEST_TASKS[0]  # Always use test case 1
    reference_outputs = build_reference_outputs(task)
    
    print("LOCAL TEST - Task 1", flush=True)
    
    # Run agent with streaming
    inputs = {"query": task["query"]}
    outputs = await run_graph_agent(inputs)
    
    # Run evaluators locally
    print(f"\n{'='*80}", flush=True)
    print("EVALUATION RESULTS", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    recall_result = recall_accuracy_evaluator_graph(inputs, outputs, reference_outputs)
    print(f"Recall Accuracy: {recall_result['score']:.2%}", flush=True)
    print(f"{recall_result['comment']}\n", flush=True)
    
    completeness_result = tool_call_completeness_evaluator(inputs, outputs, reference_outputs)
    print(f"Tool Call Completeness: {completeness_result['score']:.2%}", flush=True)
    print(f"{completeness_result['comment']}\n", flush=True)
    
    efficiency_result = tool_call_efficiency_evaluator(inputs, outputs, reference_outputs)
    print(f"Tool Call Efficiency: {efficiency_result['score']:.2%}")
    print(f"{efficiency_result['comment']}\n", flush=True)
    
    print(f"\n{'='*80}", flush=True)
    print("FINAL RESPONSE", flush=True)
    print(f"{'='*80}\n", flush=True)
    print(outputs["final_response"][:500] + "..." if len(outputs["final_response"]) > 500 else outputs["final_response"])
    
    return outputs


if __name__ == "__main__":
    import asyncio
    import sys
    
    # Check if running in local mode (no arguments = local test)
    if len(sys.argv) > 1 and sys.argv[1] == "--langsmith":
        # Run LangSmith evaluation
        full_dataset_name = "context-distraction-research"
        slim_dataset_name = "context-distraction-research-slim"
        setup_datasets(full_dataset_name, slim_dataset_name, TEST_TASKS)
        
        dataset_name = sys.argv[2] if len(sys.argv) > 2 else slim_dataset_name
        graph_experiment = asyncio.run(run_experiment(dataset_name))
        print(f"\nGraph experiment completed: {graph_experiment}")
    else:
        # Run local test with streaming (always uses test case 1)
        asyncio.run(run_local_test())

