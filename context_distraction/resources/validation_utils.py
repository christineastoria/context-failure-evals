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
    # Try to find JSON code block first
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if not json_match:
        # Try to find JSON starting with {"calculations" - match until balanced braces
        json_match = re.search(r'(\{"calculations".*?\})', response, re.DOTALL)
    
    if json_match:
        try:
            json_str = json_match.group(1)
            # Try to parse the JSON
            data = json.loads(json_str)
            return data.get("calculations", {})
        except json.JSONDecodeError:
            pass
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
    6: Primary domain investment_priority_rank
    7: Primary domain risk_adjusted_npv
    8: Primary domain weighted_investment_score
    9: Primary domain strategic_priority_rank
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
        return domain_data.get("investment_priority_rank")
    elif question_index == 7:
        return domain_data.get("risk_adjusted_npv")
    elif question_index == 8:
        return domain_data.get("weighted_investment_score")
    elif question_index == 9:
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
    inconsistencies: Annotated[List[str], "List of specific inconsistencies found with exact values from both sources"]
    consistency_score: Annotated[float, "Score from 0.0 to 1.0"]
    reasoning: Annotated[str, "Detailed explanation of consistency check, including methodology"]
    specific_examples: Annotated[List[Dict[str, str]], "List of specific examples showing conflicts, each with 'markdown_value', 'json_value', 'field_name', and 'description'"]


def extract_domain_section_from_markdown(markdown: str, domain: str) -> str:
    """Extract the markdown section for a specific domain using regex."""
    # Domain name mappings for markdown headings
    domain_names = {
        "renewable_energy": r"(?i)(renewable\s+energy|solar|wind|renewables)",
        "artificial_intelligence": r"(?i)(artificial\s+intelligence|ai|machine\s+learning)",
        "electric_vehicles": r"(?i)(electric\s+vehicles?|ev|electric\s+car)",
        "quantum_computing": r"(?i)(quantum\s+computing|quantum)",
        "biotechnology": r"(?i)(biotechnology|bio\s+tech|biotech)",
    }
    
    # Try to find domain section
    pattern = domain_names.get(domain, domain.replace("_", r"\s+"))
    
    # Look for headings (## or ###) containing domain name
    heading_pattern = rf"(?:^|\n)(#{{2,3}})\s*.*?{pattern}.*?(?:\n|$)"
    match = re.search(heading_pattern, markdown, re.MULTILINE | re.IGNORECASE)
    
    if match:
        start_pos = match.start()
        heading_level = len(match.group(1))
        
        # Find the next heading at same or higher level, or end of document
        next_heading_pattern = rf"\n#{{1,{heading_level}}}\s+"
        next_match = re.search(next_heading_pattern, markdown[start_pos + 1:], re.MULTILINE)
        
        if next_match:
            end_pos = start_pos + 1 + next_match.start()
            return markdown[start_pos:end_pos]
        else:
            return markdown[start_pos:]
    
    # Fallback: return a section around mentions of the domain
    domain_mentions = list(re.finditer(rf"\b{pattern}\b", markdown, re.IGNORECASE))
    if domain_mentions:
        # Get context around first mention (500 chars before and after)
        first_mention = domain_mentions[0].start()
        start = max(0, first_mention - 500)
        end = min(len(markdown), first_mention + 1000)
        return markdown[start:end]
    
    return ""


