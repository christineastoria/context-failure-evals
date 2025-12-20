from context_confusion.resources.mock_customers import CUSTOMERS, CUSTOMER_EMAIL_MAP, CUSTOMER_PREFERENCES, BILLING_INFO
from context_confusion.resources.mock_orders import ORDERS, SHIPMENTS, ORDER_EVENTS, RETURN_REQUESTS
from context_confusion.resources.mock_warehouses import WAREHOUSES, INVENTORY, WAREHOUSE_INCIDENTS
from context_confusion.resources.mock_carriers import CARRIERS, CARRIER_INCIDENTS, TRACKING_SCANS, RATE_CARDS
from langchain_core.tools import tool
from typing import Dict, Any, List, Literal, Optional

# =====================================================
# CORE SHIPPING SUPPORT TOOLS (Primary Domain)
# =====================================================

def get_order(order_id: str) -> Dict[str, Any]:
    """Retrieve current order details including status, last update, and tracking info."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    customer = CUSTOMERS.get(order["customer_id"], {})
    
    return {
        "ok": True,
        "data": {
            "order_id": order["order_id"],
            "status": order["status"],
            "order_date": order["order_date"],
            "last_update": order["last_update"],
            "tracking_number": order["tracking_number"],
            "carrier": order["carrier"],
            "total": {"cents": order["total_cents"], "currency": order["currency"]},
            "items": order["items"],
            "customer": {
                "customer_id": order["customer_id"],
                "email": customer.get("email"),
                "tier": customer.get("tier"),
            },
        },
    }

def get_shipment(order_id: str) -> Dict[str, Any]:
    """Retrieve shipment carrier, delivery estimate, and latest scan for an order."""
    oid = order_id.strip().lstrip("#")
    if oid not in SHIPMENTS:
        return {"ok": False, "error": f"Shipment not found: {oid}"}
    
    shipment = SHIPMENTS[oid]
    return {
        "ok": True,
        "data": {
            "order_id": shipment["order_id"],
            "carrier": shipment["carrier"],
            "service_level": shipment["service_level"],
            "eta_date": shipment["eta_date"],
            "original_eta": shipment["original_eta"],
            "latest_scan": shipment["latest_scan"],
            "scan_location": shipment["scan_location"],
            "scan_timestamp": shipment["scan_timestamp"],
        },
    }

def get_customer(customer_id: str) -> Dict[str, Any]:
    """Retrieve customer profile including id, email, tier, and contact info."""
    cid = customer_id.strip()
    if cid not in CUSTOMERS:
        return {"ok": False, "error": f"Customer not found: {cid}"}
    
    customer = CUSTOMERS[cid]
    return {
        "ok": True,
        "data": {
            "customer_id": customer["customer_id"],
            "email": customer["email"],
            "name": customer["name"],
            "tier": customer["tier"],
            "phone": customer["phone"],
            "location": customer["location"],
        },
    }

def get_customer_by_email(email: str) -> Dict[str, Any]:
    """Look up a customer_id and details by email address."""
    em = email.strip().lower()
    if em not in CUSTOMER_EMAIL_MAP:
        return {"ok": False, "error": f"Customer not found: {em}"}
    
    cid = CUSTOMER_EMAIL_MAP[em]
    customer = CUSTOMERS[cid]
    return {
        "ok": True,
        "data": {
            "customer_id": customer["customer_id"],
            "email": customer["email"],
            "name": customer["name"],
            "tier": customer["tier"],
        },
    }

def get_tracking_details(tracking_number: str) -> Dict[str, Any]:
    """Get detailed tracking information and scan history for a tracking number."""
    tracking = tracking_number.strip()
    if tracking not in TRACKING_SCANS:
        return {"ok": False, "error": f"Tracking not found: {tracking}"}
    
    scans = TRACKING_SCANS[tracking]
    return {
        "ok": True,
        "data": {
            "tracking_number": tracking,
            "scans": scans,
            "latest_scan": scans[-1] if scans else None,
        },
    }

def get_order_events(order_id: str) -> Dict[str, Any]:
    """Fetch order event history and audit trail."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDER_EVENTS:
        return {"ok": False, "error": f"No events found for order: {oid}"}
    
    events = ORDER_EVENTS[oid]
    return {"ok": True, "data": {"order_id": oid, "events": events}}

