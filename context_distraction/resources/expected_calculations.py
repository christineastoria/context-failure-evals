"""
Expected calculations and trajectories for context distraction evaluation.

This file defines complex interdependent calculations similar to SQL joins and aggregations.
We reverse-engineer from the calculations to create verifiable questions.

Complexity levels:
1. Base facts (simple lookups)
2. Single-domain calculations (compound growth, CBA)
3. Cross-domain joins (combining data from multiple topics)
4. Multi-dimensional aggregations (region × segment × time)
5. Hierarchical calculations (depend on previous aggregations)
6. Final synthesis (depends on all previous steps)
"""

# Base facts from research data (these are the "tables" we'll join)
# Values must match mock_research_data.py RESEARCH_TOPICS statistics exactly
# All fields are available in research data for agent retrieval
BASE_FACTS = {
    "renewable_energy": {
        "capacity_gw": 3372,  # global_capacity_gw
        "growth_rate": 0.096,  # annual_growth_rate_percent: 9.6 -> 0.096
        "market_size_billions": 1200,  # global_market_billions_usd
        "investment_billions": 358,  # investment_billions_usd
        "jobs_millions": 13.7,  # jobs_created_millions
    },
    "artificial_intelligence": {
        "market_size_billions": 196.6,  # global_ai_market_billions_usd
        "growth_rate": 0.312,  # annual_growth_rate_percent: 31.2 -> 0.312
        "investment_billions": 95.2,  # investment_billions_usd
        "patents_thousands": 780,  # ai_patents_filed: 780000 -> 780
    },
    "electric_vehicles": {
        "battery_cost_kwh": 139,  # battery_cost_per_kwh
        "growth_rate": 0.20,  # annual_growth_rate_percent: 20.0 -> 0.20
        "market_size_billions": 450,  # global_market_billions_usd
        "investment_billions": 120,  # investment_billions_usd
    },
    "quantum_computing": {
        "qubits": 1121,  # qubits_achieved
        "market_size_billions": 8.5,  # global_market_billions_usd
        "growth_rate": 0.35,  # annual_growth_rate_percent: 35.0 -> 0.35
        "investment_billions": 30,  # investment_billions_usd
    },
    "biotechnology": {
        "market_size_billions": 1023,  # global_market_billions_usd
        "growth_rate": 0.139,  # annual_growth_rate_percent: 13.9 -> 0.139
        "investment_billions": 180,  # investment_billions_usd
        "patents_thousands": 45,  # patents_filed: 45000 -> 45
    },
}

# STEP 1: Single-domain compound growth calculations
# These are like SELECT statements with calculations
EXPECTED_COMPOUND_GROWTH = {}
for domain, facts in BASE_FACTS.items():
    initial = facts.get("market_size_billions")
    rate = facts["growth_rate"]
    EXPECTED_COMPOUND_GROWTH[domain] = {
        "5yr": round(initial * (1 + rate) ** 5, 2),
        "10yr": round(initial * (1 + rate) ** 10, 2),
        "15yr": round(initial * (1 + rate) ** 15, 2),
    }

# STEP 2: CBA calculations (like complex WHERE + GROUP BY)
def calculate_npv(initial, benefits, discount_rate, years):
    """Calculate NPV deterministically."""
    npv = -initial
    for year in range(1, years + 1):
        benefit = benefits[min(year - 1, len(benefits) - 1)]
        discounted = benefit / ((1 + discount_rate) ** year)
        npv += discounted
    return round(npv, 2)

def calculate_roi(initial, benefits):
    """Calculate ROI deterministically."""
    total_benefits = sum(benefits)
    roi = ((total_benefits - initial) / initial) * 100
    return round(roi, 2)

# Benefit generation functions - deterministic patterns
def generate_renewable_benefits(initial_investment: float) -> list:
    """Generate benefits for renewable energy: starts at 15% of initial, grows 20% annually."""
    base = initial_investment * 0.15
    return [round(base * (1.20 ** i), 1) for i in range(10)]

def generate_ai_benefits(initial_investment: float) -> list:
    """Generate benefits for AI: starts at 15% of initial, accelerates growth (25% annually)."""
    base = initial_investment * 0.15
    return [round(base * (1.25 ** i), 1) for i in range(10)]

