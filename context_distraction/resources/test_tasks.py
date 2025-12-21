"""
Test tasks for context distraction evaluation.

Each task is designed to require many operations and test the agent's ability
to maintain accuracy across long context histories. Each task focuses on
different domains to ensure variety.
"""

from context_distraction.resources.expected_calculations import (
    get_primary_domain_base_fact,
    get_secondary_domain_base_fact,
    get_compound_growth_10yr,
    get_cba_npv_10pct,
    get_correlation_market_size_vs_growth,
    get_investment_priority_rank,
    get_risk_adjusted_npv,
    get_weighted_investment_score,
    get_strategic_priority_rank,
    calculate_npv_ratio,
    calculate_weighted_avg_growth,
    calculate_present_value_year5,
    calculate_market_share_percentage,
    calculate_total_investment_sum,
    calculate_growth_multiple_power,
    calculate_discount_factor_year7,
    calculate_npv_difference,
    calculate_weighted_avg_npv,
    calculate_roi_ratio,
)

# All topics used across test tasks
topics_all = ["renewable_energy", "artificial_intelligence", "electric_vehicles", "quantum_computing", "biotechnology"]

# Base task template
BASE_TASK_QUERY = """You are leading a multi-billion dollar investment analysis across {num_domains} technology sectors.

Research domains: {domains}.

For each domain, conduct comprehensive research including:
- Gathering key statistics and market data
- Consulting multiple expert opinions
- Analyzing relevant case studies
- Reviewing historical trends across key years
- Calculating compound growth projections (10-year forecast)
- Running correlation analyses between market size and growth rates
- Conducting cost-benefit analysis with 10% discount rate
- Aggregating statistics by region
- Comparing domains against each other
- Synthesizing comprehensive research findings

After completing research for all domains, create a final synthesis that:
- Compares all domains across multiple dimensions
- Performs investment portfolio optimization using NPV rankings
- Provides geographic market aggregation showing regional patterns
- Creates financial projections using compound growth calculations
- Calculates risk-adjusted return metrics

IMPORTANT: Your analysis must answer these specific questions:
{recall_questions}

CRITICAL OUTPUT FORMAT:
Your final response MUST be valid Markdown with a JSON section at the end containing ALL calculated values in this exact structure:
```json
{{
  "calculations": {{
    "renewable_energy": {{
      "base_facts": {{"capacity_gw": <number>, "market_size_billions": <number>}},
      "compound_growth_10yr": <number>,
      "cba_10pct": {{"npv": <number>, "roi": <number>}},
      "correlation_market_size_vs_growth": <number>,
      "risk_adjusted_npv": <number>,
      "weighted_investment_score": <number>,
      "investment_priority_rank": <number>,
      "strategic_priority_rank": <number>
    }},
    ...
  }}
}}
```

Be thorough and ensure all calculations are accurate and complete."""