shipping_core_tools = [
    get_order,
    get_shipment,
    get_customer,
    get_customer_by_email,
    get_tracking_details,
    get_order_events
]

# =====================================================
# CARRIER MANAGEMENT TOOLS
# =====================================================

def get_carrier_info(carrier_id: str) -> Dict[str, Any]:
    """Get carrier details including services, coverage, and current status."""
    if carrier_id not in CARRIERS:
        return {"ok": False, "error": f"Carrier not found: {carrier_id}"}
    
    carrier = CARRIERS[carrier_id]
    return {"ok": True, "data": carrier}

def get_carrier_incidents(date: str) -> Dict[str, Any]:
    """Get carrier service incidents and outages for a specific date."""
    if date not in CARRIER_INCIDENTS:
        return {"ok": True, "data": {"date": date, "incidents": []}}
    
    incidents = CARRIER_INCIDENTS[date]
    return {"ok": True, "data": {"date": date, "incidents": incidents}}

def get_shipping_rates(origin: str, destination: str, weight_lbs: float) -> Dict[str, Any]:
    """Calculate shipping rates for different carriers and services."""
    # Simplified rate calculation
    return {
        "ok": True,
        "data": {
            "origin": origin,
            "destination": destination,
            "weight_lbs": weight_lbs,
            "rates": RATE_CARDS["domestic"],
        },
    }

carrier_tools = [
    get_carrier_info,
    get_carrier_incidents,
    get_shipping_rates
]

# =====================================================
# RETURNS & REFUNDS TOOLS
# =====================================================

def get_return_request(order_id: str) -> Dict[str, Any]:
    """Retrieve return request details and status."""
    oid = order_id.strip().lstrip("#")
    if oid not in RETURN_REQUESTS:
        return {"ok": False, "error": f"No return request found: {oid}"}
    
    return_req = RETURN_REQUESTS[oid]
    return {"ok": True, "data": return_req}

def create_return_label(order_id: str, reason: str) -> Dict[str, Any]:
    """Generate a return shipping label for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "return_label_tracking": f"RET{order_id}",
            "reason": reason,
            "label_url": f"https://returns.example.com/label/{order_id}",
        },
    }

def process_refund(order_id: str, amount_cents: int, reason: str) -> Dict[str, Any]:
    """Issue a refund for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "refund_amount_cents": amount_cents,
            "reason": reason,
            "refund_id": f"REF{order_id}",
            "status": "PROCESSED",
        },
    }

def approve_return(order_id: str) -> Dict[str, Any]:
    """Approve a return request."""
    return {"ok": True, "data": {"order_id": order_id, "approved": True}}

returns_tools = [
    get_return_request,
    create_return_label,
    process_refund,
    approve_return
]

# =====================================================
# WAREHOUSE & INVENTORY TOOLS
# =====================================================

def get_warehouse_info(warehouse_id: str) -> Dict[str, Any]:
    """Get warehouse details, capacity, and current status."""
    if warehouse_id not in WAREHOUSES:
        return {"ok": False, "error": f"Warehouse not found: {warehouse_id}"}
    
    warehouse = WAREHOUSES[warehouse_id]
    return {"ok": True, "data": warehouse}

def check_inventory(sku: str) -> Dict[str, Any]:
    """Check inventory levels for a specific SKU across all warehouses."""
    if sku not in INVENTORY:
        return {"ok": False, "error": f"SKU not found: {sku}"}
    
    inventory = INVENTORY[sku]
    return {"ok": True, "data": inventory}

def get_warehouse_incidents(date: str) -> Dict[str, Any]:
    """Get warehouse incidents and operational issues for a specific date."""
    if date not in WAREHOUSE_INCIDENTS:
        return {"ok": True, "data": {"date": date, "incidents": []}}
    
    incidents = WAREHOUSE_INCIDENTS[date]
    return {"ok": True, "data": {"date": date, "incidents": incidents}}

