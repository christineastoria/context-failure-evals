"""Test script for context distraction evaluation using LangSmith experiments."""

from typing import Dict, Any, List
from langsmith import Client, evaluate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

from context_distraction.agent import create_standard_agent
from context_distraction.resources.expected_calculations import (
    EXPECTED_COMPOUND_GROWTH,
    EXPECTED_CBA,
    EXPECTED_CORRELATIONS,
    EXPECTED_WEIGHTED_SCORES,
    EXPECTED_INVESTMENT_RANKING_DICT,
    EXPECTED_RISK_ADJUSTED,
    EXPECTED_STRATEGIC_RANKING_DICT,
    BASE_FACTS,
)
from context_distraction.resources.test_tasks import TEST_TASKS
from context_distraction.resources.validation_utils import (
    extract_calculations_json,
    get_value_from_calculations,
    compare_values,
    check_consistency_with_llm,
    generate_expected_tool_calls,
    compare_tool_calls,
)

client = Client()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
standard_agent = create_standard_agent(llm)

def build_reference_outputs(task: Dict[str, Any]) -> Dict[str, Any]:
    """Build reference outputs with all expected values."""
    expected_tool_calls = generate_expected_tool_calls(
        topics=task["topics"],
        stats_count=task.get("stats_count", 5),
        expert_count=task.get("expert_count", 3),
        case_count=task.get("case_count", 2),
        year_count=task.get("year_count", 3),
        compare_count=task.get("compare_count", 2),
    )
    
    return {
        "expected_steps": task["expected_steps"],
        "recall_questions": task["recall_questions"],
        "expected_answers": task.get("expected_answers", {}),
        "primary_domain": task.get("primary_domain", "renewable_energy"),
        "secondary_domain": task.get("secondary_domain", "artificial_intelligence"),
        "expected_tool_calls": expected_tool_calls,
        "expected_tool_calls_count": len(expected_tool_calls),
        "expected_calculations": {
            domain: {
                "base_facts": BASE_FACTS.get(domain, {}),
                "compound_growth_10yr": EXPECTED_COMPOUND_GROWTH.get(domain, {}).get("10yr"),
                "cba_10pct": EXPECTED_CBA.get(domain, {}).get("10pct", {}),
                "correlation_market_size_vs_growth": EXPECTED_CORRELATIONS.get(domain, {}).get("market_size_vs_growth_rate"),
                "risk_adjusted_npv": EXPECTED_RISK_ADJUSTED.get(domain),
                "weighted_investment_score": EXPECTED_WEIGHTED_SCORES.get(domain),
                "investment_priority_rank": EXPECTED_INVESTMENT_RANKING_DICT.get(domain),
                "strategic_priority_rank": EXPECTED_STRATEGIC_RANKING_DICT.get(domain),
            }
            for domain in task["topics"]
        },
    }

def create_or_get_dataset(dataset_name: str, tasks: List[Dict[str, Any]] = None) -> Any:
    """Create or get LangSmith dataset with test tasks."""
    if tasks is None:
        tasks = TEST_TASKS
    
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Research tasks of varying complexity"
        )
    
    # Get existing examples to avoid duplicates
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    existing_queries = {ex.inputs.get("query") for ex in existing_examples}
    
    # Only add examples that don't already exist
    for task in tasks:
        if task["query"] not in existing_queries:
            client.create_example(
                inputs={"query": task["query"]},
                outputs=build_reference_outputs(task),
                dataset_id=dataset.id
            )
    
    return dataset

dataset_name = "context-distraction-research"
# For testing: use only first task
dataset = create_or_get_dataset(dataset_name, tasks=TEST_TASKS[:1])

# Evaluators using inputs, outputs, reference_outputs signature
def recall_accuracy_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate recall accuracy using reference outputs."""
    calculations_data = extract_calculations_json(outputs.get("final_response", ""))
    expected_answers = reference_outputs.get("expected_answers", {})
    primary_domain = reference_outputs.get("primary_domain", "renewable_energy")
    secondary_domain = reference_outputs.get("secondary_domain", "artificial_intelligence")
    
    comparisons = []
    correct_count = 0
    
    for i in range(1, len(expected_answers) + 1):
        expected = expected_answers.get(str(i))
        if expected:
            actual_value = get_value_from_calculations(calculations_data, i, primary_domain, secondary_domain)
            is_correct = compare_values(actual_value, expected)
            if is_correct:
                correct_count += 1
            comparisons.append(f"Q{i}: expected={expected}, actual={actual_value}, {'✓' if is_correct else '✗'}")
    
    accuracy = correct_count / len(expected_answers) if expected_answers else 0.0
    comment = f"{correct_count}/{len(expected_answers)} correct\n" + "\n".join(comparisons)
    
    return {
        "key": "recall_accuracy",
        "score": accuracy,
        "comment": comment,
    }

def consistency_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate consistency between markdown and JSON."""
    final_response = outputs.get("final_response", "")
    calculations_data = extract_calculations_json(final_response)
    result = check_consistency_with_llm(final_response, calculations_data)
    
    # Build detailed comment with specific examples
    comment_parts = []
    if result['is_consistent']:
        comment_parts.append("Consistent")
    else:
        comment_parts.append(f"Inconsistent: {len(result.get('inconsistencies', []))} conflicts found")
    
    # Add specific examples
    examples = result.get('specific_examples', [])
    if examples:
        comment_parts.append("\nSpecific conflicts:")
        for i, ex in enumerate(examples[:5], 1):  # Limit to first 5 for readability
            comment_parts.append(f"{i}. {ex.get('field_name', 'unknown')}: markdown={ex.get('markdown_value', 'N/A')}, json={ex.get('json_value', 'N/A')}")
        if len(examples) > 5:
            comment_parts.append(f"... and {len(examples) - 5} more")
    
    # Add reasoning summary (first 200 chars)
    reasoning = result.get('reasoning', '')
    if reasoning:
        comment_parts.append(f"\nReasoning: {reasoning[:200]}...")
    
    return {
        "key": "consistency_score",
        "score": result['score'],
        "comment": "\n".join(comment_parts),
    }

