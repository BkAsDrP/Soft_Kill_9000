# Running SOFTKILL-9000 on Google Colab

This guide shows you how to run SOFTKILL-9000 in Google Colab to see your changes in action.

## 🚀 Quick Start

### Option 1: Use the Pre-built Notebook (Recommended)

1. **Open the Colab Notebook**:
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click **File → Open notebook**
   - Select the **GitHub** tab
   - Enter: `BkAsDrP/Softkill9000`
   - Open `examples/run_in_colab.ipynb`

2. **Run the Cells**:
   - Click **Runtime → Run all** or run cells individually
   - The notebook will automatically install the package and run demonstrations

### Option 2: Quick Installation in Any Colab Notebook

Create a new Colab notebook and run:

```python
# Install SOFTKILL-9000 from GitHub
!pip install git+https://github.com/BkAsDrP/Softkill9000.git -q

# Upgrade NumPy to resolve dependency conflicts (Colab has older NumPy by default)
# This fixes conflicts with jax, opencv, pytensor, and thinc
!pip install --upgrade "numpy>=2.0.0,<3.0.0" -q

# Verify installation
import softkill9000
print(f"✅ SOFTKILL-9000 v{softkill9000.__version__} installed!")

# Verify NumPy version
import numpy as np
print(f"✅ NumPy {np.__version__} (compatible with modern ML libraries)")
```

## 📋 Step-by-Step Demo

### 1. Basic Simulation

```python
from softkill9000.simulator import MissionSimulator
from softkill9000.agents.agent import Agent
from softkill9000.environments.environment import CosmicScenario

# Create agents
agents = [
    Agent(agent_id="Scout", role="scout"),
    Agent(agent_id="Medic", role="medic"),
    Agent(agent_id="Assault", role="assault")
]

# Create scenario
scenario = CosmicScenario.generate_random(
    width=100.0,
    height=100.0,
    num_objectives=3,
    num_obstacles=5
)

# Run simulation
simulator = MissionSimulator(agents=agents, scenario=scenario, timesteps=20)
results = simulator.run_simulation()

# Display results
print(f"Total Reward: {results['total_reward']:.2f}")
print(f"Objectives Completed: {results['objectives_completed']}")
print(f"Average Health: {results['average_health']:.1f}%")
```

### 2. Visualize Trajectories

```python
import matplotlib.pyplot as plt
from softkill9000.visualization import plot_agent_trajectories

# Plot agent paths
fig = plot_agent_trajectories(results['agent_histories'], scenario)
plt.show()
```

### 3. Performance Metrics

```python
from softkill9000.visualization import plot_performance_metrics

# Plot health, morale, and energy over time
fig = plot_performance_metrics(results['agent_histories'])
plt.tight_layout()
plt.show()
```

### 4. Q-Learning Training

```python
from softkill9000.environments.environment import QLearningTrainer
from softkill9000.config.models import QLearningConfig

# Configure training
config = QLearningConfig(
    learning_rate=0.1,
    discount_factor=0.95,
    exploration_rate=0.2
)

trainer = QLearningTrainer(config=config)

# Training loop
for episode in range(50):
    # Create fresh scenario
    scenario = CosmicScenario.generate_random(100.0, 100.0, 3, 5)
    
    # Run episode
    sim = MissionSimulator(agents=agents, scenario=scenario, timesteps=20)
    results = sim.run_simulation()
    
    # Train agents (simplified)
    for agent in agents:
        state = hash((agent.position.x, agent.position.y))
        trainer.train_agent(agent, state, "move", results['total_reward'], state)
    
    if (episode + 1) % 10 == 0:
        print(f"Episode {episode + 1}: Reward = {results['total_reward']:.2f}")
```

## 🔧 Testing Your Changes

### If you've made local changes to the code:

1. **Push your changes to GitHub**:
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```

2. **In Colab, install from your branch**:
   ```python
   !pip install git+https://github.com/BkAsDrP/Softkill9000.git@your-branch-name -q --force-reinstall
   ```

3. **Restart the runtime** (Runtime → Restart runtime) and re-import:
   ```python
   import softkill9000
   # Your test code here
   ```

## 📊 What the Demo Shows

The Colab notebook demonstrates:

1. ✅ **Installation**: From GitHub repository
2. ✅ **Basic Simulation**: Multi-agent mission execution
3. ✅ **Visualization**: Agent trajectories and performance metrics
4. ✅ **Q-Learning**: Training agents with reinforcement learning
5. ✅ **Custom Configuration**: Using YAML config files
6. ✅ **Statistical Analysis**: Comparing multiple scenario runs

## 🎯 Key Features to Test

### Agent Behaviors
- Watch agents navigate to objectives
- See health/morale changes over time
- Observe different roles (scout, medic, assault)

### Scenario Dynamics
- Random obstacle generation
- Objective placement
- Environmental effects

### Learning Progress
- Q-learning convergence
- Exploration vs exploitation
- Reward optimization

## 💡 Tips for Colab

1. **GPU Acceleration**: For larger simulations, enable GPU
   - Runtime → Change runtime type → GPU

2. **Save Results**: Download outputs before closing
   ```python
   from google.colab import files
   files.download('results.json')
   ```

3. **Mount Google Drive**: Persist data across sessions
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

4. **Check Package Version**: Ensure you have latest changes
   ```python
   !pip show softkill9000 | grep Version
   ```

## 🐛 Troubleshooting

### NumPy Dependency Conflicts
If you see warnings about numpy version conflicts with opencv, jax, pytensor, or thinc:
```python
# Upgrade to NumPy 2.x (required by modern ML libraries)
!pip install --upgrade "numpy>=2.0.0,<3.0.0"

# Verify no conflicts remain
!pip check
```

### Installation Issues
```python
# Force reinstall
!pip uninstall softkill9000 -y
!pip install git+https://github.com/BkAsDrP/Softkill9000.git --force-reinstall
```

### Import Errors
```python
# Restart runtime
import sys
sys.path.append('/usr/local/lib/python3.10/site-packages')
import softkill9000
```

### Visualization Issues
```python
# Ensure matplotlib is working
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
```

## 📚 Additional Resources

- **Full Notebook**: [run_in_colab.ipynb](examples/run_in_colab.ipynb)
- **Documentation**: [docs/](docs/)
- **API Reference**: [docs/api_reference.md](docs/api_reference.md)
- **User Guide**: [docs/user_guide.md](docs/user_guide.md)

## 🎉 Quick Verification Checklist

After running the Colab notebook, you should see:

- ✅ Package installed successfully
- ✅ Simulation runs without errors
- ✅ Agent trajectories plotted
- ✅ Performance metrics displayed
- ✅ Q-learning training progresses
- ✅ Custom configurations work

---

**Ready to explore? Open the [Colab Notebook](https://colab.research.google.com/github/BkAsDrP/Softkill9000/blob/main/examples/run_in_colab.ipynb) now! 🚀**
