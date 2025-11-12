# Contributing to SOFTKILL-9000

Thank you for your interest in contributing to SOFTKILL-9000! This document provides guidelines and instructions for contributing.

## 🌟 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include detailed information**:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and stack traces

### Suggesting Enhancements

1. **Check the roadmap** in README.md
2. **Open an issue** with the enhancement proposal
3. **Describe the use case** and expected benefits
4. **Provide examples** if applicable

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the coding style** (Black, isort, type hints)
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass** before submitting
6. **Write clear commit messages**

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Softkill9000.git
cd Softkill9000

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=softkill9000 --cov-report=html

# Run specific test
pytest tests/test_agents.py::TestAgent::test_action_selection -v
```

## 📝 Code Style

We use:
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## 📚 Documentation

- Add **docstrings** to all public functions/classes (Google style)
- Include **type hints** for function signatures
- Update **README.md** for user-facing changes
- Add **examples** for new features

### Docstring Example

```python
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
        
    Example:
        >>> trainer = QLearningTrainer()
        >>> q_table, keys = trainer.train_agent("Longsight", 1000)
    """
```

## 🔀 Git Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** with clear, atomic commits:
   ```bash
   git commit -m "feat: add advanced navigation system"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/my-new-feature
   ```

## 📋 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add ethics-aware reward calculator`

## 🎯 Areas for Contribution

### High Priority
- Additional agent roles and behaviors
- New scenario types and environments
- Performance optimizations
- Integration tests

### Documentation
- Tutorial notebooks
- API usage examples
- Architecture diagrams
- Deployment guides

### Features
- Real-time motion capture integration
- Advanced visualization options
- Distributed simulation support
- Neural network policies

## ❓ Questions?

- Open an issue with the `question` label
- Join our discussions on GitHub
- Contact the maintainers

## 📜 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 🙏 Thank You!

Your contributions make SOFTKILL-9000 better for everyone. We appreciate your time and effort!
