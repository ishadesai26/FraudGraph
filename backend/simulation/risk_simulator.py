"""Live Risk Simulator for real-time transaction scoring and agentic investigation."""

import uuid
from typing import Dict, Any, Optional
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.schemas import SimulationResponse
from backend.api.data_service import DataService


class RiskSimulator:
    """Evaluates simulated transactions through the live risk pipeline and multi-agent engine."""

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.data_service = DataService.get_instance()

    def simulate_and_investigate(self, transaction: Dict[str, Any], scenario_id: Optional[str] = None) -> SimulationResponse:
        cust_id = transaction.get("customer_id", "CUST_00803")
        amount = float(transaction.get("amount", 1000.0))
        seconds_prev = transaction.get("seconds_since_previous")
        device_id = transaction.get("device_id")
        ip_id = transaction.get("ip_id")

        # 1. Retrieve baseline customer metadata & graph context from DataService
        cust_profile_raw = self.data_service.get_customer_detail(cust_id)
        cust_profile = cust_profile_raw.model_dump() if hasattr(cust_profile_raw, "model_dump") else (cust_profile_raw or {})
        
        # 2. Compute Real-Time Risk Signals on the Simulated Transaction
        base_risk = float(cust_profile.get("risk_score", 15.0)) if cust_profile else 15.0
        ring_id = cust_profile.get("associated_ring_id") if cust_profile else None
        
        if scenario_id == "NORMAL_TXN":
            ring_id = None
            base_risk = min(15.0, base_risk)

        # Anomaly scoring based on amount and velocity
        is_burst = seconds_prev is not None and seconds_prev <= 180
        anomaly_score = 10.0
        if amount >= 50000.0:
            anomaly_score += 45.0
        elif amount >= 25000.0:
            anomaly_score += 25.0

        if is_burst:
            anomaly_score += 35.0
        if scenario_id == "SHARED_DEVICE_CLUSTER" or (scenario_id != "NORMAL_TXN" and len(cust_profile.get("shared_devices", [])) > 0):
            anomaly_score += 20.0
        anomaly_score = min(100.0, anomaly_score)

        # Supervised probability estimation
        supervised_prob = (base_risk / 100.0) * 0.60
        if amount >= 40000.0:
            supervised_prob += 0.25
        if is_burst:
            supervised_prob += 0.15
        if ring_id and str(ring_id).lower() not in ["none", "isolated", "none (isolated node)"]:
            supervised_prob += 0.20
        supervised_prob = min(0.998, max(0.01, supervised_prob))

        # Network risk score
        net_risk = cust_profile.get("contributing_signals", [])
        net_risk_val = 0.0
        for s in net_risk:
            if s.get("name") == "network_risk_score":
                net_risk_val = float(s.get("value", 0.0))
        if scenario_id == "FRAUD_RING_SYNDICATE":
            net_risk_val = max(95.0, net_risk_val)
        elif scenario_id == "SHARED_DEVICE_CLUSTER":
            net_risk_val = max(75.0, net_risk_val)

        # Multi-factor composite risk
        composite_risk = (supervised_prob * 100.0 * 0.50) + (net_risk_val * 0.25) + (anomaly_score * 0.25)
        composite_risk = round(min(100.0, max(0.0, composite_risk)), 1)

        # Synthesize timeline
        sim_timeline = list(cust_profile.get("timeline", [])) if cust_profile else []
        sim_timeline.insert(0, {
            "transaction_id": transaction.get("transaction_id", f"SIM_{uuid.uuid4().hex[:6]}"),
            "timestamp": transaction.get("timestamp", "NOW"),
            "amount": amount,
            "merchant_id": transaction.get("merchant_id", "MERCH_0001"),
            "payment_type": transaction.get("payment_type", "UPI"),
            "device_id": device_id,
            "ip_id": ip_id,
            "city": transaction.get("city", "Mumbai"),
            "seconds_since_previous": seconds_prev,
            "is_burst": is_burst,
        })

        # 3. Trigger 6-Agent Investigation
        risk_data = {
            "risk_score": composite_risk,
            "supervised_model_probability": supervised_prob,
            "unsupervised_anomaly_score": anomaly_score,
            "baseline_probability": supervised_prob * 0.75,
            "graph_model_probability": supervised_prob,
        }

        graph_data = {
            "network_risk_score": 0.0 if scenario_id == "NORMAL_TXN" else net_risk_val,
            "associated_ring_id": ring_id or ("FR_015" if scenario_id == "FRAUD_RING_SYNDICATE" else None),
            "member_role": cust_profile.get("member_role", "MEMBER") if cust_profile else "MEMBER",
            "shared_devices": [] if scenario_id == "NORMAL_TXN" else cust_profile.get("shared_devices", []),
            "shared_payments": [] if scenario_id == "NORMAL_TXN" else cust_profile.get("shared_payments", []),
            "shared_ips": [{"resource_id": ip_id, "shared_with_count": 3}] if scenario_id == "SHARED_IP_PROXY" else [],
            "connected_neighbors": cust_profile.get("connected_neighbors", []) if cust_profile else [],
        }

        behavior_data = {
            "total_transactions": len(sim_timeline),
            "total_spend": sum([float(e.get("amount", 0.0)) for e in sim_timeline]),
            "account_age_days": cust_profile.get("account_age_days", 120) if cust_profile else 120,
            "kyc_verified": cust_profile.get("kyc_verified", True) if cust_profile else True,
        }

        investigation_res = self.orchestrator.investigate(
            entity_type="transaction",
            entity_id=transaction.get("transaction_id", "SIM_TXN"),
            risk_data=risk_data,
            graph_data=graph_data,
            behavior_data=behavior_data,
            timeline=sim_timeline[:10],
        )

        simulation_id = f"SIM_{uuid.uuid4().hex[:10].upper()}"

        return SimulationResponse(
            simulation_id=simulation_id,
            scenario_id=scenario_id,
            transaction=transaction,
            risk={
                "composite_risk_score": composite_risk,
                "supervised_ml_probability": round(supervised_prob, 4),
                "unsupervised_anomaly_score": round(anomaly_score, 1),
                "network_risk_score": round(net_risk_val, 1),
                "risk_tier": investigation_res.decision.status,
            },
            evidence={
                "evidence_items": [e.model_dump() for e in investigation_res.evidence_items],
                "conflicts": [c.model_dump() for c in investigation_res.conflicts],
                "evidence_coverage": investigation_res.decision.evidence_coverage,
            },
            investigation=investigation_res,
            agent_trace=investigation_res.agent_trace,
            decision=investigation_res.decision,
        )