def generate_ev_benefits(initial_investment: float) -> list:
    """Generate benefits for EVs: starts at 11% of initial, grows 22% annually."""
    base = initial_investment * 0.11
    return [round(base * (1.22 ** i), 1) for i in range(10)]

def generate_quantum_benefits(initial_investment: float) -> list:
    """Generate benefits for quantum: starts at 10% of initial, exponential growth (35% annually)."""
    base = initial_investment * 0.10
    return [round(base * (1.35 ** i), 1) for i in range(10)]

def generate_biotech_benefits(initial_investment: float) -> list:
    """Generate benefits for biotech: starts at 15% of initial, steady growth (15% annually)."""
    base = initial_investment * 0.15
    return [round(base * (1.15 ** i), 1) for i in range(10)]

# CBA calculations for all domains
DOMAIN_CBA_CONFIGS = {
    "renewable_energy": {
        "initial": 100,
        "benefits": generate_renewable_benefits(100),
    },
    "artificial_intelligence": {
        "initial": 80,
        "benefits": generate_ai_benefits(80),
    },
    "electric_vehicles": {
        "initial": 90,
        "benefits": generate_ev_benefits(90),
    },
    "quantum_computing": {
        "initial": 50,
        "benefits": generate_quantum_benefits(50),
    },
    "biotechnology": {
        "initial": 120,
        "benefits": generate_biotech_benefits(120),
    },
}

EXPECTED_CBA = {}
for domain, config in DOMAIN_CBA_CONFIGS.items():
    EXPECTED_CBA[domain] = {
        "5pct": {
            "npv": calculate_npv(config["initial"], config["benefits"], 0.05, 10),
            "roi": calculate_roi(config["initial"], config["benefits"]),
        },
        "10pct": {
            "npv": calculate_npv(config["initial"], config["benefits"], 0.10, 10),
            "roi": calculate_roi(config["initial"], config["benefits"]),
        },
        "15pct": {
            "npv": calculate_npv(config["initial"], config["benefits"], 0.15, 10),
            "roi": calculate_roi(config["initial"], config["benefits"]),
        },
    }

# STEP 3: Complex JOIN - Cross-domain correlation analysis
# This is like: SELECT corr(a.market_size, b.growth_rate) FROM domain_a a JOIN domain_b b
EXPECTED_CORRELATIONS = {
    "renewable_energy": {
        "market_size_vs_growth_rate": 0.847,
        "investment_vs_roi": 0.723,
        "market_size_vs_expert_confidence": 0.691,
    },
    "artificial_intelligence": {
        "market_size_vs_growth_rate": 0.782,
        "investment_vs_roi": 0.654,
        "market_size_vs_expert_confidence": 0.712,
    },
    "electric_vehicles": {
        "market_size_vs_growth_rate": 0.765,
        "investment_vs_roi": 0.689,
        "market_size_vs_expert_confidence": 0.698,
    },
    "quantum_computing": {
        "market_size_vs_growth_rate": 0.891,
        "investment_vs_roi": 0.745,
        "market_size_vs_expert_confidence": 0.823,
    },
    "biotechnology": {
        "market_size_vs_growth_rate": 0.721,
        "investment_vs_roi": 0.667,
        "market_size_vs_expert_confidence": 0.684,
    },
    # Cross-domain correlations (like SQL joins)
    "renewable_ai": {
        "renewable_market_vs_ai_patents": 0.634,
        "renewable_investment_vs_ai_growth": 0.582,
    },
    "renewable_ev": {
        "renewable_capacity_vs_ev_battery_cost": -0.712,
        "renewable_growth_vs_ev_market": 0.789,
    },
}

# STEP 5: Multi-dimensional aggregation (like SQL GROUP BY multiple columns)
# Aggregate by region × segment × time_period
EXPECTED_AGGREGATIONS = {
    "renewable_energy": {
        "by_region": {
            "Asia": {"total_billions": 580, "segments": 5, "avg_growth": 0.16},
            "Europe": {"total_billions": 380, "segments": 5, "avg_growth": 0.14},
            "Americas": {"total_billions": 240, "segments": 5, "avg_growth": 0.15},
        },
        "by_segment": {
            "Solar": {"regions": 3, "total_billions": 510, "avg_investment": 85},
            "Wind": {"regions": 3, "total_billions": 360, "avg_investment": 72},
            "Hydro": {"regions": 3, "total_billions": 240, "avg_investment": 48},
        },
        "by_time_period": {
            "2020-2022": {"total_billions": 900, "growth_rate": 0.12},
            "2022-2024": {"total_billions": 1200, "growth_rate": 0.15},
            "2024-2026": {"total_billions": 1587, "growth_rate": 0.15},  # Projected
        },
    }
}

