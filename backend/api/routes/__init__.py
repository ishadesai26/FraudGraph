"""API route endpoints for FraudGraph Phase 5 and Phase 6."""

from backend.api.routes.health import router as health_router
from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.customers import router as customers_router
from backend.api.routes.transactions import router as transactions_router
from backend.api.routes.fraud_rings import router as fraud_rings_router
from backend.api.routes.investigation import router as investigation_router
from backend.api.routes.network import router as network_router
from backend.api.routes.agents import router as agents_router
from backend.api.routes.simulation import router as simulation_router

__all__ = [
    "health_router",
    "dashboard_router",
    "customers_router",
    "transactions_router",
    "fraud_rings_router",
    "investigation_router",
    "network_router",
    "agents_router",
    "simulation_router",
]
