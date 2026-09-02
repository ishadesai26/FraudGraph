"""Transaction Generator for Phase 6 Simulation."""

import uuid
from datetime import datetime
from typing import Dict, Any
from backend.simulation.scenarios import get_scenario_by_id


class TransactionGenerator:
    """Generates realistic test transactions for demo scenarios without mutating disk datasets."""

    @staticmethod
    def generate(scenario_id: str = "NORMAL_TXN", overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        scenario = get_scenario_by_id(scenario_id)
        payload = dict(scenario.sample_payload)

        if overrides:
            payload.update(overrides)

        txn_id = f"SIM_{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload["transaction_id"] = payload.get("transaction_id", txn_id)
        payload["timestamp"] = payload.get("timestamp", timestamp)
        payload["scenario_id"] = scenario.scenario_id

        return payload
