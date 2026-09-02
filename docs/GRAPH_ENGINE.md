# FraudGraph Phase 2: Graph Construction & Coordinated Fraud-Ring Detection Engine

## 1. Overview & Architecture

The FraudGraph Graph Engine converts the heterogeneous fintech transactional database from Phase 1 into graph structures to detect **coordinated fraud syndicates**. 

While individual fraudulent transactions often appear legitimate when examined in isolation (e.g., standard amounts, valid cards), collusive fraud rings leave structural signatures across shared hardware, payment instruments, network proxies, and temporal synchronicity.

```
+-------------------------------------------------------------------------------+
|                       Phase 1 Relational Datasets                             |
| (customers.csv, transactions.csv, devices.csv, ips.csv, payment_methods.csv)  |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                          Graph Construction Engine                            |
|  1. Heterogeneous Graph H: MultiDiGraph (14,110 Nodes, 90,000 Edges)          |
|  2. Customer Projection Graph G_cust: Homogeneous Weighted Graph (2,000 Nodes)|
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                        Graph Feature Extractor                                |
|  - Centrality (PageRank, Sampled Betweenness, Weighted Degree)                |
|  - Topology (Clustering Coefficient, Customer Degree)                         |
|  - Behavioral (Merchant HHI, Velocity, Burst Synchronicity, Geo Dispersion)   |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                      Modularity Community Detection                           |
|  - Louvain Modularity Maximization (nx.community.louvain_communities)        |
|  - Partitions network into dense structural subgraphs                         |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                 Multi-Signal Deterministic Risk Scoring                       |
|  - Individual Risk Score (0-100) vs Network Risk Score (0-100)                |
|  - Multi-Signal Compounding (Shared Devs + Shared PMs + Proxy + Bursts + HHI) |
|  - False-Positive Dampening for Single Legitimate Resource Sharing            |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                      Processed Output Artifacts                               |
|  - data/processed/fraud_rings.csv                                             |
|  - data/processed/ring_members.csv                                            |
|  - data/processed/graph_nodes.csv                                             |
|  - data/processed/graph_edges.csv                                             |
+-------------------------------------------------------------------------------+
```

---

## 2. Graph Construction & Schema

### 2.1 Heterogeneous Multi-Directed Graph (`H`)
The heterogeneous graph `H` represents the complete ecosystem of entities and their transactional relationships.

- **Total Nodes**: `14,110`
- **Total Directed Edges**: `90,000`

#### Node Schema:
| Node Type | Count | Key Attributes | Description |
| :--- | :--- | :--- | :--- |
| **`Customer`** | 2,000 | `customer_id`, `name`, `city`, `risk_tier` | Account holders initiating financial activity. |
| **`Transaction`**| 10,000 | `transaction_id`, `amount`, `timestamp`, `status` | Individual payment events. |
| **`Device`** | 500 | `device_id`, `device_type`, `os`, `browser` | Hardware/mobile/desktop endpoints. |
| **`IP`** | 1,000 | `ip_id`, `ip_address`, `ip_type`, `isp`, `vpn_flag` | Network origin (Residential, Datacenter, VPN). |
| **`PaymentMethod`** | 500 | `payment_method_id`, `payment_type`, `issuer_bank` | Cards, VPAs, Wallets, NetBanking. |
| **`Merchant`** | 100 | `merchant_id`, `merchant_name`, `category` | Payment receivers. |
| **`Location`** | 10 | `location_id`, `city`, `state` | Geographic transaction hubs. |

