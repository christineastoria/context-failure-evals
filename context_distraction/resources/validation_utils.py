"""
Validation utilities for context distraction evaluation.

Contains reusable functions for extracting, validating, and comparing
agent outputs against expected calculations.
"""

import json
import re
from typing import Dict, Any, Optional, List
from collections import Counter
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated


def extract_calculations_json(response: str) -> Dict[str, Any]:
    """
    Extract calculations JSON from markdown response.
    
    Returns empty dict if JSON is missing or invalid (format validation handled by JSON parsing).
    """
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if not json_match:
        json_match = re.search(r'(\{"calculations".*?\})', response, re.DOTALL)
    
    if json_match:
        try:
            return json.loads(json_match.group(1)).get("calculations", {})
        except json.JSONDecodeError:
            pass  # Invalid JSON format - handled by parsing error
    return {}


def get_value_from_calculations(
    calculations_data: Dict[str, Any],
    question_index: int,
    primary_domain: str = "renewable_energy",
    secondary_domain: str = "artificial_intelligence"
) -> Optional[Any]:
    """
    Extract a specific value from calculations JSON based on question index.
    
    Question mapping:
    1: Primary domain base fact (capacity_gw or market_size_billions)
    2: Secondary domain base fact (market_size_billions or capacity_gw)
    3: Primary domain compound_growth_10yr
    4: Primary domain CBA NPV (cba_10pct.npv)
    5: Primary domain correlation_market_size_vs_growth
    6: Primary domain market_share_top_segment_percent
    7: Primary domain investment_priority_rank
    8: Primary domain risk_adjusted_npv
    9: Primary domain weighted_investment_score
    10: Primary domain strategic_priority_rank
    """
    domain_data = calculations_data.get(primary_domain, {})
    
    if question_index == 1:
        base_facts = domain_data.get("base_facts", {})
        return base_facts.get("capacity_gw") or base_facts.get("market_size_billions")
    elif question_index == 2:
        secondary_data = calculations_data.get(secondary_domain, {})
        base_facts = secondary_data.get("base_facts", {})
        return base_facts.get("market_size_billions") or base_facts.get("capacity_gw")
    elif question_index == 3:
        return domain_data.get("compound_growth_10yr")
    elif question_index == 4:
        cba = domain_data.get("cba_10pct", {})
        return cba.get("npv") if isinstance(cba, dict) else None
    elif question_index == 5:
        return domain_data.get("correlation_market_size_vs_growth")
    elif question_index == 6:
        return domain_data.get("market_share_top_segment_percent")
    elif question_index == 7:
        return domain_data.get("investment_priority_rank")
    elif question_index == 8:
        return domain_data.get("risk_adjusted_npv")
    elif question_index == 9:
        return domain_data.get("weighted_investment_score")
    elif question_index == 10:
        return domain_data.get("strategic_priority_rank")
    
    return None


def compare_values(actual_value: Any, expected_value: str, tolerance: float = 0.01) -> bool:
    """
    Compare actual value with expected value.
    
    Args:
        actual_value: The actual value from agent output
        expected_value: The expected value as a string
        tolerance: Numeric tolerance (default 1%)
    
    Returns:
        True if values match within tolerance
    """
    if actual_value is None:
        return False
    
    try:
        expected_num = float(expected_value)
        actual_num = float(actual_value)
        # Check within tolerance
        if abs(actual_num - expected_num) / max(abs(expected_num), 1) < tolerance:
            return True
    except (ValueError, TypeError):
        # String comparison
        if str(actual_value) == str(expected_value):
            return True
    
    return False


class ConsistencyCheck(TypedDict):
    """Check if markdown and JSON are consistent."""
    is_consistent: Annotated[bool, "True if markdown and JSON values match"]
    inconsistencies: Annotated[list, "List of inconsistencies found"]
    consistency_score: Annotated[float, "Score from 0.0 to 1.0"]
    reasoning: Annotated[str, "Brief explanation of consistency check"]


