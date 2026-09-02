# FraudGraph Phase 4: Explainable AI & Fraud Investigation Intelligence

## 1. Overview & Two-Layer Architecture

FraudGraph Phase 4 transforms the system from a predictive scoring model into an **evidence-based forensic investigation intelligence engine**. 

To eliminate hallucinated explanations while maintaining rich interpretability, FraudGraph enforces a **strict two-layer architectural boundary**:

```
+---------------------------------------------------------------------------------------+
|                                Phase 1, 2, & 3 Data                                   |
|  - Raw Transactional History (10k txns, 2k customers, hardware & IP usage)           |
|  - Graph Topology (14.1k nodes, 90k edges, Louvain communities, 26 fraud rings)       |
|  - ML Inferences (RandomForest probas, IsolationForest anomaly scores, importances)   |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                       LAYER 1: DETERMINISTIC EVIDENCE ENGINE                          |
|  (The Immutable Source of Truth — Zero Hallucination, Exact Graph Tracing)            |
|                                                                                       |
|  1. FeatureExplainer: Amount spikes, velocity, proxy IP, and protective tenure.       |
|  2. NetworkExplainer: Exact shared hardware IDs, mule cards/VPAs, community density.  |
|  3. TimelineBuilder: Chronological event sequencing & burst synchronization.          |
|  4. RecommendationEngine: Neutral, evidence-backed investigative next steps.          |
|  5. ConfidenceAssessor: Multi-source corroboration metric (HIGH / MEDIUM / LOW).      |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
                        [ Structured JSON Evidence Object ]
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
+---------------------------------------+     +---------------------------------------+
|       LAYER 2A: DETERMINISTIC         |     |          LAYER 2B: ISOLATED           |
|           REPORT GENERATOR            |     |             LLM EXPLAINER             |
|                                       |     |                                       |
| - Standardized markdown dossiers.     |     | - Strictly bounded by Layer 1 JSON.   |
| - Zero API dependencies.              |     | - Strict zero-hallucination prompts.  |
| - 100% reproducible test output.      |     | - Graceful deterministic fallback.    |
+---------------------------------------+     +---------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                             Investigation Deliverables                                |
|  - data/processed/investigation_index.json (Searchable fast-lookup index)             |
|  - data/processed/investigation_summary.json (Executive high-level summary)           |
|  - data/processed/investigation_reports/*.json (Individual entity forensic dossiers)  |
+---------------------------------------------------------------------------------------+
```

---

## 2. Deterministic Evidence Engine (Layer 1)

The **Evidence Engine** (`backend/explainability/evidence_engine.py`) is the quantitative foundation. It traces every finding back to raw data, graph structures, or ML outputs.

### 2.1 Evidence Object Schema
```json
{
  "entity_id": "CUST_00028",
  "entity_type": "customer",
  "risk_score": 99.1,
  "risk_level": "CRITICAL",
  "explanation_confidence": "MEDIUM",
  "associated_ring_id": "FR_015",
  "member_role": "MEMBER",
  "total_transactions": 15,
  "total_spend": 488216.93,
  "evidence": [
    {
      "source": "BEHAVIORAL_MODEL",
      "signal": "supervised_model_risk",
      "severity": "CRITICAL",
      "description": "Supervised RandomForest fraud classifier estimated a 99.8% fraud probability."
    },
    {
      "source": "BEHAVIORAL_MODEL",
      "signal": "behavioral_anomaly_score",
      "severity": "HIGH",
      "description": "Unsupervised IsolationForest flagged multi-dimensional behavioral deviation (Score: 100.0/100)."
    }
  ]
}
```

---

## 3. Network & Graph Topological Explanations

The **Network Explainer** (`backend/explainability/network_explanations.py`) reveals multi-entity infrastructure sharing:

1. **Shared Hardware Clusters**: Identifies specific hardware identifiers (`dev_xxx`) used by multiple customer accounts, citing exact co-transacting account IDs.
2. **Mule Payment Instruments**: Identifies payment methods (`pm_xxx` cards or UPI VPAs) circulating among distinct customers.
3. **Proxy IP Infrastructure**: Detects shared VPN and Datacenter network routing.
4. **Syndicate Modularity Context**: Details community size, internal graph density, and fraud ring associations.