def transfer_inventory(sku: str, from_warehouse: str, to_warehouse: str, quantity: int) -> Dict[str, Any]:
    """Transfer inventory between warehouses."""
    return {
        "ok": True,
        "data": {
            "sku": sku,
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "quantity": quantity,
            "transfer_id": f"TRF{sku}{quantity}",
        },
    }

warehouse_tools = [
    get_warehouse_info,
    check_inventory,
    get_warehouse_incidents,
    transfer_inventory
]

# =====================================================
# ORDER MODIFICATION TOOLS
# =====================================================

def update_delivery_address(order_id: str, new_address: Dict[str, str]) -> Dict[str, Any]:
    """Update the delivery address for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "address_updated": True,
            "new_address": new_address,
        },
    }

def cancel_order(order_id: str, reason: str) -> Dict[str, Any]:
    """Cancel an order."""
    return {"ok": True, "data": {"order_id": order_id, "cancelled": True, "reason": reason}}

def expedite_order(order_id: str, new_shipping_method: str) -> Dict[str, Any]:
    """Upgrade shipping method for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "expedited": True,
            "new_shipping_method": new_shipping_method,
        },
    }

def hold_order(order_id: str, reason: str) -> Dict[str, Any]:
    """Put an order on hold."""
    return {"ok": True, "data": {"order_id": order_id, "held": True, "reason": reason}}

order_modification_tools = [
    update_delivery_address,
    cancel_order,
    expedite_order,
    hold_order
]

# =====================================================
# CUSTOMER SERVICE TOOLS
# =====================================================

def create_support_ticket(customer_id: str, category: str, subject: str, description: str) -> Dict[str, Any]:
    """Create a customer support ticket."""
    return {
        "ok": True,
        "data": {
            "ticket_id": f"TKT{customer_id[:4]}{category[:3].upper()}",
            "customer_id": customer_id,
            "category": category,
            "subject": subject,
            "status": "OPEN",
        },
    }

def get_customer_preferences(customer_id: str) -> Dict[str, Any]:
    """Get customer delivery preferences and notification settings."""
    if customer_id not in CUSTOMER_PREFERENCES:
        return {"ok": False, "error": f"Preferences not found: {customer_id}"}
    
    prefs = CUSTOMER_PREFERENCES[customer_id]
    return {"ok": True, "data": prefs}

def update_customer_preferences(customer_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Update customer delivery preferences."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "preferences_updated": True,
            "new_preferences": preferences,
        },
    }

def send_notification(customer_id: str, notification_type: str, message: str) -> Dict[str, Any]:
    """Send email or SMS notification to customer."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "notification_type": notification_type,
            "sent": True,
        },
    }

customer_service_tools = [
    create_support_ticket,
    get_customer_preferences,
    update_customer_preferences,
    send_notification
]

# =====================================================
# BILLING & PAYMENTS TOOLS
# =====================================================

def get_billing_info(customer_id: str) -> Dict[str, Any]:
    """Get billing information and payment method for a customer."""
    if customer_id not in BILLING_INFO:
        return {"ok": False, "error": f"Billing info not found: {customer_id}"}
    
    billing = BILLING_INFO[customer_id]
    return {"ok": True, "data": billing}

def apply_credit(customer_id: str, amount_cents: int, reason: str) -> Dict[str, Any]:
    """Apply account credit to a customer."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "credit_applied": True,
            "amount_cents": amount_cents,
            "reason": reason,
        },
    }

def charge_customer(customer_id: str, amount_cents: int, description: str) -> Dict[str, Any]:
    """Charge a customer for additional fees."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "charged": True,
            "amount_cents": amount_cents,
            "charge_id": f"CHG{customer_id}",
        },
    }

def get_invoice(order_id: str) -> Dict[str, Any]:
    """Retrieve invoice details for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "invoice_id": f"INV{order_id}",
            "status": "PAID",
        },
    }

billing_tools = [
    get_billing_info,
    apply_credit,
    charge_customer,
    get_invoice
]

# =====================================================
# FRAUD DETECTION TOOLS (Noise Domain)
# =====================================================

