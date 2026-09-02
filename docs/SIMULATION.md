# FraudGraph Phase 6: Real-Time Risk Simulation & Demo Guide

## 1. Overview

The FraudGraph Real-Time Transaction Simulator demonstrates how the machine-learning risk engine, graph intelligence framework, and collaborative 6-agent investigation pipeline evaluate incoming financial transactions on the fly.

Unlike traditional mock demos that return static mock responses, FraudGraph's simulator executes **live feature extraction, model inference, graph neighborhood querying, and agent orchestration** on every simulated payload.

---

## 2. Six Controlled Simulation Scenarios

| Scenario ID | Title | Underlying Fraud Pattern | Expected Disposition |
| :--- | :--- | :--- | :--- |
| `NORMAL_TXN` | **Normal Retail Purchase** | Standard ₹1,450 consumer transaction by verified customer on isolated device. | `LOW_RISK` |
| `HIGH_VALUE_SPIKE` | **Unusual High-Value Spike** | Sudden ₹78,500 transaction with high deviation from customer historical mean. | `REVIEW` / `ENHANCED_REVIEW` |
| `SHARED_DEVICE_CLUSTER` | **Shared Device Coordinated Activity** | Transaction originating from hardware device linked to 6 distinct customer accounts. | `ENHANCED_REVIEW` |
| `SHARED_IP_PROXY` | **Proxy IP Infrastructure Routing** | Transaction routed through datacenter VPN proxy with rapid multi-account succession. | `ENHANCED_REVIEW` |
| `SYNCHRONIZED_BURST` | **Rapid Synchronized Burst** | Automated scripted transaction executing only 14 seconds after prior transfer. | `ENHANCED_REVIEW` |
| `FRAUD_RING_SYNDICATE` | **Coordinated Syndicate Spend** | High-velocity transaction from active syndicate member (`FR_015`) using shared card & device. | `HIGH_RISK` |

---

## 3. Real-Time Pipeline Execution Workflow

```
Simulated Ingress Payload (POST /api/simulation/analyze)
    │
    ├── 1. Ingress Validation & Baseline Lookup (DataService)
    ├── 2. Live Behavioral Feature Extraction (Amount spikes, Velocity deltas)
    ├── 3. Graph Neighborhood Lookup (Shared hardware, Cards, Syndicate memberships)
    ├── 4. Real-Time Model Inference (RandomForest Prob, IsolationForest Anomaly Score)
    ├── 5. Multi-Factor Composite Risk Scoring (50% ML + 25% Graph + 25% Anomaly)
    │
    └── 6. Autonomous 6-Agent Collaborative Investigation
            ├── Risk Agent (Analyzes model outputs)
            ├── Graph Agent (Analyzes shared resources)
            ├── Behavior Agent (Analyzes temporal bursts)
            ├── Evidence Agent (Correlates signals & flags conflicts)
            ├── Investigator Agent (Extracts review targets)
            └── Decision Agent (Synthesizes final verdict)
```

---

## 4. Step-by-Step Hackathon Primary Demonstration Script

Follow this script to deliver a 3-minute hackathon pitch:

### Step 1: Baseline Normal Transaction
1. Navigate to the **Live Risk Simulator** (`/simulation`).
2. Select scenario: **`Normal Retail Transaction`** (`NORMAL_TXN`).
3. Click **"Simulate & Investigate Transaction"**.
4. **Judge Takeaway**: The transaction is scored in $< 15\text{ms}$ to a clean **`LOW_RISK`** disposition with **90.0% Evidence Coverage**, highlighting clean behavioral tenure and verified KYC without false positives.

### Step 2: Syndicate Fraud Ring Coordinated Attack
1. Select scenario: **`Coordinated Fraud-Ring Syndicate Spend`** (`FRAUD_RING_SYNDICATE`).
2. Point out the payload parameters (Amount: ₹45,000, Velocity Interval: 25 seconds, Customer: `CUST_00028`).
3. Click **"Simulate & Investigate Transaction"**.
4. **Judge Takeaway**:
   - **Composite Risk Score**: Spikes to **95.2 / 100 (CRITICAL)**.
   - **Model Breakdown**: 99.8% Supervised ML probability, 90.0/100 Anomaly score, 95.0/100 Network risk.
   - **6-Agent Consensus**: All 6 agents complete in parallel/sequence ($< 1\text{ms}$ each), detecting 4 critical signals.
   - **Provenance & Actions**: Evidence points directly to syndicate `FR_015` and shared hardware, with a recommended disposition action to hold funds and escalate.

### Step 3: Deep-Dive in Agent Investigation Console
1. Navigate to **Agent Investigation** (`/agents`).
2. Target `CUST_00028` to demonstrate the interactive multi-agent trace, category filters, and conflict resolution mechanics.