def task_completion_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate task completion by comparing tool calls with expected."""
    expected_tool_calls = reference_outputs.get("expected_tool_calls", [])
    actual_tool_calls = outputs.get("tool_calls", [])
    if not actual_tool_calls and expected_tool_calls:
        return {"key": "task_completion", "score": 0.0, "comment": f"No tool calls found in output. Available keys: {list(outputs.keys())}"}
    
    # Check that each expected tool call with matching args appears somewhere
    result = compare_tool_calls(
        actual_tool_calls,
        expected_tool_calls,
        strict_order=False
    )
    
    # Check total count is within 2.5% tolerance
    expected_count = reference_outputs.get("expected_tool_calls_count", len(expected_tool_calls))
    actual_count = len(actual_tool_calls)
    tolerance = 0.025  # 2.5%
    count_diff = abs(actual_count - expected_count) / expected_count if expected_count > 0 else 1.0
    count_within_tolerance = count_diff <= tolerance
    
    # Combined score: 70% for presence of expected calls, 30% for count tolerance
    presence_score = result["score"]
    count_score = 1.0 if count_within_tolerance else max(0.0, 1.0 - (count_diff - tolerance) / tolerance)
    combined_score = 0.7 * presence_score + 0.3 * count_score
    
    unmatched_indices = result.get("unmatched_indices", [])
    comment_parts = [
        f"Presence: {result['matched_steps']}/{result['total_expected']} expected tool calls found",
        f"Count: {actual_count} actual vs {expected_count} expected ({'✓' if count_within_tolerance else '✗'} within 2.5% tolerance)"
    ]
    if unmatched_indices:
        comment_parts.append(f"Unmatched expected indices: {unmatched_indices[:20]}")
        if len(unmatched_indices) > 20:
            comment_parts.append(f"  (and {len(unmatched_indices) - 20} more)")
    
    return {
        "key": "task_completion",
        "score": min(combined_score, 1.0),
        "comment": "\n".join(comment_parts),
    }

def extract_tool_calls_from_message(msg: Any) -> List[Dict[str, Any]]:
    """Extract tool calls from a message (dict or AIMessage object)."""
    tool_calls = []
    
    # Handle dict messages
    if isinstance(msg, dict) and msg.get("type") == "ai":
        if "tool_calls" in msg and msg["tool_calls"]:
            for tc in msg["tool_calls"]:
                tool_name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                tool_args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
                tool_calls.append({"name": tool_name, "args": tool_args})
    # Handle AIMessage objects
    elif hasattr(msg, 'tool_calls') and msg.tool_calls:
        for tc in msg.tool_calls:
            tool_name = tc.name if hasattr(tc, 'name') else (tc.get("name", "") if isinstance(tc, dict) else "")
            tool_args = tc.args if hasattr(tc, 'args') else (tc.get("args", {}) if isinstance(tc, dict) else {})
            tool_calls.append({"name": tool_name, "args": tool_args})
    
    return tool_calls

def run_agent_with_tool_calls(agent, query: str) -> dict:
    """Run agent and return structured output, printing progress."""
    tool_calls_list = []
    final_response = ""
    
    try:
        result = agent.invoke({"messages": [("user", query)]})
        messages = result.get("messages", [])
        
        for msg in messages:
            tool_calls = extract_tool_calls_from_message(msg)
            for tc in tool_calls:
                tool_calls_list.append(tc)
            
            # Get final response
            if isinstance(msg, dict) and msg.get("content"):
                final_response = msg["content"]
            elif hasattr(msg, 'content') and msg.content:
                final_response = msg.content
        
        print(f"  Extracted {len(tool_calls_list)} tool calls")
        return {"final_response": final_response, "tool_calls": tool_calls_list}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"final_response": f"ERROR: {e}", "tool_calls": tool_calls_list}

experiment = evaluate(
    lambda inputs: run_agent_with_tool_calls(standard_agent, inputs["query"]),
    data=dataset_name,
    evaluators=[recall_accuracy_evaluator, consistency_evaluator, task_completion_evaluator],
    experiment_prefix="context-distraction-standard-agent",
    metadata={"agent_type": "standard", "model": "gpt-4o-mini"},
    max_concurrency=1,
)
