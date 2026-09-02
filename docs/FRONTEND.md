# FraudGraph Phase 5 Frontend Documentation

## 1. Overview & UI Design Philosophy

The FraudGraph frontend is an **investigation console for fintech fraud analysts**.

- **Aesthetic**: Modern dark-mode forensic console (`#0B0F19` background) with high-density information display, glassmorphism cards, and vivid color-coded risk indicators.
- **Framework**: React 18 + Vite with React Router v6.
- **Graph Visualizer**: Cytoscape.js supporting multiple interactive layout topologies (Force Directed COSE, Concentric Radial, Breadthfirst Tree, Circle Ring).

---

## 2. Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── CytoscapeGraph.jsx      # Interactive network visualizer with custom styling
│   │   ├── EvidenceTable.jsx       # Layer 1 forensic evidence & model feature weights
│   │   ├── Navbar.jsx              # Header with omni-search & quick demo buttons
│   │   ├── RiskBadge.jsx           # Risk tier badges (LOW, MEDIUM, HIGH, CRITICAL)
│   │   ├── RiskMeter.jsx           # Circular SVG 0-100 risk score gauge
│   │   ├── Sidebar.jsx             # Left navigation & pipeline health monitor
│   │   ├── StatCard.jsx            # KPI metric cards with icons & trends
│   │   └── TimelineView.jsx        # Chronological transaction flow with burst tags
│   │
│   ├── pages/
│   │   ├── DashboardPage.jsx       # Platform overview, KPIs, and critical alerts
│   │   ├── CustomersPage.jsx       # Filterable & searchable 2,000-customer registry
│   │   ├── CustomerDetailPage.jsx  # Full forensic investigation console
│   │   ├── FraudRingsPage.jsx      # Syndicate directory and scale metrics
│   │   ├── FraudRingDetailPage.jsx # Syndicate graph topology & member rosters
│   │   └── TransactionDetailPage.jsx # Single transaction forensic inspection
│   │
│   ├── services/
│   │   └── api.js                  # Centralized fetch client with normalized errors
│   │
│   ├── App.jsx                     # Application router and layout wrapper
│   ├── index.css                   # Custom fintech dark theme & glass utility styles
│   └── main.jsx                    # React entrypoint
│
├── index.html                      # HTML template with Plus Jakarta Sans typography
├── package.json                    # Dependencies & build scripts
└── vite.config.js                  # Vite server & backend API proxy configuration
```

---

## 3. Key Investigation Views

### 3.1 Investigation Dashboard (`/`)
- Platform KPI cards: Monitored Customers, High/Critical Accounts, Detected Rings, Suspicious Volume.
- Entity Risk Distribution bars (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Highest-Risk Customer (`CUST_00028` - 99.1 Score) & Syndicate Ring (`FR_017` - 100.0 Score) quick callouts.
- High-Risk Accounts quick table with instant row-click investigation.

### 3.2 Customer Investigation Console (`/customers/:customerId`)
- Comprehensive header with Name, Customer ID, City, Account Age, KYC status, and Explanation Confidence.
- Circular animated 0–100 Risk Meter with tier badge.
- **Why Flagged?** Structured Layer 1 evidence table with signal names, values, and percentage weights.
- **Interactive Cytoscape Network Visualizer**: Local 1–2 hop neighborhood showing connected accounts, shared devices, shared payment cards, and fraud ring associations.
- **Shared Infrastructure Modules**: Hardware endpoints and card/VPA sharing rosters.
- **Chronological Transaction Timeline**: With **`BURST SYNC`** tags for events executed $\le 180\text{s}$ apart.
- **Investigator Action Plan**: Step-by-step neutral recommendations.
- **Deterministic Report Artifact**: Full markdown dossier viewer.

### 3.3 Syndicate Ring Investigation (`/fraud-rings/:ringId`)
- Syndicate scale and total rupee volume.
- Interactive syndicate network graph canvas.
- Syndicate member roster highlighting Core Organizers vs regular accounts with individual risk scores.
- Syndicate Disruption Action Plan.

---

## 4. Cytoscape Network Graph Node Styling

| Entity Type | Node Shape | Default Color | Highlight Rule |
| :--- | :--- | :--- | :--- |
| **Customer** | Ellipse | Cyan (`#06B6D4`) | Crimson for Critical, Orange for High |
| **Device** | Rectangle | Blue (`#3B82F6`) | Standard |
| **IP Address** | Diamond | Purple (`#A855F7`) | Standard |
| **Payment Card / VPA** | Round Rectangle | Amber (`#F59E0B`) | Standard |
| **Merchant** | Vee | Pink (`#EC4899`) | Standard |
| **Fraud Ring Syndicate** | Hexagon | Crimson (`#EF4444`) | Core focus node |

---

## 5. Development & Build Commands

### Install Dependencies
```bash
cd frontend
npm install
```

### Start Development Server
```bash
npm run dev
```
Runs Vite dev server at `http://localhost:5173`. Requests to `/api/*` are proxied to `http://127.0.0.1:8000`.

### Build for Production
```bash
npm run build
```
Outputs optimized production bundle in `frontend/dist/`.