def check_consistency_with_llm(
    response: str,
    calculations_json: Dict[str, Any],
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """Use LLM to check consistency between markdown and JSON, checking each domain separately."""
    judge_llm = ChatOpenAI(model=model, temperature=0)
    judge = judge_llm.with_structured_output(ConsistencyCheck)
    
    system_prompt = """You are checking consistency between markdown content and JSON data in a research report.

CRITICAL: Extract NUMERIC VALUES from markdown before comparing!
- Ignore formatting: "$", commas, "billion", "million", "thousand", etc.
- Extract the actual number: "$196.6 billion" → 196.6, "$1,000.00 billion" → 1000.0
- Compare the extracted numeric value to the JSON numeric value
- Values match if the numbers are equal (within 0.01 tolerance for floating point)

CHECK THESE SPECIFIC FIELDS:
- Base facts: capacity_gw, market_size_billions, battery_cost_kwh, qubits, growth_rate
- Compound growth: compound_growth_10yr values
- CBA: cba_10pct.npv and cba_10pct.roi values
- Correlations: correlation_market_size_vs_growth values
- Rankings: investment_priority_rank, strategic_priority_rank values
- Scores: risk_adjusted_npv, weighted_investment_score values

REQUIREMENTS:
1. For each inconsistency found, provide a SPECIFIC EXAMPLE in the 'specific_examples' list with:
   - field_name: The exact field name (e.g., "renewable_energy.compound_growth_10yr")
   - markdown_value: The EXTRACTED NUMERIC VALUE from markdown (not the formatted string)
   - json_value: The exact value from JSON
   - description: Brief explanation of the conflict

2. In 'inconsistencies', list each conflict as a clear sentence showing the extracted numeric comparison

3. In 'reasoning', explain your methodology and findings for this domain

4. Set 'consistency_score' to 1.0 if all extracted numeric values match JSON values, decreasing proportionally for each real inconsistency found.

5. DO NOT flag values as inconsistent if they match after extracting the numeric value. For example:
   - "$196.6 billion" in markdown vs 196.6 in JSON → CONSISTENT
   - "$1,000.00 billion" in markdown vs 1000.0 in JSON → CONSISTENT
   - "$1,112.82 million" in markdown vs 1112.82 in JSON → CONSISTENT"""

    all_inconsistencies = []
    all_examples = []
    all_reasoning = []
    domain_scores = []
    
    # Check each domain separately
    domains = list(calculations_json.get("calculations", {}).keys())
    
    for domain in domains:
        # Extract domain-specific markdown section
        domain_markdown = extract_domain_section_from_markdown(response, domain)
        domain_json = calculations_json.get("calculations", {}).get(domain, {})
        
        if not domain_markdown or not domain_json:
            continue
        
        # Create human message with domain-specific content
        human_message = f"""Markdown Content for {domain}:
{domain_markdown[:2000]}

JSON Data for {domain}:
{json.dumps(domain_json, indent=2)[:1500]}

Check consistency between the markdown and JSON for the {domain} domain."""
        
        try:
            result = judge.invoke([
                ("system", system_prompt),
                ("human", human_message)
            ])
            
            # Aggregate results
            inconsistencies = result.get("inconsistencies", [])
            examples = result.get("specific_examples", [])
            reasoning = result.get("reasoning", "")
            score = result.get("consistency_score", 0.0)
            
            # Prefix domain name to inconsistencies and examples
            for inc in inconsistencies:
                all_inconsistencies.append(f"{domain}: {inc}")
            for ex in examples:
                ex_copy = dict(ex)
                if "field_name" in ex_copy:
                    ex_copy["field_name"] = f"{domain}.{ex_copy['field_name']}"
                all_examples.append(ex_copy)
            
            all_reasoning.append(f"{domain}: {reasoning[:150]}")
            domain_scores.append(score)
            
        except Exception as e:
            all_inconsistencies.append(f"{domain}: Error checking consistency: {str(e)}")
            domain_scores.append(0.0)
    
    # Calculate overall score as average of domain scores
    overall_score = sum(domain_scores) / len(domain_scores) if domain_scores else 0.0
    is_consistent = overall_score >= 0.95  # Consider consistent if 95%+ match
    
    return {
        "score": overall_score,
        "is_consistent": is_consistent,
        "inconsistencies": all_inconsistencies,
        "reasoning": "\n\n".join(all_reasoning),
        "specific_examples": all_examples,
    }


def generate_expected_tool_calls(
    topics: List[str],
    primary_domain: str,
    secondary_domain: str,
    stats_count: int,
    expert_count: int,
    case_count: int,
    year_count: int,
    compare_count: int,
) -> List[Dict[str, Any]]:
    """
    Generate expected tool calls based on questions and expected calculations.
    
    Each tool + argument combination should only be called once, as the agent
    can look back in conversation history for previous results.
    
    We derive exact tool calls from the questions:
    - Q1: Primary domain base fact -> get_statistics(primary_domain)
    - Q2: Secondary domain base fact -> get_statistics(secondary_domain)
    - Q3: Compound growth -> calculate_compound_growth with exact values
    - Q4: CBA NPV -> calculate_cost_benefit_analysis with exact values
    - Q5: Correlation -> analyze_correlation with data from all domains
    - Q6-Q9: Rankings -> require compound growth and CBA for ALL domains
    """
    from context_distraction.resources.expected_calculations import (
        BASE_FACTS, DOMAIN_CBA_CONFIGS
    )
    
    expected = []
    seen_calls = set()  # Track (tool_name, args_tuple) to avoid duplicates
    
    def add_call(tool_name: str, args: Dict[str, Any]):
        """Add tool call if not already seen."""
        # Create hashable key (convert lists/dicts to tuples)
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, list):
                return tuple(make_hashable(item) for item in obj)
            else:
                return obj
        
        args_key = tuple(sorted((k, make_hashable(v)) for k, v in args.items()))
        call_key = (tool_name, args_key)
        if call_key not in seen_calls:
            seen_calls.add(call_key)
            expected.append({"name": tool_name, "args": args})
    
    # Q1: Primary domain base fact - need statistics
    add_call("get_statistics", {"topic": primary_domain})
    
    # Q2: Secondary domain base fact - need statistics
    add_call("get_statistics", {"topic": secondary_domain})
    
    # Q3: Compound growth for primary domain
    primary_facts = BASE_FACTS[primary_domain]
    primary_initial = primary_facts["market_size_billions"]
    primary_growth = primary_facts["growth_rate"]
    add_call("calculate_compound_growth", {
        "initial_value": primary_initial,
        "growth_rate": primary_growth,
        "years": 10
    })
    
    # Q4: CBA NPV for primary domain
    primary_cba = DOMAIN_CBA_CONFIGS[primary_domain]
    add_call("calculate_cost_benefit_analysis", {
        "initial_investment": primary_cba["initial"],
        "annual_benefits": primary_cba["benefits"],
        "discount_rate": 0.10,
        "years": 10
    })
    
    # Q5: Correlation - needs data from ALL domains
    # First ensure we have statistics for all domains
    for domain in topics:
        add_call("get_statistics", {"topic": domain})
    
    # Then calculate correlation with data from all domains
    data_points = []
    for domain in topics:
        d_facts = BASE_FACTS[domain]
        data_points.append({
            "market_size_billions": d_facts["market_size_billions"],
            "growth_rate": d_facts["growth_rate"]
        })
    add_call("analyze_correlation", {
        "data_points": data_points,
        "variable1": "market_size_billions",
        "variable2": "growth_rate"
    })
    
    # Q6-Q9: Rankings require compound growth and CBA for ALL domains
    # (to calculate weighted scores and rankings)
    for domain in topics:
        d_facts = BASE_FACTS[domain]
        d_initial = d_facts["market_size_billions"]
        d_growth = d_facts["growth_rate"]
        d_cba = DOMAIN_CBA_CONFIGS[domain]
        
        # Compound growth for each domain
        add_call("calculate_compound_growth", {
            "initial_value": d_initial,
            "growth_rate": d_growth,
            "years": 10
        })
        
        # CBA for each domain
        add_call("calculate_cost_benefit_analysis", {
            "initial_investment": d_cba["initial"],
            "annual_benefits": d_cba["benefits"],
            "discount_rate": 0.10,
            "years": 10
        })
    
    return expected


