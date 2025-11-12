"""
Agent module for SOFTKILL-9000.

Defines agent roles, capabilities, and decision-making logic for the multi-agent
cosmic mission simulator.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logging_utils import logger_decorator, LogContext

logger = logging.getLogger(__name__)

# Import numpy with fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False


class ActionType(Enum):
    """Available action types for agents."""
    ADVANCE = "advance"
    DEFEND = "defend"
    STABILISE = "stabilise"
    NEGOTIATE = "negotiate"
    WITHDRAW = "withdraw"


@dataclass
class AgentStats:
    """
    Statistical attributes for an agent.
    
    Attributes:
        strength: Physical and combat capability (0-110)
        empathy: Social awareness and cooperation ability (0-110)
        intelligence: Analytical and learning capacity (0-110)
        mobility: Movement speed and agility (0-110)
        tactical: Strategic planning and execution (0-110)
    """
    strength: int = 60
    empathy: int = 60
    intelligence: int = 60
    mobility: int = 60
    tactical: int = 60
    
    def __post_init__(self):
        """Validate stat ranges."""
        for attr in ['strength', 'empathy', 'intelligence', 'mobility', 'tactical']:
            value = getattr(self, attr)
            if not 0 <= value <= 110:
                raise ValueError(f"{attr} must be between 0 and 110, got {value}")
    
    def to_dict(self) -> Dict[str, int]:
        """Convert stats to dictionary."""
        return {
            'Strength': self.strength,
            'Empathy': self.empathy,
            'Intelligence': self.intelligence,
            'Mobility': self.mobility,
            'Tactical': self.tactical
        }
    
    def apply_species_modifiers(self, modifiers: Dict[str, int]) -> 'AgentStats':
        """
        Apply species-specific modifiers to stats.
        
        Args:
            modifiers: Dictionary of stat modifiers
            
        Returns:
            New AgentStats instance with modifiers applied
        """
        return AgentStats(
            strength=max(0, min(110, self.strength + modifiers.get('Strength', 0))),
            empathy=max(0, min(110, self.empathy + modifiers.get('Empathy', 0))),
            intelligence=max(0, min(110, self.intelligence + modifiers.get('Intelligence', 0))),
            mobility=max(0, min(110, self.mobility + modifiers.get('Mobility', 0))),
            tactical=max(0, min(110, self.tactical + modifiers.get('Tactical', 0)))
        )


@dataclass
class Agent:
    """
    Represents an agent in the mission simulator.
    
    Each agent has a role, species, capabilities, and can perform actions
    in the mission environment.
    
    Attributes:
        role: Agent's role (e.g., "Longsight", "Lifebinder")
        description: Role description
        species: Species type
        stats: Agent's statistical attributes
        position: Current position in mission space (x, y)
        trajectory: Historical positions during mission
        cumulative_reward: Total reward accumulated
    """
    role: str
    description: str
    species: str
    stats: AgentStats
    position: Tuple[float, float] = (0.5, 0.5)
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    cumulative_reward: float = 0.0
    
    def __post_init__(self):
        """Initialize trajectory with starting position."""
        if not self.trajectory:
            self.trajectory = [self.position]
        logger.debug(f"Agent created: {self.role} ({self.species})")
    
    @logger_decorator(log_entry=True, log_exit=True, log_time=True)
    def choose_action(
        self,
        scenario: str,
        terrain: str,
        weather: str,
        q_table: Optional[Any] = None,
        scenario_keys: Optional[List[str]] = None
    ) -> ActionType:
        """
        Choose an action based on scenario and agent capabilities.
        
        Args:
            scenario: Current scenario description
            terrain: Terrain type
            weather: Weather conditions
            q_table: Optional Q-learning table for RL-based decision
            scenario_keys: Keys for Q-table indexing
            
        Returns:
            Selected ActionType
        """
        logger.debug(f"{self.role} evaluating action for scenario: {scenario[:50]}...")
        
        # If agent has Q-learning capability (e.g., Longsight)
        if self.role == "Longsight" and q_table is not None and scenario_keys:
            action = self._q_learning_action(scenario, q_table, scenario_keys)
            logger.info(f"{self.role} chose Q-learned action: {action.value}")
            return action
        
        # Rule-based action selection for other roles
        action = self._rule_based_action(scenario)
        logger.info(f"{self.role} chose rule-based action: {action.value}")
        return action
    
    def _q_learning_action(
        self,
        scenario: str,
        q_table: Any,
        scenario_keys: List[str]
    ) -> ActionType:
        """Select action using Q-learning table."""
        scenario_lower = scenario.lower()
        state_idx = 0
        
        # Find matching scenario key
        for i, key in enumerate(scenario_keys):
            if key in scenario_lower:
                state_idx = i
                break
        
        # Get action with highest Q-value
        action_idx = int(np.argmax(q_table[state_idx]))
        actions = list(ActionType)
        return actions[action_idx]
    
    def _rule_based_action(self, scenario: str) -> ActionType:
        """Select action based on role-specific rules."""
        scenario_lower = scenario.lower()
        
        # Role-specific decision trees
        if self.role == "Lifebinder":
            if any(key in scenario_lower for key in ["ocean", "xenofauna", "magnetar"]):
                return ActionType.STABILISE
            return ActionType.DEFEND
        
        elif self.role == "Whisper":
            if any(key in scenario_lower for key in ["schism", "pirate"]):
                return ActionType.NEGOTIATE
            return ActionType.DEFEND
        
        elif self.role == "Specter":
            if "pirate" in scenario_lower:
                return ActionType.ADVANCE
            return ActionType.DEFEND
        
        elif self.role == "Archivist":
            if any(key in scenario_lower for key in ["schism", "pirate"]):
                return ActionType.NEGOTIATE
            return ActionType.DEFEND
        
        elif self.role == "Brawler":
            if any(key in scenario_lower for key in ["xenofauna", "pirate"]):
                return ActionType.ADVANCE
            return ActionType.DEFEND
        
        elif self.role == "Armsmaster":
            if any(key in scenario_lower for key in ["pirate", "magnetar"]):
                return ActionType.DEFEND
            return ActionType.ADVANCE
        
        elif self.role == "Explosives Expert":
            if "pirate" in scenario_lower:
                return ActionType.ADVANCE
            return ActionType.DEFEND
        
        # Default action
        return ActionType.DEFEND
    
    @logger_decorator(log_entry=True, log_exit=False)
    def update_position(self, delta_x: Optional[float] = None, delta_y: Optional[float] = None) -> None:
        """
        Update agent position in mission space.
        
        Args:
            delta_x: Change in x coordinate (random if None)
            delta_y: Change in y coordinate (random if None)
        """
        step_magnitude = (self.stats.mobility / 200.0) * 0.1
        
        if delta_x is None:
            if HAS_NUMPY and np is not None:
                delta_x = float(np.random.uniform(-step_magnitude, step_magnitude))
            else:
                import random
                delta_x = random.uniform(-step_magnitude, step_magnitude)
        if delta_y is None:
            if HAS_NUMPY and np is not None:
                delta_y = float(np.random.uniform(-step_magnitude, step_magnitude))
            else:
                import random
                delta_y = random.uniform(-step_magnitude, step_magnitude)
        
        x, y = self.position
        new_x = max(0.0, min(1.0, x + delta_x))
        new_y = max(0.0, min(1.0, y + delta_y))
        
        self.position = (new_x, new_y)
        self.trajectory.append(self.position)
        
        logger.debug(f"{self.role} moved to position: ({new_x:.3f}, {new_y:.3f})")
    
    def update_reward(self, reward: float) -> None:
        """
        Update cumulative reward.
        
        Args:
            reward: Reward value to add
        """
        self.cumulative_reward += reward
        logger.debug(f"{self.role} reward updated: +{reward:.2f}, total: {self.cumulative_reward:.2f}")
    
    def get_banter(self, banter_options: List[str]) -> str:
        """
        Get a random banter line for this agent.
        
        Args:
            banter_options: List of available banter lines
            
        Returns:
            Random banter string
        """
        import random
        return random.choice(banter_options)


class SquadManager:
    """
    Manages a squad of agents in a mission.
    
    Coordinates agent actions, tracks performance, and manages squad-level
    operations.
    """
    
    def __init__(self, agents: List[Agent]):
        """
        Initialize squad manager.
        
        Args:
            agents: List of Agent instances
        """
        self.agents = {agent.role: agent for agent in agents}
        logger.info(f"SquadManager initialized with {len(self.agents)} agents")
    
    @logger_decorator(log_entry=True, log_exit=True, log_time=True)
    def execute_timestep(
        self,
        scenario: str,
        terrain: str,
        weather: str,
        reward_calculator: Callable[..., float],
        q_table: Optional[Any] = None,
        scenario_keys: Optional[List[str]] = None,
        banter_dict: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute one timestep for all agents.
        
        Args:
            scenario: Current scenario
            terrain: Terrain type
            weather: Weather conditions
            reward_calculator: Function to calculate rewards
            q_table: Optional Q-learning table
            scenario_keys: Keys for Q-table
            banter_dict: Dictionary of banter options per role
            
        Returns:
            Dictionary of actions and rewards per agent
        """
        results = {}
        
        for role, agent in self.agents.items():
            # Choose action
            action = agent.choose_action(scenario, terrain, weather, q_table, scenario_keys)
            
            # Calculate reward
            reward = reward_calculator(
                role=role,
                action=action.value,
                scenario=scenario,
                terrain=terrain,
                weather=weather
            )
            
            # Apply strength modifier to reward
            reward *= (0.5 + agent.stats.strength / 200.0)
            
            # Update agent
            agent.update_reward(reward)
            agent.update_position()
            
            # Get banter
            banter = ""
            if banter_dict and role in banter_dict:
                banter = agent.get_banter(banter_dict[role])
            
            results[role] = {
                'action': action.value,
                'reward': reward,
                'banter': banter,
                'position': agent.position
            }
        
        return results
    
    def get_squad_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all agents in the squad."""
        return {role: agent.stats.to_dict() for role, agent in self.agents.items()}
    
    def get_cumulative_rewards(self) -> Dict[str, float]:
        """Get cumulative rewards for all agents."""
        return {role: agent.cumulative_reward for role, agent in self.agents.items()}
    
    def get_trajectories(self) -> Dict[str, List[Tuple[float, float]]]:
        """Get movement trajectories for all agents."""
        return {role: agent.trajectory for role, agent in self.agents.items()}
