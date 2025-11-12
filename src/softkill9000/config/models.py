"""
Configuration models for SOFTKILL-9000.

Pydantic models for validated configuration management.
"""

from typing import Dict, List, Optional
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    role: str = Field(..., description="Agent role (e.g., 'Longsight', 'Lifebinder')")
    species: str = Field(..., description="Species type")
    base_strength: int = Field(60, ge=0, le=110, description="Base strength attribute")
    base_empathy: int = Field(60, ge=0, le=110, description="Base empathy attribute")
    base_intelligence: int = Field(60, ge=0, le=110, description="Base intelligence attribute")
    base_mobility: int = Field(60, ge=0, le=110, description="Base mobility attribute")
    base_tactical: int = Field(60, ge=0, le=110, description="Base tactical attribute")


class MissionConfig(BaseModel):
    """Configuration for a mission simulation."""
    galaxy: Optional[str] = Field(None, description="Galaxy location (random if None)")
    planet: Optional[str] = Field(None, description="Planet designation (random if None)")
    terrain: Optional[str] = Field(None, description="Terrain type (random if None)")
    weather: Optional[str] = Field(None, description="Weather conditions (random if None)")
    scenario: Optional[str] = Field(None, description="Scenario description (random if None)")
    num_timesteps: int = Field(60, ge=10, le=500, description="Number of simulation timesteps")
    ethics_enabled: bool = Field(True, description="Enable ethics-aware reward shaping")
    

class QLearningConfig(BaseModel):
    """Configuration for Q-learning training."""
    episodes: int = Field(1000, ge=100, le=10000, description="Number of training episodes")
    gamma: float = Field(0.90, ge=0.0, le=1.0, description="Discount factor")
    alpha: float = Field(0.3, ge=0.0, le=1.0, description="Learning rate")
    epsilon: float = Field(0.2, ge=0.0, le=1.0, description="Exploration rate")


class SimulationConfig(BaseModel):
    """Complete configuration for a SOFTKILL-9000 simulation."""
    agents: List[AgentConfig] = Field(..., description="List of agent configurations")
    mission: MissionConfig = Field(default_factory=MissionConfig, description="Mission configuration")
    q_learning: QLearningConfig = Field(default_factory=QLearningConfig, description="Q-learning configuration")
    
    @field_validator('agents')
    @classmethod
    def validate_agents(cls, v):
        """Ensure at least one agent is configured."""
        if len(v) < 1:
            raise ValueError("At least one agent must be configured")
        return v
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
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
                },
                "q_learning": {
                    "episodes": 1000,
                    "gamma": 0.90,
                    "alpha": 0.3,
                    "epsilon": 0.2
                }
            }
        }


def load_config_from_yaml(path: str) -> SimulationConfig:
    """
    Load simulation configuration from a YAML file.
    
    Args:
        path: Path to YAML configuration file
        
    Returns:
        Validated SimulationConfig instance
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the YAML is malformed
        pydantic.ValidationError: If the config is invalid
    """
    config_path = Path(path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return SimulationConfig(**config_data)