# STEP 6: Hierarchical calculation - Investment priority ranking
# This is like: SELECT domain, RANK() OVER (ORDER BY weighted_score DESC)
# The weighted score depends on multiple previous calculations
def calculate_weighted_score(domain):
    """Calculate weighted investment score using multiple factors."""
    facts = BASE_FACTS[domain]
    cba = EXPECTED_CBA.get(domain, {}).get("10pct", {})
    compound_growth = EXPECTED_COMPOUND_GROWTH.get(domain, {}).get("10yr", 0)
    
    # Normalize values
    npv_score = (cba.get("npv", 0) / 200) * 0.4  # Max NPV ~200 (increased weight)
    roi_score = (cba.get("roi", 0) / 200) * 0.3  # Max ROI ~200% (increased weight)
    growth_score = (compound_growth / facts.get("market_size_billions", 1) / 5) * 0.3  # Growth multiple
    
    return round(npv_score + roi_score + growth_score, 4)

EXPECTED_WEIGHTED_SCORES = {
    domain: calculate_weighted_score(domain)
    for domain in BASE_FACTS.keys()
}

# Rank domains by weighted score
EXPECTED_INVESTMENT_RANKING = sorted(
    EXPECTED_WEIGHTED_SCORES.items(),
    key=lambda x: x[1],
    reverse=True
)
# Convert to dict with rank numbers
EXPECTED_INVESTMENT_RANKING_DICT = {
    domain: rank + 1
    for rank, (domain, score) in enumerate(EXPECTED_INVESTMENT_RANKING)
}

# STEP 7: Complex SQL-like query - Risk-adjusted return
# This is like: SELECT domain, (npv / risk_factor) as risk_adjusted_npv FROM cba JOIN risk_data
EXPECTED_RISK_ADJUSTED = {}
for domain in BASE_FACTS.keys():
    cba = EXPECTED_CBA.get(domain, {}).get("10pct", {})
    npv = cba.get("npv", 0)
    # Risk factor based on market maturity and volatility
    risk_factors = {
        "renewable_energy": 1.2,  # Lower risk
        "artificial_intelligence": 1.8,  # Higher risk
        "electric_vehicles": 1.5,
        "quantum_computing": 2.5,  # Very high risk
        "biotechnology": 1.6,
    }
    risk_factor = risk_factors.get(domain, 1.5)
    risk_adjusted_npv = round(npv / risk_factor, 2)
    EXPECTED_RISK_ADJUSTED[domain] = risk_adjusted_npv

# STEP 8: Final synthesis - Strategic recommendation priority
# This is like a complex query with multiple JOINs and ORDER BY
# Combines: weighted scores, risk adjustment, market share, growth projections
def calculate_strategic_priority_score(domain):
    """Final priority score combining all factors."""
    weighted = EXPECTED_WEIGHTED_SCORES.get(domain, 0)
    risk_adj = EXPECTED_RISK_ADJUSTED.get(domain, 0) / 100  # Normalize
    growth_multiple = EXPECTED_COMPOUND_GROWTH.get(domain, {}).get("10yr", 0) / BASE_FACTS[domain].get("market_size_billions", 1)
    
    # Weighted combination
    priority_score = (
        weighted * 0.45 +
        risk_adj * 0.30 +
        min(growth_multiple / 5, 1.0) * 0.25  # Cap growth multiple contribution
    )
    return round(priority_score, 4)

EXPECTED_STRATEGIC_PRIORITY_SCORES = {
    domain: calculate_strategic_priority_score(domain)
    for domain in BASE_FACTS.keys()
}

EXPECTED_STRATEGIC_RANKING = sorted(
    EXPECTED_STRATEGIC_PRIORITY_SCORES.items(),
    key=lambda x: x[1],
    reverse=True
)
EXPECTED_STRATEGIC_RANKING_DICT = {
    domain: rank + 1
    for rank, (domain, score) in enumerate(EXPECTED_STRATEGIC_RANKING)
}

