"""Command-line interface for SOFTKILL-9000."""

import argparse
import logging
import sys
from pathlib import Path

from . import setup_logging, __version__


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SOFTKILL-9000: Multi-Agent Cosmic Mission Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"SOFTKILL-9000 v{__version__}"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration YAML file"
    )
    
    parser.add_argument(
        "--timesteps",
        type=int,
        default=60,
        help="Number of mission timesteps (default: 60)"
    )
    
    parser.add_argument(
        "--no-ethics",
        action="store_true",
        help="Disable ethics-aware reward shaping"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to JSON file"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        verbose=args.verbose,
        log_file=args.log_file
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"SOFTKILL-9000 v{__version__} CLI started")
    
    try:
        # Import simulator (deferred to avoid import errors at CLI startup)
        from .simulator import MissionSimulator
        from .config.models import SimulationConfig, MissionConfig, AgentConfig
        
        # Load config or create default
        config = None
        if args.config:
            import yaml
            config_path = Path(args.config)
            if config_path.exists():
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
                    config = SimulationConfig(**config_data)
                logger.info(f"Loaded configuration from {args.config}")
            else:
                logger.error(f"Config file not found: {args.config}")
                return 1
        else:
            # Create config with CLI args and default agents
            default_agents = [
                AgentConfig(role="Longsight", species="Vyr'khai"),
                AgentConfig(role="Lifebinder", species="Lumenari"),
                AgentConfig(role="Specter", species="Zephryl"),
            ]
            config = SimulationConfig(
                agents=default_agents,
                mission=MissionConfig(
                    num_timesteps=args.timesteps,
                    ethics_enabled=not args.no_ethics
                )
            )
        
        # Run simulation
        logger.info("Starting mission simulation...")
        simulator = MissionSimulator(config=config)
        results = simulator.run()
        
        # Display results
        print("\n" + "="*80)
        print("MISSION COMPLETE")
        print("="*80)
        print(f"\nScenario: {results['scenario']['description']}")
        print(f"Location: {results['scenario']['galaxy']} // {results['scenario']['planet']}")
        print(f"Environment: {results['scenario']['terrain']} // {results['scenario']['weather']}")
        print(f"\nFinal Rewards:")
        for role, reward in results['final_rewards'].items():
            print(f"  {role:20s}: {reward:8.2f}")
        
        # Export if requested
        if args.export:
            export_path = Path(args.export)
            simulator.export_results(results, str(export_path))
            print(f"\nResults exported to: {export_path}")
        
        logger.info("Mission simulation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Mission simulation failed: {e}", exc_info=True)
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
