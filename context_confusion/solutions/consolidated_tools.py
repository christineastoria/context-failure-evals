"""
Consolidated tool definitions for context confusion solution.

This module demonstrates Tool Consolidation - a key strategy for reducing 
context confusion by replacing many specific tools with fewer flexible tools 
that use parameters.

Key consolidation patterns:
1. **Flexible parameters**: get_carrier_info(include=["details", "incidents"]) 
   replaces 4 separate carrier tools
2. **Action-based dispatch**: manage_order(action="cancel") replaces 4 
   order modification tools
3. **Reduced cognitive load**: Agent chooses parameters, not tools

Benefits measured via LangSmith evaluators:
- Higher trajectory match (agent makes correct tool choices)
- Better success criteria (complete, accurate responses)
- Improved efficiency (fewer redundant calls)
"""

from typing import List, Literal, Optional, Dict
from context_confusion.resources.mock_orders import ORDERS, SHIPMENTS, ORDER_EVENTS
from context_confusion.resources.mock_customers import CUSTOMERS, CUSTOMER_EMAIL_MAP, CUSTOMER_PREFERENCES, BILLING_INFO
from context_confusion.resources.mock_carriers import TRACKING_SCANS, CARRIERS, CARRIER_INCIDENTS, RATE_CARDS
from context_confusion.resources.mock_warehouses import WAREHOUSES, INVENTORY, WAREHOUSE_INCIDENTS
from context_confusion.tools import (
    get_customer_by_email, get_customer, get_customer_preferences, get_billing_info,
    get_tracking_details, get_carrier_info as get_carrier_info_orig, get_carrier_incidents,
    get_shipping_rates, get_carrier_performance, get_return_request, create_return_label,
    cancel_order, hold_order, expedite_order, update_delivery_address, process_refund,
    get_warehouse_info as get_warehouse_info_orig, check_inventory, get_warehouse_incidents,
    create_support_ticket, send_notification, apply_credit, check_fraud_score
)


# ============================================================================
# SWEET SPOT: 12 Consolidated Tools with Flexible Parameters
# ============================================================================

# Tool 1: get_order_info
def get_order_info(
    order_id: str,
    include: List[Literal["status", "tracking", "events", "shipment", "customer"]] = ["status", "shipment"]
) -> dict:
    """
    Retrieve comprehensive order information with flexible parameters.
    
    This consolidated tool replaces multiple specific tools:
    - get_order (basic status)
    - get_shipment (carrier & delivery info)
    - get_order_events (history & tracking events)
    - get_order_summary (combined view)
    - check_order_status (status lookup)
    
    Design advantage: Single flexible call with 'include' parameter replaces 5+ separate tool calls.
    Reduces context confusion by providing one clear choice for order queries.
    
    Args:
        order_id: Order ID to look up  
        include: Information types to fetch in ONE call:
                - "status": Current order state & timestamps
                - "tracking": Tracking number & scan history
                - "events": Full order event log
                - "shipment": Carrier, service level, ETA
                - "customer": Associated customer details
    
    Example:
        get_order_info("12345", include=["status", "tracking", "shipment"])
        Returns complete info in one call instead of 3 separate calls
    """
    oid = order_id.strip().lstrip("#")
    
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    result = {"ok": True, "order_id": oid}
    
    if "status" in include:
        result.update({
            "status": order["status"],
            "order_date": order["order_date"],
            "last_update": order["last_update"],
            "total": {"cents": order["total_cents"], "currency": order["currency"]}
        })
    
    if "tracking" in include and order["tracking_number"]:
        tracking_num = order["tracking_number"]
        result["tracking_number"] = tracking_num
        if tracking_num in TRACKING_SCANS:
            result["tracking_scans"] = TRACKING_SCANS[tracking_num]
    
    if "events" in include and oid in ORDER_EVENTS:
        result["events"] = ORDER_EVENTS[oid]
    
    if "shipment" in include and oid in SHIPMENTS:
        shipment = SHIPMENTS[oid]
        result["shipment"] = {
            "carrier": shipment["carrier"],
            "service_level": shipment["service_level"],
            "eta_date": shipment["eta_date"],
            "latest_scan": shipment["latest_scan"],
            "scan_location": shipment["scan_location"],
            "scan_timestamp": shipment["scan_timestamp"],
        }
    
    if "customer" in include:
        customer = CUSTOMERS.get(order["customer_id"], {})
        result["customer"] = {
            "email": customer.get("email"),
            "name": customer.get("name"),
            "tier": customer.get("tier"),
        }
    
    return result


