# SOFTKILL-9000 API Reference

Complete reference for all public APIs in the SOFTKILL-9000 package.

## Table of Contents

- [Core API](#core-api)
- [Agent Module](#agent-module)
- [Environment Module](#environment-module)
- [Configuration Module](#configuration-module)
- [Visualization Module](#visualization-module)
- [REST API](#rest-api)
- [Logging Utilities](#logging-utilities)

---

## Core API

### MissionSimulator

Main orchestrator for running simulations.

**Module**: `softkill9000.simulator`

```python
from softkill9000.simulator import MissionSimulator
```

#### Constructor

```python
MissionSimulator(config: Optional[SimulationConfig] = None)
```

**Parameters**:
- `config` (Optional[SimulationConfig]): Simulation configuration. If None, uses default config.

**Example**:
```python
from softkill9000.config import SimulationConfig, AgentConfig

config = SimulationConfig(
    agents=[AgentConfig(role="Longsight", species="Vyr'khai")]
)
sim = MissionSimulator(config=config)
```

#### Methods

##### `setup() -> None`

Initialize simulation components (environment, agents, Q-learning).

```python
sim.setup()
```

**Side Effects**:
- Creates mission environment
- Trains Q-learning model
- Initializes agent squad

**Logging**: Logs setup progress with timing information

---

##### `run() -> Dict[str, Any]`

Execute the simulation and return results.

```python
results = sim.run()
```

**Returns**: Dictionary containing:
- `mission_summary`: Summary statistics
- `agent_performance`: Per-agent metrics
- `scenario`: Mission scenario details
- `final_rewards`: Final reward per agent
- `mission_log`: List of all actions
- `config`: Configuration used

**Example**:
```python
results = sim.run()
print(f"Total reward: {results['mission_summary']['total_reward']}")
for agent, reward in results['final_rewards'].items():
    print(f"{agent}: {reward:.2f}")
```

---

##### `export_results(results: Dict, filepath: str) -> None`

Export simulation results to JSON file.

```python
sim.export_results(results, "results.json")
```

**Parameters**:
- `results`: Results dictionary from `run()`
- `filepath`: Path to output JSON file

---

## Agent Module

### AgentStats

Dataclass representing agent attributes.

**Module**: `softkill9000.agents.agent`

```python
from softkill9000.agents import AgentStats
```

#### Constructor

```python
AgentStats(
    strength: int,
    empathy: int,
    intelligence: int,
    mobility: int,
    tactical: int
)
```

**Parameters**: All int values typically 0-110

**Example**:
```python
stats = AgentStats(
    strength=70,
    empathy=60,
    intelligence=65,
    mobility=75,
    tactical=80
)
```

#### Methods

##### `apply_modifiers(modifiers: Dict[str, int]) -> None`

Apply stat modifiers (e.g., species bonuses).

```python
modifiers = {"Strength": +6, "Empathy": -2}
stats.apply_modifiers(modifiers)
```

---

##### `to_dict() -> Dict[str, int]`

Convert stats to dictionary.

```python
stats_dict = stats.to_dict()
# {'Strength': 70, 'Empathy': 60, ...}
```

---

### Agent

Individual agent with role, species, and capabilities.

**Module**: `softkill9000.agents.agent`

```python
from softkill9000.agents import Agent
```

#### Constructor

```python
Agent(
    role: str,
    description: str,
    species: str,
    stats: AgentStats,
    position: Tuple[float, float] = (0.0, 0.0)
)
```

**Parameters**:
- `role`: Agent role (e.g., "Longsight", "Lifebinder")
- `description`: Role description
- `species`: Species name
- `stats`: AgentStats instance
- `position`: Initial (x, y) coordinates

**Example**:
```python
agent = Agent(
    role="Longsight",
    description="Marksman",
    species="Vyr'khai",
    stats=AgentStats(70, 60, 65, 75, 80)
)
```

#### Methods

##### `choose_action(scenario: str, q_table: Optional[np.ndarray] = None) -> str`

Select action based on Q-learning or rules.

```python
action = agent.choose_action("Combat scenario", q_table)
# Returns: "advance", "defend", "stabilise", "negotiate", or "withdraw"
```

**Parameters**:
- `scenario`: Current scenario description
- `q_table`: Q-learning table (if None, uses rule-based)

**Returns**: Action string

---

##### `update_position(dx: float = 0.0, dy: float = 0.0) -> None`

Update agent position.

```python
agent.update_position(dx=1.5, dy=0.5)
```

---

##### `update_reward(reward: float) -> None`

Add reward to cumulative total.

```python
agent.update_reward(15.5)
```

---

### SquadManager

Manages multiple agents as a coordinated squad.

**Module**: `softkill9000.agents.agent`

```python
from softkill9000.agents import SquadManager
```

#### Constructor

```python
SquadManager(agents: List[Agent])
```

**Parameters**:
- `agents`: List of Agent instances

**Example**:
```python
manager = SquadManager([agent1, agent2, agent3])
```

#### Methods

##### `get_squad_stats() -> Dict[str, Dict[str, int]]`

Get all agent statistics.

```python
stats = manager.get_squad_stats()
# {'Longsight': {'Strength': 70, ...}, 'Lifebinder': {...}}
```

---

##### `get_cumulative_rewards() -> Dict[str, float]`

Get total rewards per agent.

```python
rewards = manager.get_cumulative_rewards()
# {'Longsight': 150.5, 'Lifebinder': 180.2}
```

---

##### `execute_timestep(scenario: str, q_table: Optional[np.ndarray] = None) -> List[Tuple[str, str, float]]`

Execute one timestep for all agents.

```python
actions = manager.execute_timestep("Combat", q_table)
# [('Longsight', 'advance', 12.5), ('Lifebinder', 'stabilise', 15.0)]
```

**Returns**: List of (role, action, reward) tuples

---

## Environment Module

### CosmicScenario

Represents a mission scenario.

**Module**: `softkill9000.environments.environment`

```python
from softkill9000.environments import CosmicScenario
```

#### Constructor

```python
CosmicScenario(
    galaxy: str,
    planet: str,
    terrain: str,
    weather: str,
    scenario: str
)
```

#### Class Methods

##### `generate_random() -> CosmicScenario`

Generate random scenario from templates.

```python
scenario = CosmicScenario.generate_random()
print(scenario)
# MISSION: Andromeda (M31) // Planet Zornak-442
# Terrain: Urban Lattice // Weather: Ion Storm
```

---

### RewardCalculator

Calculates rewards for agent actions.

**Module**: `softkill9000.environments.environment`

```python
from softkill9000.environments import RewardCalculator
```

#### Constructor

```python
RewardCalculator(ethics_enabled: bool = True)
```

#### Methods

##### `calculate(role: str, action: str, scenario: str, terrain: str, weather: str) -> float`

Calculate reward for an action.

```python
calc = RewardCalculator(ethics_enabled=True)
reward = calc.calculate(
    role="Longsight",
    action="advance",
    scenario="Combat scenario",
    terrain="Urban Lattice",
    weather="Clear"
)
# Returns: 45.5 (example)
```

**Parameters**:
- `role`: Agent role
- `action`: Action taken
- `scenario`: Current scenario
- `terrain`: Terrain type
- `weather`: Weather conditions

**Returns**: Float reward value

---

### QLearningTrainer

Trains Q-learning models for agents.

**Module**: `softkill9000.environments.environment`

```python
from softkill9000.environments import QLearningTrainer
```

#### Constructor

```python
QLearningTrainer(
    gamma: float = 0.9,
    alpha: float = 0.3,
    epsilon: float = 0.2,
    ethics_enabled: bool = True
)
```

**Parameters**:
- `gamma`: Discount factor (0-1)
- `alpha`: Learning rate (0-1)
- `epsilon`: Exploration rate (0-1)
- `ethics_enabled`: Enable ethics-aware rewards

#### Methods

##### `train_agent(role: str = "Longsight", episodes: int = 1000) -> Tuple[np.ndarray, List[str]]`

Train Q-learning model for agent role.

```python
trainer = QLearningTrainer(gamma=0.9, alpha=0.3, epsilon=0.2)
q_table, actions = trainer.train_agent(role="Longsight", episodes=1000)
```

**Returns**: Tuple of (Q-table array, action list)

---

### MissionEnvironment

Simulation environment manager.

**Module**: `softkill9000.environments.environment`

```python
from softkill9000.environments import MissionEnvironment
```

#### Constructor

```python
MissionEnvironment(
    scenario: Optional[CosmicScenario] = None,
    ethics_enabled: bool = True
)
```

**Parameters**:
- `scenario`: Mission scenario (generates random if None)
- `ethics_enabled`: Enable ethics-aware rewards

#### Methods

##### `get_state() -> Dict[str, Any]`

Get current environment state.

```python
env = MissionEnvironment()
state = env.get_state()
# {'timestep': 0, 'ethics_enabled': True, 'scenario': {...}}
```

---

##### `reset() -> None`

Reset environment to initial state.

```python
env.reset()
```

---

## Configuration Module

### SimulationConfig

Main configuration model.

**Module**: `softkill9000.config.models`

```python
from softkill9000.config import SimulationConfig
```

#### Constructor

```python
SimulationConfig(
    agents: List[AgentConfig],
    mission: MissionConfig = MissionConfig(),
    q_learning: QLearningConfig = QLearningConfig()
)
```

**Example**:
```python
config = SimulationConfig(
    agents=[AgentConfig(role="Longsight", species="Vyr'khai")],
    mission=MissionConfig(num_timesteps=100),
    q_learning=QLearningConfig(episodes=2000)
)
```

---

### AgentConfig

Agent configuration model.

```python
AgentConfig(
    role: str,
    species: str,
    base_strength: int = 60,
    base_empathy: int = 60,
    base_intelligence: int = 60,
    base_mobility: int = 60,
    base_tactical: int = 60
)
```

**Validation**: All stats must be 0-110

---

### MissionConfig

Mission parameters configuration.

```python
MissionConfig(
    num_timesteps: int = 60,
    ethics_enabled: bool = True
)
```

**Validation**: `num_timesteps` must be 10-500

---

### QLearningConfig

Q-learning hyperparameters.

```python
QLearningConfig(
    episodes: int = 1000,
    gamma: float = 0.90,
    alpha: float = 0.3,
    epsilon: float = 0.2
)
```

**Validation**:
- `episodes`: 100-10000
- All floats: 0.0-1.0

---

### load_config_from_yaml

Load config from YAML file.

```python
from softkill9000.config import load_config_from_yaml

config = load_config_from_yaml("config.yaml")
```

**Parameters**:
- `path`: Path to YAML file

**Returns**: SimulationConfig instance

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `yaml.YAMLError`: If YAML is invalid
- `ValidationError`: If config is invalid

---

## Visualization Module

### create_radar_chart

Create radar chart of agent statistics.

**Module**: `softkill9000.visualization.plots`

```python
from softkill9000.visualization import create_radar_chart
```

#### Function Signature

```python
create_radar_chart(
    agent_stats: Dict[str, Dict[str, int]],
    title: str = "Agent Squad Capabilities"
) -> Figure
```

**Parameters**:
- `agent_stats`: Nested dict of {agent: {stat: value}}
- `title`: Chart title

**Returns**: matplotlib Figure

**Example**:
```python
stats = {
    'Longsight': {'Strength': 70, 'Empathy': 60, ...},
    'Lifebinder': {'Strength': 50, 'Empathy': 90, ...}
}
fig = create_radar_chart(stats)
fig.savefig('squad_radar.png')
```

---

### create_reward_curve

Plot reward progression over time.

```python
create_reward_curve(
    reward_history: Dict[str, List[float]],
    title: str = "Mission Reward Progression"
) -> Figure
```

**Parameters**:
- `reward_history`: Dict of {agent: [rewards...]}
- `title`: Chart title

**Example**:
```python
history = {
    'Longsight': [10, 15, 20, 25],
    'Lifebinder': [12, 18, 22, 28]
}
fig = create_reward_curve(history)
```

---

### create_mission_timeline_gif

Generate animated GIF of mission timeline.

```python
create_mission_timeline_gif(
    trajectories: List[Dict],
    output_path: str = "mission_timeline.gif",
    duration: float = 0.5
) -> str
```

**Parameters**:
- `trajectories`: List of position data per timestep
- `output_path`: Output file path
- `duration`: Frame duration in seconds

**Returns**: Path to generated GIF

**Requires**: `imageio` package

---

## REST API

Base URL: `http://localhost:8000`

### Start Server

```bash
softkill9000-api
# or
uvicorn softkill9000.api.server:app --reload
```

### Endpoints

#### POST /api/simulations

Create and run a new simulation.

**Request Body**:
```json
{
  "config": {
    "agents": [
      {
        "role": "Longsight",
        "species": "Vyr'khai"
      }
    ],
    "mission": {
      "num_timesteps": 60,
      "ethics_enabled": true
    }
  }
}
```

**Response**:
```json
{
  "simulation_id": "abc123",
  "status": "completed",
  "results": {
    "final_rewards": {...},
    "mission_summary": {...}
  }
}
```

---

#### GET /api/simulations/{id}

Retrieve simulation results.

**Response**:
```json
{
  "simulation_id": "abc123",
  "status": "completed",
  "results": {...}
}
```

---

#### GET /api/config/species

List available species and modifiers.

**Response**:
```json
{
  "Vyr'khai": {
    "Strength": 6,
    "Empathy": -2,
    ...
  }
}
```

---

#### GET /api/config/roles

List available agent roles.

**Response**:
```json
{
  "Longsight": "Marksman from the Vyr'khai star-clans",
  "Lifebinder": "Medic-priest of the Lumenari bioconclave"
}
```

---

#### GET /api/config/scenarios

List scenario templates.

**Response**:
```json
[
  "Refugee flotilla near a magnetar; containment fields failing.",
  "Xenofauna stampede through crystalline corridors; civilians trapped."
]
```

---

## Logging Utilities

### setup_logging

Initialize package-wide logging.

**Module**: `softkill9000`

```python
from softkill9000 import setup_logging

setup_logging(
    verbose: bool = False,
    log_file: Optional[str] = None,
    level: str = "INFO"
)
```

**Parameters**:
- `verbose`: Enable detailed logging
- `log_file`: Path to log file (None for console only)
- `level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")

**Example**:
```python
setup_logging(verbose=True, log_file="simulation.log")
```

---

### logger_decorator

Decorator for function logging.

**Module**: `softkill9000.utils.logging_utils`

```python
from softkill9000.utils import logger_decorator

@logger_decorator(log_entry=True, log_exit=True, log_timing=True)
def my_function(arg1, arg2):
    return arg1 + arg2
```

**Parameters**:
- `log_entry`: Log function entry
- `log_exit`: Log function exit
- `log_timing`: Log execution time

---

### LogContext

Context manager for operation logging.

```python
from softkill9000.utils import LogContext

with LogContext("Data Processing"):
    # Your code here
    process_data()
```

**Output**:
```
╔══ Data Processing START ══╗
...
╚══ Data Processing COMPLETE [1.234s] ══╝
```

---

## Constants

### Species Modifiers

Available in `softkill9000.environments.environment.SPECIES_MODIFIERS`

```python
SPECIES_MODIFIERS = {
    "Vyr'khai": {"Strength": +6, "Empathy": -2, ...},
    "Lumenari": {"Strength": +1, "Empathy": +8, ...},
    # ... 8 species total
}
```

### Agent Roles

Available in `softkill9000.environments.environment.ROLE_DESCRIPTIONS`

```python
ROLE_DESCRIPTIONS = {
    "Longsight": "Marksman from the Vyr'khai star-clans",
    "Lifebinder": "Medic-priest of the Lumenari bioconclave",
    # ... 8 roles total
}
```

### Actions

```python
ACTIONS = ["advance", "defend", "stabilise", "negotiate", "withdraw"]
```

---

## Version Information

```python
import softkill9000
print(softkill9000.__version__)  # "1.0.0"
```

---

**API Version**: 1.0.0  
**Last Updated**: November 12, 2025  
**Documentation**: https://github.com/BkAsDrP/Softkill9000/docs