def _normalize_tool_call(tc: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a tool call for comparison (handle different argument formats)."""
    normalized = {"name": tc.get("name", "")}
    args = tc.get("args", {})
    if isinstance(args, dict):
        normalized["args"] = {k: v for k, v in args.items() if v is not None}
    else:
        normalized["args"] = {}
    return normalized


def _tool_call_matches(actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """Check if actual tool call matches expected (name + arguments)."""
    if actual.get("name") != expected.get("name"):
        return False
    
    actual_args = actual.get("args", {})
    expected_args = expected.get("args", {})
    
    # Check that all expected arguments are present and match exactly
    for key, expected_value in expected_args.items():
        if key not in actual_args:
            return False
        actual_value = actual_args[key]
        
        # Exact match required (tolerance = 0)
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            if expected_value != actual_value:
                return False
        elif expected_value != actual_value:
            return False
    
    return True


def compare_tool_calls(
    actual_tool_calls: List[Dict[str, Any]],
    expected_tool_calls: List[Dict[str, Any]],
    strict_order: bool = False
) -> Dict[str, Any]:
    """
    Compare actual tool calls with expected tool calls.
    
    Checks that expected tool calls with matching arguments are PRESENT in the actual tool calls,
    regardless of order (unless strict_order=True).
    
    Args:
        actual_tool_calls: List of actual tool calls with {"name": str, "args": dict}
        expected_tool_calls: List of expected tool calls with {"name": str, "args": dict}
        strict_order: If True, also check order. If False, only check presence.
    
    Returns:
        Dict with score, matched_steps, unmatched_steps, total_expected, and unmatched_indices
    """
    if not expected_tool_calls:
        return {
            "score": 0.0,
            "matched_steps": 0,
            "unmatched_steps": len(actual_tool_calls),
            "total_expected": 0,
            "unmatched_indices": [],
        }
    
    # Normalize both tool call lists
    actual_normalized = [_normalize_tool_call(tc) for tc in actual_tool_calls]
    expected_normalized = [_normalize_tool_call(tc) for tc in expected_tool_calls]
    
    if strict_order:
        # Check order: match at each position
        matches = 0
        unmatched_indices = []
        for idx, expected_tc in enumerate(expected_normalized):
            if idx < len(actual_normalized):
                if _tool_call_matches(actual_normalized[idx], expected_tc):
                    matches += 1
                else:
                    unmatched_indices.append(idx)
            else:
                unmatched_indices.append(idx)
        
        matched_steps = matches
        unmatched_steps = len(expected_normalized) - matches
    else:
        # Check presence: find each expected tool call somewhere in actual tool calls
        matched_indices = []
        unmatched_indices = []
        
        for idx, expected_tc in enumerate(expected_normalized):
            found = False
            for actual_tc in actual_normalized:
                if _tool_call_matches(actual_tc, expected_tc):
                    matched_indices.append(idx)
                    found = True
                    break
            if not found:
                unmatched_indices.append(idx)
        
        matched_steps = len(matched_indices)
        unmatched_steps = len(unmatched_indices)
    
    total_expected = len(expected_normalized)
    score = matched_steps / total_expected if total_expected > 0 else 0.0
    
    return {
        "score": min(score, 1.0),
        "matched_steps": matched_steps,
        "unmatched_steps": unmatched_steps,
        "total_expected": total_expected,
        "unmatched_indices": unmatched_indices,
    }