---

## 4. Feature Attribution & Protective Signal Isolation

The **Feature Explainer** (`backend/explainability/feature_explanations.py`) separates risk drivers from mitigating factors:

### Positive Risk Signals
- **`amount_spike`**: Current transaction exceeds $3\times$ customer historical average.
- **`elevated_velocity`**: Customer exceeds $> 3.0\text{ txns/day}$.
- **`proxy_ip_routing`**: Request routed via Datacenter/VPN proxy.
- **`geographic_deviation`**: Transaction executed outside registered primary city.
- **`unusual_timing`**: Transactions initiated during overnight off-hours (02:00–05:00 HRS).

### Mitigating / Protective Signals
- **`mature_account`**: Account tenure $> 180\text{ days}$ with established legitimate track record.
- **`consistent_amount`**: Transaction aligns with typical historical spending baseline.

> [!NOTE]
> Explanations explicitly state that feature importance reflects statistical attribution to the risk score, rather than definitive proof of causal intent.

---

## 5. Chronological Investigation Timeline & Burst Detection

The **Timeline Builder** reconstructed in `InvestigationEngine.build_investigation_timeline` sorts customer transactions chronologically and identifies coordinated timing attacks:

- **Burst Synchronization (`BURST_SYNC`)**: Flagged when interval between consecutive transactions is $\le 180\text{ seconds}$.
- **High-Value Spikes (`HIGH_VALUE`)**: Flagged when transaction amount exceeds ₹25,000.
- **Device / IP Hopping**: Highlights transitions between hardware endpoints and proxy gateways.

---

## 6. Evidence-Based Investigator Recommendations

Recommendations use neutral, investigative language to guide human analysts without pre-judging guilt:

| Trigger Evidence | Generated Recommendation |
| :--- | :--- |
| **Shared Payment Method** | *"Review authorization logs for shared payment instrument 'PM_xxx' across N linked accounts."* |
| **Shared Hardware Device** | *"Examine device fingerprint integrity for hardware endpoint 'DEV_xxx'."* |
| **Syndicate Membership** | *"Audit coordinated transaction flow within syndicate 'FR_xxx'."* |
| **Critical Composite Risk** | *"Initiate mandatory step-up identity verification challenge prior to fund release."* |

---

## 7. Explanation Confidence Assessment

Explanation confidence measures **multi-source evidence breadth**, distinguishing multi-corroborated alerts from single-signal alerts:

- **`HIGH` Confidence**: Independent evidence corroborated across all three layers (Graph Relational + Supervised ML + Unsupervised Anomaly).
- **`MEDIUM` Confidence**: Corroboration across two independent sources (e.g. Behavioral Velocity + Graph Ring Link).
- **`LOW` Confidence**: Single isolated signal with minimal network context.

---

## 8. LLM Safety Boundary & Hallucination Prevention

The **LLM Explainer** (`backend/explainability/llm_explainer.py`) is strictly quarantined:
1. **Input Isolation**: Receives only pre-verified JSON dictionaries generated by Layer 1.
2. **Strict System Prompt**: Explicitly prohibits the model from fabricating entities, amounts, transactions, or fraud rings.
3. **Deterministic Fallback**: If no API key is provided in `GEMINI_API_KEY` or `GOOGLE_API_KEY`, the system automatically defaults to `ReportGenerator`.

---

## 9. Searchable Investigation Index & Summary

- **`data/processed/investigation_index.json`**: Indexed 2,005 entities for rapid frontend search without graph recomputation.
- **`data/processed/investigation_summary.json`**: Executive summary capturing highest-risk rings, highest-risk accounts, and primary risk patterns.
- **`data/processed/investigation_reports/`**: Full JSON dossiers for high-risk accounts and detected fraud rings.

---

## 10. Execution Instructions

### Run Investigation Engine & Generate Reports:
```bash
python -m backend.explainability.investigation_engine
```

### Run Automated Test Suite (Phases 1-4):
```bash
pytest -v
```
