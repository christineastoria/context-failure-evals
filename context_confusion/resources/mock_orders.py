ORDERS = {
    "84721": {
        "order_id": "84721",
        "customer_id": "cust_123",
        "status": "IN_TRANSIT",
        "order_date": "2025-12-16T08:30:00Z",
        "last_update": "2025-12-18T16:22:00Z",
        "tracking_number": "1Z999AA10123456784",
        "carrier": "UPS",
        "total_cents": 12999,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-123",
                "name": "Premium Widget",
                "qty": 1,
                "price_cents": 12999
            }
        ],
        "origin_warehouse": "WH-01",
        "destination_warehouse": None,
        "shipping_method": "ground",
        "insurance_value": 150.00,
        "signature_required": True
    },
    "99002": {
        "order_id": "99002",
        "customer_id": "cust_456",
        "status": "DELIVERED",
        "order_date": "2025-12-10T14:20:00Z",
        "last_update": "2025-12-15T11:04:00Z",
        "tracking_number": "9400111899223856923412",
        "carrier": "USPS",
        "total_cents": 4599,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-777",
                "name": "Standard Gadget",
                "qty": 2,
                "price_cents": 2299
            }
        ],
        "origin_warehouse": "WH-02",
        "destination_warehouse": None,
        "shipping_method": "standard",
        "insurance_value": 50.00,
        "signature_required": False
    },
    "10015": {
        "order_id": "10015",
        "customer_id": "cust_789",
        "status": "LABEL_CREATED",
        "order_date": "2025-12-18T22:00:00Z",
        "last_update": "2025-12-19T09:10:00Z",
        "tracking_number": None,
        "carrier": "FedEx",
        "total_cents": 250000,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-ENT-1",
                "name": "Enterprise Solution",
                "qty": 5,
                "price_cents": 50000
            }
        ],
        "origin_warehouse": "WH-01",
        "destination_warehouse": None,
        "shipping_method": "express",
        "insurance_value": 3000.00,
        "signature_required": True
    },
    "45678": {
        "order_id": "45678",
        "customer_id": "cust_321",
        "status": "PROCESSING",
        "order_date": "2025-12-19T10:00:00Z",
        "last_update": "2025-12-19T10:30:00Z",
        "tracking_number": None,
        "carrier": "DHL",
        "total_cents": 8500,
        "currency": "EUR",
        "items": [
            {
                "sku": "SKU-456",
                "name": "European Widget",
                "qty": 1,
                "price_cents": 8500
            }
        ],
        "origin_warehouse": "WH-EU-01",
        "destination_warehouse": None,
        "shipping_method": "international",
        "insurance_value": 100.00,
        "signature_required": True
    },
    "23456": {
        "order_id": "23456",
        "customer_id": "cust_654",
        "status": "DELAYED",
        "order_date": "2025-12-12T09:00:00Z",
        "last_update": "2025-12-17T14:00:00Z",
        "tracking_number": "RM123456789GB",
        "carrier": "Royal Mail",
        "total_cents": 3200,
        "currency": "GBP",
        "items": [
            {
                "sku": "SKU-UK-1",
                "name": "UK Widget",
                "qty": 1,
                "price_cents": 3200
            }
        ],
        "origin_warehouse": "WH-UK-01",
        "destination_warehouse": None,
        "shipping_method": "standard",
        "insurance_value": 40.00,
        "signature_required": False
    },
    "98765": {
        "order_id": "98765",
        "customer_id": "cust_987",
        "status": "IN_TRANSIT",
        "order_date": "2025-12-18T07:00:00Z",
        "last_update": "2025-12-19T08:00:00Z",
        "tracking_number": "123456789012",
        "carrier": "FedEx",
        "total_cents": 75000,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-LUX-1",
                "name": "Luxury Item",
                "qty": 3,
                "price_cents": 25000
            }
        ],
        "origin_warehouse": "WH-01",
        "destination_warehouse": None,
        "shipping_method": "overnight",
        "insurance_value": 1000.00,
        "signature_required": True
    },
    "11111": {
        "order_id": "11111",
        "customer_id": "cust_111",
        "status": "RETURNED",
        "order_date": "2025-12-05T12:00:00Z",
        "last_update": "2025-12-18T15:00:00Z",
        "tracking_number": "9405511899223856923413",
        "carrier": "USPS",
        "total_cents": 1999,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-999",
                "name": "Basic Widget",
                "qty": 1,
                "price_cents": 1999
            }
        ],
        "origin_warehouse": "WH-02",
        "destination_warehouse": "WH-02",
        "shipping_method": "return",
        "insurance_value": 25.00,
        "signature_required": False
    },
    "12345": {
        "order_id": "12345",
        "customer_id": "cust_222",
        "status": "IN_TRANSIT",
        "order_date": "2025-12-17T10:00:00Z",
        "last_update": "2025-12-19T14:30:00Z",
        "tracking_number": "TRK12345ABC",
        "carrier": "FedEx",
        "total_cents": 5499,
        "currency": "USD",
        "items": [
            {
                "sku": "SKU-888",
                "name": "Standard Widget",
                "qty": 1,
                "price_cents": 5499
            }
        ],
        "origin_warehouse": "WH-01",
        "destination_warehouse": None,
        "shipping_method": "standard",
        "insurance_value": 60.00,
        "signature_required": False
    }
}

