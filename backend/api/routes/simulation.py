"""FastAPI routes for Real-Time Transaction Simulation."""

from typing import List
from fastapi import APIRouter
from backend.agents.schemas import SimulationScenario, SimulationRequest, SimulationResponse
from backend.simulation.scenarios import SCENARIOS
from backend.simulation.risk_simulator import RiskSimulator

router = APIRouter(prefix="/api/simulation", tags=["Real-Time Simulation"])
simulator = RiskSimulator()


@router.get("/scenarios", response_model=List[SimulationScenario])
def list_simulation_scenarios():
    """Returns the list of available controlled demo scenarios."""
    return SCENARIOS


@router.post("/analyze", response_model=SimulationResponse)
def analyze_simulated_transaction(request: SimulationRequest):
    """Evaluates a simulated transaction through the live risk pipeline and 6-agent investigation."""
    response = simulator.simulate_and_investigate(
        transaction=request.transaction,
        scenario_id=request.scenario_id,
    )
    return response
