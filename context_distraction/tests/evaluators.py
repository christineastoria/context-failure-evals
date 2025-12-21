"""Evaluators for context distraction evaluation."""

import json
import re
from typing import Dict, Any, List
from context_distraction.resources.validation_utils import (
    compare_values,
    compare_tool_calls,
)


def extract_answers_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract answers JSON from text (markdown or plain text).
    Expected format: {"answers": {"1": <answer>, "2": <answer>, ...}}
    
    Returns empty dict if JSON is missing or invalid.
    """
    if not text:
        return {}
    
    # Look for JSON code block - the closing ``` tells us exactly where it ends
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return data.get("answers", {})
        except json.JSONDecodeError:
            pass
    
    return {}


def recall_accuracy_evaluator_agent(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate recall accuracy for standard agent - extracts JSON from final_response."""
    final_response = outputs.get("final_response", "")
    answers = extract_answers_json_from_text(final_response)
    expected_answers = reference_outputs.get("expected_answers", {})
    
    comparisons = []
    correct_count = 0
    
    for i in range(1, len(expected_answers) + 1):
        # Try both string and integer keys for expected_answers (test data uses integer keys)
        expected = expected_answers.get(i) or expected_answers.get(str(i))
        # Answers from JSON are typically string keys
        actual_value = answers.get(str(i)) or answers.get(i)
        is_correct = compare_values(actual_value, expected) if expected else False
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


def recall_accuracy_evaluator_graph(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate recall accuracy for graph agent - extracts JSON from final_report."""
    final_report = outputs.get("final_response", "")
    answers = extract_answers_json_from_text(final_report)
    expected_answers = reference_outputs.get("expected_answers", {})
    
    comparisons = []
    correct_count = 0
    
    for i in range(1, len(expected_answers) + 1):
        # Try both string and integer keys
        expected = expected_answers.get(str(i)) or expected_answers.get(i)
        actual_value = answers.get(str(i)) or answers.get(i)
        is_correct = compare_values(actual_value, expected) if expected else False
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


def tool_call_completeness_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate how many expected tool calls with exact arguments are missing."""
    expected_trajectory = reference_outputs.get("expected_trajectory", [])
    actual_trajectory = outputs.get("trajectory", [])
    
    if not actual_trajectory and expected_trajectory:
        return {
            "key": "tool_call_completeness",
            "score": 0.0,
            "comment": f"No tool calls found in trajectory. Expected {len(expected_trajectory)} tool calls."
        }
    
    if not expected_trajectory:
        return {
            "key": "tool_call_completeness",
            "score": 1.0,
            "comment": "No expected tool calls defined."
        }
    
    # Check that each expected tool call with matching args appears somewhere
    result = compare_tool_calls(
        actual_trajectory,
        expected_trajectory,
        strict_order=False
    )
    
    matched_count = result["matched_steps"]
    total_expected = result["total_expected"]
    missing_count = result["unmatched_steps"]
    unmatched_indices = result.get("unmatched_indices", [])
    
    # Score is fraction of expected calls that were found
    score = matched_count / total_expected if total_expected > 0 else 0.0
    
    comment_parts = [
        f"Found {matched_count}/{total_expected} expected tool calls with exact arguments",
        f"Missing {missing_count} expected tool calls"
    ]
    
    if unmatched_indices:
        comment_parts.append(f"Missing expected tool call indices: {unmatched_indices[:20]}")
        if len(unmatched_indices) > 20:
            comment_parts.append(f"  (and {len(unmatched_indices) - 20} more)")
    
    return {
        "key": "tool_call_completeness",
        "score": score,
        "comment": "\n".join(comment_parts),
    }


def tool_call_efficiency_evaluator(inputs: Dict[str, Any], outputs: Dict[str, Any], reference_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate how many extra tool calls were made beyond the optimal trajectory."""
    expected_trajectory = reference_outputs.get("expected_trajectory", [])
    actual_trajectory = outputs.get("trajectory", [])
    
    expected_count = reference_outputs.get("expected_trajectory_count", len(expected_trajectory))
    actual_count = len(actual_trajectory)
    
    extra_calls = max(0, actual_count - expected_count)
    
    # Score: 1.0 if no extra calls, decreases as extra calls increase
    # Penalty: -0.1 per extra call, minimum score of 0.0
    if expected_count == 0:
        score = 1.0 if actual_count == 0 else 0.0
    else:
        # Score starts at 1.0 and decreases by 0.05 per extra call
        # So 1 extra call = 0.95, 2 extra = 0.90, etc.
        score = max(0.0, 1.0 - (extra_calls * 0.05))
    
    comment_parts = [
        f"Expected: {expected_count} tool calls",
        f"Actual: {actual_count} tool calls",
        f"Extra calls: {extra_calls}"
    ]
    
    if extra_calls > 0:
        comment_parts.append(f"Efficiency: Made {extra_calls} more tool call(s) than optimal")
    else:
        comment_parts.append("Efficiency: Optimal (no extra calls)")
    
    return {
        "key": "tool_call_efficiency",
        "score": score,
        "comment": "\n".join(comment_parts),
    }

