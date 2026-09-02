"""Controlled Demo Scenarios for Real-Time Transaction Simulation."""

from typing import Dict, List, Any
from backend.agents.schemas import SimulationScenario

SCENARIOS: List[SimulationScenario] = [
    SimulationScenario(
        scenario_id="NORMAL_TXN",
        title="Normal Retail Transaction",
        description="Standard consumer purchase with verified KYC, normal amount, and isolated endpoint.",
        expected_risk_tier="LOW_RISK",
        sample_payload={
            "customer_id": "CUST_00803",
            "amount": 1450.0,
            "merchant_id": "MERCH_0012",
            "payment_type": "CREDIT_CARD",
            "device_id": "DEV_00340",
            "ip_id": "IP_00780",
            "city": "Mumbai",
            "seconds_since_previous": 86400,
        },
    ),
    SimulationScenario(
        scenario_id="HIGH_VALUE_SPIKE",
        title="Unusual High-Value Spike",
        description="Sudden ₹78,500 transaction with high deviation from customer historical mean.",
        expected_risk_tier="REVIEW",
        sample_payload={
            "customer_id": "CUST_00450",
            "amount": 78500.0,
            "merchant_id": "MERCH_0005",
            "payment_type": "NET_BANKING",
            "device_id": "DEV_00110",
            "ip_id": "IP_00250",
            "city": "Delhi",
            "seconds_since_previous": 43200,
        },
    ),
    SimulationScenario(
        scenario_id="SHARED_DEVICE_CLUSTER",
        title="Shared Device Coordinated Activity",
        description="Transaction originating from hardware linked to multiple customer accounts.",
        expected_risk_tier="ENHANCED_REVIEW",
        sample_payload={
            "customer_id": "CUST_00112",
            "amount": 16500.0,
            "merchant_id": "MERCH_0044",
            "payment_type": "UPI",
            "device_id": "DEV_00078",
            "ip_id": "IP_00095",
            "city": "Bangalore",
            "seconds_since_previous": 600,
        },
    ),
    SimulationScenario(
        scenario_id="SHARED_IP_PROXY",
        title="Proxy IP Infrastructure Routing",
        description="Transaction routed through shared proxy IP cluster with abnormal endpoint velocity.",
        expected_risk_tier="ENHANCED_REVIEW",
        sample_payload={
            "customer_id": "CUST_00230",
            "amount": 12800.0,
            "merchant_id": "MERCH_0022",
            "payment_type": "DEBIT_CARD",
            "device_id": "DEV_00190",
            "ip_id": "IP_00120",
            "city": "Hyderabad",
            "seconds_since_previous": 300,
        },
    ),
    SimulationScenario(
        scenario_id="SYNCHRONIZED_BURST",
        title="Rapid Synchronized Velocity Burst",
        description="Automated scripted transaction executing only 14 seconds after prior transfer.",
        expected_risk_tier="ENHANCED_REVIEW",
        sample_payload={
            "customer_id": "CUST_00340",
            "amount": 28900.0,
            "merchant_id": "MERCH_0088",
            "payment_type": "UPI",
            "device_id": "DEV_00210",
            "ip_id": "IP_00440",
            "city": "Pune",
            "seconds_since_previous": 14,
        },
    ),
    SimulationScenario(
        scenario_id="FRAUD_RING_SYNDICATE",
        title="Coordinated Fraud-Ring Syndicate Spend",
        description="High-velocity transaction from active syndicate core member using shared card and device.",
        expected_risk_tier="HIGH_RISK",
        sample_payload={
            "customer_id": "CUST_00028",
            "amount": 45000.0,
            "merchant_id": "MERCH_0067",
            "payment_type": "UPI",
            "device_id": "DEV_00028",
            "ip_id": "IP_00028",
            "city": "Mumbai",
            "seconds_since_previous": 25,
        },
    ),
]


def get_scenario_by_id(scenario_id: str) -> SimulationScenario:
    """Retrieve a scenario by ID or return default normal scenario."""
    for sc in SCENARIOS:
        if sc.scenario_id.upper() == scenario_id.upper():
            return sc
    return SCENARIOS[0]
