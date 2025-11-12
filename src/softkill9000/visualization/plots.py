"""
Visualization module for SOFTKILL-9000.

Provides plotting and animation functions for mission data visualization.
"""

import logging
import io
import tempfile
from typing import Dict, List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt

from ..utils.logging_utils import logger_decorator

logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import imageio
    GIF_AVAILABLE = True
except ImportError:
    GIF_AVAILABLE = False
    logger.warning("imageio not available - GIF generation disabled")


@logger_decorator(log_entry=True, log_exit=True, log_time=True)
def create_radar_chart(
    agent_stats: Dict[str, Dict[str, int]],
    title: str = "Squad Capability Radar",
    figsize: Tuple[int, int] = (8, 8)
) -> plt.Figure:
    """
    Create a radar chart showing agent capabilities.
    
    Args:
        agent_stats: Dictionary mapping agent roles to their stats
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib Figure object
        
    Example:
        >>> stats = {
        ...     "Longsight": {"Strength": 66, "Empathy": 58, ...},
        ...     "Lifebinder": {"Strength": 61, "Empathy": 68, ...}
        ... }
        >>> fig = create_radar_chart(stats)
    """
    logger.info(f"Creating radar chart for {len(agent_stats)} agents")
    
    # Get attribute labels from first agent
    labels = list(next(iter(agent_stats.values())).keys())
    num_vars = len(labels)
    
    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    
    # Plot each agent
    for role, stats in agent_stats.items():
        values = list(stats.values())
        values += values[:1]  # Complete the circle
        
        ax.plot(angles, values, label=role, linewidth=2)
        ax.fill(angles, values, alpha=0.15)
    
    # Customize chart
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 150)
    ax.set_title(title, y=1.1, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1))
    ax.grid(True)
    
    fig.tight_layout()
    logger.debug("Radar chart created successfully")
    
    return fig


@logger_decorator(log_entry=True, log_exit=True, log_time=True)
def create_reward_curve(
    reward_history: Dict[str, List[float]],
    title: str = "Cumulative Reward // Cosmic Mission",
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Create a line plot showing cumulative rewards over time.
    
    Args:
        reward_history: Dictionary mapping agent roles to reward lists
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib Figure object
    """
    logger.info(f"Creating reward curve for {len(reward_history)} agents")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each agent's reward history
    for role, rewards in reward_history.items():
        ax.plot(rewards, label=role, linewidth=2, marker='o', markersize=3, alpha=0.8)
    
    # Customize chart
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Mission Ticks", fontsize=12)
    ax.set_ylabel("Cumulative Reward", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    fig.tight_layout()
    logger.debug("Reward curve created successfully")
    
    return fig


@logger_decorator(log_entry=True, log_exit=True, log_time=True)
def create_mission_timeline_gif(
    trajectories: Dict[str, List[Tuple[float, float]]],
    duration: float = 0.15,
    figsize: Tuple[int, int] = (6, 6),
    dpi: int = 120
) -> Optional[str]:
    """
    Create an animated GIF showing agent movement over time.
    
    Args:
        trajectories: Dictionary mapping agent roles to position trajectories
        duration: Frame duration in seconds
        figsize: Figure size tuple
        dpi: DPI for rendered frames
        
    Returns:
        Path to generated GIF file, or None if imageio not available
        
    Note:
        Requires imageio to be installed
    """
    if not GIF_AVAILABLE:
        logger.warning("Cannot create GIF - imageio not installed")
        return None
    
    logger.info(f"Creating mission timeline GIF with {len(trajectories)} agents")
    
    # Determine number of frames
    num_frames = len(next(iter(trajectories.values())))
    logger.debug(f"Generating {num_frames} frames")
    
    frames = []
    
    # Generate each frame
    for t in range(num_frames):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("X Position")
        ax.set_ylabel("Y Position")
        ax.set_title(f"Mission Map — Timeline (t={t})", fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot each agent's position and trail
        for role, trajectory in trajectories.items():
            if t < len(trajectory):
                # Plot trail up to current time
                trail_x = [pos[0] for pos in trajectory[:t+1]]
                trail_y = [pos[1] for pos in trajectory[:t+1]]
                ax.plot(trail_x, trail_y, alpha=0.5, linewidth=1.5)
                
                # Plot current position
                x, y = trajectory[t]
                ax.scatter([x], [y], s=100, alpha=0.8, edgecolors='black', linewidths=1.5)
                ax.text(x, y, f" {role}", fontsize=9, verticalalignment='center')
        
        fig.tight_layout()
        
        # Render to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        
        # Read as image
        frames.append(imageio.v2.imread(buf))
        buf.close()
        
        if (t + 1) % 10 == 0:
            logger.debug(f"Generated frame {t + 1}/{num_frames}")
    
    # Save as GIF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
    output_path = temp_file.name
    temp_file.close()
    
    imageio.mimsave(output_path, frames, duration=duration)
    logger.info(f"Mission timeline GIF saved to: {output_path}")
    
    return output_path


@logger_decorator(log_entry=True, log_exit=True)
def create_mission_snapshot(
    trajectories: Dict[str, List[Tuple[float, float]]],
    current_timestep: int,
    figsize: Tuple[int, int] = (8, 8)
) -> plt.Figure:
    """
    Create a static snapshot of agent positions at a specific timestep.
    
    Args:
        trajectories: Dictionary mapping agent roles to position trajectories
        current_timestep: Timestep to visualize
        figsize: Figure size tuple
        
    Returns:
        Matplotlib Figure object
    """
    logger.info(f"Creating mission snapshot at timestep {current_timestep}")
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("X Position", fontsize=12)
    ax.set_ylabel("Y Position", fontsize=12)
    ax.set_title(f"Mission Snapshot (t={current_timestep})", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot each agent
    for role, trajectory in trajectories.items():
        if current_timestep < len(trajectory):
            # Plot full trail
            trail_x = [pos[0] for pos in trajectory[:current_timestep+1]]
            trail_y = [pos[1] for pos in trajectory[:current_timestep+1]]
            ax.plot(trail_x, trail_y, alpha=0.6, linewidth=2, label=role)
            
            # Plot current position
            x, y = trajectory[current_timestep]
            ax.scatter([x], [y], s=150, alpha=0.9, edgecolors='black', linewidths=2)
            ax.text(x + 0.02, y + 0.02, role, fontsize=10, fontweight='bold')
    
    ax.legend(loc='best')
    fig.tight_layout()
    
    return fig


def close_all_figures() -> None:
    """
    Close all matplotlib figures to free memory.
    
    Useful for batch processing or notebook environments.
    """
    plt.close('all')
    logger.debug("All matplotlib figures closed")