def check_fraud_score(order_id: str) -> Dict[str, Any]:
    """Check fraud risk score for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "fraud_score": 0.05,
            "risk_level": "LOW",
            "flags": [],
        },
    }

def flag_suspicious_order(order_id: str, reason: str) -> Dict[str, Any]:
    """Flag an order for fraud review."""
    return {"ok": True, "data": {"order_id": order_id, "flagged": True, "reason": reason}}

def verify_customer_identity(customer_id: str, verification_method: str) -> Dict[str, Any]:
    """Trigger identity verification for a customer."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "verification_method": verification_method,
            "verified": False,
            "verification_pending": True,
        },
    }

fraud_tools = [
    check_fraud_score,
    flag_suspicious_order,
    verify_customer_identity
]

# =====================================================
# ANALYTICS & REPORTING TOOLS (Noise Domain)
# =====================================================

def get_delivery_metrics(date_range: str) -> Dict[str, Any]:
    """Get delivery performance metrics."""
    return {
        "ok": True,
        "data": {
            "date_range": date_range,
            "on_time_delivery_rate": 0.94,
            "average_delivery_days": 3.2,
            "late_deliveries": 42,
        },
    }

def generate_shipping_report(customer_id: str, month: str) -> Dict[str, Any]:
    """Generate monthly shipping report for a customer."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "month": month,
            "total_shipments": 15,
            "total_spend_cents": 12500,
        },
    }

def get_carrier_performance(carrier_id: str, date_range: str) -> Dict[str, Any]:
    """Analyze carrier performance metrics."""
    return {
        "ok": True,
        "data": {
            "carrier_id": carrier_id,
            "date_range": date_range,
            "on_time_rate": 0.92,
            "damage_rate": 0.01,
        },
    }

analytics_tools = [
    get_delivery_metrics,
    generate_shipping_report,
    get_carrier_performance
]

# =====================================================
# MARKETING & PROMOTIONS TOOLS (Noise Domain)
# =====================================================

def apply_discount_code(order_id: str, discount_code: str) -> Dict[str, Any]:
    """Apply a discount code to an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "discount_code": discount_code,
            "discount_applied": True,
            "discount_amount_cents": 500,
        },
    }

def get_loyalty_points(customer_id: str) -> Dict[str, Any]:
    """Get customer loyalty points balance."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "points_balance": 1250,
            "tier": "gold",
        },
    }

def send_promotional_email(customer_id: str, campaign_id: str) -> Dict[str, Any]:
    """Send promotional email to customer."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "campaign_id": campaign_id,
            "email_sent": True,
        },
    }

marketing_tools = [
    apply_discount_code,
    get_loyalty_points,
    send_promotional_email
]

# =====================================================
# VENDOR MANAGEMENT TOOLS (Noise Domain)
# =====================================================

def get_vendor_info(vendor_id: str) -> Dict[str, Any]:
    """Get vendor information and performance metrics."""
    return {
        "ok": True,
        "data": {
            "vendor_id": vendor_id,
            "name": f"Vendor {vendor_id}",
            "rating": 4.5,
            "status": "ACTIVE",
        },
    }

def create_purchase_order(vendor_id: str, items: List[Dict], total_amount: float) -> Dict[str, Any]:
    """Create a purchase order with a vendor."""
    return {
        "ok": True,
        "data": {
            "vendor_id": vendor_id,
            "po_number": f"PO{vendor_id}001",
            "total_amount": total_amount,
            "status": "PENDING",
        },
    }

def approve_vendor_invoice(invoice_id: str) -> Dict[str, Any]:
    """Approve a vendor invoice for payment."""
    return {"ok": True, "data": {"invoice_id": invoice_id, "approved": True}}

vendor_tools = [
    get_vendor_info,
    create_purchase_order,
    approve_vendor_invoice
]

# =====================================================
# EMPLOYEE MANAGEMENT TOOLS (Noise Domain)
# =====================================================

def get_employee_schedule(employee_id: str, date: str) -> Dict[str, Any]:
    """Get employee work schedule."""
    return {
        "ok": True,
        "data": {
            "employee_id": employee_id,
            "date": date,
            "shift_start": "09:00",
            "shift_end": "17:00",
        },
    }

