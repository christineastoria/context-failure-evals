"""Evaluators for context confusion evaluation."""

from typing import Dict, Any, Literal, Annotated, TypedDict
from langsmith.schemas import Run, Example
from langchain_openai import ChatOpenAI


def compare_trajectory(tool_calls, expected_tool_calls, mode="strict"):
    """
    Compare tool call trajectories with multiple comparison modes.
    Returns a score between 0.0 and 1.0 for partial credit.
    Trajectory mode is defined in the dataset
    
    Modes:
        strict: Exact match - same tools, same order
        unordered: Same tools, any order
        superset: Actual contains all expected (allows extras)
        subset: Actual contains only expected tools (penalizes missing)
    
    This flexible comparison is critical for evaluating agents with different tool designs.
    """
    def make_hashable(obj):
        """Recursively convert unhashable types to hashable ones."""
        if isinstance(obj, dict):
            return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, list):
            return tuple(make_hashable(item) for item in obj)
        elif isinstance(obj, set):
            return tuple(sorted(make_hashable(item) for item in obj))
        else:
            return obj
    
    def normalize_tool_call(tc):
        """
        Normalize a tool call for comparison.
        Converts to a hashable tuple of (name, sorted_args).
        """
        name = tc.get("name", "")
        args = tc.get("args", {})
        # Convert args to completely hashable structure (handles nested lists/dicts)
        args_hashable = make_hashable(args)
        return (name, args_hashable)
    
    # Handle empty cases
    if len(tool_calls) == 0 and len(expected_tool_calls) == 0:
        return 1.0
    if len(expected_tool_calls) == 0:
        return 0.0 if len(tool_calls) > 0 else 1.0
    if len(tool_calls) == 0:
        return 0.0
    
    # Normalize both trajectories
    actual_normalized = [normalize_tool_call(tc) for tc in tool_calls]
    expected_normalized = [normalize_tool_call(tc) for tc in expected_tool_calls]
    
    if mode == "strict":
        # Exact match - same tools, same order
        # Score = ratio of correct positions
        matches = sum(1 for a, e in zip(actual_normalized, expected_normalized) if a == e)
        max_len = max(len(actual_normalized), len(expected_normalized))
        return matches / max_len if max_len > 0 else 0.0
        
    elif mode == "unordered":
        # Same tools, any order - compare as multisets
        from collections import Counter
        actual_counter = Counter(actual_normalized)
        expected_counter = Counter(expected_normalized)
        
        # Count matches (intersection)
        matches = sum((actual_counter & expected_counter).values())
        total_expected = len(expected_normalized)
        return matches / total_expected if total_expected > 0 else 0.0
        
    elif mode == "superset":
        # Actual must contain all expected (extras allowed)
        # Score = ratio of expected tools found, penalized by extras
        expected_set = set(expected_normalized)
        actual_set = set(actual_normalized)
        
        # How many expected tools were called?
        found = len(expected_set.intersection(actual_set))
        expected_count = len(expected_set)
        
        if expected_count == 0:
            return 1.0
        
        # Base score: ratio of expected tools found
        base_score = found / expected_count
        
        # Penalty for extra tools (noise)
        extra = len(actual_set - expected_set)
        noise_penalty = extra / (expected_count + extra) if (expected_count + extra) > 0 else 0
        
        return max(0.0, base_score - noise_penalty)
        
    elif mode == "subset":
        # All actual tools must be in expected (no extras)
        # Score = ratio of actual tools that are valid (in expected)
        expected_set = set(expected_normalized)
        actual_set = set(actual_normalized)
        
        # How many actual tools are valid (in expected)?
        valid = len(actual_set.intersection(expected_set))
        actual_count = len(actual_set)
        
        if actual_count == 0:
            return 0.0
        
        # Base score: ratio of valid actual tools
        base_score = valid / actual_count
        
        # Additional check: did we call all expected tools?
        expected_count = len(expected_set)
        coverage = len(expected_set.intersection(actual_set)) / expected_count if expected_count > 0 else 1.0
        
        # Final score is average of validity and coverage
        return (base_score + coverage) / 2.0
    else:
        raise ValueError(f"Unknown mode: {mode}")


