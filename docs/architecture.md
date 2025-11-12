# SOFTKILL-9000 Architecture Guide

## Overview

SOFTKILL-9000 is designed as a modular, extensible multi-agent simulation framework with clear separation of concerns and plugin-based architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interfaces                       │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  CLI Tool    │  Python API  │  REST API    │  Gradio UI     │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘
                      │
       ┌──────────────▼──────────────┐
       │   MissionSimulator (Core)   │
       │  - Setup & Orchestration    │
       │  - Result Aggregation       │
       └──────────────┬──────────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
   ┌───▼───┐    ┌────▼────┐   ┌────▼────┐
   │Agents │    │  Env.   │   │ Config  │
   │Module │    │ Module  │   │ Module  │
   └───┬───┘    └────┬────┘   └────┬────┘
       │             │              │
   ┌───▼────────┐ ┌──▼──────────┐  │
   │ Squad      │ │ Q-Learning  │  │
   │ Manager    │ │ Trainer     │  │
   └────────────┘ └─────────────┘  │
       │                            │
   ┌───▼────────┐              ┌───▼────────┐
   │ Individual │              │  Pydantic  │
   │   Agents   │              │ Validators │
   └────────────┘              └────────────┘
```

## Core Components

### 1. MissionSimulator (Orchestrator)

**Location**: `src/softkill9000/simulator.py`

**Responsibilities**:
- Initialize simulation environment
- Coordinate agent squad
- Execute timestep loop
- Aggregate results
- Export data

**Key Methods**:
```python
setup() -> None                    # Initialize components
run() -> Dict[str, Any]            # Execute simulation
export_results(results, path)      # Save results to file
```

**Flow**:
1. Parse configuration
2. Generate or load scenario
3. Create mission environment
4. Train Q-learning model
5. Initialize agent squad
6. Run timestep loop
7. Collect and return results

### 2. Agent Module

**Location**: `src/softkill9000/agents/`

**Components**:

#### AgentStats (Dataclass)
```python
@dataclass
class AgentStats:
    strength: int       # Combat effectiveness
    empathy: int        # Social/healing capability
    intelligence: int   # Problem-solving ability
    mobility: int       # Movement speed
    tactical: int       # Strategic planning
```

#### Agent (Core Class)
```python
class Agent:
    def __init__(self, role, description, species, stats)
    def choose_action(self, scenario, q_table) -> str
    def update_position(self, dx, dy)
    def update_reward(self, reward)
```

**Action Selection**:
- Uses Q-learning table if available
- Falls back to rule-based logic
- Considers agent role and stats

#### SquadManager
```python
class SquadManager:
    def __init__(self, agents)
    def get_squad_stats() -> Dict
    def get_cumulative_rewards() -> Dict
    def execute_timestep(scenario, q_table) -> List
```

**Responsibilities**:
- Coordinate multiple agents
- Track collective performance
- Execute synchronized actions

### 3. Environment Module

**Location**: `src/softkill9000/environments/`

**Components**:

#### CosmicScenario (Dataclass)
```python
@dataclass
class CosmicScenario:
    galaxy: str
    planet: str
    terrain: str
    weather: str
    scenario: str
    
    @classmethod
    def generate_random(cls) -> 'CosmicScenario'
```

**Data Sources**:
- 17 galaxies (Andromeda, Triangulum, etc.)
- 9 terrain types (Urban, Desert, Ice, etc.)
- 9 weather conditions (Clear, Ion Storm, etc.)
- 5 scenario templates

#### RewardCalculator
```python
class RewardCalculator:
    def __init__(self, ethics_enabled)
    def calculate(self, role, action, scenario, terrain, weather) -> float
```

**Reward Components**:
- Base reward (-100 to +100)
- Terrain modifiers (-20% to +20%)
- Weather modifiers (-30% to +30%)
- Ethics bonuses/penalties (-8 to +8)

#### QLearningTrainer
```python
class QLearningTrainer:
    def __init__(self, gamma, alpha, epsilon, ethics_enabled)
    def train_agent(self, role, episodes) -> Tuple[np.ndarray, List]
