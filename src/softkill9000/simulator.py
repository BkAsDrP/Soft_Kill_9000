"""
Main mission simulator for SOFTKILL-9000.

Coordinates all components to run complete mission simulations.
"""

import logging
from typing import Dict, List, Optional
import json

from .agents import Agent, AgentStats, SquadManager
from .environments import (
    MissionEnvironment,
    CosmicScenario,
    SPECIES_MODIFIERS,
    ROLE_DESCRIPTIONS,
    BANTER
)
from .config.models import SimulationConfig, AgentConfig
from .utils.logging_utils import logger_decorator, LogContext

logger = logging.getLogger(__name__)


class MissionSimulator:
    """
    Main simulator for SOFTKILL-9000 cosmic missions.
    
    Orchestrates agents, environment, training, and execution of missions.
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """
        Initialize mission simulator.
        
        Args:
            config: Simulation configuration (default config if None)
        """
        self.config = config or self._get_default_config()
        self.environment = None
        self.squad_manager = None
        self.q_table = None
        self.scenario_keys = None
        
        logger.info("MissionSimulator initialized")
    
    def _get_default_config(self) -> SimulationConfig:
        """Get default simulation configuration."""
        from .environments import ROLE_DESCRIPTIONS
        
        # Create default agents for all roles
        default_agents = []
        species_map = {
            "Longsight": "Vyr'khai",
            "Lifebinder": "Lumenari",
            "Specter": "Zephryl",
            "Whisper": "Mycelian",
            "Archivist": "Ferroth",
            "Brawler": "Aetherborn",
            "Armsmaster": "Kinetari",
            "Explosives Expert": "Verdan",
        }
        
        for role in ROLE_DESCRIPTIONS.keys():
            default_agents.append(
                AgentConfig(
                    role=role,
                    species=species_map.get(role, "Aetherborn")
                )
            )
        
        return SimulationConfig(agents=default_agents)
    
    @logger_decorator(log_entry=True, log_exit=True, log_time=True)
    def setup(self) -> None:
        """
        Set up the simulation environment and agents.
        
        This includes creating the mission environment, initializing agents,
        and training Q-learning models.
        """
        with LogContext("Simulation Setup", logger):
            # Create mission environment
            logger.info("Creating mission environment...")
            self.environment = MissionEnvironment(
                ethics_enabled=self.config.mission.ethics_enabled
            )
            
            # Train Q-learning model
            logger.info("Training Q-learning model...")
            q_trainer = self.environment.get_q_trainer()
            self.q_table, self.scenario_keys = q_trainer.train_agent(
                role="Longsight",
                episodes=self.config.q_learning.episodes
            )
            
            # Create agents
            logger.info("Creating agent squad...")
            agents = []
            for agent_config in self.config.agents:
                # Create base stats
                base_stats = AgentStats(
                    strength=agent_config.base_strength,
                    empathy=agent_config.base_empathy,
                    intelligence=agent_config.base_intelligence,
                    mobility=agent_config.base_mobility,
                    tactical=agent_config.base_tactical
                )
                
                # Apply species modifiers
                species_mods = SPECIES_MODIFIERS.get(agent_config.species, {})
                final_stats = base_stats.apply_species_modifiers(species_mods)
                
                # Create agent
                agent = Agent(
                    role=agent_config.role,
                    description=ROLE_DESCRIPTIONS.get(agent_config.role, "Unknown role"),
                    species=agent_config.species,
                    stats=final_stats
                )
                agents.append(agent)
            
            # Create squad manager
            self.squad_manager = SquadManager(agents)
            
            logger.info(f"Setup complete: {len(agents)} agents ready")
    
    @logger_decorator(log_entry=True, log_exit=True, log_time=True)
    def run(self) -> Dict:
        """
        Run the complete mission simulation.
        
        Returns:
            Dictionary containing mission results, logs, and statistics
        """
        if self.environment is None or self.squad_manager is None:
            self.setup()
        
        with LogContext("Mission Execution", logger):
            mission_log = []
            reward_history = {role: [] for role in self.squad_manager.agents.keys()}
            
            # Log mission start
            scenario = self.environment.scenario
            mission_log.append(str(scenario))
            mission_log.append(f"Ethics Mode: {'ENABLED' if self.config.mission.ethics_enabled else 'DISABLED'}")
            mission_log.append(f"Mission Duration: {self.config.mission.num_timesteps} ticks")
            mission_log.append("=" * 80)
            
            # Execute mission timesteps
            for tick in range(self.config.mission.num_timesteps):
                # Execute timestep for all agents
                results = self.squad_manager.execute_timestep(
                    scenario=scenario.scenario,
                    terrain=scenario.terrain,
                    weather=scenario.weather,
                    reward_calculator=self.environment.reward_calculator.calculate,
                    q_table=self.q_table,
                    scenario_keys=self.scenario_keys,
                    banter_dict=BANTER
                )
                
                # Log results for each agent
                for role, result in results.items():
                    agent = self.squad_manager.agents[role]
                    reward_history[role].append(agent.cumulative_reward)
                    
                    log_entry = (
                        f"[{tick:03d}] {role}: {result['banter']} | "
                        f"Action={result['action']} | "
                        f"Δ={result['reward']:.2f} | "
                        f"Total={agent.cumulative_reward:.2f}"
                    )
                    mission_log.append(log_entry)
                
                if (tick + 1) % 10 == 0:
                    logger.info(f"Mission progress: {tick + 1}/{self.config.mission.num_timesteps} ticks")
            
            # Compile final results
            results = {
                "scenario": {
                    "galaxy": scenario.galaxy,
                    "planet": scenario.planet,
                    "terrain": scenario.terrain,
                    "weather": scenario.weather,
                    "description": scenario.scenario
                },
                "config": {
                    "num_timesteps": self.config.mission.num_timesteps,
                    "ethics_enabled": self.config.mission.ethics_enabled,
                    "q_learning_episodes": self.config.q_learning.episodes
                },
                "agent_stats": self.squad_manager.get_squad_stats(),
                "final_rewards": self.squad_manager.get_cumulative_rewards(),
                "reward_history": reward_history,
                "trajectories": self.squad_manager.get_trajectories(),
                "mission_log": mission_log
            }
            
            logger.info("Mission execution complete")
            return results
    
    def export_results(self, results: Dict, filepath: str) -> None:
        """
        Export simulation results to JSON file.
        
        Args:
            results: Results dictionary from run()
            filepath: Output file path
        """
        logger.info(f"Exporting results to: {filepath}")
        
        # Convert trajectories to serializable format
        export_data = results.copy()
        export_data["trajectories"] = {
            role: [(float(x), float(y)) for x, y in traj]
            for role, traj in results["trajectories"].items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info("Export complete")
