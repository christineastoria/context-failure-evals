"""
Expected calculations for context distraction evaluation.

This file defines deterministic expected values for all calculations used in test tasks.
All values are derived from BASE_FACTS which must match synthetic_data.py.
"""

# ============================================================================
# BASE DATA
# ============================================================================
# Base facts from research data - must match synthetic_data.py exactly
BASE_FACTS = {
    "renewable_energy": {
        "capacity_gw": 3372,
        "growth_rate": 0.096,
        "market_size_billions": 1200,
        "investment_billions": 358,
        "jobs_millions": 13.7,
    },
    "artificial_intelligence": {
        "market_size_billions": 196.6,
        "growth_rate": 0.312,
        "investment_billions": 95.2,
        "patents_thousands": 780,
    },
    "electric_vehicles": {
        "battery_cost_kwh": 139,
        "growth_rate": 0.20,
        "market_size_billions": 450,
        "investment_billions": 120,
    },
    "quantum_computing": {
        "qubits": 1121,
        "market_size_billions": 8.5,
        "growth_rate": 0.35,
        "investment_billions": 30,
    },
    "biotechnology": {
        "market_size_billions": 1023,
        "growth_rate": 0.139,
        "investment_billions": 180,
        "patents_thousands": 45,
    },
}

# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

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

def generate_renewable_benefits(initial_investment: float) -> list:
    """Generate benefits: starts at 15% of initial, grows 20% annually."""
    base = initial_investment * 0.15
    return [round(base * (1.20 ** i), 1) for i in range(10)]

def generate_ai_benefits(initial_investment: float) -> list:
    """Generate benefits: starts at 15% of initial, grows 25% annually."""
    base = initial_investment * 0.15
    return [round(base * (1.25 ** i), 1) for i in range(10)]

def generate_ev_benefits(initial_investment: float) -> list:
    """Generate benefits: starts at 11% of initial, grows 22% annually."""
    base = initial_investment * 0.11
    return [round(base * (1.22 ** i), 1) for i in range(10)]

def generate_quantum_benefits(initial_investment: float) -> list:
    """Generate benefits: starts at 10% of initial, grows 35% annually."""
    base = initial_investment * 0.10
    return [round(base * (1.35 ** i), 1) for i in range(10)]

def generate_biotech_benefits(initial_investment: float) -> list:
    """Generate benefits: starts at 15% of initial, grows 15% annually."""
    base = initial_investment * 0.15
    return [round(base * (1.15 ** i), 1) for i in range(10)]

# ============================================================================
# DERIVED DATA STRUCTURES
# ============================================================================

# Compound growth calculations
EXPECTED_COMPOUND_GROWTH = {}
for domain, facts in BASE_FACTS.items():
    initial = facts.get("market_size_billions")
    rate = facts["growth_rate"]
    EXPECTED_COMPOUND_GROWTH[domain] = {
        "5yr": round(initial * (1 + rate) ** 5, 2),
        "10yr": round(initial * (1 + rate) ** 10, 2),
        "15yr": round(initial * (1 + rate) ** 15, 2),
    }