def check_consistency_with_llm(
    response: str,
    calculations_json: Dict[str, Any],
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """Use LLM to check consistency between markdown and JSON."""
    judge_llm = ChatOpenAI(model=model, temperature=0)
    judge = judge_llm.with_structured_output(ConsistencyCheck)
    
    prompt = f"""You are checking consistency between markdown content and JSON data in a research report.

Markdown Content:
{response[:4000]}

JSON Data:
{json.dumps(calculations_json, indent=2)[:2000]}

Check if the values mentioned in the markdown text match the values in the JSON section. 
Look for:
- Base facts (capacity, market size)
- Calculated values (compound growth, NPV, ROI)
- Correlation coefficients
- Market share percentages
- Rankings and scores

Consider values consistent if they match within 5% tolerance for numeric values.
Report any inconsistencies you find."""

    try:
        result = judge.invoke(prompt)
        return {
            "score": result.get("consistency_score", 0.0),
            "is_consistent": result.get("is_consistent", False),
            "inconsistencies": result.get("inconsistencies", []),
            "reasoning": result.get("reasoning", ""),
        }
    except Exception as e:
        return {
            "score": 0.0,
            "is_consistent": False,
            "inconsistencies": [f"Error checking consistency: {str(e)}"],
            "reasoning": f"Failed to check consistency: {str(e)}",
        }


def generate_expected_trajectory(
    topics: List[str],
    stats_count: int,
    expert_count: int,
    case_count: int,
    year_count: int,
    compare_count: int,
) -> List[Dict[str, Any]]:
    """Generate expected trajectory pattern based on task structure."""
    expected = []
    for topic in topics:
        expected.append({"name": "research_topic", "topic": topic})
        for i in range(stats_count):
            expected.append({"name": "get_statistics", "topic": topic, "index": i})
        for i in range(expert_count):
            expected.append({"name": "get_expert_opinion", "topic": topic, "index": i})
        for i in range(case_count):
            expected.append({"name": "get_case_study", "topic": topic, "index": i})
        for i in range(year_count):
            expected.append({"name": "get_year_data", "topic": topic, "index": i})
        expected.append({"name": "calculate_compound_growth", "topic": topic})
        expected.append({"name": "calculate_market_share", "topic": topic})
        expected.append({"name": "analyze_correlation", "topic": topic})
        expected.append({"name": "calculate_cost_benefit_analysis", "topic": topic})
        expected.append({"name": "aggregate_statistics", "topic": topic})
        for i in range(compare_count):
            expected.append({"name": "compare_topics", "topic": topic, "index": i})
        expected.append({"name": "synthesize_research", "topic": topic})
    return expected


def compare_trajectory_order(
    actual_trajectory: List[Dict[str, Any]],
    expected_trajectory: List[Dict[str, Any]],
    strict_order: bool = False
) -> Dict[str, Any]:
    """Compare actual trajectory with expected trajectory."""
    if not expected_trajectory:
        return {
            "score": 0.0,
            "matched_steps": 0,
            "unmatched_steps": len(actual_trajectory),
            "total_expected": 0,
        }
    
    actual_tool_names = [tc.get("name", "") for tc in actual_trajectory]
    expected_tool_names = [tc.get("name", "") for tc in expected_trajectory]
    
    if strict_order:
        matches = sum(1 for a, e in zip(actual_tool_names, expected_tool_names) if a == e)
        matched_steps = matches
        unmatched_steps = len(expected_tool_names) - matches
    else:
        actual_counter = Counter(actual_tool_names)
        expected_counter = Counter(expected_tool_names)
        matched_counter = actual_counter & expected_counter
        matched_steps = sum(matched_counter.values())
        unmatched_steps = sum(expected_counter.values()) - matched_steps
    
    total_expected = len(expected_tool_names)
    score = matched_steps / total_expected if total_expected > 0 else 0.0
    
    return {
        "score": min(score, 1.0),
        "matched_steps": matched_steps,
        "unmatched_steps": unmatched_steps,
        "total_expected": total_expected,
    }

