# 🌌 SOFTKILL-9000

**Multi-Agent Cosmic Mission Simulator with Ethics-Aware Reinforcement Learning**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BkAsDrP/Softkill9000/blob/main/examples/run_in_colab.ipynb)

SOFTKILL-9000 is a sophisticated multi-agent reinforcement learning framework for simulating cosmic missions with ethics-aware decision-making, advanced motion capture integration, and real-time visualization capabilities. Designed for research in multi-agent systems, motion blending AI, and kinetic ledger applications.

> **🚀 Try it now!** Run the [interactive demo on Google Colab](https://colab.research.google.com/github/BkAsDrP/Softkill9000/blob/main/examples/run_in_colab.ipynb) - no installation required!

## ✨ Features

- **🤖 Multi-Agent System**: Coordinate up to 8 specialized agent roles with distinct capabilities and behaviors
- **🧠 Ethics-Aware RL**: Q-learning with integrated ethical reward shaping for responsible AI decision-making
- **🎮 Rich Simulations**: Dynamic scenarios across 17 galaxies with varied terrain and weather conditions
- **📊 Advanced Visualization**: Radar charts, reward curves, and animated mission timelines
- **🌐 REST API**: FastAPI-based service for remote mission execution and monitoring
- **🎨 Interactive UI**: Gradio-powered web interface for live mission visualization
- **📝 Comprehensive Logging**: Verbose entry/exit tracking with structured output
- **⚙️ Flexible Configuration**: YAML/JSON config files with Pydantic validation

## 🚀 Quick Start

### Option 1: Try on Google Colab (No Installation Required!)

Click the badge above or [open the interactive notebook](https://colab.research.google.com/github/BkAsDrP/Softkill9000/blob/main/examples/run_in_colab.ipynb) to:
- Run simulations in your browser
- Visualize agent trajectories and performance
- Train agents with Q-learning
- Experiment with custom configurations

See [COLAB_SETUP.md](COLAB_SETUP.md) for detailed instructions.

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/BkAsDrP/Softkill9000.git
cd Softkill9000

# Install with all optional dependencies
pip install -e ".[all]"

# Or install minimal version
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/BkAsDrP/Softkill9000.git
```

> **Note for Google Colab users**: After installation, upgrade NumPy to v2.0.x for compatibility:
> ```python
> !pip install --upgrade "numpy>=2.0.0,<2.1.0"
> ```
> Then **restart the runtime** (Runtime → Restart runtime) before importing the package.
> See [COLAB_SETUP.md](COLAB_SETUP.md) for details.

### Basic Usage

```python
from softkill9000 import setup_logging, MissionSimulator
from softkill9000.agents.agent import Agent
from softkill9000.environments.environment import CosmicScenario

# Enable verbose logging
setup_logging(verbose=True, log_file='mission.log')

# Create agents
agents = [
    Agent(agent_id="Scout", role="scout"),
    Agent(agent_id="Medic", role="medic"),
    Agent(agent_id="Assault", role="assault")
]

# Create scenario
scenario = CosmicScenario.generate_random(
    width=100.0, height=100.0, num_objectives=3, num_obstacles=5
)

# Run simulation
simulator = MissionSimulator(agents=agents, scenario=scenario, timesteps=20)
results = simulator.run_simulation()

# Access results
print(f"Total Reward: {results['total_reward']:.2f}")
print(f"Objectives Completed: {results['objectives_completed']}")
```

### Command Line Interface

```bash
# Run with default settings
python -m softkill9000

# Run with custom parameters
python -m softkill9000 --timesteps 50 --verbose

# Use custom configuration
python -m softkill9000 --config configs/custom.yaml
```

### Run Interactive UI

```bash
# Launch Gradio interface
python -m examples.gradio_demo
```

### Start REST API Server

```bash
# Launch API server
softkill9000-api

# Or using uvicorn directly
uvicorn softkill9000.api.server:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/api/docs for interactive API documentation.

## 📚 Examples

- **[Google Colab Demo](examples/run_in_colab.ipynb)**: Interactive notebook with complete walkthrough
  - Installation and setup
  - Basic and advanced simulations
  - Visualization and analysis
  - Q-learning training
  - Custom configurations
- **[Setup Guide](COLAB_SETUP.md)**: Detailed instructions for running on Google Colab

## 📦 Project Structure

```
Softkill9000/
├── src/softkill9000/          # Main package source
│   ├── agents/                # Agent classes and squad management
│   ├── environments/          # Mission environments and scenarios
│   ├── visualization/         # Plotting and animation tools
│   ├── api/                   # FastAPI REST endpoints
│   ├── config/                # Pydantic configuration models
│   ├── utils/                 # Logging and helper utilities
│   └── simulator.py           # Main simulation orchestrator
├── configs/                   # Configuration files
│   └── default_config.yaml    # Default simulation settings
├── examples/                  # Example notebooks and scripts
├── tests/                     # Unit and integration tests
├── docs/                      # Documentation
└── assets/                    # Static assets and resources
```

## 🎯 Core Concepts

### Agent Roles

| Role | Description | Species | Key Attributes |
|------|-------------|---------|----------------|
| **Longsight** | Marksman with Q-learning | Vyr'khai | High Strength, Tactical |
| **Lifebinder** | Medic-priest | Lumenari | High Empathy, Healing Focus |
| **Specter** | Recon specialist | Zephryl | High Mobility, Stealth |
| **Whisper** | Diplomat | Mycelian | High Empathy, Negotiation |
| **Archivist** | Knowledge keeper | Ferroth | High Intelligence, Documentation |
| **Brawler** | Combat specialist | Aetherborn | High Strength, Close Combat |
| **Armsmaster** | Weapons expert | Kinetari | High Tactical, Ranged Combat |
| **Explosives Expert** | Demolitions | Verdan | High Tactical, Demolition |

### Actions

- **Advance**: Move forward toward objectives
- **Defend**: Hold position and protect
- **Stabilise**: Provide medical/technical support
- **Negotiate**: Diplomatic engagement
- **Withdraw**: Strategic retreat

### Ethics Framework

The simulation includes ethics-aware reward shaping:

- **Save Civilian**: +8 reward bonus
- **Collateral Damage**: -8 reward penalty
- **Document Events**: +3 (Archivist specialty)
- **Deescalate Conflict**: +5 reward bonus

## 🔧 Configuration

### YAML Configuration

```yaml
mission:
  num_timesteps: 60
  ethics_enabled: true

q_learning:
  episodes: 1000
  gamma: 0.90
  alpha: 0.30
  epsilon: 0.20

agents:
  - role: "Longsight"
    species: "Vyr'khai"
    base_strength: 60
    base_empathy: 60
    base_intelligence: 60
    base_mobility: 60
    base_tactical: 60
```

### Python Configuration

```python
from softkill9000.config import SimulationConfig, AgentConfig, MissionConfig

config = SimulationConfig(
    agents=[
        AgentConfig(role="Longsight", species="Vyr'khai"),
        AgentConfig(role="Lifebinder", species="Lumenari")
    ],
    mission=MissionConfig(num_timesteps=100, ethics_enabled=True)
)

simulator = MissionSimulator(config=config)
results = simulator.run()
```

## 📊 Visualization

### Radar Chart

```python
from softkill9000.visualization import create_radar_chart

stats = results['agent_stats']
fig = create_radar_chart(stats)
fig.savefig('squad_capabilities.png')
```

### Reward Curves

```python
from softkill9000.visualization import create_reward_curve

reward_history = results['reward_history']
fig = create_reward_curve(reward_history)
fig.savefig('mission_rewards.png')
```

### Animated Timeline

```python
from softkill9000.visualization import create_mission_timeline_gif

trajectories = results['trajectories']
gif_path = create_mission_timeline_gif(trajectories)
print(f"Animation saved to: {gif_path}")
```

## 🌐 API Reference

### Start Simulation

```bash
curl -X POST "http://localhost:8000/api/simulations" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "mission": {"num_timesteps": 60, "ethics_enabled": true}
    }
  }'
```

### Get Simulation Results

```bash
curl "http://localhost:8000/api/simulations/{simulation_id}"
```

### List Available Configurations

```bash
# Get species modifiers
curl "http://localhost:8000/api/config/species"

# Get agent roles
curl "http://localhost:8000/api/config/roles"

# Get scenario templates
curl "http://localhost:8000/api/config/scenarios"
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=softkill9000 --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)**: System design and component interaction
- **[API Reference](docs/api_reference.md)**: Detailed API documentation
- **[User Guide](docs/user_guide.md)**: Comprehensive usage examples
- **[Deployment Guide](docs/deployment.md)**: Production deployment instructions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MotionBlendAI Team for motion capture integration
- BlendAnim for animation blending frameworks
- Kinetic Ledger project for motion tracking systems

## 📧 Contact

- **Project Lead**: MotionBlendAI Team
- **Repository**: https://github.com/BkAsDrP/Softkill9000
- **Issues**: https://github.com/BkAsDrP/Softkill9000/issues

## 🔮 Roadmap

- [ ] Real-time motion capture integration
- [ ] Advanced multi-agent communication protocols
- [ ] Neural network policy learning
- [ ] Distributed simulation support
- [ ] VR/AR visualization interface
- [ ] Cloud deployment templates

---

**Built with ❤️ by the MotionBlendAI Team**
