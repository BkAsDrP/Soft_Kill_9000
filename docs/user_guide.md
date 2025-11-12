# SOFTKILL-9000 User Guide

Comprehensive guide for using SOFTKILL-9000 in various scenarios.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

Choose the installation method that fits your needs:

#### Minimal Installation
```bash
pip install -e .
```

Includes: Core simulation, CLI, basic configuration

#### Development Installation
```bash
pip install -e ".[dev]"
```

Includes: Testing tools, linting, type checking

#### Full Installation
```bash
pip install -e ".[all]"
```

Includes: All features (API server, Gradio UI, visualization tools)

### Verify Installation

```bash
# Check version
python -m softkill9000 --version

# Run test simulation
python -m softkill9000 --timesteps 10
```

---

## Basic Usage

### 1. Simple Simulation (CLI)

Run a quick simulation with default settings:

```bash
python -m softkill9000 --timesteps 60
```

**Output**:
```
MISSION COMPLETE
================
Scenario: Planetary ocean rising after moon-shear...
Location: Kijani Spiral // Daxzix-210
Environment: Volcanic Spires // Sonic Winds

Final Rewards:
  Longsight  : 130.72
  Lifebinder : 163.46
  Specter    :  33.01
```

### 2. With Verbose Logging

See detailed execution logs:

```bash
python -m softkill9000 --timesteps 60 --verbose
```

This shows:
- Agent action selections
- Reward calculations
- Timestep progression
- Execution timing

### 3. Export Results

Save results to JSON:

```bash
python -m softkill9000 --timesteps 60 --export results.json
```

### 4. Custom Configuration

Create `config.yaml`:

```yaml
agents:
  - role: "Longsight"
    species: "Vyr'khai"
    base_strength: 80
    base_tactical: 85
  - role: "Lifebinder"
    species: "Lumenari"
    base_empathy: 90
  - role: "Specter"
    species: "Zephryl"
    base_mobility: 95

mission:
  num_timesteps: 100
  ethics_enabled: true

q_learning:
  episodes: 2000
  gamma: 0.95
  alpha: 0.25
  epsilon: 0.15
```

Run with config:

```bash
python -m softkill9000 --config config.yaml --export results.json
```

---

## Advanced Features

### Python API

#### Basic Simulation

```python
from softkill9000 import MissionSimulator, setup_logging

# Enable logging
setup_logging(verbose=True)

# Run simulation
sim = MissionSimulator()
sim.setup()
results = sim.run()

# Access results
print(f"Total reward: {results['mission_summary']['total_reward']:.2f}")
print(f"Average reward: {results['mission_summary']['avg_reward']:.2f}")

# Agent performance
for agent, reward in results['final_rewards'].items():
    print(f"{agent}: {reward:.2f}")
```

#### Custom Configuration

```python
from softkill9000 import MissionSimulator
from softkill9000.config import SimulationConfig, AgentConfig, MissionConfig

# Define custom agents
agents = [
    AgentConfig(
        role="Longsight",
        species="Vyr'khai",
        base_strength=85,
        base_tactical=90
    ),
    AgentConfig(
        role="Lifebinder",
        species="Lumenari",
        base_empathy=95,
        base_intelligence=80
    ),
    AgentConfig(
        role="Archivist",
        species="Ferroth",
        base_intelligence=95
    )
]

# Configure mission
config = SimulationConfig(
    agents=agents,
    mission=MissionConfig(
        num_timesteps=150,
        ethics_enabled=True
    )
)

# Run simulation
sim = MissionSimulator(config=config)
sim.setup()
results = sim.run()

# Export results
sim.export_results(results, "custom_mission_results.json")
```

#### Multiple Simulations

Run multiple simulations and compare:

```python
from softkill9000 import MissionSimulator
from softkill9000.config import SimulationConfig, AgentConfig

# Define agent configuration
agents = [AgentConfig(role="Longsight", species="Vyr'khai")]

# Run 10 simulations
all_results = []
for i in range(10):
    config = SimulationConfig(agents=agents)
    sim = MissionSimulator(config=config)
    sim.setup()
    results = sim.run()
    all_results.append(results)
    print(f"Run {i+1}: Total Reward = {results['mission_summary']['total_reward']:.2f}")

# Calculate statistics
total_rewards = [r['mission_summary']['total_reward'] for r in all_results]
avg_reward = sum(total_rewards) / len(total_rewards)
print(f"\nAverage across 10 runs: {avg_reward:.2f}")
```

### Visualization

#### Radar Chart