```

**Q-Learning Parameters**:
- `gamma` (γ): Discount factor (0.9 default)
- `alpha` (α): Learning rate (0.3 default)
- `epsilon` (ε): Exploration rate (0.2 default)

**Training Process**:
1. Initialize Q-table (5 actions × 5 scenarios)
2. For each episode:
   - Select action (ε-greedy)
   - Calculate reward
   - Update Q-value
   - Track performance

#### MissionEnvironment
```python
class MissionEnvironment:
    def __init__(self, scenario, ethics_enabled)
    def get_state() -> Dict
    def reset() -> None
    def step(action) -> None
```

### 4. Configuration Module

**Location**: `src/softkill9000/config/`

**Models**:

```python
class AgentConfig(BaseModel):
    role: str
    species: str
    base_strength: int = Field(60, ge=0, le=110)
    base_empathy: int = Field(60, ge=0, le=110)
    base_intelligence: int = Field(60, ge=0, le=110)
    base_mobility: int = Field(60, ge=0, le=110)
    base_tactical: int = Field(60, ge=0, le=110)

class MissionConfig(BaseModel):
    num_timesteps: int = Field(60, ge=10, le=500)
    ethics_enabled: bool = True

class QLearningConfig(BaseModel):
    episodes: int = Field(1000, ge=100, le=10000)
    gamma: float = Field(0.90, ge=0.0, le=1.0)
    alpha: float = Field(0.3, ge=0.0, le=1.0)
    epsilon: float = Field(0.2, ge=0.0, le=1.0)

class SimulationConfig(BaseModel):
    agents: List[AgentConfig]
    mission: MissionConfig = Field(default_factory=MissionConfig)
    q_learning: QLearningConfig = Field(default_factory=QLearningConfig)
```

**Validation**:
- Field bounds checking
- Type validation
- Required field enforcement
- Custom validators

### 5. Logging System

**Location**: `src/softkill9000/utils/logging_utils.py`

**Components**:

#### logger_decorator
```python
@logger_decorator(log_entry=True, log_exit=True, log_timing=True)
def some_function():
    pass
```

**Features**:
- Function entry logging
- Function exit logging
- Execution timing
- Exception tracking

#### LogContext
```python
with LogContext("Operation Name"):
    # code here
```

**Output Format**:
```
2025-11-12 08:38:54,474 - softkill9000.simulator - INFO - [__enter__:130] - ╔══ Operation Name START ══╗
2025-11-12 08:38:54,501 - softkill9000.simulator - INFO - [__exit__:142] - ╚══ Operation Name COMPLETE [0.0262s] ══╝
```

### 6. Visualization Module

**Location**: `src/softkill9000/visualization/`

**Functions**:

```python
create_radar_chart(stats: Dict) -> Figure
create_reward_curve(history: Dict) -> Figure
create_mission_timeline_gif(trajectories: List) -> str
```

**Dependencies** (optional):
- matplotlib (required)
- imageio (for GIFs)
- numpy (for computations)

### 7. API Module

**Location**: `src/softkill9000/api/`

**Endpoints**:

```python
POST   /api/simulations          # Create simulation
GET    /api/simulations/{id}     # Get results
GET    /api/config/species        # List species
GET    /api/config/roles          # List roles
GET    /api/config/scenarios      # List scenarios
```

**Technology Stack**:
- FastAPI
- Uvicorn (ASGI server)
- Pydantic (validation)
- Background tasks

## Data Flow

### Simulation Execution Flow

```
1. Configuration Loading
   ├── YAML file → SimulationConfig
   ├── CLI args → MissionConfig
   └── Defaults → QLearningConfig

2. Environment Setup
   ├── Generate/Load CosmicScenario
   ├── Initialize MissionEnvironment
   └── Create RewardCalculator

3. Q-Learning Training
   ├── QLearningTrainer.train_agent()
   ├── 1000 episodes of exploration
   └── Returns Q-table

