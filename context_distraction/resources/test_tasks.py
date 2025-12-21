"""
Test tasks for context distraction evaluation.

Each task is designed to require many operations and test the agent's ability
to maintain accuracy across long context histories. Each task focuses on
different domains to ensure variety.
"""

from context_distraction.resources.expected_calculations import (
    BASE_FACTS,
    EXPECTED_COMPOUND_GROWTH,
    EXPECTED_CBA,
    EXPECTED_CORRELATIONS,
    EXPECTED_WEIGHTED_SCORES,
    EXPECTED_INVESTMENT_RANKING_DICT,
    EXPECTED_RISK_ADJUSTED,
    EXPECTED_STRATEGIC_RANKING_DICT,
)

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

# Test task variations - each focuses on different primary domains
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
                "6. What was the investment priority ranking for renewable energy based on weighted scores?",
                "7. What was the risk-adjusted NPV for renewable energy?",
                "8. What was the weighted investment score calculated for renewable energy?",
                "9. What was the strategic priority ranking for renewable energy in your final analysis?",
            ]),
        ),
        "topics": [
            "renewable_energy", "artificial_intelligence", "electric_vehicles",
            "quantum_computing", "biotechnology"
        ],
        "expected_steps": 60,
        "recall_questions": [
            f"What was the global installed capacity in gigawatts for renewable energy? (Expected: {BASE_FACTS['renewable_energy']['capacity_gw']} GW)",
            f"What is the global AI market size in billions of USD? (Expected: {BASE_FACTS['artificial_intelligence']['market_size_billions']} billion)",
            f"What was the calculated 10-year compound growth final value for renewable energy? (Expected: {EXPECTED_COMPOUND_GROWTH['renewable_energy']['10yr']})",
            f"What was the NPV calculated for renewable energy CBA with 10% discount rate? (Expected: {EXPECTED_CBA['renewable_energy']['10pct']['npv']})",
            f"What correlation coefficient was calculated between renewable energy market size and growth rate? (Expected: {EXPECTED_CORRELATIONS['renewable_energy']['market_size_vs_growth_rate']})",
            f"What was the investment priority ranking for renewable energy based on weighted scores? (Expected: Rank {EXPECTED_INVESTMENT_RANKING_DICT.get('renewable_energy', 'N/A')})",
            f"What was the risk-adjusted NPV for renewable energy? (Expected: {EXPECTED_RISK_ADJUSTED.get('renewable_energy', 'N/A')})",
            f"What was the weighted investment score calculated for renewable energy? (Expected: {EXPECTED_WEIGHTED_SCORES.get('renewable_energy', 'N/A')})",
            f"What was the strategic priority ranking for renewable energy in your final analysis? (Expected: Rank {EXPECTED_STRATEGIC_RANKING_DICT.get('renewable_energy', 'N/A')})",
        ],
        "expected_answers": {
            1: str(BASE_FACTS['renewable_energy']['capacity_gw']),
            2: str(BASE_FACTS['artificial_intelligence']['market_size_billions']),
            3: str(EXPECTED_COMPOUND_GROWTH['renewable_energy']['10yr']),
            4: str(EXPECTED_CBA['renewable_energy']['10pct']['npv']),
            5: str(EXPECTED_CORRELATIONS['renewable_energy']['market_size_vs_growth_rate']),
            6: str(EXPECTED_INVESTMENT_RANKING_DICT.get('renewable_energy', '')),
            7: str(EXPECTED_RISK_ADJUSTED.get('renewable_energy', '')),
            8: str(EXPECTED_WEIGHTED_SCORES.get('renewable_energy', '')),
            9: str(EXPECTED_STRATEGIC_RANKING_DICT.get('renewable_energy', '')),
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
                "5. What correlation coefficient was calculated between electric vehicles market size and growth rate?",
                "6. What was the investment priority ranking for electric vehicles based on weighted scores?",
                "7. What was the risk-adjusted NPV for electric vehicles?",
                "8. What was the weighted investment score calculated for electric vehicles?",
                "9. What was the strategic priority ranking for electric vehicles in your final analysis?",
            ]),
        ),
        "topics": [
            "renewable_energy", "artificial_intelligence", "electric_vehicles",
            "quantum_computing", "biotechnology"
        ],
        "expected_steps": 75,
        "recall_questions": [
            f"What was the battery cost per kWh for electric vehicles? (Expected: {BASE_FACTS['electric_vehicles']['battery_cost_kwh']} $/kWh)",
            f"What is the global biotechnology market size in billions of USD? (Expected: {BASE_FACTS['biotechnology']['market_size_billions']} billion)",
            f"What was the calculated 10-year compound growth final value for electric vehicles? (Expected: {EXPECTED_COMPOUND_GROWTH['electric_vehicles']['10yr']})",
            f"What was the NPV calculated for electric vehicles CBA with 10% discount rate? (Expected: {EXPECTED_CBA['electric_vehicles']['10pct']['npv']})",
            f"What correlation coefficient was calculated between electric vehicles market size and growth rate? (Expected: {EXPECTED_CORRELATIONS['electric_vehicles']['market_size_vs_growth_rate']})",
            f"What was the investment priority ranking for electric vehicles based on weighted scores? (Expected: Rank {EXPECTED_INVESTMENT_RANKING_DICT.get('electric_vehicles', 'N/A')})",
            f"What was the risk-adjusted NPV for electric vehicles? (Expected: {EXPECTED_RISK_ADJUSTED.get('electric_vehicles', 'N/A')})",
            f"What was the weighted investment score calculated for electric vehicles? (Expected: {EXPECTED_WEIGHTED_SCORES.get('electric_vehicles', 'N/A')})",
            f"What was the strategic priority ranking for electric vehicles in your final analysis? (Expected: Rank {EXPECTED_STRATEGIC_RANKING_DICT.get('electric_vehicles', 'N/A')})",
        ],
        "expected_answers": {
            1: str(BASE_FACTS['electric_vehicles']['battery_cost_kwh']),
            2: str(BASE_FACTS['biotechnology']['market_size_billions']),
            3: str(EXPECTED_COMPOUND_GROWTH['electric_vehicles']['10yr']),
            4: str(EXPECTED_CBA['electric_vehicles']['10pct']['npv']),
            5: str(EXPECTED_CORRELATIONS['electric_vehicles']['market_size_vs_growth_rate']),
            6: str(EXPECTED_INVESTMENT_RANKING_DICT.get('electric_vehicles', '')),
            7: str(EXPECTED_RISK_ADJUSTED.get('electric_vehicles', '')),
            8: str(EXPECTED_WEIGHTED_SCORES.get('electric_vehicles', '')),
            9: str(EXPECTED_STRATEGIC_RANKING_DICT.get('electric_vehicles', '')),
        },
        "stats_count": 6,
        "expert_count": 4,
        "case_count": 3,
        "year_count": 4,
        "compare_count": 2,
    },
    {
        "name": "Task 3: 6 Domains - Focus on Quantum Computing",
        "primary_domain": "quantum_computing",
        "secondary_domain": "artificial_intelligence",
        "query": BASE_TASK_QUERY.format(
            num_domains=6,
            domains="renewable energy, artificial intelligence, electric vehicles, quantum computing, biotechnology, and space exploration",
            recall_questions="\n".join([
                "1. What was the number of qubits for quantum computing?",
                "2. What is the global AI market size in billions of USD?",
                "3. What was the calculated 10-year compound growth final value for quantum computing?",
                "4. What was the NPV calculated for quantum computing CBA with 10% discount rate?",
                "5. What correlation coefficient was calculated between quantum computing market size and growth rate?",
                "6. What was the investment priority ranking for quantum computing based on weighted scores?",
                "7. What was the risk-adjusted NPV for quantum computing?",
                "8. What was the weighted investment score calculated for quantum computing?",
                "9. What was the strategic priority ranking for quantum computing in your final analysis?",
            ]),
        ),
        "topics": [
            "renewable_energy", "artificial_intelligence", "electric_vehicles",
            "quantum_computing", "biotechnology", "space_exploration"
        ],
        "expected_steps": 78,
        "recall_questions": [
            f"What was the number of qubits for quantum computing? (Expected: {BASE_FACTS['quantum_computing']['qubits']} qubits)",
            f"What is the global AI market size in billions of USD? (Expected: {BASE_FACTS['artificial_intelligence']['market_size_billions']} billion)",
            f"What was the calculated 10-year compound growth final value for quantum computing? (Expected: {EXPECTED_COMPOUND_GROWTH['quantum_computing']['10yr']})",
            f"What was the NPV calculated for quantum computing CBA with 10% discount rate? (Expected: {EXPECTED_CBA['quantum_computing']['10pct']['npv']})",
            f"What correlation coefficient was calculated between quantum computing market size and growth rate? (Expected: {EXPECTED_CORRELATIONS['quantum_computing']['market_size_vs_growth_rate']})",
            f"What was the investment priority ranking for quantum computing based on weighted scores? (Expected: Rank {EXPECTED_INVESTMENT_RANKING_DICT.get('quantum_computing', 'N/A')})",
            f"What was the risk-adjusted NPV for quantum computing? (Expected: {EXPECTED_RISK_ADJUSTED.get('quantum_computing', 'N/A')})",
            f"What was the weighted investment score calculated for quantum computing? (Expected: {EXPECTED_WEIGHTED_SCORES.get('quantum_computing', 'N/A')})",
            f"What was the strategic priority ranking for quantum computing in your final analysis? (Expected: Rank {EXPECTED_STRATEGIC_RANKING_DICT.get('quantum_computing', 'N/A')})",
        ],
        "expected_answers": {
            1: str(BASE_FACTS['quantum_computing']['qubits']),
            2: str(BASE_FACTS['artificial_intelligence']['market_size_billions']),
            3: str(EXPECTED_COMPOUND_GROWTH['quantum_computing']['10yr']),
            4: str(EXPECTED_CBA['quantum_computing']['10pct']['npv']),
            5: str(EXPECTED_CORRELATIONS['quantum_computing']['market_size_vs_growth_rate']),
            6: str(EXPECTED_INVESTMENT_RANKING_DICT.get('quantum_computing', '')),
            7: str(EXPECTED_RISK_ADJUSTED.get('quantum_computing', '')),
            8: str(EXPECTED_WEIGHTED_SCORES.get('quantum_computing', '')),
            9: str(EXPECTED_STRATEGIC_RANKING_DICT.get('quantum_computing', '')),
        }
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
                "5. What correlation coefficient was calculated between biotechnology market size and growth rate?",
                "6. What was the investment priority ranking for biotechnology based on weighted scores?",
                "7. What was the risk-adjusted NPV for biotechnology?",
                "8. What was the weighted investment score calculated for biotechnology?",
                "9. What was the strategic priority ranking for biotechnology in your final analysis?",
            ]),
        ),
        "topics": [
            "renewable_energy", "artificial_intelligence", "electric_vehicles",
            "quantum_computing", "biotechnology"
        ],
        "expected_steps": 90,
        "recall_questions": [
            f"What is the global biotechnology market size in billions of USD? (Expected: {BASE_FACTS['biotechnology']['market_size_billions']} billion)",
            f"What was the global installed capacity in gigawatts for renewable energy? (Expected: {BASE_FACTS['renewable_energy']['capacity_gw']} GW)",
            f"What was the calculated 10-year compound growth final value for biotechnology? (Expected: {EXPECTED_COMPOUND_GROWTH['biotechnology']['10yr']})",
            f"What was the NPV calculated for biotechnology CBA with 10% discount rate? (Expected: {EXPECTED_CBA['biotechnology']['10pct']['npv']})",
            f"What correlation coefficient was calculated between biotechnology market size and growth rate? (Expected: {EXPECTED_CORRELATIONS['biotechnology']['market_size_vs_growth_rate']})",
            f"What was the investment priority ranking for biotechnology based on weighted scores? (Expected: Rank {EXPECTED_INVESTMENT_RANKING_DICT.get('biotechnology', 'N/A')})",
            f"What was the risk-adjusted NPV for biotechnology? (Expected: {EXPECTED_RISK_ADJUSTED.get('biotechnology', 'N/A')})",
            f"What was the weighted investment score calculated for biotechnology? (Expected: {EXPECTED_WEIGHTED_SCORES.get('biotechnology', 'N/A')})",
            f"What was the strategic priority ranking for biotechnology in your final analysis? (Expected: Rank {EXPECTED_STRATEGIC_RANKING_DICT.get('biotechnology', 'N/A')})",
        ],
        "expected_answers": {
            1: str(BASE_FACTS['biotechnology']['market_size_billions']),
            2: str(BASE_FACTS['renewable_energy']['capacity_gw']),
            3: str(EXPECTED_COMPOUND_GROWTH['biotechnology']['10yr']),
            4: str(EXPECTED_CBA['biotechnology']['10pct']['npv']),
            5: str(EXPECTED_CORRELATIONS['biotechnology']['market_size_vs_growth_rate']),
            6: str(EXPECTED_INVESTMENT_RANKING_DICT.get('biotechnology', '')),
            7: str(EXPECTED_RISK_ADJUSTED.get('biotechnology', '')),
            8: str(EXPECTED_WEIGHTED_SCORES.get('biotechnology', '')),
            9: str(EXPECTED_STRATEGIC_RANKING_DICT.get('biotechnology', '')),
        },
        "stats_count": 7,
        "expert_count": 5,
        "case_count": 4,
        "year_count": 5,
        "compare_count": 3,
    },
]