# CBA configurations and calculations
DOMAIN_CBA_CONFIGS = {
    "renewable_energy": {"initial": 100, "benefits": generate_renewable_benefits(100)},
    "artificial_intelligence": {"initial": 80, "benefits": generate_ai_benefits(80)},
    "electric_vehicles": {"initial": 90, "benefits": generate_ev_benefits(90)},
    "quantum_computing": {"initial": 50, "benefits": generate_quantum_benefits(50)},
    "biotechnology": {"initial": 120, "benefits": generate_biotech_benefits(120)},
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

# Correlation coefficients
EXPECTED_CORRELATIONS = {
    "renewable_energy": {"market_size_vs_growth_rate": 0.847},
    "artificial_intelligence": {"market_size_vs_growth_rate": 0.782},
    "electric_vehicles": {"market_size_vs_growth_rate": 0.765},
    "quantum_computing": {"market_size_vs_growth_rate": 0.891},
    "biotechnology": {"market_size_vs_growth_rate": 0.721},
}

# Weighted investment scores
def calculate_weighted_score(domain):
    """Calculate weighted investment score."""
    facts = BASE_FACTS[domain]
    cba = EXPECTED_CBA.get(domain, {}).get("10pct", {})
    compound_growth = EXPECTED_COMPOUND_GROWTH.get(domain, {}).get("10yr", 0)
    
    npv_score = (cba.get("npv", 0) / 200) * 0.4
    roi_score = (cba.get("roi", 0) / 200) * 0.3
    growth_score = (compound_growth / facts.get("market_size_billions", 1) / 5) * 0.3
    
    return round(npv_score + roi_score + growth_score, 4)

EXPECTED_WEIGHTED_SCORES = {
    domain: calculate_weighted_score(domain)
    for domain in BASE_FACTS.keys()
}

# Investment priority ranking
EXPECTED_INVESTMENT_RANKING = sorted(
    EXPECTED_WEIGHTED_SCORES.items(),
    key=lambda x: x[1],
    reverse=True
)
EXPECTED_INVESTMENT_RANKING_DICT = {
    domain: rank + 1
    for rank, (domain, score) in enumerate(EXPECTED_INVESTMENT_RANKING)
}

# Risk-adjusted NPV
RISK_FACTORS = {
    "renewable_energy": 1.2,
    "artificial_intelligence": 1.8,
    "electric_vehicles": 1.5,
    "quantum_computing": 2.5,
    "biotechnology": 1.6,
}

EXPECTED_RISK_ADJUSTED = {
    domain: round(EXPECTED_CBA[domain]["10pct"]["npv"] / RISK_FACTORS[domain], 2)
    for domain in BASE_FACTS.keys()
}

# Strategic priority ranking
def calculate_strategic_priority_score(domain):
    """Calculate strategic priority score."""
    weighted = EXPECTED_WEIGHTED_SCORES.get(domain, 0)
    risk_adj = EXPECTED_RISK_ADJUSTED.get(domain, 0) / 100
    growth_multiple = EXPECTED_COMPOUND_GROWTH.get(domain, {}).get("10yr", 0) / BASE_FACTS[domain].get("market_size_billions", 1)
    
    priority_score = (
        weighted * 0.45 +
        risk_adj * 0.30 +
        min(growth_multiple / 5, 1.0) * 0.25
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

# ============================================================================
# HELPER FUNCTIONS FOR TEST QUESTIONS
# ============================================================================

# Q1-Q4: Base question helpers
def get_primary_domain_base_fact(primary: str) -> float:
    """Get primary domain base fact (capacity_gw, battery_cost_kwh, qubits, or market_size_billions)."""
    if "capacity_gw" in BASE_FACTS.get(primary, {}):
        return BASE_FACTS[primary]["capacity_gw"]
    elif "battery_cost_kwh" in BASE_FACTS.get(primary, {}):
        return BASE_FACTS[primary]["battery_cost_kwh"]
    elif "qubits" in BASE_FACTS.get(primary, {}):
        return BASE_FACTS[primary]["qubits"]
    else:
        return BASE_FACTS[primary]["market_size_billions"]

def get_secondary_domain_base_fact(secondary: str) -> float:
    """Get secondary domain base fact (market_size_billions or capacity_gw)."""
    return BASE_FACTS[secondary].get("market_size_billions") or BASE_FACTS[secondary].get("capacity_gw")

def get_compound_growth_10yr(primary: str) -> float:
    """Get 10-year compound growth value."""
    return EXPECTED_COMPOUND_GROWTH[primary]["10yr"]

def get_cba_npv_10pct(primary: str) -> float:
    """Get CBA NPV at 10% discount rate."""
    return EXPECTED_CBA[primary]["10pct"]["npv"]

# Q5: Additional metric helpers
def get_correlation_market_size_vs_growth(primary: str) -> float:
    """Get correlation coefficient between market size and growth rate."""
    return EXPECTED_CORRELATIONS[primary]["market_size_vs_growth_rate"]

def get_investment_priority_rank(primary: str) -> int:
    """Get investment priority ranking."""
    return EXPECTED_INVESTMENT_RANKING_DICT.get(primary)

def get_risk_adjusted_npv(primary: str) -> float:
    """Get risk-adjusted NPV."""
    return EXPECTED_RISK_ADJUSTED.get(primary)

def get_weighted_investment_score(primary: str) -> float:
    """Get weighted investment score."""
    return EXPECTED_WEIGHTED_SCORES.get(primary)

def get_strategic_priority_rank(primary: str) -> int:
    """Get strategic priority ranking."""
    return EXPECTED_STRATEGIC_RANKING_DICT.get(primary)

# Q6-Q9: Advanced calculation helpers
def calculate_npv_ratio(primary: str, secondary: str) -> float:
    """Calculate ratio of primary NPV to secondary NPV."""
    return round(EXPECTED_CBA[primary]["10pct"]["npv"] / EXPECTED_CBA[secondary]["10pct"]["npv"], 4)

def calculate_npv_difference(primary: str, secondary: str) -> float:
    """Calculate difference between primary and secondary NPV."""
    return round(EXPECTED_CBA[primary]["10pct"]["npv"] - EXPECTED_CBA[secondary]["10pct"]["npv"], 2)

def calculate_roi_ratio(primary: str, secondary: str) -> float:
    """Calculate ratio of primary ROI to secondary ROI."""
    return round(EXPECTED_CBA[primary]["10pct"]["roi"] / EXPECTED_CBA[secondary]["10pct"]["roi"], 4)

def calculate_weighted_avg_growth(topics: list) -> float:
    """Calculate weighted average growth rate weighted by market size."""
    total_weighted = sum(BASE_FACTS[d]["growth_rate"] * BASE_FACTS[d]["market_size_billions"] for d in topics)
    total_market = sum(BASE_FACTS[d]["market_size_billions"] for d in topics)
    return round(total_weighted / total_market, 4)

def calculate_weighted_avg_npv(topics: list) -> float:
    """Calculate weighted average NPV weighted by investment."""
    total_weighted = sum(EXPECTED_CBA[d]["10pct"]["npv"] * BASE_FACTS[d]["investment_billions"] for d in topics)
    total_investment = sum(BASE_FACTS[d]["investment_billions"] for d in topics)
    return round(total_weighted / total_investment, 2)

def calculate_present_value_year5(primary: str) -> float:
    """Calculate present value of year 5 benefits."""
    return round(DOMAIN_CBA_CONFIGS[primary]["benefits"][4] / ((1 + 0.10) ** 5), 2)

def calculate_market_share_percentage(primary: str, topics: list) -> float:
    """Calculate percentage of total market size."""
    primary_market = BASE_FACTS[primary]["market_size_billions"]
    total_market = sum(BASE_FACTS[d]["market_size_billions"] for d in topics)
    return round((primary_market / total_market) * 100, 2)

def calculate_total_investment_sum(topics: list) -> float:
    """Calculate sum of all domain investments."""
    return round(sum(BASE_FACTS[d]["investment_billions"] for d in topics), 2)

def calculate_growth_multiple_power(primary: str) -> float:
    """Calculate (compound_growth / market_size)^2."""
    growth = EXPECTED_COMPOUND_GROWTH[primary]["10yr"]
    market = BASE_FACTS[primary]["market_size_billions"]
    return round((growth / market) ** 2, 4)

def calculate_discount_factor_year7() -> float:
    """Calculate discount factor for year 7 at 10%."""
    return round(1 / ((1 + 0.10) ** 7), 6)
