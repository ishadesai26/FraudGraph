"""Agent 3: Behavior Agent — Evaluates transaction velocity, amounts, and device hopping."""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import AgentEvidenceItem


class BehaviorAgent(BaseAgent):
    """Specialized agent evaluating transaction velocity, amount anomalies, and device/IP switching."""

    def __init__(self):
        super().__init__(
            name="BehaviorAgent",
            description="Analyzes transaction velocity, temporal burst sync, amount spikes, and device/IP hopping.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        evidence: List[AgentEvidenceItem] = []
        behavior_data = context.get("behavior_data", {})
        timeline = context.get("timeline", [])
        
        total_txns = int(behavior_data.get("total_transactions", len(timeline)))
        total_spend = float(behavior_data.get("total_spend", 0.0))
        account_age = int(behavior_data.get("account_age_days", 90))
        kyc_verified = bool(behavior_data.get("kyc_verified", True))
        
        # Analyze timeline for bursts
        burst_events = [e for e in timeline if e.get("is_burst") or (e.get("seconds_since_previous") is not None and e.get("seconds_since_previous") <= 180)]
        burst_count = len(burst_events)

        amounts = [float(e.get("amount", 0.0)) for e in timeline if "amount" in e]
        avg_amount = sum(amounts) / len(amounts) if amounts else (total_spend / max(1, total_txns))
        max_amount = max(amounts) if amounts else total_spend

        # 1. Temporal Burst Synchronization
        if burst_count >= 2:
            evidence.append(
                self.create_evidence(
                    signal="temporal_burst_synchronization",
                    description=f"Detected {burst_count} rapid transactions executed within <= 180s of previous activity (automated velocity signature).",
                    severity="CRITICAL" if burst_count >= 4 else "HIGH",
                    value=burst_count,
                    importance=0.35,
                    category="BEHAVIORAL_HISTORY",
                )
            )

        # 2. Amount Anomalies & High-Value Spikes
        if max_amount >= 40000.0 or (avg_amount > 0 and max_amount >= 3.5 * avg_amount and max_amount >= 20000.0):
            evidence.append(
                self.create_evidence(
                    signal="high_value_transaction_spike",
                    description=f"Encountered unusual high-value transaction peak of ₹{max_amount:,.2f} (Average: ₹{avg_amount:,.2f}).",
                    severity="HIGH",
                    value=round(max_amount, 2),
                    importance=0.30,
                    category="BEHAVIORAL_HISTORY",
                )
            )

        # 3. Frequent Device & IP Switching
        device_ids = set([e.get("device_id") for e in timeline if e.get("device_id")])
        if len(device_ids) >= 3 and total_txns <= 10:
            evidence.append(
                self.create_evidence(
                    signal="excessive_device_switching",
                    description=f"Used {len(device_ids)} distinct hardware devices across {total_txns} total transactions.",
                    severity="MEDIUM",
                    value=len(device_ids),
                    importance=0.25,
                    category="BEHAVIORAL_HISTORY",
                )
            )

        # 4. Protective & Mitigating Behavioral Factors
        if kyc_verified:
            evidence.append(
                self.create_evidence(
                    signal="kyc_verification_complete",
                    description="Customer identity is fully verified via mandatory KYC protocols.",
                    severity="LOW",
                    value=True,
                    importance=0.15,
                    category="PROTECTIVE",
                )
            )
        if account_age >= 180:
            evidence.append(
                self.create_evidence(
                    signal="established_account_tenure",
                    description=f"Established account tenure of {account_age} days with consistent operating history.",
                    severity="LOW",
                    value=account_age,
                    importance=0.15,
                    category="PROTECTIVE",
                )
            )

        # Risk level determination
        behavior_level = "LOW"
        if burst_count >= 2 or (max_amount >= 40000.0 and len(device_ids) >= 3):
            behavior_level = "HIGH"
        elif burst_count == 1 or max_amount >= 25000.0:
            behavior_level = "MEDIUM"

        summary = (
            f"BehaviorAgent evaluated transaction profile: {total_txns} txns, ₹{total_spend:,.2f} spend, "
            f"{burst_count} burst sync events, max txn ₹{max_amount:,.2f} ({behavior_level} risk)."
        )

        return {
            "behavior_risk_level": behavior_level,
            "burst_count": burst_count,
            "total_transactions": total_txns,
            "total_spend": total_spend,
            "evidence": evidence,
            "summary": summary,
        }
