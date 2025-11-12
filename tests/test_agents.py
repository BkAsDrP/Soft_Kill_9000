"""Tests for agent module."""

import pytest
from softkill9000.agents import Agent, AgentStats, ActionType, SquadManager
from softkill9000.environments import SPECIES_MODIFIERS, ROLE_DESCRIPTIONS


class TestAgentStats:
    """Test AgentStats class."""
    
    def test_creation(self):
        """Test creating agent stats."""
        stats = AgentStats(
            strength=70,
            empathy=60,
            intelligence=65,
            mobility=55,
            tactical=80
        )
        assert stats.strength == 70
        assert stats.empathy == 60
    
    def test_validation(self):
        """Test stat validation."""
        with pytest.raises(ValueError):
            AgentStats(strength=150)  # Over max
        
        with pytest.raises(ValueError):
            AgentStats(strength=-10)  # Under min
    
    def test_to_dict(self):
        """Test converting stats to dict."""
        stats = AgentStats()
        result = stats.to_dict()
        assert isinstance(result, dict)
        assert 'Strength' in result
        assert 'Empathy' in result
    
    def test_apply_modifiers(self):
        """Test applying species modifiers."""
        stats = AgentStats(strength=60)
        modified = stats.apply_species_modifiers({"Strength": +10})
        assert modified.strength == 70
        assert stats.strength == 60  # Original unchanged


class TestAgent:
    """Test Agent class."""
    
    def test_creation(self):
        """Test creating an agent."""
        stats = AgentStats()
        agent = Agent(
            role="Longsight",
            description="Test marksman",
            species="Vyr'khai",
            stats=stats
        )
        assert agent.role == "Longsight"
        assert agent.species == "Vyr'khai"
        assert len(agent.trajectory) == 1  # Initial position
    
    def test_rule_based_action(self):
        """Test rule-based action selection."""
        stats = AgentStats()
        agent = Agent(
            role="Lifebinder",
            description="Test medic",
            species="Lumenari",
            stats=stats
        )
        
        # Lifebinder should stabilize in ocean scenario
        action = agent.choose_action(
            scenario="Planetary ocean rising",
            terrain="Oceanic Platforms",
            weather="Clear"
        )
        assert action == ActionType.STABILISE
    
    def test_update_position(self):
        """Test position updates."""
        stats = AgentStats(mobility=80)
        agent = Agent(
            role="Specter",
            description="Test recon",
            species="Zephryl",
            stats=stats
        )
        
        initial_pos = agent.position
        agent.update_position(delta_x=0.1, delta_y=0.1)
        
        assert agent.position != initial_pos
        assert len(agent.trajectory) == 2
    
    def test_update_reward(self):
        """Test reward updates."""
        stats = AgentStats()
        agent = Agent(
            role="Whisper",
            description="Test diplomat",
            species="Mycelian",
            stats=stats
        )
        
        assert agent.cumulative_reward == 0.0
        agent.update_reward(10.5)
        assert agent.cumulative_reward == 10.5
        agent.update_reward(-2.5)
        assert agent.cumulative_reward == 8.0


class TestSquadManager:
    """Test SquadManager class."""
    
    def test_creation(self):
        """Test creating a squad manager."""
        agents = [
            Agent(
                role="Longsight",
                description="Marksman",
                species="Vyr'khai",
                stats=AgentStats()
            ),
            Agent(
                role="Lifebinder",
                description="Medic",
                species="Lumenari",
                stats=AgentStats()
            )
        ]
        
        squad = SquadManager(agents)
        assert len(squad.agents) == 2
        assert "Longsight" in squad.agents
        assert "Lifebinder" in squad.agents
    
    def test_get_squad_stats(self):
        """Test getting squad statistics."""
        agents = [
            Agent(
                role="Brawler",
                description="Combat specialist",
                species="Aetherborn",
                stats=AgentStats(strength=80)
            )
        ]
        
        squad = SquadManager(agents)
        stats = squad.get_squad_stats()
        
        assert "Brawler" in stats
        assert stats["Brawler"]["Strength"] == 80
    
    def test_get_cumulative_rewards(self):
        """Test getting cumulative rewards."""
        agent = Agent(
            role="Archivist",
            description="Knowledge keeper",
            species="Ferroth",
            stats=AgentStats()
        )
        agent.update_reward(15.0)
        
        squad = SquadManager([agent])
        rewards = squad.get_cumulative_rewards()
        
        assert "Archivist" in rewards
        assert rewards["Archivist"] == 15.0