```python
from softkill9000 import MissionSimulator
from softkill9000.visualization import create_radar_chart

# Run simulation
sim = MissionSimulator()
sim.setup()
results = sim.run()

# Create radar chart
stats = results['agent_performance']
fig = create_radar_chart(stats, title="Squad Capabilities Analysis")
fig.savefig("squad_radar.png", dpi=300, bbox_inches='tight')
```

#### Reward Progression

```python
from softkill9000.visualization import create_reward_curve

# Assume we have reward history from results
reward_history = results.get('reward_history', {})

fig = create_reward_curve(reward_history, title="Mission Reward Progression")
fig.savefig("rewards.png", dpi=300)
```

### REST API Usage

Start the API server:

```bash
softkill9000-api
# Server running at http://localhost:8000
```

#### Using curl

```bash
# Create simulation
curl -X POST "http://localhost:8000/api/simulations" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "agents": [
        {"role": "Longsight", "species": "Vyr'\''khai"}
      ],
      "mission": {
        "num_timesteps": 60,
        "ethics_enabled": true
      }
    }
  }'

# Get results (use ID from response)
curl "http://localhost:8000/api/simulations/abc123"

# List species
curl "http://localhost:8000/api/config/species"
```

#### Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Create simulation
config = {
    "config": {
        "agents": [
            {"role": "Longsight", "species": "Vyr'khai"},
            {"role": "Lifebinder", "species": "Lumenari"}
        ],
        "mission": {
            "num_timesteps": 60,
            "ethics_enabled": True
        }
    }
}

response = requests.post(f"{BASE_URL}/api/simulations", json=config)
result = response.json()

print(f"Simulation ID: {result['simulation_id']}")
print(f"Final Rewards: {result['results']['final_rewards']}")

# Get available species
species_response = requests.get(f"{BASE_URL}/api/config/species")
species = species_response.json()
print(f"Available species: {list(species.keys())}")
```

---

## Use Cases

### Use Case 1: Agent Capability Analysis

Compare different agent compositions:

```python
from softkill9000 import MissionSimulator
from softkill9000.config import SimulationConfig, AgentConfig

# Test different squad compositions
compositions = [
    # Combat-heavy
    [
        AgentConfig(role="Longsight", species="Vyr'khai"),
        AgentConfig(role="Brawler", species="Aetherborn"),
        AgentConfig(role="Armsmaster", species="Kinetari")
    ],
    # Balanced
    [
        AgentConfig(role="Longsight", species="Vyr'khai"),
        AgentConfig(role="Lifebinder", species="Lumenari"),
        AgentConfig(role="Specter", species="Zephryl")
    ],
    # Support-heavy
    [
        AgentConfig(role="Lifebinder", species="Lumenari"),
        AgentConfig(role="Whisper", species="Mycelian"),
        AgentConfig(role="Archivist", species="Ferroth")
    ]
]

results = []
for i, agents in enumerate(compositions):
    config = SimulationConfig(agents=agents)
    sim = MissionSimulator(config=config)
    sim.setup()
    result = sim.run()
    results.append(result)
    print(f"Composition {i+1} Total Reward: {result['mission_summary']['total_reward']:.2f}")

# Find best composition
best_idx = max(range(len(results)), key=lambda i: results[i]['mission_summary']['total_reward'])
print(f"\nBest composition: {best_idx + 1}")
```

### Use Case 2: Ethics Impact Analysis

Compare ethics-enabled vs disabled:

```python
from softkill9000.config import MissionConfig

# With ethics
config_ethics = SimulationConfig(
    agents=[AgentConfig(role="Longsight", species="Vyr'khai")],
    mission=MissionConfig(ethics_enabled=True)
)

# Without ethics
config_no_ethics = SimulationConfig(
    agents=[AgentConfig(role="Longsight", species="Vyr'khai")],
    mission=MissionConfig(ethics_enabled=False)
)

# Run both
sim_ethics = MissionSimulator(config=config_ethics)
sim_ethics.setup()
results_ethics = sim_ethics.run()

sim_no_ethics = MissionSimulator(config=config_no_ethics)
sim_no_ethics.setup()
results_no_ethics = sim_no_ethics.run()

print(f"With Ethics: {results_ethics['mission_summary']['total_reward']:.2f}")
print(f"Without Ethics: {results_no_ethics['mission_summary']['total_reward']:.2f}")
```

### Use Case 3: Q-Learning Optimization

Test different Q-learning parameters:

```python
from softkill9000.config import QLearningConfig

# Test different learning rates
learning_rates = [0.1, 0.3, 0.5, 0.7]
results = {}

for alpha in learning_rates:
    config = SimulationConfig(
        agents=[AgentConfig(role="Longsight", species="Vyr'khai")],
        q_learning=QLearningConfig(alpha=alpha, episodes=1000)
    )
    
    sim = MissionSimulator(config=config)
    sim.setup()
    result = sim.run()
    results[alpha] = result['mission_summary']['total_reward']
    print(f"Alpha={alpha}: {result['mission_summary']['total_reward']:.2f}")

