# FraudGraph Phase 5 REST API Documentation

The FraudGraph API provides real-time access to the graph intelligence engine, machine-learning risk scores, forensic investigation dossiers, and localized network topologies.

## Base URL
```
http://127.0.0.1:8000/api
```

Interactive OpenAPI Documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## 1. System Health

### `GET /api/health`
Returns service health status and API version.

#### Response `200 OK`
```json
{
  "status": "ok",
  "service": "FraudGraph",
  "version": "1.0.0"
}
```

---

## 2. Dashboard KPIs & Risk Distribution

### `GET /api/dashboard`
Returns platform-wide KPIs, risk distribution tiers, and high-risk entity highlights.

#### Response `200 OK`
```json
{
  "total_customers": 2000,
  "total_transactions": 10000,
  "total_fraud_rings": 26,
  "high_risk_customers_count": 25,
  "critical_customers_count": 14,
  "suspicious_transaction_volume": 47395724.81,
  "risk_distribution": {
    "LOW": 1940,
    "MEDIUM": 21,
    "HIGH": 25,
    "CRITICAL": 14
  },
  "top_detected_signals": [
    "shared_device_cluster",
    "shared_payment_instrument",
    "proxy_ip_routing",
    "temporal_burst_synchronization"
  ],
  "highest_risk_customer": {
    "entity_id": "CUST_00028",
    "risk_score": 99.1,
    "risk_level": "CRITICAL",
    "detail": "Associated with FR_015"
  },
  "highest_risk_ring": {
    "entity_id": "FR_017",
    "risk_score": 100.0,
    "risk_level": "CRITICAL",
    "detail": "161 members · ₹4,245,171.55"
  }
}
```

---

## 3. Customers

### `GET /api/customers`
Retrieves a paginated, filterable list of customers.

#### Query Parameters
- `page` *(int, default: 1)*: Page number ($\ge 1$).
- `page_size` *(int, default: 25, max: 100)*: Number of items per page.
- `risk_level` *(string, optional)*: Filter by tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `ring_id` *(string, optional)*: Filter by associated fraud ring ID (e.g. `FR_017`).
- `minimum_risk_score` *(float, optional)*: Minimum composite score ($0.0 - 100.0$).
- `search` *(string, optional)*: Search string matching customer ID, ring ID, or signal.

#### Response `200 OK`
```json
{
  "items": [
    {
      "customer_id": "CUST_00028",
      "name": "Customer CUST_00028",
      "risk_score": 99.1,
      "risk_level": "CRITICAL",
      "ring_id": "FR_015",
      "top_signal": "supervised_model_risk",
      "total_transactions": 15,
      "total_spend": 488216.93,
      "home_city": "Mumbai"
    }
  ],
  "page": 1,
  "page_size": 25,
  "total": 2000,
  "total_pages": 80
}
```

---

### `GET /api/customers/{customer_id}`
Retrieves complete forensic dossier, model evidence, graph links, timeline, and investigator action plan.

#### Response `200 OK`
```json
{
  "customer_id": "CUST_00028",
  "name": "Customer CUST_00028",
  "home_city": "Mumbai",
  "account_age_days": 185,
  "kyc_verified": true,
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
    }
  ],
  "protective_factors": [],
  "contributing_signals": [
    { "name": "supervised_model_probability", "value": 99.8, "importance": 0.5 },
    { "name": "network_risk_score", "value": 96.95, "importance": 0.25 },
    { "name": "unsupervised_anomaly_score", "value": 100.0, "importance": 0.25 }
  ],
  "shared_devices": [],
  "shared_payments": [],
  "connected_neighbors": [],
  "recommendations": [
    "Audit coordinated transaction flow within syndicate 'FR_015'.",
    "Initiate mandatory step-up identity verification challenge prior to fund release."
  ],
  "timeline": [
    {
      "transaction_id": "TXN_00142",
      "timestamp": "2024-03-12 14:22:10",
      "amount": 35000.0,
      "merchant_id": "MERCH_0012",
      "payment_type": "UPI",
      "device_id": "DEV_0023",
      "ip_id": "IP_0055",
      "city": "Mumbai",
      "seconds_since_previous": null,
      "is_burst": false,
      "tags": ["HIGH_VALUE"]
    }
  ]
}
```

