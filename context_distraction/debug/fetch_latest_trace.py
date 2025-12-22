"""
Quick summary of LangSmith trace with inputs, outputs, deliverables, and child runs.

Usage:
    python fetch_latest_trace.py [--project PROJECT_NAME] [--run-id RUN_ID] [--limit LIMIT]

Examples:
    # Get latest run from default project
    python fetch_latest_trace.py

    # Get from specific project
    python fetch_latest_trace.py --project my-project

    # Get specific run by ID
    python fetch_latest_trace.py --run-id 019b4449-268a-7872-91e6-57e64bf272a4

    # Fetch more child runs
    python fetch_latest_trace.py --limit 200
"""
import argparse
import json
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def fetch_trace_summary(project_name="context-failure", run_id=None, child_limit=100):
    """
    Fetch and display a quick summary of a LangSmith trace.

    Args:
        project_name: LangSmith project name
        run_id: Specific run ID to fetch (if None, gets latest)
        child_limit: Maximum number of child runs to fetch
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

    # Print run header
    print(f"\n{'='*80}")
    print(f"Run ID: {root_run.id}")
    print(f"Name: {root_run.name}")
    print(f"Start Time: {root_run.start_time}")
    print(f"{'='*80}\n")

    # Print inputs
    print("INPUTS:")
    print(json.dumps(root_run.inputs, indent=2)[:500])

    # Print outputs
    print("\n\nOUTPUTS:")
    if hasattr(root_run, 'outputs') and root_run.outputs:
        print(json.dumps(root_run.outputs, indent=2)[:1000])

    # Print deliverables from outputs
    if hasattr(root_run, 'outputs') and root_run.outputs:
        if 'deliverables' in root_run.outputs:
            print("\n\nDELIVERABLES IN FINAL STATE:")
            deliverables = root_run.outputs['deliverables']
            for k, v in deliverables.items():
                print(f"  {k}: {v}")

    # Get child runs to see what researchers did
    print("\n\n" + "="*80)
    print("CHILD RUNS (deep_research calls):")
    print("="*80)

    try:
        child_runs = list(client.list_runs(
            project_name=project_name if not run_id else None,
            trace_id=root_run.trace_id,
            limit=child_limit
        ))

        for i, child in enumerate(child_runs):
            if 'deep_research' in child.name or 'researcher' in child.name.lower():
                print(f"\n[{i}] {child.name}")
                if child.inputs:
                    # Print research question if available
                    if 'research_question' in child.inputs:
                        print(f"  Research Q: {child.inputs['research_question'][:150]}...")
                    if 'deliverable_key' in child.inputs:
                        print(f"  Deliverable Key: {child.inputs['deliverable_key']}")
                if child.outputs:
                    if 'deliverables' in child.outputs:
                        print(f"  Stored Deliverables: {child.outputs['deliverables']}")
                    if 'finding' in child.outputs:
                        print(f"  Finding: {child.outputs['finding'][:200]}...")
    except Exception as e:
        print(f"Could not fetch child runs: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch quick summary of LangSmith trace")
    parser.add_argument("--project", default="context-failure", help="LangSmith project name")
    parser.add_argument("--run-id", help="Specific run ID to fetch (if not provided, gets latest)")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of child runs to fetch")

    args = parser.parse_args()
    fetch_trace_summary(args.project, args.run_id, args.limit)
