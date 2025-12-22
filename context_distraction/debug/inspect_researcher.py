"""Inspect a specific researcher run to see what tools were called."""
import os
import json
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()
client = Client()

# Get the latest root run
project_name = "context-failure"
runs = list(client.list_runs(project_name=project_name, limit=1, is_root=True))

if not runs:
    print("No runs found")
    exit(1)

root_run = runs[0]
print(f"Root run: {root_run.id}")

# Get all child runs (max 100 per API limit)
all_children = list(client.list_runs(
    project_name=project_name,
    trace_id=root_run.trace_id,
    limit=100
))

# Find researcher runs that actually called tools
print("\nLooking for researcher runs that CALLED TOOLS...")
count = 0
for child in all_children:
    if child.name == 'researcher' and child.inputs:
        # Check if this researcher has tool children
        researcher_children = [c for c in all_children if c.parent_run_id == child.id and c.run_type == 'tool']
        if researcher_children and count < 3:  # Show first 3 that called tools
            count += 1
            research_q = child.inputs.get('research_question', '')
            print(f"\n{'='*80}")
            print(f"RESEARCHER RUN: {child.id}")
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