#### Edge Schema:
| Edge Type | Source Node | Target Node | Weight | Description |
| :--- | :--- | :--- | :--- | :--- |
| `INITIATED` | Customer | Transaction | 1.0 | Customer starts transaction. |
| `PAID_TO` | Transaction | Merchant | 1.0 | Funds routed to merchant. |
| `TRANSACTED_ON` | Transaction | Device | 1.0 | Hardware device used for transaction. |
| `ROUTED_THROUGH` | Transaction | IP | 1.0 | Network IP address of request. |
| `PAID_WITH` | Transaction | PaymentMethod | 1.0 | Payment instrument utilized. |
| `LOCATED_IN` | Transaction | Location | 1.0 | City location of transaction. |
| `USES_DEVICE` | Customer | Device | $N_{txns}$ | Aggregated device usage frequency. |
| `USES_IP` | Customer | IP | $N_{txns}$ | Aggregated IP usage frequency. |
| `USES_PAYMENT` | Customer | PaymentMethod | $N_{txns}$ | Aggregated payment method usage. |

---

### 2.2 Homogeneous Customer Projection Graph (`G_cust`)
To detect collusive rings, the bipartite and entity relationships are projected onto a homogeneous graph where nodes are `Customers` and edge weights reflect relational coordination.

Edge Weight Formulation between customer $u$ and customer $v$:
$$\text{Weight}(u, v) = \sum_{e \in \text{Linkages}(u, v)} W_e \cdot \sqrt{\text{Txns}_u(e) \times \text{Txns}_v(e)}$$

Where:
- **`SHARED_DEVICE`**: Base weight $= 3.5$. Added when $u$ and $v$ execute transactions on the same hardware device.
- **`SHARED_PAYMENT`**: Base weight $= 4.5$. Added when $u$ and $v$ share a credit card or UPI VPA.
- **`SHARED_IP`**: 
  - If IP is `DATACENTER` or `VPN`: Base weight $= 3.5$.
  - If IP is `RESIDENTIAL`: Base weight $= 0.5$ (dampened to avoid false clustering on shared ISP gateways).
- **`CO_TRANSACTION`**: Base weight $= 2.0$. Added when $u$ and $v$ execute transactions at the same merchant within a 10-minute window.

---

## 3. Graph Topological & Behavioral Features

For each customer $c \in V_{\text{cust}}$, 23 structural and behavioral metrics are computed without using ground truth fraud labels:

| Feature Name | Category | Description |
| :--- | :--- | :--- |
| `degree` | Topology | Number of distinct customers connected via shared resources. |
| `weighted_degree` | Topology | Sum of all shared resource linkage weights. |
| `pagerank` | Centrality | PageRank score indicating structural centrality in the network. |
| `betweenness_centrality` | Centrality | Sampled shortest-path betweenness ($k=100$) measuring bridge roles. |
| `clustering_coefficient` | Topology | Local triangular density indicating tightly connected cliques. |
| `shared_device_count` | Shared Resource | Number of unique devices shared with other customers. |
| `shared_ip_count` | Shared Resource | Number of unique IP addresses shared with other customers. |
| `shared_payment_count` | Shared Resource | Number of unique cards/VPAs shared with other customers. |
| `co_transaction_count` | Behavioral | Number of temporal merchant co-occurrences. |
| `merchant_hhi` | Concentration | Herfindahl-Hirschman Index of customer spend across merchants ($\sum s_i^2$). |
| `transaction_volume` | Financial | Total rupee volume of all transactions. |
| `txn_velocity_per_day` | Velocity | Average transactions per active day. |
| `temporal_sync_score` | Temporal | Fraction of transactions occurring in short bursts ($\le 180\text{s}$). |
| `geographic_spread` | Geographic | Number of unique cities transacted in. |

---

## 4. Community Detection (Modularity Maximization)

Communities are detected using **Louvain Modularity Maximization** (`nx.community.louvain_communities`) on the weighted customer projection graph:

$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

- **Deterministic Seeding**: `seed=42` ensures strict reproducibility.
- **Minimum Community Size Filter**: Single isolated nodes ($N=1$) are excluded from fraud ring candidacy.
- **Structural Properties**: For each community $C$, internal density $\rho(C) = \frac{2 |E(C)|}{|V(C)|(|V(C)|-1)}$, total internal weight $W_{\text{int}}$, and distinct shared resource counts are computed.

---

## 5. Multi-Signal Deterministic Risk Scoring

