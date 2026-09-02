"""Pydantic v2 schemas for FraudGraph Phase 6 Agentic Investigation & Simulation."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AgentEvidenceItem(BaseModel):
    """Structured evidence item with strict agent provenance."""
    signal: str
    source_agent: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    value: Optional[Any] = None
    importance: Optional[float] = None
    description: str
    category: str = "GENERAL"  # ML_MODEL, GRAPH_TOPOLOGY, BEHAVIORAL_HISTORY, PROTECTIVE


class AgentTraceStep(BaseModel):
    """Execution step trace for an individual specialized agent."""
    agent_name: str
    status: str = "completed"  # completed, skipped, failed
    duration_ms: float = 0.0
    signals_found: int = 0
    summary: str = ""


class ConflictItem(BaseModel):
    """Explicit cross-agent disagreement or tension."""
    type: str
    description: str
    supporting_signals: List[str] = []
    opposing_signals: List[str] = []


class EvidenceGraphNode(BaseModel):
    """Node in the structured multi-agent evidence graph."""
    id: str
    label: str
    type: str  # entity, signal, transaction, customer, device, ip, payment_method, merchant, fraud_ring
    subtext: Optional[str] = None
    severity: Optional[str] = None


class EvidenceGraphEdge(BaseModel):
    """Edge in the structured multi-agent evidence graph."""
    id: str
    source: str
    target: str
    type: str  # SUPPORTED_BY, CONNECTED_TO, PART_OF, OBSERVED_IN, CONTRIBUTES_TO
    label: Optional[str] = None


class EvidenceGraph(BaseModel):
    """Structured network representing multi-agent evidence linkages."""
    nodes: List[EvidenceGraphNode] = []
    edges: List[EvidenceGraphEdge] = []


class DecisionResult(BaseModel):
    """Final investigation disposition from DecisionAgent."""
    status: str  # LOW_RISK, REVIEW, ENHANCED_REVIEW, HIGH_RISK
    risk_score: float  # 0.0 to 100.0
    confidence: str  # LOW, MEDIUM, HIGH
    evidence_coverage: float  # 0.0 to 100.0 (Completeness of data, NOT fraud prob)
    reasoning: str
    recommended_action: str
    recommended_actions: List[str] = []


class AgentInvestigationRequest(BaseModel):
    """Request payload to trigger multi-agent investigation."""
    entity_type: str = "customer"  # customer, transaction, ring
    entity_id: str


class AgentInvestigationResult(BaseModel):
    """Complete multi-agent collaborative investigation report."""
    investigation_id: str
    timestamp: str
    entity_type: str
    entity_id: str
    risk_score: float
    risk_level: str
    decision: DecisionResult
    key_findings: List[str] = []
    evidence_items: List[AgentEvidenceItem] = []
    conflicts: List[ConflictItem] = []
    entities_to_review: List[Dict[str, Any]] = []
    network_context: Dict[str, Any] = {}
    behavior_context: Dict[str, Any] = {}
    evidence_graph: Optional[EvidenceGraph] = None
    agent_trace: List[AgentTraceStep] = []
    narrative_summary: Optional[str] = None


class SimulationScenario(BaseModel):
    """Scenario metadata for demo transaction simulation."""
    scenario_id: str
    title: str
    description: str
    expected_risk_tier: str
    sample_payload: Dict[str, Any]


class SimulationRequest(BaseModel):
    """Request to score and investigate a simulated transaction in real-time."""
    scenario_id: Optional[str] = None
    transaction: Dict[str, Any]


class SimulationResponse(BaseModel):
    """Live transaction simulation response with real pipeline scoring and agent verdicts."""
    simulation_id: str
    scenario_id: Optional[str] = None
    transaction: Dict[str, Any]
    risk: Dict[str, Any]
    evidence: Dict[str, Any]
    investigation: AgentInvestigationResult
    agent_trace: List[AgentTraceStep]
    decision: DecisionResult
