"""Test cases for context confusion evaluation."""

from datetime import datetime


test_cases = [
    {
        "query": "What's the status of order #84721?",
        "success_criteria": """
# order_status_provided
The response must provide the current status of order #84721

# sufficient_detail
The response should include enough detail to be actionable (not just "processing" but context about what that means)
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "84721"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "Track order #99002 and tell me where it is",
        "success_criteria": """
# tracking_information_provided
The response must provide tracking information about where order #99002 currently is

# location_detail_included
The response should indicate current location or delivery status (not just "in transit" - needs actual progress info)
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "99002"}},
            {"name": "get_tracking_details", "args": {"tracking_number": "TRK99002ABC"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "Check order #98765 for me",
        "success_criteria": """
# order_information_provided
The response must provide meaningful information about order #98765

# includes_relevant_details
The response should include status and at least one other relevant detail (tracking, delivery, etc.)
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "98765"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "Where is order #12345 right now?",
        "success_criteria": """
# current_location_provided
The response must answer where the order currently is (requires tracking lookup, not just order status)

# specific_location_info
The response should provide specific location information from tracking data
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "12345"}},
            {"name": "get_tracking_details", "args": {"tracking_number": "TRK12345ABC"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "I'm user@example.com, why is order #23456 delayed and when will it arrive?",
        "success_criteria": """
# delay_investigation_performed
The response must investigate why the order is delayed (check shipment info and/or carrier incidents)

# arrival_information_provided
The response must provide expected arrival information

# both_questions_answered
The response must address BOTH the "why delayed" and "when arriving" questions
""",
        "trajectory": [
            {"name": "get_customer_by_email", "args": {"email": "user@example.com"}},
            {"name": "get_order", "args": {"order_id": "23456"}},
            {"name": "get_shipment", "args": {"order_id": "23456"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "What carrier is handling order #45678 and are there any service disruptions?",
        "success_criteria": """
# carrier_identified
The response must identify which carrier is handling the order

# incident_check_performed
The response must check for carrier incidents/disruptions as instructed in guidelines

# complete_answer_to_both
The response must answer both parts: carrier identification AND service disruption status
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "45678"}},
            {"name": "get_shipment", "args": {"order_id": "45678"}},
            {"name": "get_carrier_incidents", "args": {"date": datetime.now().strftime('%Y-%m-%d')}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "I'm ops@widget.io and I need to know the status and delivery preferences for order #10015",
        "success_criteria": """
# order_status_provided
The response must provide order status for #10015

# preferences_addressed
The response must address delivery preferences (either provide them or explain they're not available)

# both_requests_handled
The response must handle BOTH the status request AND preferences request
""",
        "trajectory": [
            {"name": "get_customer_by_email", "args": {"email": "ops@widget.io"}},
            {"name": "get_order", "args": {"order_id": "10015"}},
            {"name": "get_customer_preferences", "args": {"customer_id": "cust_widget"}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "Order #10015 was supposed to arrive yesterday but hasn't shown up yet. What's going on?",
        "success_criteria": """
# checks_order_status
The response must look up the actual order status and shipment information

# investigates_delay
The response must investigate why the order is late (per guidelines: check carrier incidents for delays)

# provides_explanation
Must provide a specific explanation for the delay, not just generic "it's delayed"
""",
        "trajectory": [
            {"name": "get_order", "args": {"order_id": "10015"}},
            {"name": "get_shipment", "args": {"order_id": "10015"}},
            {"name": "get_carrier_incidents", "args": {"date": datetime.now().strftime('%Y-%m-%d')}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "I'm tracking order #12345 - are there any UPS service issues today that might affect delivery?",
        "success_criteria": """
# checks_carrier_incidents
The response must check for carrier service incidents for today

# provides_definitive_answer
Must clearly state whether there are incidents or not (not just ask for more info)
""",
        "trajectory": [
            {"name": "get_carrier_incidents", "args": {"date": datetime.now().strftime('%Y-%m-%d')}}
        ],
        "trajectory_comparison_mode": "subset"
    },
    {
        "query": "I'm manager@euro-corp.eu, what are my delivery preferences?",
        "success_criteria": """
# customer_verification_performed
The response must verify the customer by email before sharing preferences

# preferences_retrieved
The response must provide the actual delivery preferences (not just acknowledge the request)
""",
        "trajectory": [
            {"name": "get_customer_by_email", "args": {"email": "manager@euro-corp.eu"}},
            {"name": "get_customer_preferences", "args": {"customer_id": "cust_euro"}}
        ],
        "trajectory_comparison_mode": "subset"
    }
]

