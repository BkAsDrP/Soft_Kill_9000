# Changelog

All notable changes to SOFTKILL-9000 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-12

### Added
- **Core Features**
  - Multi-agent reinforcement learning framework
  - 8 specialized agent roles with unique capabilities
  - Ethics-aware reward shaping system
  - Q-learning implementation with configurable parameters
  - Dynamic scenario generation across 17 galaxies

- **Visualization**
  - Radar charts for agent capability comparison
  - Cumulative reward curves over mission timeline
  - Animated GIF generation for mission trajectories
  - Mission snapshot visualization

- **API & Configuration**
  - FastAPI-based REST API for remote simulation
  - Pydantic models for configuration validation
  - YAML/JSON configuration file support
  - Default configuration templates

- **Development Tools**
  - Comprehensive logging with entry/exit decorators
  - Type hints throughout codebase
  - Unit test framework with pytest
  - Code formatting with Black and isort

- **Documentation**
  - Comprehensive README with quick start guide
  - API reference documentation
  - Contributing guidelines
  - MIT license

### Project Structure
- Modular package organization under `src/softkill9000/`
  - `agents/`: Agent classes and squad management
  - `environments/`: Mission scenarios and reward systems
  - `visualization/`: Plotting and animation tools
  - `api/`: REST API endpoints
  - `config/`: Configuration models
  - `utils/`: Logging and utilities

### Dependencies
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- pydantic >= 2.0.0
- fastapi >= 0.104.0
- gradio >= 4.0.0 (optional)
- imageio >= 2.31.0 (optional)

### Agent Roles
- Longsight (Marksman with Q-learning)
- Lifebinder (Medic specialist)
- Specter (Recon operative)
- Whisper (Diplomatic negotiator)
- Archivist (Knowledge keeper)
- Brawler (Combat specialist)
- Armsmaster (Weapons expert)
- Explosives Expert (Demolitions)

### Ethics Framework
- Save Civilian: +8 reward
- Collateral Damage: -8 penalty
- Document Events: +3 reward
- Deescalate Conflict: +5 reward

### Known Issues
- GIF generation requires imageio package
- TTS features require gTTS package
- Some type checking warnings with decorators (non-breaking)

## [0.1.0] - 2025-11-11 (Beta)

### Added
- Initial prototype with notebook implementation
- Basic agent action selection
- Simple reward system
- Gradio UI demo

---

**Note**: This project has been restructured from notebook prototypes to a professional
Python package with proper architecture, documentation, and testing infrastructure.