# Tool 2: get_customer_info
def get_customer_info(
    identifier: str,
    lookup_by: Literal["email", "customer_id"] = "email",
    include: List[Literal["profile", "preferences", "billing"]] = ["profile"]
) -> dict:
    """
    Retrieve customer information with flexible lookup and detail levels.
    
    This consolidated tool replaces 4 separate customer lookup tools:
    - get_customer (lookup by ID)
    - get_customer_by_email (lookup by email)
    - get_customer_preferences (delivery preferences)
    - get_billing_info (payment & billing details)
    
    Design advantage: Single tool handles both lookup methods AND multiple info types.
    Agent doesn't need to choose between "get_customer" vs "get_customer_by_email" - 
    just specify lookup_by parameter. Reduces decision fatigue and tool confusion.
    
    Args:
        identifier: Customer email or ID
        lookup_by: How to find customer - "email" or "customer_id"
        include: Information types to retrieve:
                - "profile": Name, email, tier, phone, location
                - "preferences": Delivery instructions, notifications
                - "billing": Payment methods, billing address
    
    Example:
        get_customer_info("user@example.com", lookup_by="email", include=["profile", "preferences"])
        Replaces: get_customer_by_email() + get_customer_preferences() (2 calls → 1)
    """
    if lookup_by == "email":
        email = identifier.strip().lower()
        if email not in CUSTOMER_EMAIL_MAP:
            return {"ok": False, "error": "Customer not found"}
        cid = CUSTOMER_EMAIL_MAP[email]
    else:
        cid = identifier.strip()
        if cid not in CUSTOMERS:
            return {"ok": False, "error": "Customer not found"}
    
    customer = CUSTOMERS[cid]
    result = {"ok": True, "customer_id": cid}
    
    if "profile" in include:
        result["profile"] = {
            "email": customer["email"],
            "name": customer["name"],
            "tier": customer["tier"],
            "phone": customer["phone"],
            "location": customer["location"]
        }
    
    if "preferences" in include and cid in CUSTOMER_PREFERENCES:
        result["preferences"] = CUSTOMER_PREFERENCES[cid]
    
    if "billing" in include and cid in BILLING_INFO:
        result["billing"] = BILLING_INFO[cid]
    
    return result


# Tool 3: get_tracking_info
def get_tracking_info(
    tracking_number: str,
    include: List[Literal["scans", "events", "eta"]] = ["scans"]
) -> dict:
    """Retrieve detailed tracking information. Replaces: get_tracking_details (keeps but enhances)"""
    return get_tracking_details(tracking_number)


# Tool 4: get_carrier_info
def get_carrier_info(
    carrier_id: Optional[str] = None,
    include: List[Literal["details", "incidents", "rates", "performance"]] = ["details"],
    date: Optional[str] = None
) -> dict:
    """
    Retrieve carrier information including incidents, rates, and performance.
    
    This consolidated tool replaces 4 carrier-related tools:
    - get_carrier_info (basic carrier details)
    - get_carrier_incidents (service disruptions)
    - get_shipping_rates (cost estimation)
    - get_carrier_performance (metrics & SLA)
    
    Design advantage: All carrier queries go through ONE tool with flexible parameters.
    Critical for diagnosing delivery issues where you need both carrier details AND incidents.
    
    Args:
        carrier_id: Carrier to look up (optional for incident checks)
        include: Information types:
                - "details": Carrier name, services, contact
                - "incidents": Service disruptions & delays
                - "rates": Shipping cost information
                - "performance": On-time delivery metrics
        date: Required for incident checks (YYYY-MM-DD format)
    
    Example:
        get_carrier_info("ups", include=["details", "incidents"], date="2024-12-20")
        One call replaces: get_carrier_info("ups") + get_carrier_incidents("2024-12-20")
    """
    result = {"ok": True}
    
    if carrier_id and "details" in include:
        carrier_result = get_carrier_info_orig(carrier_id)
        if carrier_result["ok"]:
            result["carrier"] = carrier_result["data"]
    
    if "incidents" in include and date:
        incidents_result = get_carrier_incidents(date)
        if incidents_result["ok"]:
            result["incidents"] = incidents_result["data"]
    
    if "rates" in include:
        result["rate_info"] = "Use get_shipping_rates with origin/destination"
    
    return result