def trajectory_match_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Flexible trajectory matching using comparison modes.
    Returns scores from 0.0 to 1.0 for partial credit.
    
    Uses the mode specified in the example to handle different agent designs.
    NO FALLBACKS - fails loudly if required data is missing.
    """
    # NO .get() - fail loudly if missing
    actual_trajectory = run.outputs["trajectory"]
    expected_trajectory = example.outputs["trajectory"]
    mode = example.outputs["trajectory_comparison_mode"]
    
    # Use flexible comparison function
    score = compare_trajectory(actual_trajectory, expected_trajectory, mode=mode)
    
    # Count noise tools (tools called that weren't expected)
    actual_tools = [t["name"] for t in actual_trajectory]
    expected_tools = [t["name"] for t in expected_trajectory]
    noise_count = len([t for t in actual_tools if t not in expected_tools])
    missing_count = len([t for t in expected_tools if t not in actual_tools])
    
    # Generate informative comment
    if score == 1.0:
        comment = f"Perfect match! Called {len(actual_tools)} tools as expected."
    elif score == 0.0:
        comment = f"No match. Called {len(actual_tools)} tools, expected {len(expected_tools)}. Missing: {missing_count}, Extra: {noise_count}"
    else:
        comment = f"Partial match ({score:.1%}). Called {len(actual_tools)} tools, expected {len(expected_tools)}. Missing: {missing_count}, Extra: {noise_count}"
    
    return {
        "key": "trajectory_match",
        "score": score,
        "comment": comment
    }


class TrajectoryAssessment(TypedDict):
    """Evaluate tool call trajectory quality."""
    reasoning: Annotated[str, ..., "Explain your assessment of the tool calls."]
    is_appropriate: Annotated[bool, ..., "True if tool calls and arguments are reasonable for the goal."]


def llm_trajectory_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    LLM judge: Evaluate if tool calls and arguments are appropriate.
    
    Recognizes that consolidated tools can accomplish the same goals as multiple specific tools.
    NO FALLBACKS - fails loudly if data missing.
    """
    # NO .get() - fail loudly if missing
    actual_trajectory = run.outputs["trajectory"]
    expected_trajectory = example.outputs["trajectory"]
    
    trajectory_judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    trajectory_judge_llm = trajectory_judge.with_structured_output(TrajectoryAssessment, method="function_calling")
    
    instructions = """
    You are evaluating an AI agent's tool usage. Judge if the agent made appropriate tool calls with correct arguments.
    
    A good trajectory:
    - Calls the right tools for the task (or functionally equivalent consolidated tools)
    - Uses correct and complete arguments
    - Doesn't call unnecessary tools
    - Follows a logical sequence
    
    **IMPORTANT**: A single consolidated tool with parameters (e.g., get_order_info with include=["status", "tracking"]) 
    is BETTER than multiple specific tools (get_order + get_tracking) because it's more efficient while providing 
    the same information. Judge consolidated tools favorably.
    """
    
    user_context = f"""
<expected_trajectory>
{expected_trajectory}
</expected_trajectory>

<actual_trajectory>
{actual_trajectory}
</actual_trajectory>

Are the actual tool calls appropriate for accomplishing the same goal?
"""
    
    try:
        grade = trajectory_judge_llm.invoke([
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_context}
        ])
        return {
            "key": "llm_trajectory",
            "score": 1.0 if grade["is_appropriate"] else 0.0,
            "comment": grade["reasoning"]
        }
    except Exception as e:
        print(f"LLM Trajectory eval error: {e}")
        return {"key": "llm_trajectory", "score": 0.0, "comment": f"Evaluation failed: {str(e)[:100]}"}


def tool_efficiency_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Measure tool call efficiency relative to expected trajectory.
    NO FALLBACKS - fail loudly if data missing.
    
    Why it matters: Context confusion causes excessive tool calls.
    Consolidated tools should be more efficient (fewer calls, same information).
    """
    actual_trajectory = run.outputs["trajectory"]
    expected_trajectory = example.outputs["trajectory"]
    
    actual_count = len(actual_trajectory)
    expected_count = len(expected_trajectory)
    
    if actual_count == 0:
        return {"key": "tool_efficiency", "score": 0.0, "comment": "No tools called"}
    
    # Efficiency: perfect if we call exactly expected number or fewer
    # Penalize calling more tools than needed
    efficiency = min(1.0, expected_count / actual_count)
    
    return {
        "key": "tool_efficiency",
        "score": efficiency,
        "comment": f"Called {actual_count} tools (expected {expected_count}). Efficiency: {efficiency:.2f}"
    }


class SuccessCriteriaAssessment(TypedDict):
    """Evaluate if response meets success criteria."""
    reasoning: str
    meets_criteria: bool
    score: float  # 0.0 to 1.0


def success_criteria_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    LLM-as-judge: STRICT evaluation focused on response completeness and accuracy.
    
    The consolidated agent should score HIGHER because it provides more complete,
    accurate responses by efficiently gathering all needed information.
    """
    final_response = run.outputs["final_response"]
    success_criteria = example.outputs["success_criteria"]
    
    # If no response, return 0
    if not final_response or final_response.strip() == "":
        return {
            "key": "success_criteria",
            "score": 0.0,
            "comment": "No response generated"
        }
    
    instructions = """
You are evaluating an AI agent's response against specific success criteria.

Focus on completeness and specificity:
- Each criterion must be FULLY satisfied with SPECIFIC details for credit
- Missing any required criterion significantly reduces the score
- Accuracy matters - incorrect or incomplete details should be heavily penalized

Scoring rubric:
- 1.0: ALL criteria fully satisfied with SPECIFIC, detailed, accurate information
- 0.7-0.9: Most criteria satisfied with specific details, very minor incompleteness
- 0.4-0.6: Some criteria satisfied but lacks specificity or misses key details
- 0.1-0.3: Vague/generic information without specifics ("in transit" without location)
- 0.0: Completely fails to address criteria or provides wrong information

Focus on: Is the response SPECIFIC and COMPLETE? Does it provide EXACT details for every criterion?
Demand precision - vague responses should score 0.3 or lower.
"""
    
    user_context = f"""
<success_criteria>
{success_criteria}
</success_criteria>

<response>
{final_response}
</response>

Evaluate strictly: Does this response FULLY and ACCURATELY meet ALL the success criteria?
Check each criterion individually. Be demanding about completeness.
"""
    
    # Use GPT-4o for better evaluation
    judge_llm = ChatOpenAI(model="gpt-4o", temperature=0)
    grader = judge_llm.with_structured_output(SuccessCriteriaAssessment, method="function_calling")
    
    try:
        assessment = grader.invoke([
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_context}
        ])
        
        return {
            "key": "success_criteria",
            "score": assessment["score"],
            "comment": f"{assessment['reasoning']}"
        }
    except Exception as e:
        return {
            "key": "success_criteria",
            "score": 0.0,
            "comment": f"Evaluation error: {str(e)[:150]}"
        }