# Find optimal
best_alpha = max(results, key=results.get)
print(f"\nOptimal learning rate: {best_alpha}")
```

### Use Case 4: Batch Processing

Process multiple scenarios:

```python
import concurrent.futures
from softkill9000 import MissionSimulator

def run_simulation(sim_id):
    """Run a single simulation."""
    sim = MissionSimulator()
    sim.setup()
    results = sim.run()
    return sim_id, results

# Run 20 simulations in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_simulation, i) for i in range(20)]
    all_results = [f.result() for f in concurrent.futures.as_completed(futures)]

# Analyze results
total_rewards = [r[1]['mission_summary']['total_reward'] for r in all_results]
print(f"Mean reward: {sum(total_rewards) / len(total_rewards):.2f}")
print(f"Min reward: {min(total_rewards):.2f}")
print(f"Max reward: {max(total_rewards):.2f}")
```

---

## Best Practices

### 1. Logging

Always enable logging for debugging:

```python
from softkill9000 import setup_logging

# Development
setup_logging(verbose=True, level='DEBUG', log_file='debug.log')

# Production
setup_logging(verbose=False, level='INFO', log_file='production.log')
```

### 2. Configuration Management

Use YAML files for reproducible experiments:

```python
from softkill9000.config import load_config_from_yaml

# Load from file
config = load_config_from_yaml('experiment_1.yaml')

# Save config for later
import yaml
with open('experiment_1_backup.yaml', 'w') as f:
    yaml.dump(config.dict(), f)
```

### 3. Result Archiving

Always save results with timestamps:

```python
from datetime import datetime
import json

# Run simulation
results = sim.run()

# Save with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"results_{timestamp}.json"

with open(filename, 'w') as f:
    json.dump(results, f, indent=2)
```

### 4. Error Handling

Wrap simulations in try-except blocks:

```python
try:
    sim = MissionSimulator(config=config)
    sim.setup()
    results = sim.run()
except Exception as e:
    logger.error(f"Simulation failed: {e}", exc_info=True)
    # Handle error appropriately
```

### 5. Performance Optimization

For large-scale experiments:

```python
# Reduce training episodes for faster iteration
config = SimulationConfig(
    agents=[...],
    q_learning=QLearningConfig(episodes=500)  # Instead of 1000
)

# Disable verbose logging in production
setup_logging(verbose=False)

# Batch process simulations
# (see Use Case 4 above)
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'softkill9000'`

**Solution**:
```bash
# Reinstall in editable mode
pip install -e .

# Verify installation
pip list | grep softkill9000
```

#### 2. Configuration Validation Errors

**Problem**: `ValidationError: num_timesteps must be >= 10`

**Solution**: Check configuration bounds:
```python
# Invalid
MissionConfig(num_timesteps=5)  # Too low

# Valid
MissionConfig(num_timesteps=10)  # Minimum is 10
```

#### 3. Low Test Coverage Warning

**Problem**: Tests running but coverage is low

**Solution**:
```bash
# Run tests with coverage
pytest --cov=softkill9000 --cov-report=html

# View detailed report
open htmlcov/index.html
```

#### 4. API Server Won't Start

**Problem**: Port already in use

**Solution**:
```bash
# Use different port
uvicorn softkill9000.api.server:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

#### 5. Slow Q-Learning Training

**Problem**: Training takes too long

**Solution**:
```python
# Reduce episodes
QLearningConfig(episodes=500)  # Instead of 1000

# Or disable Q-learning temporarily
# (agents will use rule-based logic)
```

### Debug Mode

Enable maximum verbosity:

```python
import logging
from softkill9000 import setup_logging

# Set to DEBUG level
setup_logging(verbose=True, level='DEBUG')

# Enable all loggers
logging.getLogger().setLevel(logging.DEBUG)
```

### Getting Help

1. **Check logs**: Look at console output or log files
2. **Read error messages**: Pydantic provides detailed validation errors
3. **Check documentation**: API reference for correct usage
4. **GitHub Issues**: https://github.com/BkAsDrP/Softkill9000/issues

---

## Additional Resources

- **[Architecture Guide](architecture.md)**: Understanding system design
- **[API Reference](api_reference.md)**: Complete API documentation
- **[Deployment Guide](deployment.md)**: Production deployment
- **[GitHub Repository](https://github.com/BkAsDrP/Softkill9000)**: Source code and examples

---

**Last Updated**: November 12, 2025  
**Version**: 1.0.0  
**Maintained By**: MotionBlendAI Team