# Tool 5: get_return_info
def get_return_info(
    order_id: str,
    include: List[Literal["request", "label", "status"]] = ["request"]
) -> dict:
    """
    Retrieve or manage return information.
    
    This consolidated tool replaces 2 return-related tools:
    - get_return_request (check return status)
    - create_return_label (generate label)
    
    Design advantage: All return queries through one tool. Agent doesn't need to decide
    between multiple return tools - just specify what info is needed via 'include'.
    
    Args:
        order_id: Order to check returns for
        include: Information types:
                - "request": Return request status
                - "label": Return shipping label
                - "status": Current return state
    """
    return get_return_request(order_id)


# Tool 6: manage_order
def manage_order(
    order_id: str,
    action: Literal["cancel", "hold", "expedite", "update_address"],
    **params
) -> dict:
    """
    Perform order management actions.
    
    This consolidated tool replaces 4 order modification tools:
    - cancel_order (cancel processing)
    - hold_order (pause fulfillment)
    - expedite_order (upgrade shipping speed)
    - update_delivery_address (change destination)
    
    Design advantage: Single "manage_order" tool with 'action' parameter replaces 4 tools.
    Agent chooses the action, not the tool - clearer intent, less confusion.
    Extensible design allows adding new actions without new tools.
    
    Args:
        order_id: Order to modify
        action: Management action to perform
        **params: Action-specific parameters (reason, new_address, etc)
    
    Example:
        manage_order("12345", action="expedite", new_shipping_method="express")
        Replaces: expedite_order("12345", "express")
    """
    if action == "cancel":
        return cancel_order(order_id, params.get("reason", "Customer request"))
    elif action == "hold":
        return hold_order(order_id, params.get("reason", "Hold requested"))
    elif action == "expedite":
        return expedite_order(order_id, params.get("new_shipping_method", "express"))
    elif action == "update_address":
        return update_delivery_address(order_id, params.get("new_address", {}))
    return {"ok": False, "error": "Invalid action"}


# Tool 7-12: Keep specific action tools as-is
# process_refund, get_warehouse_info_consolidated, create_support_ticket, 
# send_notification, apply_credit, check_fraud_score

def get_warehouse_info_consolidated(
    include: List[Literal["locations", "inventory", "incidents"]] = ["locations"],
    sku: Optional[str] = None
) -> dict:
    """
    Retrieve warehouse and inventory information.
    
    This consolidated tool replaces 3 warehouse tools:
    - get_warehouse_info (facility locations)
    - check_inventory (stock levels)
    - get_warehouse_incidents (facility issues)
    
    Design advantage: All warehouse queries through one flexible tool.
    Particularly useful for stock availability checks where you might need
    both inventory levels AND warehouse incidents affecting fulfillment.
    
    Args:
        include: Information types:
                - "locations": Warehouse facilities
                - "inventory": Stock levels (all or by SKU)
                - "incidents": Facility disruptions
        sku: Optional SKU to filter inventory check
    
    Example:
        get_warehouse_info_consolidated(include=["inventory", "incidents"], sku="WIDGET-123")
        Replaces: check_inventory("WIDGET-123") + get_warehouse_incidents()
    """
    result = {"ok": True}
    
    if "locations" in include:
        result["warehouses"] = WAREHOUSES
    
    if "inventory" in include:
        if sku:
            result["inventory"] = {k: v for k, v in INVENTORY.items() if k == sku}
        else:
            result["inventory"] = INVENTORY
    
    if "incidents" in include:
        result["incidents"] = WAREHOUSE_INCIDENTS
    
    return result


# Final consolidated tools list (12 tools)
consolidated_tools = [
    get_order_info,
    get_customer_info,
    get_tracking_info,
    get_carrier_info,
    get_return_info,
    manage_order,
    process_refund,
    get_warehouse_info_consolidated,
    create_support_ticket,
    send_notification,
    apply_credit,
    check_fraud_score,
]