SHIPMENTS = {
    "84721": {
        "order_id": "84721",
        "carrier": "UPS",
        "service_level": "Ground",
        "eta_date": "2025-12-22",
        "original_eta": "2025-12-22",
        "latest_scan": "Departed hub",
        "scan_location": "Oakland, CA",
        "scan_timestamp": "2025-12-18T16:22:00Z",
        "weight_lbs": 5.2,
        "dimensions": "12x10x8",
        "delivery_attempts": 0
    },
    "99002": {
        "order_id": "99002",
        "carrier": "USPS",
        "service_level": "Priority Mail",
        "eta_date": "2025-12-15",
        "original_eta": "2025-12-15",
        "latest_scan": "Delivered",
        "scan_location": "Austin, TX",
        "scan_timestamp": "2025-12-15T11:04:00Z",
        "weight_lbs": 2.1,
        "dimensions": "8x6x4",
        "delivery_attempts": 1
    },
    "10015": {
        "order_id": "10015",
        "carrier": "FedEx",
        "service_level": "Priority Overnight",
        "eta_date": "2025-12-24",
        "original_eta": "2025-12-24",
        "latest_scan": "Label created",
        "scan_location": "San Francisco, CA",
        "scan_timestamp": "2025-12-19T09:10:00Z",
        "weight_lbs": 45.0,
        "dimensions": "24x20x16",
        "delivery_attempts": 0
    },
    "45678": {
        "order_id": "45678",
        "carrier": "DHL",
        "service_level": "International Express",
        "eta_date": "2025-12-25",
        "original_eta": "2025-12-25",
        "latest_scan": "Processing at origin",
        "scan_location": "San Francisco, CA",
        "scan_timestamp": "2025-12-19T10:30:00Z",
        "weight_lbs": 3.5,
        "dimensions": "10x8x6",
        "delivery_attempts": 0
    },
    "23456": {
        "order_id": "23456",
        "carrier": "Royal Mail",
        "service_level": "First Class",
        "eta_date": "2025-12-20",
        "original_eta": "2025-12-16",
        "latest_scan": "Delayed at customs",
        "scan_location": "Heathrow, UK",
        "scan_timestamp": "2025-12-17T14:00:00Z",
        "weight_lbs": 1.8,
        "dimensions": "8x6x3",
        "delivery_attempts": 0
    },
    "98765": {
        "order_id": "98765",
        "carrier": "FedEx",
        "service_level": "Priority Overnight",
        "eta_date": "2025-12-20",
        "original_eta": "2025-12-20",
        "latest_scan": "On FedEx vehicle for delivery",
        "scan_location": "New York, NY",
        "scan_timestamp": "2025-12-19T08:00:00Z",
        "weight_lbs": 8.5,
        "dimensions": "16x12x10",
        "delivery_attempts": 0
    },
    "11111": {
        "order_id": "11111",
        "carrier": "USPS",
        "service_level": "Return",
        "eta_date": "2025-12-18",
        "original_eta": "2025-12-18",
        "latest_scan": "Returned to sender",
        "scan_location": "San Jose, CA",
        "scan_timestamp": "2025-12-18T15:00:00Z",
        "weight_lbs": 1.2,
        "dimensions": "6x6x4",
        "delivery_attempts": 3
    },
    "12345": {
        "order_id": "12345",
        "carrier": "FedEx",
        "service_level": "Standard",
        "eta_date": "2025-12-21",
        "original_eta": "2025-12-21",
        "latest_scan": "In transit",
        "scan_location": "Memphis, TN",
        "scan_timestamp": "2025-12-19T14:30:00Z",
        "weight_lbs": 3.2,
        "dimensions": "10x8x6",
        "delivery_attempts": 0
    }
}

