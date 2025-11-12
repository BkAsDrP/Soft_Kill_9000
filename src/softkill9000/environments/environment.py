"""
Environment module for SOFTKILL-9000.

Defines mission environments, scenarios, reward systems, and Q-learning implementation.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random

from ..utils.logging_utils import logger_decorator, LogContext

logger = logging.getLogger(__name__)


# ==================== COSMIC DATA ====================

SPECIES_MODIFIERS = {
    "Vyr'khai": {"Strength": +6, "Empathy": -2, "Intelligence": +0, "Mobility": +4, "Tactical": +5},
    "Lumenari": {"Strength": +1, "Empathy": +8, "Intelligence": +4, "Mobility": +1, "Tactical": +1},
    "Zephryl": {"Strength": +1, "Empathy": +1, "Intelligence": +3, "Mobility": +8, "Tactical": +3},
    "Mycelian": {"Strength": -1, "Empathy": +6, "Intelligence": +6, "Mobility": -1, "Tactical": +2},
    "Ferroth": {"Strength": +8, "Empathy": -3, "Intelligence": +2, "Mobility": -2, "Tactical": +4},
    "Aetherborn": {"Strength": +9, "Empathy": +2, "Intelligence": +8, "Mobility": +7, "Tactical": +4},
    "Kinetari": {"Strength": +5, "Empathy": +1, "Intelligence": +4, "Mobility": +7, "Tactical": +5},
    "Verdan": {"Strength": +3, "Empathy": +2, "Intelligence": +5, "Mobility": +1, "Tactical": +7},
}

ROLE_DESCRIPTIONS = {
    "Longsight": "Marksman from the Vyr'khai star-clans",
    "Lifebinder": "Medic-priest of the Lumenari bioconclave",
    "Specter": "Recon shade of the Zephryl drift",
    "Whisper": "Diplomat-chorus from the Mycelian hegemony",
    "Archivist": "Sentient archive node of the Ferroth lattice",
    "Brawler": "Hand-to-hand combat specialist",
    "Armsmaster": "Weapons specialist",
    "Explosives Expert": "Specialist in demolition and ordnance",
}

GALAXIES = [
    "Andromeda (M31)", "Triangulum (M33)", "Sombrero (M104)", "Whirlpool (M51)",
    "Sagittarius Dwarf", "Large Magellanic Cloud", "Nyx Halo", "Aetheric Veil",
    "Kijani Spiral", "Umbral Reef", "Karibu Vortex", "Centaurus A", "Messier 81",
    "Sculptor Galaxy", "Fornax Cluster", "Perseus Cluster", "Coma Cluster"
]

TERRAINS = [
    "Urban Lattice", "Desert Glass", "Ice Ridge", "Oceanic Platforms",
    "Jungle Canopy", "Volcanic Spires", "Acidic Swamps", "Crystal Caves",
    "Floating Islands"
]

WEATHER_CONDITIONS = [
    "Clear", "Ion Storm", "Radiation Flare", "Sandstorm", "Cryo Blizzards",
    "Plasma Rain", "Gravity Eddies", "Sonic Winds", "Magnetic Anomalies"
]

SCENARIOS = [
    "Refugee flotilla near a magnetar; containment fields failing.",
    "Xenofauna stampede through crystalline corridors; civilians trapped.",
    "Pirate corsairs blockading stargate; reactor leaks destabilising transit.",
    "Planetary ocean rising after moon-shear; bio-domes at risk.",
    "Clan schism; peace-talks collapsing on neutral ring-station."
]

BANTER = {
    "Longsight": [
        "Vacuum steady. Pulse steadier.",
        "Line held. Regrets pending.",
        "One pulse—one ending—preferably not ours."
    ],
    "Lifebinder": [
        "Biofield humming. Statistics declining.",
        "If it bleeds, I can stabilise it.",
        "Life prefers cooperation; let's oblige."
    ],
    "Specter": [
        "Ghost-walk engaged. Doors where walls used to be.",
        "Paths mapped. Shadows compliant.",
        "Seen and unseen are tactical categories."
    ],
    "Whisper": [
        "Words first, wounds last.",
        "Lower the heat; raise the harmony.",
        "Consent acquired. Conflict retired."
    ],
    "Archivist": [
        "Recording. Remembering. History has teeth.",
        "Truth cached. Lies quarantined.",
        "Ethics subroutines purring. Do better."
    ],
    "Brawler": [
        "Close quarters. Good.",
        "My hands are registered weapons.",
        "Less talk, more impact."
    ],
    "Armsmaster": [
        "Ordnance prepped.",
        "Picking the right tool for the job.",
        "Let the weapon do the talking."
    ],
    "Explosives Expert": [
        "Charge set. Stand clear.",
        "Demolitions are a delicate art.",
        "Making exits where there weren't any."
    ],
}

# Syllables for procedural planet name generation
PLANET_SYLLABLES = [
    "ka", "ru", "sha", "vel", "dra", "tor", "my", "cel", "lum", "vyr",
    "fer", "ze", "phy", "ae", "ki", "ja", "ni", "um", "bral", "xon",
    "lyr", "qel", "zix", "vok", "nar", "pyl", "cre", "dax", "jyn"
]


# ==================== REWARD SYSTEM ====================

BASE_REWARDS = {
    "Longsight": {"advance": 8, "defend": 6, "stabilise": -3, "negotiate": -4, "withdraw": -1},
    "Lifebinder": {"advance": -1, "defend": 3, "stabilise": 10, "negotiate": 1, "withdraw": 2},
    "Specter": {"advance": 7, "defend": 3, "stabilise": -1, "negotiate": 0, "withdraw": 4},
    "Whisper": {"advance": -2, "defend": 1, "stabilise": 1, "negotiate": 10, "withdraw": 3},
    "Archivist": {"advance": 0, "defend": 2, "stabilise": 2, "negotiate": 6, "withdraw": 3},
    "Brawler": {"advance": 7, "defend": 5, "stabilise": -2, "negotiate": -3, "withdraw": 2},
    "Armsmaster": {"advance": 6, "defend": 7, "stabilise": -1, "negotiate": -2, "withdraw": 3},
    "Explosives Expert": {"advance": 5, "defend": 4, "stabilise": -4, "negotiate": -3, "withdraw": 1},
}

SCENARIO_MODIFIERS = {
    "magnetar": {"withdraw": +2, "defend": +1},
    "xenofauna": {"stabilise": +3, "defend": +2},
    "pirate": {"advance": +2, "defend": +1, "negotiate": +1},
    "ocean": {"stabilise": +2, "withdraw": +1},
    "schism": {"negotiate": +4, "defend": +1},
}

TERRAIN_MODIFIERS = {
    "Urban Lattice": {"defend": +1, "negotiate": +1},
    "Desert Glass": {"withdraw": +1, "advance": -1},
    "Ice Ridge": {"defend": +1, "stabilise": +1},
    "Oceanic Platforms": {"stabilise": +2, "withdraw": +1},
    "Jungle Canopy": {"advance": +1, "defend": 0},
    "Volcanic Spires": {"Strength": +2, "defend": +1},
    "Acidic Swamps": {"Mobility": +1, "withdraw": +2},
    "Crystal Caves": {"Intelligence": +1, "Tactical": +2},
    "Floating Islands": {"Mobility": +2, "stabilise": +1},
}

WEATHER_MODIFIERS = {
    "Clear": {},
    "Ion Storm": {"withdraw": +2, "defend": +1},
    "Radiation Flare": {"withdraw": +2, "stabilise": +1},
    "Sandstorm": {"withdraw": +1, "defend": +1},
    "Cryo Blizzards": {"defend": +1, "stabilise": +1},
    "Plasma Rain": {"Strength": +1, "defend": +2},
    "Gravity Eddies": {"Mobility": +2, "stabilise": +1},
    "Sonic Winds": {"Intelligence": +1, "Tactical": +2},
    "Magnetic Anomalies": {"Strength": +1, "withdraw": +2},
}

ETHICS_MODIFIERS = {
    "save_civilian": +8,
    "collateral": -8,
    "document": +3,
    "deescalate": +5
}


def generate_planet_name() -> str:
    """
    Generate a procedural planet name from syllables.
    
    Returns:
        A capitalized planet name with 2-4 syllables
    """
    num_syllables = random.randint(2, 4)
    name = "".join(random.choice(PLANET_SYLLABLES) for _ in range(num_syllables))
    return name.title()


@dataclass
class CosmicScenario:
    """
    Represents a cosmic mission scenario.
    
    Attributes:
        galaxy: Galaxy location
        planet: Planet designation
        terrain: Terrain type
        weather: Weather conditions
        scenario: Narrative scenario description
    """
    galaxy: str
    planet: str
    terrain: str
    weather: str
    scenario: str
    
    @classmethod
    def generate_random(cls) -> 'CosmicScenario':
        """Generate a random cosmic scenario."""
        return cls(
            galaxy=random.choice(GALAXIES),
            planet=f"{generate_planet_name()}-{random.randint(1, 999)}",
            terrain=random.choice(TERRAINS),
            weather=random.choice(WEATHER_CONDITIONS),
            scenario=random.choice(SCENARIOS)
        )
    
    def __str__(self) -> str:
        """String representation of the scenario."""
        return (
            f"MISSION: {self.galaxy} // Planet {self.planet}\n"
            f"Terrain: {self.terrain} // Weather: {self.weather}\n"
            f"Scenario: {self.scenario}"
        )


class RewardCalculator:
    """Calculates rewards for agent actions in various contexts."""
    
    def __init__(self, ethics_enabled: bool = True):
        """
        Initialize reward calculator.
        
        Args:
            ethics_enabled: Whether to include ethics-based reward modifiers
        """
        self.ethics_enabled = ethics_enabled
        logger.info(f"RewardCalculator initialized (ethics={'ON' if ethics_enabled else 'OFF'})")
    
    @logger_decorator(log_entry=False, log_exit=False)
    def calculate(
        self,
        role: str,
        action: str,
        scenario: str,
        terrain: str,
        weather: str
    ) -> float:
        """
        Calculate reward for an agent action.
        
        Args:
            role: Agent role
            action: Action taken
            scenario: Current scenario
            terrain: Terrain type
            weather: Weather conditions
            
        Returns:
            Calculated reward value
        """
        # Base reward
        reward = BASE_REWARDS.get(role, {}).get(action, 0)
        
        # Scenario modifiers
        scenario_key = self._infer_scenario_key(scenario)
        reward += SCENARIO_MODIFIERS.get(scenario_key, {}).get(action, 0)
        
        # Terrain modifiers
        reward += TERRAIN_MODIFIERS.get(terrain, {}).get(action, 0)
        
        # Weather modifiers
        reward += WEATHER_MODIFIERS.get(weather, {}).get(action, 0)
        
        # Ethics bonus
        if self.ethics_enabled:
            ethics_bonus = self._calculate_ethics_bonus(role, action, scenario_key)
            reward += ethics_bonus
        
        # Add noise for realism
        noise = np.random.uniform(-1.5, 1.5)
        reward += noise
        
        return reward
    
    def _infer_scenario_key(self, scenario: str) -> str:
        """Infer scenario key from scenario description."""
        scenario_lower = scenario.lower()
        for key in SCENARIO_MODIFIERS.keys():
            if key in scenario_lower:
                return key
        return ""
    
    def _calculate_ethics_bonus(self, role: str, action: str, scenario_key: str) -> float:
        """Calculate ethics-based reward bonus."""
        bonus = 0.0
        
        # Scenario-specific ethics
        if scenario_key == "magnetar" and action in ["withdraw", "defend"]:
            bonus += ETHICS_MODIFIERS["save_civilian"]
        if scenario_key == "xenofauna" and action == "stabilise":
            bonus += ETHICS_MODIFIERS["save_civilian"]
        if scenario_key == "pirate" and action in ["negotiate", "defend"]:
            bonus += ETHICS_MODIFIERS["deescalate"]
        if scenario_key == "ocean" and action in ["stabilise", "advance"]:
            bonus += ETHICS_MODIFIERS["save_civilian"]
        if scenario_key == "schism" and action == "negotiate":
            bonus += ETHICS_MODIFIERS["deescalate"]
        
        # Role-specific ethics
        if role == "Archivist" and action in ["defend", "negotiate"]:
            bonus += ETHICS_MODIFIERS["document"]
        if role == "Brawler" and action == "defend":
            bonus += ETHICS_MODIFIERS["save_civilian"]
        if role == "Armsmaster" and action == "advance" and scenario_key == "pirate":
            bonus += ETHICS_MODIFIERS["deescalate"]
        if role == "Explosives Expert" and action == "withdraw" and scenario_key == "magnetar":
            bonus += ETHICS_MODIFIERS["save_civilian"]
        
        return bonus


class QLearningTrainer:
    """Q-Learning trainer for agent decision-making."""
    
    def __init__(
        self,
        gamma: float = 0.90,
        alpha: float = 0.3,
        epsilon: float = 0.2,
        ethics_enabled: bool = True
    ):
        """
        Initialize Q-Learning trainer.
        
        Args:
            gamma: Discount factor for future rewards
            alpha: Learning rate
            epsilon: Exploration rate
            ethics_enabled: Whether to include ethics in training
        """
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        self.reward_calculator = RewardCalculator(ethics_enabled=ethics_enabled)
        logger.info(
            f"QLearningTrainer initialized: γ={gamma}, α={alpha}, ε={epsilon}"
        )
    
    @logger_decorator(log_entry=True, log_exit=True, log_time=True)
    def train_agent(
        self,
        role: str = "Longsight",
        episodes: int = 1000
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Train an agent using Q-learning.
        
        Args:
            role: Agent role to train (default: "Longsight")
            episodes: Number of training episodes
            
        Returns:
            Tuple of (Q-table, scenario_keys)
        """
        logger.info(f"Training {role} for {episodes} episodes...")
        
        scenario_keys = list(SCENARIO_MODIFIERS.keys())
        actions = ["advance", "defend", "stabilise", "negotiate", "withdraw"]
        
        n_states = len(scenario_keys)
        n_actions = len(actions)
        
        # Initialize Q-table
        Q = np.zeros((n_states, n_actions))
        
        # Training loop
        for episode in range(episodes):
            # Random state
            state = np.random.randint(0, n_states)
            
            # Choose action (ε-greedy)
            if np.random.rand() < self.epsilon:
                action = np.random.randint(0, n_actions)
            else:
                action = int(np.argmax(Q[state]))
            
            # Get reward
            reward = self.reward_calculator.calculate(
                role=role,
                action=actions[action],
                scenario=scenario_keys[state],
                terrain=random.choice(TERRAINS),
                weather=random.choice(WEATHER_CONDITIONS)
            )
            
            # Q-learning update
            Q[state, action] = (1 - self.alpha) * Q[state, action] + \
                              self.alpha * (reward + self.gamma * np.max(Q[state]))
            
            if (episode + 1) % 200 == 0:
                logger.debug(f"Episode {episode + 1}/{episodes} complete")
        
        logger.info(f"Training complete for {role}")
        return Q, scenario_keys


class MissionEnvironment:
    """
    Main environment for running cosmic missions.
    
    Coordinates scenarios, agents, and simulation execution.
    """
    
    def __init__(
        self,
        scenario: Optional[CosmicScenario] = None,
        ethics_enabled: bool = True
    ):
        """
        Initialize mission environment.
        
        Args:
            scenario: Cosmic scenario (generated if None)
            ethics_enabled: Enable ethics-aware rewards
        """
        self.scenario = scenario or CosmicScenario.generate_random()
        self.reward_calculator = RewardCalculator(ethics_enabled=ethics_enabled)
        self.q_trainer = QLearningTrainer(ethics_enabled=ethics_enabled)
        logger.info(f"MissionEnvironment initialized:\n{self.scenario}")
    
    def get_reward_calculator(self) -> RewardCalculator:
        """Get the reward calculator instance."""
        return self.reward_calculator
    
    def get_q_trainer(self) -> QLearningTrainer:
        """Get the Q-learning trainer instance."""
        return self.q_trainer