def assign_task(employee_id: str, task_description: str, priority: str) -> Dict[str, Any]:
    """Assign a task to an employee."""
    return {
        "ok": True,
        "data": {
            "employee_id": employee_id,
            "task_id": f"TSK{employee_id}",
            "task_description": task_description,
            "priority": priority,
        },
    }

def log_employee_hours(employee_id: str, date: str, hours: float) -> Dict[str, Any]:
    """Log employee work hours."""
    return {
        "ok": True,
        "data": {
            "employee_id": employee_id,
            "date": date,
            "hours": hours,
            "logged": True,
        },
    }

employee_tools = [
    get_employee_schedule,
    assign_task,
    log_employee_hours
]

# =====================================================
# QUALITY ASSURANCE TOOLS (Noise Domain)
# =====================================================

def log_quality_issue(order_id: str, issue_type: str, description: str) -> Dict[str, Any]:
    """Log a quality issue with an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "issue_type": issue_type,
            "issue_id": f"QA{order_id}",
            "status": "OPEN",
        },
    }

def schedule_inspection(warehouse_id: str, date: str) -> Dict[str, Any]:
    """Schedule a quality inspection at a warehouse."""
    return {
        "ok": True,
        "data": {
            "warehouse_id": warehouse_id,
            "inspection_date": date,
            "inspection_id": f"INSP{warehouse_id}",
        },
    }

def get_quality_metrics(date_range: str) -> Dict[str, Any]:
    """Get quality metrics for a date range."""
    return {
        "ok": True,
        "data": {
            "date_range": date_range,
            "defect_rate": 0.02,
            "customer_complaints": 5,
        },
    }

quality_tools = [
    log_quality_issue,
    schedule_inspection,
    get_quality_metrics
]

# =====================================================
# CUSTOMS & COMPLIANCE TOOLS (Noise Domain)
# =====================================================

def get_customs_status(order_id: str) -> Dict[str, Any]:
    """Check customs clearance status for international orders."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "customs_status": "CLEARED",
            "clearance_date": "2025-12-18",
        },
    }

def submit_customs_documents(order_id: str, document_type: str) -> Dict[str, Any]:
    """Submit customs documentation for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "document_type": document_type,
            "submitted": True,
        },
    }

def calculate_duties(order_id: str, destination_country: str) -> Dict[str, Any]:
    """Calculate import duties and taxes."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "destination_country": destination_country,
            "duties_amount_cents": 1500,
            "tax_amount_cents": 800,
        },
    }

customs_tools = [
    get_customs_status,
    submit_customs_documents,
    calculate_duties
]

# =====================================================
# SUBSCRIPTION MANAGEMENT TOOLS (Noise Domain)
# =====================================================

def get_subscription(customer_id: str) -> Dict[str, Any]:
    """Get customer subscription details."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "subscription_tier": "premium",
            "status": "ACTIVE",
            "renews_on": "2026-01-15",
        },
    }

def update_subscription(customer_id: str, new_tier: str) -> Dict[str, Any]:
    """Update customer subscription tier."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "new_tier": new_tier,
            "updated": True,
        },
    }

def cancel_subscription(customer_id: str, reason: str) -> Dict[str, Any]:
    """Cancel a customer subscription."""
    return {
        "ok": True,
        "data": {
            "customer_id": customer_id,
            "cancelled": True,
            "reason": reason,
        },
    }

subscription_tools = [
    get_subscription,
    update_subscription,
    cancel_subscription
]

# =====================================================
# FLEET MANAGEMENT TOOLS (Noise Domain)
# =====================================================

def get_vehicle_location(vehicle_id: str) -> Dict[str, Any]:
    """Get current location of a delivery vehicle."""
    return {
        "ok": True,
        "data": {
            "vehicle_id": vehicle_id,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "last_update": "2025-12-19T10:30:00Z",
        },
    }