# STEP 9: Cross-domain aggregation - Portfolio optimization
# This is like: SELECT SUM(npv), AVG(risk_adjusted), COUNT(*) FROM all_domains GROUP BY portfolio_tier
EXPECTED_PORTFOLIO_ANALYSIS = {
    "tier_1_high_priority": {
        "domains": [domain for domain, rank in EXPECTED_STRATEGIC_RANKING_DICT.items() if rank <= 3],
        "total_npv": sum(EXPECTED_CBA.get(d, {}).get("10pct", {}).get("npv", 0) for d in EXPECTED_STRATEGIC_RANKING_DICT.keys() if EXPECTED_STRATEGIC_RANKING_DICT[d] <= 3),
        "avg_risk_adjusted": sum(EXPECTED_RISK_ADJUSTED.get(d, 0) for d in EXPECTED_STRATEGIC_RANKING_DICT.keys() if EXPECTED_STRATEGIC_RANKING_DICT[d] <= 3) / 3,
    },
    "tier_2_moderate": {
        "domains": [domain for domain, rank in EXPECTED_STRATEGIC_RANKING_DICT.items() if 4 <= rank <= 7],
        "total_npv": sum(EXPECTED_CBA.get(d, {}).get("10pct", {}).get("npv", 0) for d in EXPECTED_STRATEGIC_RANKING_DICT.keys() if 4 <= EXPECTED_STRATEGIC_RANKING_DICT[d] <= 7),
    },
    "tier_3_lower_priority": {
        "domains": [domain for domain, rank in EXPECTED_STRATEGIC_RANKING_DICT.items() if rank >= 8],
        "total_npv": sum(EXPECTED_CBA.get(d, {}).get("10pct", {}).get("npv", 0) for d in EXPECTED_STRATEGIC_RANKING_DICT.keys() if EXPECTED_STRATEGIC_RANKING_DICT[d] >= 8),
    },
}

# Print all calculated values for verification
if __name__ == "__main__":
    print("="*80)
    print("EXPECTED CALCULATIONS - Complex SQL-like Operations")
    print("="*80)
    
    print("\n1. COMPOUND GROWTH (10yr):")
    for domain, growth in EXPECTED_COMPOUND_GROWTH.items():
        print(f"   {domain}: {growth['10yr']}")
    
    print("\n2. CBA NPV (10% discount):")
    for domain, cba in EXPECTED_CBA.items():
        print(f"   {domain}: NPV={cba['10pct']['npv']}, ROI={cba['10pct']['roi']}%")
    
    print("\n3. CORRELATIONS:")
    print(f"   Renewable Market vs Growth: {EXPECTED_CORRELATIONS['renewable_energy']['market_size_vs_growth_rate']}")
    print(f"   Renewable-AI Cross-domain: {EXPECTED_CORRELATIONS['renewable_ai']['renewable_market_vs_ai_patents']}")
    
    print("\n5. WEIGHTED INVESTMENT SCORES:")
    for domain, score in EXPECTED_WEIGHTED_SCORES.items():
        print(f"   {domain}: {score}")
    
    print("\n6. INVESTMENT RANKING:")
    for rank, (domain, score) in enumerate(EXPECTED_INVESTMENT_RANKING[:5], 1):
        print(f"   {rank}. {domain}: {score}")
    
    print("\n7. RISK-ADJUSTED NPV:")
    for domain, npv in EXPECTED_RISK_ADJUSTED.items():
        print(f"   {domain}: {npv}")
    
    print("\n8. STRATEGIC PRIORITY RANKING:")
    for rank, (domain, score) in enumerate(EXPECTED_STRATEGIC_RANKING[:5], 1):
        print(f"   {rank}. {domain}: {score}")
    
    print("\n9. PORTFOLIO ANALYSIS:")
    print(f"   Tier 1 Total NPV: {EXPECTED_PORTFOLIO_ANALYSIS['tier_1_high_priority']['total_npv']}")
    print(f"   Tier 1 Avg Risk-Adjusted: {EXPECTED_PORTFOLIO_ANALYSIS['tier_1_high_priority']['avg_risk_adjusted']:.2f}")

