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
- **Graph Modeling & Ring Analysis**: NetworkX, Graph Querying Algorithms (planned for Phase 2)
- **Machine Learning & Anomaly Detection**: Unsupervised & Graph ML (Isolation Forests, Graph Embeddings / GNN architectures) (planned for Phase 3)
- **Backend API Service**: FastAPI, Pydantic, Uvicorn, SQLite/PostgreSQL (planned for Phase 4)
- **Interactive UI / Forensic Dashboard**: React, Vite, Tailwind CSS, Graph Visualization (planned for Phase 5)
- **Forensic Explanation & Integrations**: LLM-assisted forensic reporting and payment gateway simulation interfaces (planned for Phase 6)

---

## 5. Six-Phase Development Roadmap

| Phase | Milestone | Scope |
| :--- | :--- | :--- |
| **Phase 1** | **Project Foundation & Synthetic Fintech Dataset** | Setup architecture, modular foundation, synthetic fintech data generator with 7 injected fraud ring archetypes, dataset validation engine, and test suite. |
| **Phase 2** | **Graph Engine & Ring Discovery** *(Upcoming)* | Heterogeneous graph construction, topological metrics, centrality analysis, community detection algorithms. |
| **Phase 3** | **Machine Learning & Risk Intelligence** *(Upcoming)* | Anomaly detection, graph feature engineering, multi-layer risk scoring models. |
| **Phase 4** | **Backend API & Service Architecture** *(Upcoming)* | High-performance RESTful APIs, transaction ingestion pipelines, real-time query endpoints. |
| **Phase 5** | **Forensic Dashboard & Visualizer** *(Upcoming)* | Interactive web frontend, real-time graph rendering, investigation canvas, and risk alerts. |
| **Phase 6** | **AI Forensic Copilot & Integration** *(Upcoming)* | Automated narrative investigation reports, payment simulation webhooks, end-to-end evaluation. |

---

## 6. Synthetic Data & Compliance Disclaimer

> [!IMPORTANT]
> **Synthetic Data Notice**: All customers, transactions, device fingerprints, IP addresses, payment instruments, and merchants generated and used in this project are strictly **synthetic** and programmatically generated for research, testing, and prototype evaluation purposes. No personally identifiable information (PII), real customer data, live bank account numbers, real payment credentials, or live payment gateway credentials are used or stored.
