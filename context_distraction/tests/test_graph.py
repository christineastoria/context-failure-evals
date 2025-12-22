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
    config = {"recursion_limit": 200}
    
    # Stream to capture tool calls and final state
    final_state = {}
    all_messages = []
    
    from langchain_core.messages import HumanMessage
    
    async for chunk in graph.astream(
        {"supervisor_messages": [HumanMessage(content=query)]},
        config=config,
        subgraphs=True,
        stream_mode="updates",
    ):
        # chunk is a tuple: (namespace, data) or just data dict
        if isinstance(chunk, tuple) and len(chunk) >= 2:
            namespace, data = chunk
        elif isinstance(chunk, dict):
            data = chunk
        else:
            continue
        
        # Extract messages from nested node data structure
        # Structure: data[node_name][message_key] = [messages]
        if isinstance(data, dict):
            for node_key, node_data in data.items():
                if isinstance(node_data, dict):
                    # Check for messages in common message keys
                    for msg_key in ['supervisor_messages', 'reseacher_messages', 'messages']:
                        if msg_key in node_data and isinstance(node_data[msg_key], list):
                            msgs = node_data[msg_key]
                            all_messages.extend(msgs)
                            
                            # Extract tool calls from messages
                            for msg in msgs:
                                tool_calls = extract_tool_calls_from_message(msg)
                                for tc in tool_calls:
                                    trajectory.append(tc)
            
            # Update final state
            final_state.update(data)
    
    # Extract final response from last message
    final_response = ""
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
        run_graph_agent,
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


async def run_local_test(case_index=0):
    """
    Run a local test with streaming output for debugging.

    Args:
        case_index: Index of test case to run (0-3 for tasks 1-4)
    """
    task = TEST_TASKS[case_index]
    reference_outputs = build_reference_outputs(task)

    print(f"LOCAL TEST - {task['name']}", flush=True)
    
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
    import argparse

    parser = argparse.ArgumentParser(description="Test graph-based research agent")
    parser.add_argument("--langsmith", action="store_true", help="Run evaluation on LangSmith")
    parser.add_argument("--dataset", default="context-distraction-research-slim", help="LangSmith dataset name")
    parser.add_argument("--case", type=int, default=1, help="Test case number (1-4) for local testing")

    args = parser.parse_args()

    if args.langsmith:
        # Run LangSmith evaluation
        full_dataset_name = "context-distraction-research"
        slim_dataset_name = "context-distraction-research-slim"
        setup_datasets(full_dataset_name, slim_dataset_name, TEST_TASKS)

        graph_experiment = asyncio.run(run_experiment(args.dataset))
        print(f"\nGraph experiment completed: {graph_experiment}")
    else:
        # Run local test with streaming
        case_index = args.case - 1  # Convert 1-based to 0-based index
        if case_index < 0 or case_index >= len(TEST_TASKS):
            print(f"Error: Case {args.case} out of range. Valid cases: 1-{len(TEST_TASKS)}")
            exit(1)

        asyncio.run(run_local_test(case_index))

