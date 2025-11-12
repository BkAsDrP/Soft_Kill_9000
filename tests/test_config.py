"""
Unit Tests for Configuration Module
====================================

Tests for Pydantic configuration models and validation.

Author: Rydlr Team
License: MIT
"""

import pytest
from pydantic import ValidationError

from softkill9000.config.models import (
    AgentConfig,
    MissionConfig,
    QLearningConfig,
    SimulationConfig,
    load_config_from_yaml,
)


class TestAgentConfig:
    """Test suite for AgentConfig model."""

    def test_agent_config_creation(self) -> None:
        """Test basic agent configuration."""
        config = AgentConfig(
            role="Longsight",
            species="Vyr'khai",
            base_strength=70,
            base_empathy=60,
            base_intelligence=65,
            base_mobility=75,
            base_tactical=80,
        )
        
        assert config.role == "Longsight"
        assert config.species == "Vyr'khai"
        assert config.base_strength == 70
        assert config.base_empathy == 60

    def test_agent_config_defaults(self) -> None:
        """Test agent configuration with defaults."""
        config = AgentConfig(role="Test", species="TestSpecies")
        
        assert 0 <= config.base_strength <= 110
        assert 0 <= config.base_empathy <= 110
        assert 0 <= config.base_intelligence <= 110
        assert 0 <= config.base_mobility <= 110
        assert 0 <= config.base_tactical <= 110

    def test_agent_config_validation_bounds(self) -> None:
        """Test that stats are bounded correctly."""
        # Should not raise for valid values
        config = AgentConfig(role="Test", species="Test", base_strength=50)
        assert config.base_strength == 50
        
        # Stats outside bounds should be rejected
        with pytest.raises(ValidationError):
            AgentConfig(role="Test", species="Test", base_strength=-10)
        
        with pytest.raises(ValidationError):
            AgentConfig(role="Test", species="Test", base_strength=150)


class TestMissionConfig:
    """Test suite for MissionConfig model."""

    def test_mission_config_creation(self) -> None:
        """Test mission configuration."""
        config = MissionConfig(
            num_timesteps=100,
            ethics_enabled=True,
        )
        
        assert config.num_timesteps == 100
        assert config.ethics_enabled is True

    def test_mission_config_defaults(self) -> None:
        """Test mission configuration defaults."""
        config = MissionConfig()
        
        assert config.num_timesteps == 60
        assert config.ethics_enabled is True

    def test_mission_config_validation(self) -> None:
        """Test mission configuration validation."""
        # Negative timesteps should fail
        with pytest.raises(ValidationError):
            MissionConfig(num_timesteps=-10)
        
        # Zero timesteps should fail
        with pytest.raises(ValidationError):
            MissionConfig(num_timesteps=0)


class TestQLearningConfig:
    """Test suite for QLearningConfig model."""

    def test_qlearning_config_creation(self) -> None:
        """Test Q-learning configuration."""
        config = QLearningConfig(
            episodes=500,
            gamma=0.95,
            alpha=0.25,
            epsilon=0.15,
        )
        
        assert config.episodes == 500
        assert config.gamma == 0.95
        assert config.alpha == 0.25
        assert config.epsilon == 0.15

    def test_qlearning_config_defaults(self) -> None:
        """Test Q-learning configuration defaults."""
        config = QLearningConfig()
        
        assert 100 <= config.episodes <= 10000
        assert 0.0 <= config.gamma <= 1.0
        assert 0.0 <= config.alpha <= 1.0
        assert 0.0 <= config.epsilon <= 1.0

    def test_qlearning_config_validation(self) -> None:
        """Test Q-learning configuration validation."""
        # Episodes out of bounds
        with pytest.raises(ValidationError):
            QLearningConfig(episodes=50)
        
        with pytest.raises(ValidationError):
            QLearningConfig(episodes=20000)
        
        # Gamma out of bounds
        with pytest.raises(ValidationError):
            QLearningConfig(gamma=1.5)
        
        # Epsilon out of bounds
        with pytest.raises(ValidationError):
            QLearningConfig(epsilon=2.0)


class TestSimulationConfig:
    """Test suite for SimulationConfig model."""

    def test_simulation_config_creation(self) -> None:
        """Test simulation configuration."""
        agents = [AgentConfig(role="Test", species="TestSpecies")]
        mission_config = MissionConfig(num_timesteps=50)
        qlearning_config = QLearningConfig(episodes=500)
        
        config = SimulationConfig(
            agents=agents,
            mission=mission_config,
            q_learning=qlearning_config,
        )
        
        assert config.mission.num_timesteps == 50
        assert config.q_learning.episodes == 500
        assert len(config.agents) == 1

    def test_simulation_config_with_agents(self) -> None:
        """Test simulation configuration with agent list."""
        agents = [
            AgentConfig(role="Longsight", species="Vyr'khai"),
            AgentConfig(role="Bruiser", species="Kragath"),
        ]
        
        config = SimulationConfig(agents=agents)
        
        assert len(config.agents) == 2
        assert config.agents[0].role == "Longsight"
        assert config.agents[1].role == "Bruiser"

    def test_simulation_config_requires_agents(self) -> None:
        """Test that at least one agent is required."""
        with pytest.raises(ValidationError):
            SimulationConfig(agents=[])


class TestConfigLoading:
    """Test suite for configuration file loading."""

    def test_load_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        yaml_content = """
agents:
  - role: "Longsight"
    species: "Vyr'khai"
    base_strength: 70
    base_empathy: 60
    base_intelligence: 65
    base_mobility: 75
    base_tactical: 80

mission:
  num_timesteps: 30
  ethics_enabled: true

q_learning:
  episodes: 1000
  gamma: 0.9
  alpha: 0.3
  epsilon: 0.2
"""
        yaml_file = tmp_path / "test_config.yaml"
        yaml_file.write_text(yaml_content)
        
        config = load_config_from_yaml(str(yaml_file))
        
        assert config.mission.num_timesteps == 30
        assert config.mission.ethics_enabled is True
        assert config.q_learning.gamma == 0.9
        assert config.q_learning.alpha == 0.3
        assert len(config.agents) == 1
        assert config.agents[0].role == "Longsight"

    def test_load_config_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config_from_yaml("/nonexistent/path/config.yaml")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
