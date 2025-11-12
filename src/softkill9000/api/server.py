"""
FastAPI-based REST API for SOFTKILL-9000.

Provides HTTP endpoints for mission simulation, agent configuration,
and results retrieval.
"""

import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

from ..config.models import SimulationConfig, AgentConfig, MissionConfig
from ..simulator import MissionSimulator

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SOFTKILL-9000 API",
    description="Multi-Agent Cosmic Mission Simulator API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# In-memory storage for simulation results
simulation_results: Dict[str, Dict] = {}


class SimulationRequest(BaseModel):
    """Request model for starting a simulation."""
    config: Optional[SimulationConfig] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "agents": [
                        {
                            "role": "Longsight",
                            "species": "Vyr'khai",
                            "base_strength": 60,
                            "base_empathy": 60,
                            "base_intelligence": 60,
                            "base_mobility": 60,
                            "base_tactical": 60
                        }
                    ],
                    "mission": {
                        "num_timesteps": 60,
                        "ethics_enabled": True
                    }
                }
            }
        }


class SimulationResponse(BaseModel):
    """Response model for simulation status."""
    simulation_id: str
    status: str
    message: str
    created_at: str


class SimulationResult(BaseModel):
    """Model for complete simulation results."""
    simulation_id: str
    config: Dict
    scenario: Dict
    final_rewards: Dict[str, float]
    agent_stats: Dict[str, Dict[str, int]]
    mission_log: List[str]
    created_at: str
    completed_at: Optional[str] = None


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "SOFTKILL-9000 API",
        "version": "1.0.0",
        "description": "Multi-Agent Cosmic Mission Simulator",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/simulations", response_model=SimulationResponse)
async def create_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create and start a new simulation.
    
    The simulation runs in the background and results can be retrieved
    using the returned simulation_id.
    """
    try:
        # Generate unique simulation ID
        sim_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        logger.info(f"Creating simulation {sim_id}")
        
        # Initialize result entry
        simulation_results[sim_id] = {
            "status": "running",
            "created_at": created_at,
            "completed_at": None
        }
        
        # Start simulation in background
        background_tasks.add_task(
            run_simulation,
            sim_id,
            request.config
        )
        
        return SimulationResponse(
            simulation_id=sim_id,
            status="running",
            message="Simulation started successfully",
            created_at=created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/simulations/{simulation_id}")
async def get_simulation(simulation_id: str):
    """
    Retrieve simulation results by ID.
    
    Returns the current status and results (if completed).
    """
    if simulation_id not in simulation_results:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {simulation_id} not found"
        )
    
    result = simulation_results[simulation_id]
    return JSONResponse(content=result)


@app.get("/api/simulations")
async def list_simulations():
    """List all simulations with their status."""
    simulations = []
    for sim_id, result in simulation_results.items():
        simulations.append({
            "simulation_id": sim_id,
            "status": result.get("status"),
            "created_at": result.get("created_at"),
            "completed_at": result.get("completed_at")
        })
    
    return {"simulations": simulations, "total": len(simulations)}


@app.delete("/api/simulations/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete a simulation and its results."""
    if simulation_id not in simulation_results:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {simulation_id} not found"
        )
    
    del simulation_results[simulation_id]
    logger.info(f"Deleted simulation {simulation_id}")
    
    return {"message": f"Simulation {simulation_id} deleted successfully"}


@app.get("/api/config/species")
async def get_species():
    """Get available species and their modifiers."""
    from ..environments import SPECIES_MODIFIERS
    return {"species": SPECIES_MODIFIERS}


@app.get("/api/config/roles")
async def get_roles():
    """Get available agent roles and descriptions."""
    from ..environments import ROLE_DESCRIPTIONS
    return {"roles": ROLE_DESCRIPTIONS}


@app.get("/api/config/scenarios")
async def get_scenarios():
    """Get available scenario templates."""
    from ..environments import SCENARIOS, GALAXIES, TERRAINS, WEATHER_CONDITIONS
    return {
        "scenarios": SCENARIOS,
        "galaxies": GALAXIES,
        "terrains": TERRAINS,
        "weather_conditions": WEATHER_CONDITIONS
    }


async def run_simulation(simulation_id: str, config: Optional[SimulationConfig]):
    """
    Run a simulation (background task).
    
    Args:
        simulation_id: Unique simulation identifier
        config: Simulation configuration
    """
    try:
        logger.info(f"Running simulation {simulation_id}")
        
        # Create simulator
        simulator = MissionSimulator(config=config)
        
        # Run simulation
        results = simulator.run()
        
        # Store results
        simulation_results[simulation_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "config": config.model_dump() if config else {},
            "scenario": results.get("scenario", {}),
            "final_rewards": results.get("final_rewards", {}),
            "agent_stats": results.get("agent_stats", {}),
            "mission_log": results.get("mission_log", [])
        })
        
        logger.info(f"Simulation {simulation_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Simulation {simulation_id} failed: {e}")
        simulation_results[simulation_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