FraudGraph uses a multi-tiered risk scoring framework separating **Individual Risk** from **Network Risk**.

### 5.1 Individual Risk Score ($0 - 100$)
Evaluates node-level behavioral anomalies:
- Ticket size anomaly: Transactions $> ₹25,000$ (+25 pts).
- Merchant concentration: $\text{HHI} > 0.40$ on high-ticket merchants (+25 pts).
- Velocity spikes: Velocity $> 1.0\text{ txns/day}$ (+20 pts).
- Remote city jump: Transacting away from registered home city (+15 pts).
- Individual burst: Rapid sequential transactions (+15 pts).

### 5.2 Network Risk Score ($0 - 100$)
Evaluates community-level collusive signatures:
1. **Shared Device Intensity ($S_{\text{dev}}$)**: Max accounts per device $\ge 4$ and heavy transaction volume ($+30\text{ pts}$).
2. **Shared Payment Mule Intensity ($S_{\text{pm}}$)**: Multiple accounts using the same cards/VPAs ($+35\text{ pts}$).
3. **Proxy IP Routing ($S_{\text{ip}}$)**: Shared Datacenter/VPN proxy infrastructure ($+25\text{ pts}$).
4. **Synchronized Bursts ($S_{\text{sync}}$)**: High ratio of transactions occurring within narrow $\le 180\text{s}$ windows ($+25\text{ pts}$).
5. **Targeted Merchant Concentration ($S_{\text{merch}}$)**: Concentrated high-value merchant extraction ($+25\text{ pts}$).
6. **Geographic Inconsistency ($S_{\text{geo}}$)**: Collusive accounts jumping across disparate cities ($+25\text{ pts}$).

#### Multi-Signal Synergy Multiplier:
$$\text{Score}_{\text{final}} = \min\left(100.0, \sum S_i \times M(N_{\text{signals}})\right)$$

- $N_{\text{signals}} = 1$: Multiplier $= 0.70$ (Dampens single-signal noise like a legitimate shared household IP).
- $N_{\text{signals}} = 2$: Multiplier $= 1.00$.
- $N_{\text{signals}} \ge 3$: Multiplier $= 1.0 + 0.15 \times (N_{\text{signals}} - 2)$ (Compounding synergy).

Communities with $\text{Network Risk} \ge 50.0$ are classified as **Suspicious Fraud Rings**.

---

## 6. Evaluation Methodology & Ground Truth Validation

Ground truth labels from Phase 1 (`is_fraud`, `fraud_ring_id`) are **strictly excluded** during graph construction, feature extraction, community detection, and risk scoring. They are loaded exclusively inside `backend/graph/evaluation.py` to benchmark performance:

1. **Ring Detection Rate**:
   $$\text{Ring Detection Rate} = \frac{|\{R_{\text{GT}} : |R_{\text{GT}} \cap R_{\text{pred}}| \ge 2\}|}{|\text{Total Ground Truth Rings}|} \times 100\%$$
2. **Customer-Level Metrics**: Precision, Recall, and F1 score against all 52 known ground-truth fraudsters.
3. **Transaction-Level Metrics**: Precision, Recall, and F1 score across the 10,000 transaction corpus.
4. **False-Positive Resistance**: Verification that legitimate customers sharing residential IPs or single merchants remain unflagged.

---

## 7. Execution Instructions

### Run the Graph Pipeline:
```bash
python -m backend.graph.run_pipeline
```

### Run the Phase 1 & Phase 2 Pytest Suite:
```bash
pytest -v
```

---

## 8. Limitations of Graph-Only Detection

1. **Cold Start Problem**: Newly registered accounts with zero transaction history lack graph edges and cannot be evaluated by graph topology alone until initial transactions occur.
2. **Threshold Dependency**: Deterministic rules require threshold tuning (e.g., minimum transactions on shared devices).
3. **Decentralized Rings**: Highly sophisticated fraudsters using clean dedicated devices per identity may evade projection links without deeper ML-based feature embedding (addressed in Phase 3 ML Risk Engine).
