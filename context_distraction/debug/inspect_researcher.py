"""
Detailed inspection of researcher runs showing inputs, parameters, tool calls, and outputs.

Usage:
    python inspect_researcher.py [--project PROJECT_NAME] [--run-id RUN_ID] [--limit LIMIT] [--max-researchers N]

Examples:
    # Inspect latest run from default project (show first 3 researchers)
    python inspect_researcher.py

    # Get from specific project
    python inspect_researcher.py --project my-project

    # Get specific run by ID
    python inspect_researcher.py --run-id 019b4449-268a-7872-91e6-57e64bf272a4

    # Show more researchers
    python inspect_researcher.py --max-researchers 10

    # Fetch more child runs to analyze
    python inspect_researcher.py --limit 200
"""
import argparse
import json
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def inspect_researchers(project_name="context-failure", run_id=None, child_limit=100, max_researchers=3):
    """
    Inspect researcher runs to see what tools were called and what parameters were passed.

    Args:
        project_name: LangSmith project name
        run_id: Specific run ID to fetch (if None, gets latest)
        child_limit: Maximum number of child runs to fetch
        max_researchers: Maximum number of researcher runs to display
    """
    client = Client()

    # Get run
    if run_id:
        print(f"Fetching run: {run_id}")
        root_run = client.read_run(run_id)
    else:
        print(f"Fetching latest run from project: {project_name}")
        runs = list(client.list_runs(project_name=project_name, limit=1, is_root=True))
        if not runs:
            print(f"No runs found in project: {project_name}")
            return
        root_run = runs[0]

    print(f"Root run: {root_run.id}")

    # Get all child runs
    all_children = list(client.list_runs(
        project_name=project_name if not run_id else None,
        trace_id=root_run.trace_id,
        limit=child_limit
    ))

    # Find researcher runs that actually called tools
    print(f"\nLooking for researcher runs that CALLED TOOLS (showing first {max_researchers})...")
    count = 0
    for child in all_children:
        if child.name == 'researcher' and child.inputs:
            # Check if this researcher has tool children
            researcher_children = [c for c in all_children if c.parent_run_id == child.id and c.run_type == 'tool']
            if researcher_children and count < max_researchers:
                count += 1
                research_q = child.inputs.get('research_question', '')
                print(f"\n{'='*80}")
                print(f"RESEARCHER RUN {count}: {child.id}")
                print(f"\nAll Inputs Keys: {list(child.inputs.keys())}")

                # Check if guidance is in messages
                if 'reseacher_messages' in child.inputs:
                    msgs = child.inputs['reseacher_messages']
                    if msgs and len(msgs) > 0:
                        first_msg = msgs[0]
                        if isinstance(first_msg, dict) and 'content' in first_msg:
                            content = first_msg['content']
                            print(f"\nFirst Message Content:")
                            print(content[:600])

                print(f"\nResearch Question: {research_q}")
                print(f"Deliverable Key: {child.inputs.get('deliverable_key', 'N/A')}")
                print(f"Data Level: {child.inputs.get('data_level', 'N/A')}")
                print(f"Data Source: {child.inputs.get('data_source', 'N/A')}")
                print(f"Calculation Guidance: {child.inputs.get('calculation_guidance', 'N/A')}")

                if child.outputs:
                    print(f"\nOutputs:")
                    if 'deliverables' in child.outputs:
                        print(f"  Stored value: {child.outputs['deliverables']}")
                    if 'finding' in child.outputs:
                        print(f"  Finding: {child.outputs['finding'][:300]}")

                # Get tool calls within this researcher run
                print(f"\nTool calls in this researcher run:")
                researcher_children = [c for c in all_children if c.parent_run_id == child.id]
                tool_calls_found = False
                for tool_run in researcher_children:
                    if tool_run.run_type == 'tool':
                        tool_calls_found = True
                        print(f"\n  [{tool_run.name}]")
                        if tool_run.inputs:
                            # Print args more cleanly
                            for key, val in tool_run.inputs.items():
                                if isinstance(val, (list, dict)):
                                    print(f"    {key}: {json.dumps(val, indent=8)[:200]}")
                                else:
                                    print(f"    {key}: {val}")
                        if tool_run.outputs:
                            output_str = str(tool_run.outputs)
                            if len(output_str) > 500:
                                output_str = output_str[:500] + "..."
                            print(f"    => {output_str}")

                if not tool_calls_found:
                    print("  (No tool calls found - researcher may not have called any tools)")

    if count == 0:
        print("\nNo researcher runs with tool calls found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect researcher runs and their tool calls")
    parser.add_argument("--project", default="context-failure", help="LangSmith project name")
    parser.add_argument("--run-id", help="Specific run ID to fetch (if not provided, gets latest)")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of child runs to fetch")
    parser.add_argument("--max-researchers", type=int, default=3, help="Maximum number of researcher runs to display")

    args = parser.parse_args()
    inspect_researchers(args.project, args.run_id, args.limit, args.max_researchers)
