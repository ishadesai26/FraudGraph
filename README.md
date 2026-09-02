# FraudGraph

**AI-Powered Coordinated Fraud Ring Detection for Digital Payments**

---

## 1. Problem Statement

In modern digital payments and fintech ecosystems, fraudulent actors rarely operate in isolation. Sophisticated fraudsters organize into **coordinated fraud rings**, leveraging shared devices, rotating IP addresses/proxies, synthetic identities, mule bank accounts, and coordinated timing attacks to evade traditional rule-based filters and single-transaction fraud detection systems.

Traditional fraud monitoring inspects transactions as isolated events. Consequently, sophisticated collusion schemes—such as distributed chargeback abuse, promo exploitation rings, and coordinated merchant-draining attacks—slip through undetected until massive financial loss occurs.

---

## 2. Project Objective

**FraudGraph** aims to uncover, visualize, and dismantle multi-entity coordinated fraud syndicates by modeling digital payment ecosystems as dynamic, heterogeneous graphs. 

By analyzing the complex structural topologies and hidden relational linkages connecting:
- **Customers / Accounts**
- **Transactions**
- **Devices & OS environments**
- **IP addresses & Geo-locations**
- **Payment instruments** (Cards, UPI VPAs, Wallets, Bank Accounts)
- **Merchants & Categories**

FraudGraph enables risk teams to detect emerging fraud rings in real-time, explain the interconnected evidence clearly, and mitigate systemic risks before balance depletion or chargeback settlement.

---

## 3. Core Innovation

1. **Heterogeneous Entity-Graph Modeling**: Linking disparate transactional identifiers into a cohesive multi-partite graph structure to reveal hidden multi-hop relationships.
2. **Coordinated Ring Topology Detection**: Identifying dense bipartite and multi-partite clusters, anomalous graph cycles, and shared hardware/network signatures.
3. **Graph-Augmented Machine Learning**: Combining graph structural embeddings with node behavioral metrics to identify collusive fraud without relying on rigid threshold rules.
4. **Explainable Ring Intelligence**: Transforming complex multi-hop graph clusters into actionable forensic intelligence for risk analysis and compliance teams.

---

## 4. Planned Technology Stack

- **Data Engineering & Analysis**: Python 3.12, Pandas, NumPy, Faker
- **Graph Modeling & Ring Analysis**: NetworkX 3.6+, Louvain Modularity Community Detection, Multi-Signal Risk Scoring
- **Machine Learning & Risk Engine**: Scikit-Learn (RandomForest, IsolationForest, RobustScaler, OneHotEncoder), Joblib, Matplotlib
- **Backend API Service**: FastAPI, Pydantic, Uvicorn, SQLite/PostgreSQL *(Phase 4)*
- **Interactive UI / Forensic Dashboard**: React, Vite, Tailwind CSS, Graph Visualization (Cytoscape.js / D3.js) *(Phase 5)*
- **Forensic Explanation & Integrations**: LLM-assisted forensic reporting and payment gateway simulation interfaces *(Phase 6)*

---

## 5. Six-Phase Development Roadmap

| Phase | Milestone | Status | Scope |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Project Foundation & Synthetic Fintech Dataset** | `COMPLETED` | Architecture, synthetic fintech dataset (2k customers, 10k transactions, 500 devices, 1k IPs, 500 PMs, 100 merchants), 7 injected fraud rings, validation engine, test suite. |
| **Phase 2** | **Graph Construction & Fraud-Ring Detection** | `COMPLETED` | Heterogeneous graph (14.1k nodes, 90k edges), customer projection graph, graph features & centrality, Louvain community detection, multi-signal risk engine ($0-100$), export artifacts. |
| **Phase 3** | **Machine Learning Risk Engine & Model Evaluation** | `COMPLETED` | Transaction/behavioral baseline, unsupervised IsolationForest anomaly detector, graph-enhanced RandomForest classifier, multi-factor composite risk scorer ($0-100$), time-aware split, threshold analysis, evaluation visualizations. |
| **Phase 4** | **Backend API & Service Architecture** | `PLANNED` | High-performance RESTful APIs, transaction ingestion pipelines, real-time query endpoints. |
| **Phase 5** | **Forensic Dashboard & Visualizer** | `PLANNED` | Interactive web frontend, real-time graph rendering, investigation canvas, and risk alerts. |
| **Phase 6** | **AI Forensic Copilot & Integration** | `PLANNED` | Automated narrative investigation reports, payment simulation webhooks, end-to-end evaluation. |

---

## 6. Getting Started & Running FraudGraph

### 1. Setup Environment
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Generate Synthetic Fintech Dataset (Phase 1)
```bash
python data/generate_data.py
python data/validate_data.py
```

### 3. Run Graph Intelligence & Fraud-Ring Engine (Phase 2)
```bash
python -m backend.graph.run_pipeline
```
This builds the heterogeneous graph, calculates graph centrality & behavioral features, detects connected communities, executes multi-signal risk scoring, and exports:
- `data/processed/fraud_rings.csv`
- `data/processed/ring_members.csv`
- `data/processed/graph_nodes.csv`
- `data/processed/graph_edges.csv`

### 4. Train & Evaluate ML Risk Engine (Phase 3)
```bash
# Train Baseline, Anomaly Detector, and FraudGraph Models:
python -m backend.ml.train

# Evaluate on Held-Out Test Set and Generate Visual Charts:
python -m backend.ml.evaluate
```
This exports:
- `backend/ml/artifacts/*.joblib` (Trained model pipelines)
- `data/processed/model_metrics.json` (Comparative performance metrics)
- `data/processed/feature_importance.json` (Feature ranking breakdown)
- `data/processed/evaluation/` (ROC, PR curves, Confusion matrices, Feature importance chart)

### 5. Run Automated Test Suite (Phases 1, 2, and 3)
```bash
pytest -v
```

---

## 6. Synthetic Data & Compliance Disclaimer

> [!IMPORTANT]
> **Synthetic Data Notice**: All customers, transactions, device fingerprints, IP addresses, payment instruments, and merchants generated and used in this project are strictly **synthetic** and programmatically generated for research, testing, and prototype evaluation purposes. No personally identifiable information (PII), real customer data, live bank account numbers, real payment credentials, or live payment gateway credentials are used or stored.
