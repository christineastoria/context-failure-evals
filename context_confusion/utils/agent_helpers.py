"""Agent helper utilities for context confusion demonstrations."""

from typing import Dict
import pandas as pd
from IPython.display import display


def run_agent_with_trajectory(agent, query: str) -> dict:
    """
    Runs an agent and returns structured output to compare the reference output
    
    Returns:
        {
            "final_response": str,  # The final AI message text
            "trajectory": [         # List of tool calls made with args
                {"name": str, "args": dict},
                ...
            ]
        }
    """
    # Execute the agent
    result = agent.invoke({"messages": [("user", query)]})
    
    # Extract final AI message
    final_response = ""
    trajectory = []
    
    # NO .get() - fail if messages missing
    messages = result["messages"]
    
    # Extract trajectory from all AI messages with tool calls
    for msg in messages:
        if isinstance(msg, dict) and msg["type"] == "ai":
            # Collect tool calls
            if "tool_calls" in msg and msg["tool_calls"]:
                for tc in msg["tool_calls"]:
                    trajectory.append({
                        "name": tc["name"],  # No .get()
                        "args": tc["args"]   # No .get()
                    })
            # Get final response (last AI message with content)
            if msg["content"]:
                final_response = msg["content"]
        # Handle AIMessage objects
        elif hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                trajectory.append({
                    "name": tc.name if hasattr(tc, 'name') else tc["name"],
                    "args": tc.args if hasattr(tc, 'args') else tc["args"]
                })
        if hasattr(msg, 'content') and msg.content:
            final_response = msg.content
    
    return {
        "final_response": final_response,
        "trajectory": trajectory
    }


def display_metrics_table(metrics: Dict[str, float], title: str = "Evaluation Metrics", note: str = ""):
    """
    Display evaluation metrics as a formatted dataframe.
    
    Args:
        metrics: Dictionary of metric names to values
        title: Header text to display above the table
        note: Optional note to display after the table
    """
    # Build dataframe with only metrics that exist
    metric_rows = []
    
    if 'trajectory_match' in metrics:
        metric_rows.append(("Trajectory Match", f"{metrics['trajectory_match']:.2%}"))
    if 'success_criteria' in metrics:
        metric_rows.append(("Success Criteria", f"{metrics['success_criteria']:.2%}"))
    if 'llm_trajectory' in metrics:
        metric_rows.append(("LLM Trajectory", f"{metrics['llm_trajectory']:.2%}"))
    if 'tool_efficiency' in metrics:
        metric_rows.append(("Tool Efficiency", f"{metrics['tool_efficiency']:.2f}"))
    if 'latency' in metrics:
        metric_rows.append(("Avg Latency", f"{metrics['latency']:.2f}s"))
    if 'tokens' in metrics:
        metric_rows.append(("Avg Tokens", f"{metrics['tokens']:.0f}"))
    if 'cost' in metrics:
        metric_rows.append(("Avg Cost", f"${metrics['cost']:.4f}"))
    
    df = pd.DataFrame(metric_rows, columns=["Metric", "Value"])
    print(f"\n✓ {title}")
    display(df)
    if note:
        print(f"\n   {note}")

