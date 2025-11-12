"""
SOFTKILL-9000: Multi-Agent Cosmic Mission Simulator

A sophisticated reinforcement learning framework for simulating multi-agent missions
in cosmic environments with ethics-aware decision-making, motion capture integration,
and real-time visualization capabilities.

Authors: MotionBlendAI Team
License: MIT
Version: 1.0.0
"""

import logging
from typing import Optional, List

__version__ = "1.0.0"
__author__ = "MotionBlendAI Team"
__license__ = "MIT"

# Configure package-level logger
logger = logging.getLogger(__name__)

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    Configure logging for the SOFTKILL-9000 package.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path to write logs
        verbose: If True, enables DEBUG level logging with detailed output
    
    Example:
        >>> from softkill9000 import setup_logging
        >>> setup_logging(verbose=True, log_file='mission.log')
    """
    if verbose:
        level = logging.DEBUG
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    logger.info(f"SOFTKILL-9000 v{__version__} logging initialized")

# Conditional imports - only import if components exist
try:
    from .agents import Agent, SquadManager
    from .environments import MissionEnvironment, CosmicScenario
    from .utils import logger_decorator
    
    __all__ = [
        '__version__',
        'setup_logging',
        'Agent',
        'SquadManager',
        'MissionEnvironment',
        'CosmicScenario',
        'logger_decorator',
    ]
except ImportError:
    # If imports fail, only export basics
    __all__ = [
        '__version__',
        'setup_logging',
    ]