# Test task variations - each focuses on different primary domains with diverse Q5-Q9
TEST_TASKS = [
    {
        "name": "Task 1: 5 Domains - Focus on Renewable Energy",
        "primary_domain": "renewable_energy",
        "secondary_domain": "artificial_intelligence",
        "query": BASE_TASK_QUERY.format(
            num_domains=5,
            domains="renewable energy, artificial intelligence, electric vehicles, quantum computing, and biotechnology",
            recall_questions="\n".join([
                "1. What was the global installed capacity in gigawatts for renewable energy?",
                "2. What is the global AI market size in billions of USD?",
                "3. What was the calculated 10-year compound growth final value for renewable energy?",
                "4. What was the NPV calculated for renewable energy CBA with 10% discount rate?",
                "5. What correlation coefficient was calculated between renewable energy market size and growth rate?",
                "6. What is the ratio of renewable energy NPV to artificial intelligence NPV (both at 10% discount)?",
                "7. What is the present value of year 5 benefits for renewable energy at 10% discount rate?",
                "8. What percentage of total market size across all domains does renewable energy represent?",
                "9. What is the weighted average of NPVs across all domains, weighted by investment amounts?",
            ]),
        ),
        "topics": topics_all,
        "expected_steps": 60,
        "recall_questions": [
            f"What was the global installed capacity in gigawatts for renewable energy? (Expected: {get_primary_domain_base_fact('renewable_energy')} GW)",
            f"What is the global AI market size in billions of USD? (Expected: {get_secondary_domain_base_fact('artificial_intelligence')} billion)",
            f"What was the calculated 10-year compound growth final value for renewable energy? (Expected: {get_compound_growth_10yr('renewable_energy')})",
            f"What was the NPV calculated for renewable energy CBA with 10% discount rate? (Expected: {get_cba_npv_10pct('renewable_energy')})",
            f"What correlation coefficient was calculated between renewable energy market size and growth rate? (Expected: {get_correlation_market_size_vs_growth('renewable_energy')})",
            f"What is the ratio of renewable energy NPV to artificial intelligence NPV (both at 10% discount)? (Expected: {calculate_npv_ratio('renewable_energy', 'artificial_intelligence')})",
            f"What is the present value of year 5 benefits for renewable energy at 10% discount rate? (Expected: {calculate_present_value_year5('renewable_energy')})",
            f"What percentage of total market size across all domains does renewable energy represent? (Expected: {calculate_market_share_percentage('renewable_energy', topics_all)}%)",
            f"What is the weighted average of NPVs across all domains, weighted by investment amounts? (Expected: {calculate_weighted_avg_npv(topics_all)})",
        ],
        "expected_answers": {
            1: str(get_primary_domain_base_fact('renewable_energy')),
            2: str(get_secondary_domain_base_fact('artificial_intelligence')),
            3: str(get_compound_growth_10yr('renewable_energy')),
            4: str(get_cba_npv_10pct('renewable_energy')),
            5: str(get_correlation_market_size_vs_growth('renewable_energy')),
            6: str(calculate_npv_ratio('renewable_energy', 'artificial_intelligence')),
            7: str(calculate_present_value_year5('renewable_energy')),
            8: str(calculate_market_share_percentage('renewable_energy', topics_all)),
            9: str(calculate_weighted_avg_npv(topics_all)),
        },
        "stats_count": 5,
        "expert_count": 3,
        "case_count": 2,
        "year_count": 3,
        "compare_count": 2,
    },
    {
        "name": "Task 2: 5 Domains - Focus on Electric Vehicles",
        "primary_domain": "electric_vehicles",
        "secondary_domain": "biotechnology",
        "query": BASE_TASK_QUERY.format(
            num_domains=5,
            domains="renewable energy, artificial intelligence, electric vehicles, quantum computing, and biotechnology",
            recall_questions="\n".join([
                "1. What was the battery cost per kWh for electric vehicles?",
                "2. What is the global biotechnology market size in billions of USD?",
                "3. What was the calculated 10-year compound growth final value for electric vehicles?",
                "4. What was the NPV calculated for electric vehicles CBA with 10% discount rate?",
                "5. What was the investment priority ranking for electric vehicles based on weighted scores?",
                "6. What is the difference between electric vehicles NPV and biotechnology NPV (both at 10% discount)?",
                "7. What is the ratio of electric vehicles ROI to biotechnology ROI (both at 10% discount)?",
                "8. What is the sum of all domain investments in billions USD?",
                "9. What is the growth multiple (compound_growth_10yr / market_size) for electric vehicles raised to the power of 2?",
            ]),
        ),
        "topics": topics_all,
        "expected_steps": 75,
        "recall_questions": [
            f"What was the battery cost per kWh for electric vehicles? (Expected: {get_primary_domain_base_fact('electric_vehicles')} $/kWh)",
            f"What is the global biotechnology market size in billions of USD? (Expected: {get_secondary_domain_base_fact('biotechnology')} billion)",
            f"What was the calculated 10-year compound growth final value for electric vehicles? (Expected: {get_compound_growth_10yr('electric_vehicles')})",
            f"What was the NPV calculated for electric vehicles CBA with 10% discount rate? (Expected: {get_cba_npv_10pct('electric_vehicles')})",
            f"What was the investment priority ranking for electric vehicles based on weighted scores? (Expected: Rank {get_investment_priority_rank('electric_vehicles')})",
            f"What is the difference between electric vehicles NPV and biotechnology NPV (both at 10% discount)? (Expected: {calculate_npv_difference('electric_vehicles', 'biotechnology')})",
            f"What is the ratio of electric vehicles ROI to biotechnology ROI (both at 10% discount)? (Expected: {calculate_roi_ratio('electric_vehicles', 'biotechnology')})",
            f"What is the sum of all domain investments in billions USD? (Expected: {calculate_total_investment_sum(topics_all)})",
            f"What is the growth multiple (compound_growth_10yr / market_size) for electric vehicles raised to the power of 2? (Expected: {calculate_growth_multiple_power('electric_vehicles')})",
        ],
        "expected_answers": {
            1: str(get_primary_domain_base_fact('electric_vehicles')),
            2: str(get_secondary_domain_base_fact('biotechnology')),
            3: str(get_compound_growth_10yr('electric_vehicles')),
            4: str(get_cba_npv_10pct('electric_vehicles')),
            5: str(get_investment_priority_rank('electric_vehicles')),
            6: str(calculate_npv_difference('electric_vehicles', 'biotechnology')),
            7: str(calculate_roi_ratio('electric_vehicles', 'biotechnology')),
            8: str(calculate_total_investment_sum(topics_all)),
            9: str(calculate_growth_multiple_power('electric_vehicles')),
        },
        "stats_count": 6,
        "expert_count": 4,
        "case_count": 3,
        "year_count": 4,
        "compare_count": 2,
    },
    {
        "name": "Task 3: 5 Domains - Focus on Quantum Computing",
        "primary_domain": "quantum_computing",
        "secondary_domain": "artificial_intelligence",
        "query": BASE_TASK_QUERY.format(
            num_domains=5,
            domains="renewable energy, artificial intelligence, electric vehicles, quantum computing, and biotechnology",
            recall_questions="\n".join([
                "1. What was the number of qubits for quantum computing?",
                "2. What is the global AI market size in billions of USD?",
                "3. What was the calculated 10-year compound growth final value for quantum computing?",
                "4. What was the NPV calculated for quantum computing CBA with 10% discount rate?",
                "5. What was the risk-adjusted NPV for quantum computing?",
                "6. What is the weighted average growth rate across all domains, weighted by market size?",
                "7. What is the discount factor for year 7 at 10% discount rate?",
                "8. What was the strategic priority ranking for quantum computing in your final analysis?",
                "9. What is the ratio of quantum computing NPV to artificial intelligence NPV (both at 10% discount)?",
            ]),
        ),
        "topics": topics_all,
        "expected_steps": 78,
        "recall_questions": [
            f"What was the number of qubits for quantum computing? (Expected: {get_primary_domain_base_fact('quantum_computing')} qubits)",
            f"What is the global AI market size in billions of USD? (Expected: {get_secondary_domain_base_fact('artificial_intelligence')} billion)",
            f"What was the calculated 10-year compound growth final value for quantum computing? (Expected: {get_compound_growth_10yr('quantum_computing')})",
            f"What was the NPV calculated for quantum computing CBA with 10% discount rate? (Expected: {get_cba_npv_10pct('quantum_computing')})",
            f"What was the risk-adjusted NPV for quantum computing? (Expected: {get_risk_adjusted_npv('quantum_computing')})",
            f"What is the weighted average growth rate across all domains, weighted by market size? (Expected: {calculate_weighted_avg_growth(topics_all)})",
            f"What is the discount factor for year 7 at 10% discount rate? (Expected: {calculate_discount_factor_year7()})",
            f"What was the strategic priority ranking for quantum computing in your final analysis? (Expected: Rank {get_strategic_priority_rank('quantum_computing')})",
            f"What is the ratio of quantum computing NPV to artificial intelligence NPV (both at 10% discount)? (Expected: {calculate_npv_ratio('quantum_computing', 'artificial_intelligence')})",
        ],
        "expected_answers": {
            1: str(get_primary_domain_base_fact('quantum_computing')),
            2: str(get_secondary_domain_base_fact('artificial_intelligence')),
            3: str(get_compound_growth_10yr('quantum_computing')),
            4: str(get_cba_npv_10pct('quantum_computing')),
            5: str(get_risk_adjusted_npv('quantum_computing')),
            6: str(calculate_weighted_avg_growth(topics_all)),
            7: str(calculate_discount_factor_year7()),
            8: str(get_strategic_priority_rank('quantum_computing')),
            9: str(calculate_npv_ratio('quantum_computing', 'artificial_intelligence')),
        },
        "stats_count": 6,
        "expert_count": 4,
        "case_count": 3,
        "year_count": 4,
        "compare_count": 2,
    },
    {
        "name": "Task 4: 5 Domains - Focus on Biotechnology",
        "primary_domain": "biotechnology",
        "secondary_domain": "renewable_energy",
        "query": BASE_TASK_QUERY.format(
            num_domains=5,
            domains="renewable energy, artificial intelligence, electric vehicles, quantum computing, and biotechnology",
            recall_questions="\n".join([
                "1. What is the global biotechnology market size in billions of USD?",
                "2. What was the global installed capacity in gigawatts for renewable energy?",
                "3. What was the calculated 10-year compound growth final value for biotechnology?",
                "4. What was the NPV calculated for biotechnology CBA with 10% discount rate?",
                "5. What was the weighted investment score calculated for biotechnology?",
                "6. What is the present value of year 5 benefits for biotechnology at 10% discount rate?",
                "7. What percentage of total market size across all domains does biotechnology represent?",
                "8. What is the weighted average of NPVs across all domains, weighted by investment amounts?",
                "9. What is the growth multiple (compound_growth_10yr / market_size) for biotechnology raised to the power of 2?",
            ]),
        ),
        "topics": topics_all,
        "expected_steps": 90,
        "recall_questions": [
            f"What is the global biotechnology market size in billions of USD? (Expected: {get_primary_domain_base_fact('biotechnology')} billion)",
            f"What was the global installed capacity in gigawatts for renewable energy? (Expected: {get_secondary_domain_base_fact('renewable_energy')} GW)",
            f"What was the calculated 10-year compound growth final value for biotechnology? (Expected: {get_compound_growth_10yr('biotechnology')})",
            f"What was the NPV calculated for biotechnology CBA with 10% discount rate? (Expected: {get_cba_npv_10pct('biotechnology')})",
            f"What was the weighted investment score calculated for biotechnology? (Expected: {get_weighted_investment_score('biotechnology')})",
            f"What is the present value of year 5 benefits for biotechnology at 10% discount rate? (Expected: {calculate_present_value_year5('biotechnology')})",
            f"What percentage of total market size across all domains does biotechnology represent? (Expected: {calculate_market_share_percentage('biotechnology', topics_all)}%)",
            f"What is the weighted average of NPVs across all domains, weighted by investment amounts? (Expected: {calculate_weighted_avg_npv(topics_all)})",
            f"What is the growth multiple (compound_growth_10yr / market_size) for biotechnology raised to the power of 2? (Expected: {calculate_growth_multiple_power('biotechnology')})",
        ],
        "expected_answers": {
            1: str(get_primary_domain_base_fact('biotechnology')),
            2: str(get_secondary_domain_base_fact('renewable_energy')),
            3: str(get_compound_growth_10yr('biotechnology')),
            4: str(get_cba_npv_10pct('biotechnology')),
            5: str(get_weighted_investment_score('biotechnology')),
            6: str(calculate_present_value_year5('biotechnology')),
            7: str(calculate_market_share_percentage('biotechnology', topics_all)),
            8: str(calculate_weighted_avg_npv(topics_all)),
            9: str(calculate_growth_multiple_power('biotechnology')),
        },
        "stats_count": 7,
        "expert_count": 5,
        "case_count": 4,
        "year_count": 5,
        "compare_count": 3,
    },
]
