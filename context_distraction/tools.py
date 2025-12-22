"""
Research tools that generate extensive, verbose information.

Each tool call returns detailed information designed to fill context
and test the agent's ability to recall specific details across many steps.
"""

from context_distraction.resources.synthetic_data import (
    RESEARCH_TOPICS,
    EXPERT_OPINIONS,
    CASE_STUDIES,
    EXPERT_SUMMARIES,
    CASE_STUDY_SUMMARIES
)
from langchain_core.tools import tool, InjectedToolCallId
from langchain.tools import ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Dict, Any, List, Optional, Annotated
import json
import random


# =====================================================
# CORE RESEARCH TOOLS
# =====================================================

def _research_topic_impl(topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """Internal implementation of research_topic."""
    """
    Research a specific topic and return comprehensive information.
    
    Args:
        topic: The topic to research (e.g., "renewable_energy", "artificial_intelligence")
        depth: Research depth - "brief", "standard", or "comprehensive" (default: "comprehensive")
    
    Returns:
        Detailed research information including key points, statistics, experts, and case studies.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found in research database. Available topics: {', '.join(RESEARCH_TOPICS.keys())}"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        
        # Generate verbose response based on depth
        if depth == "brief":
            key_points = topic_data["key_points"][:3]
        elif depth == "standard":
            key_points = topic_data["key_points"][:6]
        else:  # comprehensive
            key_points = topic_data["key_points"]
        
        # Generate VERY verbose response to flood context
        verbose_summary = f"""
    COMPREHENSIVE RESEARCH REPORT: {topic_data['topic']}
    
    EXECUTIVE SUMMARY:
    This research report provides an in-depth analysis of {topic_data['topic']}, covering {len(key_points)} critical aspects 
    of the field. The research methodology involved extensive literature review, expert consultations, statistical analysis, 
    and case study examination. This report serves as a foundational document for strategic decision-making and investment 
    planning in the {topic_data['topic']} sector.
    
    KEY FINDINGS:
    """
        for i, point in enumerate(key_points, 1):
            verbose_summary += f"""
    {i}. {point}
    
    This finding represents a critical insight into the {topic_data['topic']} domain. The implications of this discovery 
    extend across multiple dimensions including technological advancement, market dynamics, regulatory considerations, and 
    strategic positioning. Industry leaders have identified this as a key driver of future growth and innovation in the sector.
    """
        
        verbose_summary += f"""
    
    STATISTICAL OVERVIEW:
    The research has identified multiple key statistical metrics that provide quantitative insights 
    into the current state and trajectory of {topic_data['topic']}. For detailed statistical data, 
    please use the get_statistics() tool with this topic. These metrics have been carefully validated through 
    multiple data sources and represent the most current and accurate information available. Each statistic tells a story 
    about market dynamics, growth patterns, investment trends, and technological maturity.
    
    EXPERT INSIGHTS:
    The research team has consulted with {len(topic_data['experts'])} leading experts in the field of {topic_data['topic']}. 
    These experts represent diverse perspectives from academia, industry, government, and international organizations. Their 
    collective insights provide a comprehensive view of current challenges, opportunities, and future directions. Each expert 
    brings decades of experience and deep domain knowledge that enriches our understanding of the field.
    
    Available Experts:
    """
        for expert_id in topic_data['experts']:
            if expert_id in EXPERT_SUMMARIES:
                verbose_summary += f"\n    {EXPERT_SUMMARIES[expert_id]}\n"
        
        verbose_summary += f"""
    
    CASE STUDY RECOMMENDATIONS:
    {len(topic_data['case_studies'])} relevant case studies have been identified that illustrate key principles, successful 
    implementations, and lessons learned in {topic_data['topic']}. These case studies span multiple geographies, scales, 
    and contexts, providing valuable real-world examples of how theoretical concepts translate into practical applications. 
    Each case study offers unique insights into implementation challenges, success factors, and measurable outcomes.
    
    Available Case Studies:
    """
        for case_id in topic_data['case_studies']:
            if case_id in CASE_STUDY_SUMMARIES:
                verbose_summary += f"\n    {CASE_STUDY_SUMMARIES[case_id]}\n"
        
        verbose_summary += f"""
    
    METHODOLOGY AND DATA SOURCES:
    This research employed a rigorous multi-method approach combining quantitative analysis, qualitative expert interviews, 
    case study examination, and trend analysis. Data was collected from peer-reviewed academic sources, industry reports, 
    government databases, international organizations, and proprietary research databases. All data has been cross-validated 
    for accuracy and reliability. The research methodology follows international standards for academic and professional research.
    
    IMPLICATIONS AND RECOMMENDATIONS:
    The findings presented in this report have significant implications for stakeholders including investors, policymakers, 
    researchers, and industry participants. Key recommendations include strategic investment priorities, research directions, 
    policy considerations, and market opportunities. These recommendations are based on the comprehensive analysis of current 
    trends, expert insights, and quantitative projections.
    
    FUTURE RESEARCH DIRECTIONS:
    While this report provides comprehensive coverage of {topic_data['topic']}, ongoing research continues to uncover new 
    insights and developments. Future research directions include emerging technologies, evolving market dynamics, regulatory 
    changes, and international developments. Stakeholders are encouraged to stay informed about ongoing developments in this 
    rapidly evolving field.
    """
        
        # Build expert summaries list
        expert_summaries_list = []
        for expert_id in topic_data['experts']:
            if expert_id in EXPERT_SUMMARIES:
                expert_summaries_list.append({
                    "expert_id": expert_id,
                    "summary": EXPERT_SUMMARIES[expert_id]
                })
        
        # Build case study summaries list
        case_study_summaries_list = []
        for case_id in topic_data['case_studies']:
            if case_id in CASE_STUDY_SUMMARIES:
                case_study_summaries_list.append({
                    "case_study_id": case_id,
                    "summary": CASE_STUDY_SUMMARIES[case_id]
                })
        
        return {
            "data": {
                "topic": topic_data["topic"],
                "research_depth": depth,
                "key_points": key_points,
                # Note: Statistics are NOT included here - use get_statistics() tool for detailed metrics
                "expert_summaries": expert_summaries_list,  # Verbose summaries with IDs for calling get_expert_opinion
                "case_study_summaries": case_study_summaries_list,  # Verbose summaries with IDs for calling get_case_study
                "summary": verbose_summary,
                "detailed_analysis": verbose_summary  # Duplicate for extra verbosity
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing research_topic: {str(e)}"}


@tool
def research_topic(topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """Research a specific topic and return comprehensive information."""
    return _research_topic_impl(topic, depth)


@tool
def get_expert_opinion(topic: str, expert_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get expert opinion on a specific topic.
    
    Args:
        topic: The topic to get expert opinion on
        expert_id: Optional specific expert ID. If not provided, selects a relevant expert.
    
    Returns:
        Detailed expert opinion including name, affiliation, expertise, and detailed commentary.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found. Available topics: {', '.join(RESEARCH_TOPICS.keys())}"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        available_experts = topic_data["experts"]
        
        if expert_id and expert_id in EXPERT_OPINIONS:
            expert_key = expert_id
        else:
            # Select random expert for this topic
            expert_key = random.choice(available_experts)
        
        if expert_key not in EXPERT_OPINIONS:
            return {
                "ok": False,
                "error": f"Expert '{expert_key}' not found"
            }
        
        expert = EXPERT_OPINIONS[expert_key]
        
        # Get opinion on this topic
        opinion = expert["opinions"].get(topic_key, "No specific opinion available for this topic.")
        
        return {
            "ok": True,
            "data": {
                "expert_id": expert_key,
                "expert_name": expert["name"],
                "affiliation": expert["affiliation"],
                "expertise_areas": expert["expertise"],
                "topic": topic_data["topic"],
                "opinion": opinion,
                "related_topics": [t for t in expert["opinions"].keys() if t != topic_key],
                "credibility_notes": f"{expert['name']} is a recognized expert in {', '.join(expert['expertise'][:2])} "
                                    f"with extensive research and industry experience. Their insights are based on "
                                    f"years of study and practical application in the field."
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing get_expert_opinion: {str(e)}"}


@tool
def get_statistics(topic: str) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific topic.
    
    Args:
        topic: The topic to get statistics for
    
    Returns:
        Comprehensive statistics including all metrics, trends, and contextual information.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found. Available topics: {', '.join(RESEARCH_TOPICS.keys())}"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        stats = topic_data["statistics"]
        selected_stats = stats
        
        # Generate verbose statistical analysis
        stat_descriptions = {
        "global_capacity_gw": "Global installed capacity in gigawatts",
        "annual_growth_rate_percent": "Year-over-year growth rate percentage",
        "investment_billions_usd": "Total annual investment in billions of US dollars",
        "jobs_created_millions": "Total jobs created globally in millions",
        "co2_reduction_mt": "Annual CO2 reduction in million metric tons",
        "global_market_billions_usd": "Total global market size in billions of US dollars",
        "qubits_achieved": "Maximum number of qubits achieved in quantum processors",
        "quantum_computers_built": "Total number of quantum computers built globally",
        "patents_filed": "Total number of patents filed in this field",
        "research_papers_published": "Total research papers published",
        "evs_on_road_millions": "Total electric vehicles on the road globally in millions",
        "charging_stations_global": "Total charging stations worldwide in millions",
        "battery_cost_per_kwh": "Battery cost per kilowatt-hour in US dollars",
        "market_share_percent": "Market share percentage",
        "co2_emissions_gt": "Annual CO2 emissions in gigatons",
        "temperature_increase_c": "Temperature increase in degrees Celsius since pre-industrial times",
        "sea_level_rise_cm": "Sea level rise in centimeters",
        "extreme_events_count": "Number of extreme weather events recorded",
        "adaptation_cost_billions_usd": "Estimated adaptation costs in billions of US dollars",
        "cyberattacks_per_day": "Average number of cyberattacks per day globally",
        "data_breaches_2023": "Total data breaches recorded in 2023",
        "cybersecurity_market_billions_usd": "Global cybersecurity market size in billions of US dollars",
        "security_professionals_needed": "Number of cybersecurity professionals needed globally in millions",
        "average_breach_cost_millions_usd": "Average cost of a data breach in millions of US dollars",
        "crypto_market_cap_billions_usd": "Total cryptocurrency market capitalization in billions of US dollars",
        "blockchain_transactions_daily": "Daily blockchain transactions in millions",
        "defi_tvl_billions_usd": "Total value locked in DeFi protocols in billions of US dollars",
        "nft_sales_billions_usd": "Total NFT sales volume in billions of US dollars",
        "blockchain_developers": "Number of active blockchain developers globally",
        "satellites_launched_2023": "Total satellites launched in 2023",
        "space_industry_value_billions_usd": "Total space industry market value in billions of US dollars",
        "mars_missions_active": "Number of active Mars missions",
        "astronauts_in_space": "Current number of astronauts in space",
            "space_debris_tracked": "Number of space debris objects being tracked"
        }
        
        detailed_stats = {}
        for key, value in selected_stats.items():
            description = stat_descriptions.get(key, "Statistical metric")
            detailed_stats[key] = {
                "value": value,
                "description": description,
                "unit": _get_unit(key),
                "context": f"This metric represents {description.lower()} for {topic_data['topic']}. "
                          f"The value of {value} {_get_unit(key)} indicates significant activity and growth in this field."
            }
        
        return {
            "data": {
                "topic": topic_data["topic"],
                "statistics": detailed_stats,
                "analysis": f"Statistical analysis for {topic_data['topic']} reveals {len(selected_stats)} key metrics. "
                           f"These metrics demonstrate the scale, growth, and impact of this field. "
                           f"Trends indicate strong growth and increasing importance in the global economy.",
                "data_sources": "Statistics compiled from industry reports, academic research, government data, "
                              "and market analysis. Data is current as of 2023-2024 and represents the most "
                              "recent comprehensive analysis available.",
                "methodology": "Metrics are calculated using standardized methodologies across sources. "
                             "Where multiple sources exist, values represent consensus estimates. "
                             "All financial figures are in US dollars unless otherwise specified."
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing get_statistics: {str(e)}"}


@tool
def get_case_study(topic: str, case_study_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed case study information for a topic.
    
    Args:
        topic: The topic to get case studies for
        case_study_id: Optional specific case study ID. If not provided, returns a relevant case study.
    
    Returns:
        Comprehensive case study including title, details, metrics, lessons learned, and analysis.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found. Available topics: {', '.join(RESEARCH_TOPICS.keys())}"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        available_case_studies = topic_data["case_studies"]
        
        if case_study_id and case_study_id in CASE_STUDIES:
            case_key = case_study_id
        else:
            # Select random case study for this topic
            case_key = random.choice(available_case_studies)
        
        if case_key not in CASE_STUDIES:
            return {
                "ok": False,
                "error": f"Case study '{case_key}' not found"
            }
        
        case = CASE_STUDIES[case_key]
        
        return {
            "ok": True,
            "data": {
                "case_study_id": case_key,
                "title": case["title"],
                "topic": case["topic"],
                "detailed_description": case["details"],
                "key_metrics": case["metrics"],
                "lessons_learned": case["lessons"],
                "relevance": f"This case study is highly relevant to understanding {topic_data['topic']}. "
                            f"It provides concrete examples of real-world implementation, challenges faced, "
                            f"and outcomes achieved. The metrics demonstrate measurable impact, while the "
                            f"lessons learned offer valuable insights for future projects and initiatives.",
                "applicability": f"The principles demonstrated in this case study can be applied to similar "
                               f"situations in {topic_data['topic']}. Key factors for success include "
                               f"{', '.join(case['lessons'][:2])}. Organizations looking to implement "
                               f"similar initiatives should consider these factors carefully.",
                "additional_context": f"This case study represents one of {len(available_case_studies)} "
                                     f"notable examples in {topic_data['topic']}. Each case study offers "
                                     f"unique insights into different aspects, challenges, and approaches "
                                     f"within this field."
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing get_case_study: {str(e)}"}


@tool
def compare_topics(topic1: str, topic2: str) -> Dict[str, Any]:
    """
    Compare two topics across multiple dimensions.
    
    Args:
        topic1: First topic to compare
        topic2: Second topic to compare
        comparison_aspects: Optional list of specific aspects to compare. If not provided, compares all aspects.
    
    Returns:
        Detailed comparison including similarities, differences, market size, growth rates, and implications.
    """
    try:
        topic1_key = topic1.lower().replace(" ", "_")
        topic2_key = topic2.lower().replace(" ", "_")
        
        if topic1_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic1}' not found"
            }
        
        if topic2_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic2}' not found"
            }
        
        topic1_data = RESEARCH_TOPICS[topic1_key]
        topic2_data = RESEARCH_TOPICS[topic2_key]
        
        # Compare statistics
        stats1 = topic1_data["statistics"]
        stats2 = topic2_data["statistics"]
        
        comparison = {
            "topic1": topic1_data["topic"],
            "topic2": topic2_data["topic"],
            "statistical_comparison": {},
            "key_points_overlap": [],
            "key_points_differences": [],
            "market_comparison": {},
            "growth_comparison": {},
            "synergies": [],
            "trade_offs": []
        }
        
        # Compare common metrics
        common_metrics = set(stats1.keys()) & set(stats2.keys())
        for metric in common_metrics:
            val1 = stats1[metric]
            val2 = stats2[metric]
            comparison["statistical_comparison"][metric] = {
                "topic1_value": val1,
                "topic2_value": val2,
                "difference": val2 - val1,
                "difference_percent": ((val2 - val1) / val1 * 100) if val1 != 0 else 0,
                "analysis": f"{topic2_data['topic']} has a {metric} of {val2}, compared to {val1} for {topic1_data['topic']}. "
                           f"This represents a difference of {abs(val2 - val1)} {_get_unit(metric)}."
            }
        
        # Find overlapping key points
        points1 = set([p[:50] for p in topic1_data["key_points"]])
        points2 = set([p[:50] for p in topic2_data["key_points"]])
        comparison["key_points_overlap"] = list(points1 & points2)[:3]
        comparison["key_points_differences"] = [
            f"{topic1_data['topic']} focuses on: {topic1_data['key_points'][0][:100]}",
            f"{topic2_data['topic']} focuses on: {topic2_data['key_points'][0][:100]}"
        ]
        
        # Market and growth comparison
        if "global_market_billions_usd" in stats1 and "global_market_billions_usd" in stats2:
            comparison["market_comparison"] = {
                "topic1_market": stats1["global_market_billions_usd"],
                "topic2_market": stats2["global_market_billions_usd"],
                "combined_market": stats1["global_market_billions_usd"] + stats2["global_market_billions_usd"],
                "analysis": f"The combined market size for both topics is ${stats1['global_market_billions_usd'] + stats2['global_market_billions_usd']} billion, "
                           f"indicating significant economic activity across both fields."
            }
        
        if "annual_growth_rate_percent" in stats1 and "annual_growth_rate_percent" in stats2:
            comparison["growth_comparison"] = {
                "topic1_growth": stats1["annual_growth_rate_percent"],
                "topic2_growth": stats2["annual_growth_rate_percent"],
                "faster_growing": topic2_data["topic"] if stats2["annual_growth_rate_percent"] > stats1["annual_growth_rate_percent"] else topic1_data["topic"],
                "analysis": f"{topic2_data['topic'] if stats2['annual_growth_rate_percent'] > stats1['annual_growth_rate_percent'] else topic1_data['topic']} "
                           f"is growing faster at {max(stats1['annual_growth_rate_percent'], stats2['annual_growth_rate_percent'])}% annually."
            }
        
        # Generate synergies and trade-offs
        comparison["synergies"] = [
            f"Both {topic1_data['topic']} and {topic2_data['topic']} benefit from advances in artificial intelligence and computing.",
            f"Cross-pollination between these fields could accelerate innovation in both areas.",
            f"Combined applications could address complex challenges requiring expertise from both domains."
        ]
        
        comparison["trade_offs"] = [
            f"Investment in {topic1_data['topic']} may compete with resources for {topic2_data['topic']}.",
            f"Different regulatory frameworks may apply to each field, requiring separate approaches.",
            f"Technical expertise requirements differ, potentially limiting cross-field collaboration."
        ]
        
        return {
            "ok": True,
            "data": comparison,
            "summary": f"Comprehensive comparison between {topic1_data['topic']} and {topic2_data['topic']} "
                     f"reveals {len(common_metrics)} comparable metrics, {len(comparison['synergies'])} potential synergies, "
                     f"and {len(comparison['trade_offs'])} important trade-offs to consider. "
                     f"This analysis provides valuable insights for strategic planning and resource allocation."
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing compare_topics: {str(e)}"}


@tool
def get_year_data(topic: str, year: int) -> Dict[str, Any]:
    """
    Get data for a specific topic in a specific year. More atomic than get_historical_trends.
    You must call this multiple times for different years to build historical trends.
    
    Args:
        topic: The topic to get data for
        year: The specific year to retrieve data for
    
    Returns:
        Data for the topic in that specific year.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        stats = topic_data["statistics"]
        current_year = 2024
        years_ago = current_year - year
        
        if years_ago < 0:
            return {"ok": False, "error": f"Year {year} is in the future"}
        
        # Simulate data for that year
        year_data = {}
        growth_rate = 0.1
        for metric, current_value in stats.items():
            if isinstance(current_value, (int, float)) and current_value > 0:
                if "growth_rate" in metric or "percent" in metric:
                    value = current_value * (1 - growth_rate * years_ago / 10)
                else:
                    value = current_value / ((1 + growth_rate) ** years_ago)
                year_data[metric] = value
        
        verbose_response = f"""
    HISTORICAL DATA RETRIEVAL: {topic_data['topic']} - YEAR {year}
    
    This data point represents the state of {topic_data['topic']} in the year {year}, which was {years_ago} years ago. 
    The data has been carefully reconstructed from historical records, industry reports, and statistical databases. 
    Understanding the historical context of this year is crucial for analyzing long-term trends and patterns in the field.
    
    YEAR-SPECIFIC CONTEXT:
    The year {year} was a significant period in the evolution of {topic_data['topic']}. During this time, the industry was 
    characterized by specific technological capabilities, market conditions, regulatory environments, and competitive landscapes. 
    The data presented here reflects the state of knowledge, market size, and technological maturity at that specific point 
    in time. This historical snapshot provides essential context for understanding how the field has evolved and where it 
    may be heading in the future.
    
    METRIC VALUES FOR YEAR {year}:
    """
        for metric, value in year_data.items():
            verbose_response += f"""
    - {metric}: {value}
    
    This metric represents a key indicator of the {topic_data['topic']} sector's performance in {year}. The value reflects 
    the cumulative impact of technological advances, market forces, policy decisions, and industry dynamics up to that point. 
    Comparing this value to current values reveals the trajectory and pace of change in the field. This historical data point 
    is essential for trend analysis, growth projections, and understanding the long-term evolution of the sector.
    """
        
        return {
            "ok": True,
            "data": {
                "topic": topic_data["topic"],
                "year": year,
                "years_ago": years_ago,
                "metrics": year_data,
                "detailed_report": verbose_response
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing get_year_data: {str(e)}"}


@tool
def get_historical_trends(topic: str, time_range_years: int = 10) -> Dict[str, Any]:
    """
    Get historical trends and evolution of a topic over time.
    
    Args:
        topic: The topic to analyze historical trends for
        time_range_years: Number of years to analyze (default: 10)
    
    Returns:
        Detailed historical analysis including trends, milestones, and evolution.
    """
    try:
        topic_key = topic.lower().replace(" ", "_")
        
        if topic_key not in RESEARCH_TOPICS:
            return {
                "ok": False,
                "error": f"Topic '{topic}' not found"
            }
        
        topic_data = RESEARCH_TOPICS[topic_key]
        stats = topic_data["statistics"]
        
        # Generate historical trend data (simulated)
        current_year = 2024
        years = list(range(current_year - time_range_years, current_year + 1))
        
        # Simulate growth trends
        trends = {}
        for metric, current_value in stats.items():
            if isinstance(current_value, (int, float)) and current_value > 0:
                # Simulate exponential or linear growth
                growth_rate = 0.1  # 10% annual growth assumption
                historical_values = []
                for year in years:
                    years_ago = current_year - year
                    if "growth_rate" in metric or "percent" in metric:
                        # For percentages, use different logic
                        value = current_value * (1 - growth_rate * years_ago / time_range_years)
                    else:
                        # For absolute values, assume exponential growth
                        value = current_value / ((1 + growth_rate) ** years_ago)
                    historical_values.append({"year": year, "value": value})
                trends[metric] = historical_values
        
        return {
            "ok": True,
            "data": {
                "topic": topic_data["topic"],
                "time_range_years": time_range_years,
                "historical_trends": trends,
                "key_milestones": [
                    f"{time_range_years} years ago: Early research and development phase",
                    f"{time_range_years // 2} years ago: First commercial applications emerged",
                    "Recent years: Rapid growth and mainstream adoption",
                    "Current: Mature market with established players and standards"
                ],
                "trend_analysis": f"Analysis of {topic_data['topic']} over the past {time_range_years} years reveals "
                                f"consistent growth across all major metrics. The field has evolved from early research "
                                f"to commercial viability, with accelerating adoption in recent years. Key drivers "
                                f"include technological advances, cost reductions, and increasing market demand.",
                "future_projection": f"Based on current trends, {topic_data['topic']} is expected to continue growing "
                                   f"at a strong pace. Factors supporting continued growth include ongoing innovation, "
                                   f"expanding applications, and increasing investment from both public and private sectors."
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing get_historical_trends: {str(e)}"}


@tool
def synthesize_research(topics: List[str], focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Synthesize research findings across multiple topics.
    
    Args:
        topics: List of topics to synthesize
        focus_areas: Optional list of specific areas to focus on (e.g., ["market_size", "growth", "applications"])
    
    Returns:
        Comprehensive synthesis including cross-topic insights, patterns, and recommendations.
    """
    try:
        if not topics:
            return {
                "ok": False,
                "error": "At least one topic must be provided"
            }
        
        topic_data_list = []
        for topic in topics:
            topic_key = topic.lower().replace(" ", "_")
            if topic_key in RESEARCH_TOPICS:
                topic_data_list.append(RESEARCH_TOPICS[topic_key])
            else:
                return {
                    "ok": False,
                    "error": f"Topic '{topic}' not found"
                }
        
        # Generate synthesis
        all_key_points = []
        all_statistics = {}
        all_experts = set()
        all_case_studies = []
        
        for topic_data in topic_data_list:
            all_key_points.extend(topic_data["key_points"])
            all_statistics.update(topic_data["statistics"])
            all_experts.update(topic_data["experts"])
            all_case_studies.extend(topic_data["case_studies"])
        
        # Find common themes
        common_themes = [
            "Technological innovation driving growth",
            "Significant market opportunities",
            "Impact on global economy and society",
            "Need for skilled professionals",
            "Regulatory and policy considerations"
        ]
        
        return {
            "ok": True,
            "data": {
                "topics_synthesized": [td["topic"] for td in topic_data_list],
                "total_key_points": len(all_key_points),
                "total_statistics": len(all_statistics),
                "total_experts": len(all_experts),
                "total_case_studies": len(all_case_studies),
                "common_themes": common_themes,
                "cross_topic_insights": [
                    f"All {len(topic_data_list)} topics show strong growth potential and significant market size.",
                    f"Combined expertise across these fields includes {len(all_experts)} leading researchers and practitioners.",
                    f"Case studies reveal {len(all_case_studies)} successful implementations across the topics.",
                    f"Statistical analysis shows combined market value exceeding $500 billion.",
                    f"Key challenges include talent acquisition, regulatory compliance, and technological integration."
                ],
                "recommendations": [
                    f"Focus on areas where {len(topic_data_list)} topics intersect for maximum impact.",
                    f"Leverage expertise from {len(all_experts)} identified experts for strategic guidance.",
                    f"Study {len(all_case_studies)} case studies to understand best practices and lessons learned.",
                    f"Monitor trends across all topics to identify emerging opportunities.",
                    f"Develop integrated strategies that leverage synergies between topics."
                ],
                "synthesis_summary": f"This synthesis combines research from {len(topic_data_list)} major topics, "
                                  f"incorporating {len(all_key_points)} key points, {len(all_statistics)} statistical metrics, "
                                  f"insights from {len(all_experts)} experts, and analysis of {len(all_case_studies)} case studies. "
                                  f"The comprehensive analysis reveals {len(common_themes)} common themes and provides "
                                  f"{len(common_themes)} strategic recommendations for moving forward."
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing synthesize_research: {str(e)}"}


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _get_unit(metric_key: str) -> str:
    """Get unit for a metric."""
    if "billions_usd" in metric_key or "millions_usd" in metric_key:
        return "USD"
    elif "percent" in metric_key or "rate" in metric_key:
        return "%"
    elif "gw" in metric_key or "mw" in metric_key:
        return "W"
    elif "tons" in metric_key or "mt" in metric_key:
        return "tons"
    elif "qubits" in metric_key:
        return "qubits"
    elif "c" in metric_key and "temperature" in metric_key:
        return "°C"
    elif "cm" in metric_key:
        return "cm"
    elif "miles" in metric_key:
        return "miles"
    elif "kwh" in metric_key:
        return "kWh"
    else:
        return "units"


# =====================================================
# TOOL EXPORTS
# =====================================================

core_research_tools = [
    research_topic,
    get_expert_opinion,
    get_statistics,
    get_case_study,
    get_year_data,  
]

@tool
def calculate_compound_growth(initial_value: float, growth_rate: float, years: int) -> Dict[str, Any]:
    """
    Calculate compound growth over multiple years.
    
    Args:
        initial_value: Starting value
        growth_rate: Annual growth rate as decimal (e.g., 0.15 for 15%)
        years: Number of years
    
    Returns:
        Detailed calculation results including final value, total growth, and year-by-year breakdown.
    """
    try:
        final_value = initial_value * ((1 + growth_rate) ** years)
        total_growth = final_value - initial_value
        growth_percentage = (total_growth / initial_value) * 100
        
        year_by_year = []
        current_value = initial_value
        for year in range(1, years + 1):
            current_value = current_value * (1 + growth_rate)
            year_by_year.append({
                "year": year,
                "value": round(current_value, 2),
                "growth_this_year": round(current_value - (current_value / (1 + growth_rate)), 2)
            })
        
        return {
            "ok": True,
            "calculation": {
                "initial_value": initial_value,
                "growth_rate": f"{growth_rate * 100:.2f}%",
                "years": years,
                "final_value": round(final_value, 2),
                "total_growth": round(total_growth, 2),
                "growth_percentage": round(growth_percentage, 2),
                "year_by_year_breakdown": year_by_year,
                "formula": f"Final = {initial_value} × (1 + {growth_rate})^{years} = {round(final_value, 2)}"
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_compound_growth: {str(e)}"}


@tool
def calculate_market_share(market_size: float, company_revenue: float, market_segments: Optional[List[Dict[str, float]]] = None) -> Dict[str, Any]:
    """
    Calculate market share and perform market analysis.
    
    Args:
        market_size: Total market size in billions USD
        company_revenue: Company revenue in billions USD
        market_segments: Optional list of market segments with their sizes
    
    Returns:
        Market share analysis with detailed breakdowns.
    """
    try:
        if market_size == 0:
            return {"ok": False, "error": "Market size cannot be zero"}
        
        market_share_percent = (company_revenue / market_size) * 100
        
        segment_analysis = []
        if market_segments:
            for segment in market_segments:
                segment_name = segment.get("name", "Unknown")
                segment_size = segment.get("size", 0)
                segment_share = (segment_size / market_size) * 100
                segment_analysis.append({
                    "segment": segment_name,
                    "size_billions": segment_size,
                    "market_share_percent": round(segment_share, 2)
                })
        
        return {
            "ok": True,
            "analysis": {
                "total_market_size_billions": market_size,
                "company_revenue_billions": company_revenue,
                "market_share_percent": round(market_share_percent, 2),
                "remaining_market_billions": round(market_size - company_revenue, 2),
                "segment_breakdown": segment_analysis,
                "competitive_position": "dominant" if market_share_percent > 30 else "strong" if market_share_percent > 15 else "moderate" if market_share_percent > 5 else "niche"
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_market_share: {str(e)}"}


@tool
def analyze_correlation(data_points: List[Dict[str, float]], variable1: str, variable2: str) -> Dict[str, Any]:
    """
    Perform correlation analysis between two variables across multiple data points.

    Args:
        data_points: List of dictionaries with data points
        variable1: First variable name to analyze
        variable2: Second variable name to analyze
    
    Returns:
        Correlation analysis with statistical measures.
    """
    try:
        if not data_points:
            return {"ok": False, "error": "No data points provided"}
        
        values1 = [dp.get(variable1, 0) for dp in data_points]
        values2 = [dp.get(variable2, 0) for dp in data_points]
        
        if len(values1) != len(values2):
            return {"ok": False, "error": "Mismatched data lengths"}
        
        n = len(values1)
        if n == 0:
            return {"ok": False, "error": "No valid data points"}
        
        mean1 = sum(values1) / n
        mean2 = sum(values2) / n
        
        # Calculate correlation coefficient
        numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))
        variance1 = sum((x - mean1) ** 2 for x in values1)
        variance2 = sum((x - mean2) ** 2 for x in values2)
        denominator = (variance1 * variance2) ** 0.5
        
        correlation = numerator / denominator if denominator > 0 else 0
        
        # Calculate additional statistics
        min1, max1 = min(values1), max(values1)
        min2, max2 = min(values2), max(values2)
        
        return {
            "ok": True,
            "correlation_analysis": {
                "variable1": variable1,
                "variable2": variable2,
                "data_points": n,
                "correlation_coefficient": round(correlation, 4),
                "correlation_strength": "strong positive" if correlation > 0.7 else "moderate positive" if correlation > 0.3 else "weak positive" if correlation > 0 else "weak negative" if correlation > -0.3 else "moderate negative" if correlation > -0.7 else "strong negative",
                "variable1_stats": {
                    "mean": round(mean1, 2),
                    "min": min1,
                    "max": max1,
                    "range": round(max1 - min1, 2)
                },
                "variable2_stats": {
                    "mean": round(mean2, 2),
                    "min": min2,
                    "max": max2,
                    "range": round(max2 - min2, 2)
                }
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing analyze_correlation: {str(e)}"}


@tool
def calculate_cost_benefit_analysis(
    initial_investment: float,
    annual_benefits: List[float],
    discount_rate: float,
    years: int
) -> Dict[str, Any]:
    """
    Perform cost-benefit analysis with NPV calculations.
    Consultant-level financial analysis.
    
    Args:
        initial_investment: Initial cost
        annual_benefits: List of annual benefits (can vary by year)
        discount_rate: Discount rate as decimal
        years: Number of years
    
    Returns:
        Detailed CBA with NPV, ROI, payback period, etc.
    """
    try:
        if not annual_benefits:
            return {"ok": False, "error": "Annual benefits list cannot be empty"}
        if initial_investment == 0:
            return {"ok": False, "error": "Initial investment cannot be zero"}
        
        if len(annual_benefits) < years:
            annual_benefits = annual_benefits + [annual_benefits[-1]] * (years - len(annual_benefits))
        
        npv = -initial_investment
        discounted_benefits = []
        cumulative_benefits = 0
        payback_period = None
        
        for year in range(1, years + 1):
            benefit = annual_benefits[year - 1]
            discounted = benefit / ((1 + discount_rate) ** year)
            discounted_benefits.append({
                "year": year,
                "benefit": benefit,
                "discounted_benefit": round(discounted, 2),
                "discount_factor": round(1 / ((1 + discount_rate) ** year), 4)
            })
            npv += discounted
            cumulative_benefits += discounted
            
            if payback_period is None and cumulative_benefits >= initial_investment:
                payback_period = year
        
        total_benefits = sum(annual_benefits)
        roi = ((total_benefits - initial_investment) / initial_investment) * 100
        
        return {
            "ok": True,
            "cba_results": {
                "initial_investment": initial_investment,
                "discount_rate": f"{discount_rate * 100:.2f}%",
                "years": years,
                "total_benefits": round(total_benefits, 2),
                "net_present_value": round(npv, 2),
                "roi_percent": round(roi, 2),
                "payback_period_years": payback_period,
                "year_by_year_analysis": discounted_benefits,
                "recommendation": "proceed" if npv > 0 else "reconsider"
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_cost_benefit_analysis: {str(e)}"}


@tool
def aggregate_statistics(data: List[Dict[str, Any]], group_by: str, metrics: List[str]) -> Dict[str, Any]:
    """
    SQL-like aggregation: group by field and calculate metrics.
    Real consultant analysis task.
    
    Args:
        data: List of data records
        group_by: Field to group by
        metrics: List of metrics to calculate (e.g., ["sum", "avg", "count", "max", "min"])
    
    Returns:
        Aggregated statistics grouped by the specified field.
    """
    try:
        if not data:
            return {"ok": False, "error": "No data provided"}
        
        groups = {}
        for record in data:
            group_key = record.get(group_by, "unknown")
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)
        
        aggregated = {}
        numeric_fields = []
        
        # Find numeric fields
        if data:
            for key, value in data[0].items():
                if isinstance(value, (int, float)) and key != group_by:
                    numeric_fields.append(key)
        
        for group_key, group_data in groups.items():
            group_stats = {"count": len(group_data)}
            
            for field in numeric_fields:
                values = [r.get(field, 0) for r in group_data if isinstance(r.get(field), (int, float))]
                if values:
                    group_stats[field] = {
                        "sum": round(sum(values), 2),
                        "avg": round(sum(values) / len(values), 2),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
            
            aggregated[group_key] = group_stats
        
        return {
            "ok": True,
            "aggregation": {
                "group_by": group_by,
                "total_groups": len(groups),
                "total_records": len(data),
                "grouped_statistics": aggregated,
                "numeric_fields_analyzed": numeric_fields
            }
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing aggregate_statistics: {str(e)}"}


analysis_tools = [
    compare_topics,
    get_historical_trends,
]

# =====================================================
# ATOMIC MATH TOOLS
# =====================================================

@tool
def calculate_discount_factor(discount_rate: float, year: int) -> Dict[str, Any]:
    """
    Calculate discount factor for a specific year.
    Atomic math operation: 1 / (1 + r)^n
    
    Args:
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
        year: Year number (1, 2, 3, ...)
    
    Returns:
        Discount factor and calculation details
    """
    try:
        if year <= 0:
            return {"ok": False, "error": "Year must be greater than 0"}
        discount_factor = 1 / ((1 + discount_rate) ** year)
        return {
            "ok": True,
            "discount_factor": round(discount_factor, 6),
            "discount_rate": discount_rate,
            "year": year,
            "formula": f"1 / (1 + {discount_rate})^{year} = {round(discount_factor, 6)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_discount_factor: {str(e)}"}


@tool
def calculate_present_value(future_value: float, discount_rate: float, year: int) -> Dict[str, Any]:
    """
    Calculate present value of a future cash flow.
    Atomic math operation: PV = FV / (1 + r)^n
    
    Args:
        future_value: Future cash flow amount
        discount_rate: Discount rate as decimal
        year: Year when cash flow occurs
    
    Returns:
        Present value and calculation details
    """
    try:
        if year <= 0:
            return {"ok": False, "error": "Year must be greater than 0"}
        discount_factor = 1 / ((1 + discount_rate) ** year)
        present_value = future_value * discount_factor
        return {
            "ok": True,
            "present_value": round(present_value, 2),
            "future_value": future_value,
            "discount_rate": discount_rate,
            "year": year,
            "discount_factor": round(discount_factor, 6),
            "formula": f"{future_value} / (1 + {discount_rate})^{year} = {round(present_value, 2)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_present_value: {str(e)}"}


@tool
def calculate_percentage(value: float, total: float) -> Dict[str, Any]:
    """
    Calculate percentage: (value / total) * 100
    Atomic math operation for percentages.
    
    Args:
        value: The value to calculate percentage of
        total: The total/base value
    
    Returns:
        Percentage and calculation details
    """
    try:
        if total == 0:
            return {"ok": False, "error": "Cannot divide by zero"}
        percentage = (value / total) * 100
        return {
            "ok": True,
            "percentage": round(percentage, 2),
            "value": value,
            "total": total,
            "formula": f"({value} / {total}) × 100 = {round(percentage, 2)}%"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_percentage: {str(e)}"}


@tool
def calculate_weighted_average(values: List[float], weights: List[float]) -> Dict[str, Any]:
    """
    Calculate weighted average: Σ(value × weight) / Σ(weights)
    Atomic math operation for weighted calculations.
    
    Args:
        values: List of values
        weights: List of corresponding weights
    
    Returns:
        Weighted average and calculation details
    """
    try:
        if len(values) != len(weights):
            return {"ok": False, "error": "Values and weights must have same length"}
        if len(values) == 0:
            return {"ok": False, "error": "Empty lists"}
        
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        total_weight = sum(weights)
        
        if total_weight == 0:
            return {"ok": False, "error": "Total weight cannot be zero"}
        
        weighted_avg = weighted_sum / total_weight
        
        return {
            "ok": True,
            "weighted_average": round(weighted_avg, 4),
            "weighted_sum": round(weighted_sum, 2),
            "total_weight": round(total_weight, 2),
            "components": [{"value": v, "weight": w, "contribution": round(v * w, 2)} for v, w in zip(values, weights)],
            "formula": f"Σ(value × weight) / Σ(weights) = {round(weighted_sum, 2)} / {round(total_weight, 2)} = {round(weighted_avg, 4)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_weighted_average: {str(e)}"}


@tool
def calculate_ratio(numerator: float, denominator: float) -> Dict[str, Any]:
    """
    Calculate ratio: numerator / denominator
    Atomic math operation for ratios.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
    
    Returns:
        Ratio and calculation details
    """
    try:
        if denominator == 0:
            return {"ok": False, "error": "Cannot divide by zero"}
        ratio = numerator / denominator
        return {
            "ok": True,
            "ratio": round(ratio, 4),
            "numerator": numerator,
            "denominator": denominator,
            "formula": f"{numerator} / {denominator} = {round(ratio, 4)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_ratio: {str(e)}"}


@tool
def calculate_power(base: float, exponent: float) -> Dict[str, Any]:
    """
    Calculate power: base^exponent
    Atomic math operation for exponentiation.
    
    Args:
        base: Base value
        exponent: Exponent value
    
    Returns:
        Power result and calculation details
    """
    try:
        result = base ** exponent
        return {
            "ok": True,
            "result": round(result, 6),
            "base": base,
            "exponent": exponent,
            "formula": f"{base}^{exponent} = {round(result, 6)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_power: {str(e)}"}


@tool
def calculate_sum(values: List[float]) -> Dict[str, Any]:
    """
    Calculate sum of a list of values.
    Atomic math operation for summation.
    
    Args:
        values: List of numeric values to sum
    
    Returns:
        Sum and calculation details
    """
    try:
        if not values:
            return {"ok": False, "error": "Values list cannot be empty"}
        total = sum(values)
        return {
            "ok": True,
            "sum": round(total, 2),
            "values": values,
            "count": len(values),
            "formula": f"Sum of {len(values)} values = {round(total, 2)}"
        }
    except Exception as e:
        return {"ok": False, "error": f"Error executing calculate_sum: {str(e)}"}


calculation_tools = [
    calculate_compound_growth,
    calculate_market_share,
    analyze_correlation,
    calculate_cost_benefit_analysis,
    aggregate_statistics,
]

atomic_math_tools = [
    calculate_discount_factor,
    calculate_present_value,
    calculate_percentage,
    calculate_weighted_average,
    calculate_ratio,
    calculate_power,
    calculate_sum,
]

# ------------------------------------------------------------
# CUSTOM GRAPH RESEARCH TOOLS
# ------------------------------------------------------------
@tool
def general_research(topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """
    Gather general research information needed for report construction.
    This tool provides comprehensive research on a topic, including key points, statistics,
    expert insights, and case studies. Use this for general information gathering.
    
    Args:
        topic: The topic to research (e.g., "renewable_energy", "artificial_intelligence")
        depth: Research depth - "brief", "standard", or "comprehensive" (default: "comprehensive")
    
    Returns:
        Detailed research information including key points, statistics, experts, and case studies.
    """
    # Call the underlying implementation directly
    return _research_topic_impl(topic, depth)




def create_deep_research_tool(researcher_subgraph):
    """
    Create a deep_research tool that invokes the researcher subgraph.
    
    Args:
        researcher_subgraph: The compiled researcher subgraph to invoke
    
    Returns:
        The deep_research tool function
    """
    @tool
    async def deep_research(
        research_question: str,
        deliverable_key: str,
        data_level: str,
        data_source: str,
        calculation_guidance: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
        runtime: ToolRuntime = None  # ToolRuntime parameter is not visible to the model
    ) -> Command:
        """
        Delegate research tasks to a specialized research agent for resolving a key deliverable.

        This tool delegates the research question to a dedicated research agent that will conduct
        comprehensive research and return findings. The actual research is performed by a specialized
        sub-agent that has access to all research tools.

        Args:
            research_question: The specific research question or deliverable to investigate.
                              Should be clear and specific.
            deliverable_key: The shorthand name/key for this deliverable, from the state.
                            This is the key that should be used when calling store_deliverable.
            data_level: The level of data needed. Must be one of:
                       - "aggregate" (overall metrics across a domain, use statistics)
                       - "specific" (particular scenarios/cases with detailed parameters, use key_points)
                       - "stated" (pre-analyzed results already reported in research)
            data_source: Where to find the data. Should be:
                        - "statistics" for aggregate-level data
                        - "key_points" for specific-level detailed descriptions
                        - "research_findings" for stated values
            calculation_guidance: What formula/method to use and what types of inputs are needed.
                                 Do NOT include actual numeric values - just describe the calculation approach.
                                 Example: "Use compound growth formula with initial value and growth rate over 10 years"

        Returns:
            The compressed research findings from the specialized research agent.
        """
        from langchain_core.messages import HumanMessage
        
        # Invoke the researcher subgraph
        # Get config from runtime if available, otherwise use empty config
        config = runtime.config if runtime else {}
        # Set recursion limit for researcher subgraph (increased to allow for research + store + finish)
        config["recursion_limit"] = 100
        
        # Include deliverable_key and structured guidance in the message
        message_content = f"""=== YOUR ASSIGNED DELIVERABLE KEY ===
**DELIVERABLE_KEY: "{deliverable_key}"**
You MUST use this exact key "{deliverable_key}" when calling store_deliverable with your final answer.
=====================================

Research Question: {research_question}

Data Level: {data_level}
Data Source: {data_source}
Calculation Guidance: {calculation_guidance}"""
        
        result = await researcher_subgraph.ainvoke({
            "reseacher_messages": [HumanMessage(content=message_content)],
            "research_question": research_question,
            "deliverable_key": deliverable_key,
            "data_level": data_level,
            "data_source": data_source,
            "calculation_guidance": calculation_guidance
        }, config)

        # Extract deliverable value and findings from researcher result
        deliverable_value = result.get("deliverables", {}).get(deliverable_key, "To be determined")
        finding = result.get("finding", "Research completed.")

        # Update supervisor deliverables - pass key-value pair, let reducer merge
        return Command(
            update={
                "deliverables": {deliverable_key: deliverable_value},
                "supervisor_messages": [ToolMessage(
                    content=finding,
                    tool_call_id=tool_call_id
                )]
            }
        )
    
    return deep_research


@tool
def think_tool(
    reflection: str,
    runtime: ToolRuntime,  # ToolRuntime parameter is not visible to the model
) -> Dict[str, Any]:
    """
    Think tool for reflection and strategic planning during research.
    Use this tool to plan your approach, including any calculations and formulas you need to use.
    
    Args:
        reflection: Your thoughts, approach, and formulas needed.
    
    Returns:
        Dictionary with confirmation and current status of key deliverables as JSON.
    """
    # Access deliverables from graph state via ToolRuntime
    deliverables_status = runtime.state.get("deliverables", {})
    
    return {
        "confirmation": "Reflection recorded.",
        "status": json.dumps(deliverables_status, indent=2)
    }

@tool
def store_deliverable(
    deliverable_key: str,
    value: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    runtime: ToolRuntime = None  # ToolRuntime parameter is not visible to the model
) -> Command:
    """
    Store a deliverable value in the state.

    Args:
        deliverable_key: The key for the deliverable (e.g., "Q1", "Q2", "renewable_energy_npv")
        value: The value for the deliverable (can be a number, text, or structured data)

    Returns:
        Command that updates the deliverables state.
    """
    # Return Command to update state - pass key-value pair, let reducer merge
    return Command(
        update={
            "deliverables": {deliverable_key: value},
            "reseacher_messages": [ToolMessage(
                content=f"Deliverable '{deliverable_key}' stored successfully.",
                tool_call_id=tool_call_id
            )]
        }
    )


@tool
def finish(
    findings: str,
    runtime: ToolRuntime = None  # ToolRuntime parameter is not visible to the model
) -> Dict[str, Any]:
    """
    Finish the research task and return findings in JSON format.
    
    Args:
        findings: A string summarizing the findings and calculations used to reach the answer.
                  Should include key findings, calculation methods, formulas, and data sources.
    
    Returns:
        JSON object containing the original question and the summary of findings.
    """
    # Get the original question from state
    query = runtime.state.get("query", "") if runtime else ""
    if not query:
        # Try alternative state keys
        query = runtime.state.get("research_question", "") if runtime else ""
    
    # Return JSON format with original question and summary
    return {
        "task": query,
        "findings": findings 
    }


@tool
def research_complete(
    runtime: ToolRuntime = None  # ToolRuntime parameter is not visible to the model
) -> str:
    """
    Indicate that research is complete and ready for final report generation.
    
    Call this tool when you have gathered all necessary research and all key deliverables
    have been resolved. This will transition the workflow to final report generation.
    """
    return "Research complete. Ready for final report generation."


# Standard tools (without reflection)
all_research_tools = core_research_tools + analysis_tools + calculation_tools + atomic_math_tools