ORDER_EVENTS = {
    "84721": [
        {"timestamp": "2025-12-16T08:30:00Z", "event": "Order placed", "details": "Customer order received"},
        {"timestamp": "2025-12-17T08:10:00Z", "event": "Packed", "details": "Order packed at warehouse WH-01"},
        {"timestamp": "2025-12-17T18:02:00Z", "event": "Picked up by carrier", "details": "UPS collected package"},
        {"timestamp": "2025-12-18T16:22:00Z", "event": "Departed hub", "details": "Left Oakland facility"}
    ],
    "99002": [
        {"timestamp": "2025-12-10T14:20:00Z", "event": "Order placed", "details": "Customer order received"},
        {"timestamp": "2025-12-11T10:00:00Z", "event": "Packed", "details": "Order packed at warehouse WH-02"},
        {"timestamp": "2025-12-12T09:00:00Z", "event": "Picked up by carrier", "details": "USPS collected package"},
        {"timestamp": "2025-12-13T14:30:00Z", "event": "In transit", "details": "Package moving to destination"},
        {"timestamp": "2025-12-15T11:04:00Z", "event": "Delivered", "details": "Left at front door"}
    ],
    "10015": [
        {"timestamp": "2025-12-18T22:00:00Z", "event": "Order placed", "details": "Enterprise order received"},
        {"timestamp": "2025-12-19T09:10:00Z", "event": "Label created", "details": "Shipping label generated"}
    ],
    "23456": [
        {"timestamp": "2025-12-12T09:00:00Z", "event": "Order placed", "details": "International order received"},
        {"timestamp": "2025-12-13T11:00:00Z", "event": "Packed", "details": "Order packed at warehouse WH-UK-01"},
        {"timestamp": "2025-12-14T08:00:00Z", "event": "Picked up by carrier", "details": "Royal Mail collected"},
        {"timestamp": "2025-12-15T22:00:00Z", "event": "At customs", "details": "Awaiting customs clearance"},
        {"timestamp": "2025-12-17T14:00:00Z", "event": "Delayed", "details": "Customs delay - missing documentation"}
    ]
}

RETURN_REQUESTS = {
    "11111": {
        "order_id": "11111",
        "customer_id": "cust_111",
        "return_reason": "Wrong item received",
        "return_status": "COMPLETED",
        "refund_amount_cents": 1999,
        "refund_status": "PROCESSED",
        "return_label_tracking": "9405511899223856923413",
        "initiated_date": "2025-12-10T10:00:00Z",
        "completed_date": "2025-12-18T15:00:00Z"
    }
}

