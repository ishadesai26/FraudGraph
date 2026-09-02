"""FraudGraph Phase 4 Explainable AI & Fraud Investigation Intelligence."""

from backend.explainability.evidence_engine import EvidenceEngine
from backend.explainability.feature_explanations import FeatureExplainer
from backend.explainability.network_explanations import NetworkExplainer
from backend.explainability.report_generator import ReportGenerator
from backend.explainability.llm_explainer import LLMExplainer

# Safe import for InvestigationEngine
try:
    from backend.explainability.investigation_engine import InvestigationEngine
except ImportError:
    InvestigationEngine = None  # type: ignore

__all__ = [
    "EvidenceEngine",
    "FeatureExplainer",
    "NetworkExplainer",
    "InvestigationEngine",
    "ReportGenerator",
    "LLMExplainer",
]