---

## 4. Transactions

### `GET /api/transactions/{transaction_id}`
Retrieves transaction details, initiator context, and risk signals.

#### Response `200 OK`
```json
{
  "transaction_id": "TXN_00001",
  "customer_id": "CUST_00803",
  "merchant_id": "MERCH_0045",
  "amount": 2500.0,
  "timestamp": "2024-01-05 10:15:30",
  "payment_type": "CREDIT_CARD",
  "device_id": "DEV_0012",
  "ip_id": "IP_0089",
  "city": "Delhi",
  "is_flagged_fraud": false,
  "risk_score": 41.78,
  "risk_level": "MEDIUM",
  "explanation_confidence": "LOW"
}
```

---

## 5. Fraud Rings & Syndicates

### `GET /api/fraud-rings`
Retrieves detected syndicates.

#### Response `200 OK`
```json
{
  "items": [
    {
      "ring_id": "FR_017",
      "risk_score": 100.0,
      "risk_level": "CRITICAL",
      "customer_count": 161,
      "transaction_count": 750,
      "transaction_volume": 4245171.55,
      "shared_devices_count": 45,
      "shared_payments_count": 41,
      "shared_ips_count": 30,
      "top_signals": ["shared_devices(45)", "shared_payment_instruments(41)"]
    }
  ],
  "page": 1,
  "page_size": 25,
  "total": 26,
  "total_pages": 2
}
```

---

### `GET /api/fraud-rings/{ring_id}`
Retrieves syndicate members, shared infrastructure, evidence, and disruption actions.

#### Response `200 OK`
```json
{
  "ring_id": "FR_017",
  "risk_score": 100.0,
  "risk_level": "CRITICAL",
  "explanation_confidence": "HIGH",
  "customer_count": 161,
  "transaction_count": 750,
  "transaction_volume": 4245171.55,
  "shared_devices_count": 45,
  "shared_payments_count": 41,
  "shared_ips_count": 30,
  "merchant_targets_count": 100,
  "evidence": [
    {
      "source": "GRAPH_NETWORK",
      "signal": "syndicate_shared_devices",
      "severity": "HIGH",
      "description": "Syndicate shares 45 hardware devices across 161 member accounts."
    }
  ],
  "members": [
    {
      "customer_id": "CUST_00002",
      "individual_risk_score": 62.5,
      "network_risk_score": 100.0,
      "is_core_member": false
    }
  ],
  "recommendations": [
    "Audit 41 shared payment instruments across member accounts for synthetic identity collusion.",
    "Review session logs for 45 shared hardware devices for automated script or bot activity."
  ]
}
```

---

## 6. Network Graph Subgraphs

### `GET /api/network/{entity_type}/{entity_id}`
Extracts localized, interactive graph neighborhood formatted for Cytoscape.js.

- `entity_type`: `customer`, `ring`, or `transaction`.
- `entity_id`: Entity identifier (e.g. `CUST_00028`, `FR_017`, `TXN_00001`).

#### Response `200 OK`
```json
{
  "nodes": [
    {
      "data": {
        "id": "CUST_00028",
        "label": "CUST_00028",
        "type": "customer",
        "risk_score": 99.1,
        "risk_level": "CRITICAL",
        "subtext": "Primary Focus"
      }
    },
    {
      "data": {
        "id": "FR_015",
        "label": "FR_015",
        "type": "ring",
        "risk_score": 100.0,
        "risk_level": "CRITICAL",
        "subtext": "Syndicate"
      }
    }
  ],
  "edges": [
    {
      "data": {
        "id": "e_CUST_00028_FR_015",
        "source": "CUST_00028",
        "target": "FR_015",
        "type": "MEMBER_OF",
        "label": "MEMBER_OF"
      }
    }
  ],
  "center_node_id": "CUST_00028",
  "total_nodes": 2,
  "total_edges": 1
}
```

---

## 7. Error Handling

Standardized JSON error envelope:
```json
{
  "error": true,
  "status_code": 404,
  "message": "Customer 'CUST_99999' not found in registry."
}
```
- `400 Bad Request`: Invalid entity type or malformed query parameter.
- `404 Not Found`: Target entity ID not in repository.
- `500 Internal Server Error`: Internal exception safely masked.