4. Agent Initialization
   ├── Create Agent instances
   ├── Apply species modifiers
   └── Initialize SquadManager

5. Simulation Loop (for each timestep)
   ├── SquadManager.execute_timestep()
   ├── Each Agent.choose_action()
   ├── RewardCalculator.calculate()
   ├── Agent.update_reward()
   └── Log actions and rewards

6. Result Aggregation
   ├── Final rewards per agent
   ├── Mission log (all actions)
   ├── Squad statistics
   └── Trajectories

7. Export/Display
   ├── JSON export (optional)
   ├── Console output
   └── Visualization (optional)
```

## Extension Points

### Adding New Agent Roles

1. Add role to `ROLE_DESCRIPTIONS` in `environments/environment.py`
2. Add species to `SPECIES_MODIFIERS`
3. Update rule-based logic in `Agent.choose_action()`
4. Create config in YAML or Python

### Adding New Actions

1. Add action to action list in `QLearningTrainer`
2. Update `RewardCalculator.calculate()` logic
3. Update Q-table dimensions
4. Add action descriptions

### Adding New Scenarios

1. Add to `SCENARIOS` list in `environments/environment.py`
2. Add terrain to `TERRAINS` list
3. Add weather to `WEATHER_CONDITIONS` list
4. Update reward modifiers if needed

### Custom Visualization

```python
from softkill9000.visualization import plots

# Create custom plot
def create_custom_plot(data):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    # Your plotting logic
    return fig
```

## Performance Considerations

### Scalability

- **Agents**: Linear scaling up to 8 agents
- **Timesteps**: Linear time complexity
- **Q-Learning**: O(episodes × actions × scenarios)
- **Memory**: ~10MB for standard simulation

### Optimization Opportunities

1. **Parallel Training**: Train multiple Q-tables concurrently
2. **Batch Processing**: Process multiple simulations
3. **Caching**: Cache scenario generation
4. **Vectorization**: Use NumPy for batch operations

### Resource Requirements

**Minimal**:
- RAM: 512MB
- CPU: Single core
- Time: ~1 second for 60 timesteps

**Recommended**:
- RAM: 2GB
- CPU: 2+ cores
- Time: Sub-second execution

## Security Considerations

### Input Validation

- All config values validated by Pydantic
- File paths sanitized
- API rate limiting (recommended)

### Safe Defaults

- Ethics mode enabled by default
- Reasonable bounds on all parameters
- No arbitrary code execution

### Production Deployment

- Use environment variables for secrets
- Enable HTTPS for API
- Implement authentication
- Rate limit API endpoints
- Log all access attempts

## Testing Strategy

### Unit Tests

```python
# Test individual components
tests/test_agents.py       # Agent, SquadManager
tests/test_config.py       # Config models
```

### Integration Tests

```python
# Test component interaction
tests/test_simulator.py    # Full simulation
```

### Coverage Goals

- Core modules: 80%+
- Utils: 60%+
- API: 70%+
- Overall: 70%+

## Deployment Patterns

### Development

```bash
pip install -e ".[dev]"
python -m softkill9000 --verbose
```

### Production

```bash
pip install softkill9000
gunicorn softkill9000.api.server:app --workers 4
```

### Docker

```dockerfile
FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["softkill9000-api"]
```

### Cloud (AWS Lambda)

```python
# lambda_handler.py
from softkill9000 import MissionSimulator

def lambda_handler(event, context):
    sim = MissionSimulator()
    return sim.run()
```

## Monitoring & Observability

### Logging Levels

```python
setup_logging(level='INFO')    # Production
setup_logging(level='DEBUG')   # Development
setup_logging(verbose=True)    # Verbose mode
```

### Metrics to Track

- Simulation execution time
- Agent action distribution
- Reward trends
- Error rates
- API response times

### Health Checks

```bash
# CLI health check
python -m softkill9000 --version

# API health check
curl http://localhost:8000/health
```

---

**Last Updated**: November 12, 2025  
**Version**: 1.0.0  
**Maintained By**: MotionBlendAI Team