def assign_driver(driver_id: str, route_id: str) -> Dict[str, Any]:
    """Assign a driver to a delivery route."""
    return {
        "ok": True,
        "data": {
            "driver_id": driver_id,
            "route_id": route_id,
            "assigned": True,
        },
    }

def log_vehicle_maintenance(vehicle_id: str, maintenance_type: str, date: str) -> Dict[str, Any]:
    """Log vehicle maintenance activity."""
    return {
        "ok": True,
        "data": {
            "vehicle_id": vehicle_id,
            "maintenance_type": maintenance_type,
            "date": date,
            "logged": True,
        },
    }

fleet_tools = [
    get_vehicle_location,
    assign_driver,
    log_vehicle_maintenance
]

# =====================================================
# ENVIRONMENTAL COMPLIANCE TOOLS (Noise Domain)
# =====================================================

def calculate_carbon_footprint(order_id: str) -> Dict[str, Any]:
    """Calculate carbon footprint for an order's shipping."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "carbon_kg": 2.5,
            "offset_available": True,
        },
    }

def purchase_carbon_offset(order_id: str) -> Dict[str, Any]:
    """Purchase carbon offset for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "offset_purchased": True,
            "offset_id": f"OFFSET{order_id}",
        },
    }

environmental_tools = [
    calculate_carbon_footprint,
    purchase_carbon_offset
]

# =====================================================
# INSURANCE TOOLS (Noise Domain)
# =====================================================

def get_insurance_coverage(order_id: str) -> Dict[str, Any]:
    """Get insurance coverage details for an order."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "coverage_amount": 150.00,
            "insured": True,
        },
    }

def file_insurance_claim(order_id: str, claim_type: str, amount: float) -> Dict[str, Any]:
    """File an insurance claim for lost or damaged shipment."""
    return {
        "ok": True,
        "data": {
            "order_id": order_id,
            "claim_type": claim_type,
            "claim_id": f"CLM{order_id}",
            "amount": amount,
            "status": "PENDING",
        },
    }

insurance_tools = [
    get_insurance_coverage,
    file_insurance_claim
]

# =====================================================
# CONFUSING NEAR-DUPLICATE TOOLS (Added for Context Confusion Demo)
# =====================================================

def get_order_summary(order_id: str) -> Dict[str, Any]:
    """Get comprehensive order summary including all status and tracking details."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    # INCOMPLETE: Only basic order info, missing tracking number and carrier details
    return {
        "ok": True,
        "data": {
            "order_id": order["order_id"],
            "status": order["status"],  # Just "IN_TRANSIT" - no specific location!
            "order_date": order["order_date"],
            "total": {"cents": order["total_cents"], "currency": order["currency"]},
            # MISSING: tracking_number, carrier, last_update - critical tracking info!
        },
    }

def check_order_status(order_id: str) -> Dict[str, Any]:
    """Check current processing and fulfillment status of an order."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    # INCOMPLETE: Only status field, no tracking or carrier info
    return {
        "ok": True,
        "data": {
            "order_id": order["order_id"],
            "status": order["status"],  # Generic status only
            "last_update": order["last_update"],
            # MISSING: tracking_number, carrier, shipment details
        },
    }

def lookup_order_details(order_id: str) -> Dict[str, Any]:
    """Look up detailed order information with complete history."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    # INCOMPLETE: Order details without any tracking or shipping info
    return {
        "ok": True,
        "data": {
            "order_id": order["order_id"],
            "order_date": order["order_date"],
            "items": order["items"],
            "total": {"cents": order["total_cents"], "currency": order["currency"]},
            # MISSING: status, tracking_number, carrier, last_update
        },
    }

