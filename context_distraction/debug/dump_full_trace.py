"""
Dump full trace with all children to JSON file for debugging.

Usage:
    python dump_full_trace.py [--project PROJECT_NAME] [--run-id RUN_ID] [--output OUTPUT_FILE] [--limit LIMIT]

Examples:
    # Get latest run from default project
    python dump_full_trace.py

    # Get from specific project
    python dump_full_trace.py --project my-project

    # Get specific run by ID
    python dump_full_trace.py --run-id 019b4449-268a-7872-91e6-57e64bf272a4

    # Save to custom file
    python dump_full_trace.py --output my_trace.json

    # Get more children (up to 100)
    python dump_full_trace.py --limit 100
"""
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def dump_trace(project_name="context-failure", run_id=None, output_file="full_trace.json", limit=100):
    """
    Fetch and dump a full trace from LangSmith.

    Args:
        project_name: LangSmith project name
        run_id: Specific run ID to fetch (if None, gets latest)
        output_file: Output JSON file path
        limit: Maximum number of child runs to fetch
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
        print(f"Found run: {root_run.id}")

    # Get all children
    print(f"Fetching up to {limit} child runs...")
    children = list(client.list_runs(
        project_name=project_name if not run_id else None,
        trace_id=root_run.trace_id,
        limit=limit
    ))
    print(f"Found {len(children)} child runs")

    # Convert to serializable dicts
    trace_data = {
        "root_run": {
            "id": str(root_run.id),
            "name": root_run.name,
            "inputs": root_run.inputs,
            "outputs": root_run.outputs,
        },
        "children": []
    }

    for child in children:
        child_data = {
            "id": str(child.id),
            "name": child.name,
            "parent_id": str(child.parent_run_id) if child.parent_run_id else None,
            "run_type": child.run_type,
            "inputs": child.inputs,
            "outputs": child.outputs,
        }
        trace_data["children"].append(child_data)

    # Save to file
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(trace_data, f, indent=2, default=str)

    print(f"\nSaved to {output_path.absolute()}")

    # Print summary
    print(f"\nRoot run outputs keys: {list(root_run.outputs.keys()) if root_run.outputs else 'None'}")
    if root_run.outputs and 'deliverables' in root_run.outputs:
        print("\nDeliverables:")
        for k, v in root_run.outputs['deliverables'].items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump LangSmith trace to JSON for debugging")
    parser.add_argument("--project", default="context-failure", help="LangSmith project name")
    parser.add_argument("--run-id", help="Specific run ID to fetch (if not provided, gets latest)")
    parser.add_argument("--output", default="full_trace.json", help="Output JSON file path")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of child runs to fetch")

    args = parser.parse_args()
    dump_trace(args.project, args.run_id, args.output, args.limit)
