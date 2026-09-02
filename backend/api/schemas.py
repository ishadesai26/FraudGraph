"""Pydantic data schemas for FraudGraph Phase 5 REST API."""

from typing import Dict, List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "ok"
    service: str = "FraudGraph"
    version: str = "1.0.0"


class RiskDistribution(BaseModel):
    """Count of entities across risk tiers."""
    LOW: int = 0
    MEDIUM: int = 0
    HIGH: int = 0
    CRITICAL: int = 0


class KeyEntitySummary(BaseModel):
    """Summary of highest-risk entity."""
    entity_id: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    detail: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    """High-level metrics and risk distribution for the main investigation dashboard."""
    total_customers: int
    total_transactions: int
    total_fraud_rings: int
    high_risk_customers_count: int
    critical_customers_count: int
    suspicious_transaction_volume: float
    risk_distribution: RiskDistribution
    top_detected_signals: List[str]
    highest_risk_customer: KeyEntitySummary
    highest_risk_ring: KeyEntitySummary


class CustomerSummary(BaseModel):
    """Lightweight customer item for tables and search results."""
    customer_id: str
    name: Optional[str] = None
    risk_score: float
    risk_level: str
    ring_id: Optional[str] = None
    top_signal: str
    total_transactions: int = 0
    total_spend: float = 0.0
    home_city: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated container."""
    items: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int


class EvidenceItem(BaseModel):
    """Individual forensic evidence signal."""
    source: Optional[str] = None
    signal: str
    severity: str
    description: str
    value: Optional[Any] = None
    importance: Optional[float] = None


class ContributingSignal(BaseModel):
    """Quantitative contribution of model/graph feature."""
    name: str
    value: float
    importance: float


class ProtectiveFactor(BaseModel):
    """Mitigating signal reducing estimated risk."""
    signal: str
    description: str


class SharedResource(BaseModel):
    """Shared hardware device or payment instrument."""
    resource_id: str
    resource_type: str
    shared_with_count: int
    connected_customers: List[str]


class ConnectedNeighbor(BaseModel):
    """Connected customer account in graph."""
    customer_id: str
    relational_weight: Optional[float] = 1.0


class TimelineEvent(BaseModel):
    """Single chronological transaction event."""
    transaction_id: str
    timestamp: str
    amount: float
    merchant_id: str
    payment_type: str
    device_id: str
    ip_id: str
    city: str
    seconds_since_previous: Optional[float] = None
    is_burst: bool = False
    tags: List[str] = []


class CustomerDetailResponse(BaseModel):
    """Comprehensive forensic investigation dossier for a customer."""
    customer_id: str
    name: Optional[str] = None
    home_city: Optional[str] = None
    account_age_days: Optional[int] = None
    kyc_verified: Optional[bool] = None
    risk_score: float
    risk_level: str
    explanation_confidence: str
    associated_ring_id: Optional[str] = None
    member_role: Optional[str] = None
    total_transactions: int
    total_spend: float
    evidence: List[EvidenceItem]
    protective_factors: List[ProtectiveFactor] = []
    contributing_signals: List[ContributingSignal] = []
    shared_devices: List[SharedResource] = []
    shared_payments: List[SharedResource] = []
    connected_neighbors: List[ConnectedNeighbor] = []
    recommendations: List[str] = []
    timeline: List[TimelineEvent] = []
    investigation_report_markdown: Optional[str] = None


class TransactionDetailResponse(BaseModel):
    """Forensic investigation dossier for a specific transaction."""
    transaction_id: str
    customer_id: str
    merchant_id: str
    amount: float
    timestamp: str
    payment_type: str
    device_id: str
    ip_id: str
    city: str
    is_flagged_fraud: Optional[bool] = None
    risk_score: float
    risk_level: str
    explanation_confidence: str
    associated_ring_id: Optional[str] = None
    evidence: List[EvidenceItem] = []
    protective_factors: List[ProtectiveFactor] = []
    contributing_signals: List[ContributingSignal] = []
    recommendations: List[str] = []
    timeline: List[TimelineEvent] = []


class RingMemberSummary(BaseModel):
    """Member account within a fraud ring syndicate."""
    customer_id: str
    individual_risk_score: float
    network_risk_score: float
    is_core_member: bool


class FraudRingSummary(BaseModel):
    """Syndicate card summary item."""
    ring_id: str
    risk_score: float
    risk_level: str
    customer_count: int
    transaction_count: int
    transaction_volume: float
    shared_devices_count: int
    shared_payments_count: int
    shared_ips_count: int
    top_signals: List[str] = []


class FraudRingDetailResponse(BaseModel):
    """Comprehensive syndicate investigation dossier."""
    ring_id: str
    risk_score: float
    risk_level: str
    explanation_confidence: str
    customer_count: int
    transaction_count: int
    transaction_volume: float
    shared_devices_count: int
    shared_payments_count: int
    shared_ips_count: int
    merchant_targets_count: int
    evidence: List[EvidenceItem] = []
    members: List[RingMemberSummary] = []
    recommendations: List[str] = []
    investigation_report_markdown: Optional[str] = None


# Cytoscape Graph Schemas
class NetworkNodeData(BaseModel):
    id: str
    label: str
    type: str  # customer, device, ip, payment_method, merchant, ring
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    subtext: Optional[str] = None


class NetworkNode(BaseModel):
    data: NetworkNodeData


class NetworkEdgeData(BaseModel):
    id: str
    source: str
    target: str
    type: str  # USED_DEVICE, USED_IP, USED_PAYMENT, TRANSACTED_AT, CONNECTED_TO, MEMBER_OF
    label: Optional[str] = None
    weight: Optional[float] = None


class NetworkEdge(BaseModel):
    data: NetworkEdgeData


class NetworkGraphResponse(BaseModel):
    """Cytoscape.js compatible graph payload."""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    center_node_id: Optional[str] = None
    total_nodes: int
    total_edges: int
