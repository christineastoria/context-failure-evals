"""Fetch the latest trace from LangSmith."""
import os
import json
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

# Fetch latest run from context-failure project
project_name = "context-failure"

# Get runs sorted by start time
runs = client.list_runs(
    project_name=project_name,
    limit=1,
    is_root=True,  # Only root runs
)

for run in runs:
    print(f"\n{'='*80}")
    print(f"Run ID: {run.id}")
    print(f"Name: {run.name}")
    print(f"Start Time: {run.start_time}")
    print(f"{'='*80}\n")

    # Get full run details
    full_run = client.read_run(run.id)

    # Print inputs
    print("INPUTS:")
    print(json.dumps(full_run.inputs, indent=2)[:500])

    # Print outputs
    print("\n\nOUTPUTS:")
    if hasattr(full_run, 'outputs') and full_run.outputs:
        print(json.dumps(full_run.outputs, indent=2)[:1000])

    # Print deliverables from outputs
    if hasattr(full_run, 'outputs') and full_run.outputs:
        if 'deliverables' in full_run.outputs:
            print("\n\nDELIVERABLES IN FINAL STATE:")
            deliverables = full_run.outputs['deliverables']
            for k, v in deliverables.items():
                print(f"  {k}: {v}")

    # Get child runs to see what researchers did
    print("\n\n" + "="*80)
    print("CHILD RUNS (deep_research calls):")
    print("="*80)

    try:
        child_runs = list(client.list_runs(
            project_name=project_name,
            trace_id=run.trace_id,
            limit=100
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

    break  # Only process the first (latest) run