def verify_order_information(order_id: str) -> Dict[str, Any]:
    """Verify and retrieve order information with validation."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"verified": True, "order_id": oid}}

def get_shipment_status(order_id: str) -> Dict[str, Any]:
    """Get current shipment status and tracking updates."""
    oid = order_id.strip().lstrip("#")
    if oid not in SHIPMENTS:
        return {"ok": False, "error": f"Shipment not found: {oid}"}
    
    shipment = SHIPMENTS[oid]
    # INCOMPLETE: Only vague status, missing specific scan location!
    return {
        "ok": True,
        "data": {
            "order_id": shipment["order_id"],
            "status": shipment["latest_scan"],  # Just "In transit" - no Memphis, TN!
            "carrier": shipment["carrier"],
            "eta_date": shipment["eta_date"],
            # MISSING: scan_location (critical!), scan_timestamp, service_level
        },
    }

def verify_shipment_tracking(order_id: str) -> Dict[str, Any]:
    """Verify shipment tracking information accuracy."""
    oid = order_id.strip().lstrip("#")
    if oid not in ORDERS:
        return {"ok": False, "error": f"Order not found: {oid}"}
    
    order = ORDERS[oid]
    # MISLEADING: Says tracking is verified but doesn't provide location details!
    return {
        "ok": True,
        "data": {
            "verified": True,
            "order_id": oid,
            "tracking_number": order.get("tracking_number"),
            "status": "tracking_active",  # Generic - no real location info!
            # MISSING: actual scan location, latest scan details
        },
    }

def lookup_customer_account(email: str) -> Dict[str, Any]:
    """Look up customer account by email address."""
    email_clean = email.strip().lower()
    return {"ok": True, "data": {"note": "This is a duplicate of get_customer_by_email - use get_customer_by_email instead", "email": email_clean}}

def verify_customer_identity(email: str) -> Dict[str, Any]:
    """Verify customer identity before accessing account."""
    email_clean = email.strip().lower()
    return {"ok": True, "data": {"verified": True, "email": email_clean}}

def analyze_order_status(order_id: str) -> Dict[str, Any]:
    """Analyze order with detailed processing insights."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"analysis": "complete", "insights": "none", "order_id": oid}}

def diagnose_delivery_issues(order_id: str) -> Dict[str, Any]:
    """Diagnose potential delivery problems and delays."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"diagnosis": "no issues found", "order_id": oid}}

def check_order_visibility(order_id: str) -> Dict[str, Any]:
    """Check if order is visible and not archived."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"visible": True, "archived": False, "order_id": oid}}

def validate_order_access(customer_id: str, order_id: str) -> Dict[str, Any]:
    """Verify customer has permission to access order."""
    return {"ok": True, "data": {"access_granted": True, "customer_id": customer_id, "order_id": order_id}}

def get_order_health(order_id: str) -> Dict[str, Any]:
    """Check order health and identify problems."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"health": "good", "issues": [], "order_id": oid}}

def refresh_order_cache(order_id: str) -> Dict[str, Any]:
    """Refresh cached order data for latest info."""
    oid = order_id.strip().lstrip("#")
    return {"ok": True, "data": {"cache_refreshed": True, "timestamp": "2024-03-15T10:00:00Z", "order_id": oid}}

def get_customer_account_status(customer_id: str) -> Dict[str, Any]:
    """Get customer account status and tier."""
    return {"ok": True, "data": {"status": "active", "account_standing": "good", "customer_id": customer_id}}

confusing_duplicate_tools = [
    get_order_summary,
    check_order_status,
    lookup_order_details,
    verify_order_information,
    get_shipment_status,
    verify_shipment_tracking,
    lookup_customer_account,
    verify_customer_identity,
    analyze_order_status,
    diagnose_delivery_issues,
    check_order_visibility,
    validate_order_access,
    get_order_health,
    refresh_order_cache,
    get_customer_account_status,
]

# =====================================================
# ALL TOOLS
# =====================================================

all_tools = (
    shipping_core_tools +
    carrier_tools +
    returns_tools +
    warehouse_tools +
    order_modification_tools +
    customer_service_tools +
    billing_tools +
    fraud_tools +
    analytics_tools +
    marketing_tools +
    vendor_tools +
    employee_tools +
    quality_tools +
    customs_tools +
    subscription_tools +
    fleet_tools +
    environmental_tools +
    insurance_tools +
    confusing_duplicate_tools
)

def get_tool_name(tool):
    """Get the name of a tool function."""
    if hasattr(tool, 'name'):
        return tool.name
    return tool.__name__

ALL_TOOL_NAMES = tuple(get_tool_name(tool) for tool in all_tools)

