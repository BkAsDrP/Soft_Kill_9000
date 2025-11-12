"""
Logging utilities for SOFTKILL-9000.

Provides decorators and utilities for comprehensive function entry/exit logging,
performance tracking, and error handling.
"""

import logging
import functools
import time
from typing import Callable, Any, Optional, TypeVar, cast
from types import TracebackType
import inspect

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def logger_decorator(
    log_entry: bool = True,
    log_exit: bool = True,
    log_args: bool = True,
    log_return: bool = False,
    log_time: bool = True,
    level: int = logging.DEBUG
) -> Callable[[F], F]:
    """
    Decorator for comprehensive function logging with entry/exit tracking.
    
    Args:
        log_entry: Log function entry with arguments
        log_exit: Log function exit
        log_args: Include function arguments in entry log
        log_return: Include return value in exit log
        log_time: Log execution time
        level: Logging level to use
    
    Returns:
        Decorated function with logging capabilities
    
    Example:
        >>> @logger_decorator(log_return=True, log_time=True)
        >>> def train_agent(episodes: int) -> dict:
        >>>     # Training logic here
        >>>     return {"status": "complete"}
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_logger = logging.getLogger(func.__module__)
            func_name = func.__name__
            
            # Log entry
            if log_entry:
                if log_args:
                    # Get function signature for better arg logging
                    sig = inspect.signature(func)
                    bound_args = sig.bind_partial(*args, **kwargs)
                    bound_args.apply_defaults()
                    args_str = ", ".join(f"{k}={v}" for k, v in bound_args.arguments.items())
                    func_logger.log(level, f"→ ENTER {func_name}({args_str})")
                else:
                    func_logger.log(level, f"→ ENTER {func_name}")
            
            # Execute function with timing
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                
                # Log successful exit
                if log_exit:
                    exit_msg = f"← EXIT {func_name}"
                    if log_time:
                        exit_msg += f" [elapsed: {elapsed_time:.4f}s]"
                    if log_return and result is not None:
                        # Truncate long return values
                        result_str = str(result)
                        if len(result_str) > 200:
                            result_str = result_str[:200] + "..."
                        exit_msg += f" [return: {result_str}]"
                    func_logger.log(level, exit_msg)
                
                return result
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                func_logger.error(
                    f"✗ ERROR in {func_name} after {elapsed_time:.4f}s: {type(e).__name__}: {str(e)}"
                )
                raise
        
        return cast(F, wrapper)
    return decorator


class LogContext:
    """
    Context manager for scoped logging with indentation.
    
    Example:
        >>> with LogContext("Training Phase", logger):
        >>>     # All logs in this block will be indented
        >>>     train_model()
    """
    
    def __init__(
        self,
        context_name: str,
        logger: logging.Logger,
        level: int = logging.INFO
    ):
        """
        Initialize log context.
        
        Args:
            context_name: Name of the context for logging
            logger: Logger instance to use
            level: Logging level
        """
        self.context_name = context_name
        self.logger = logger
        self.level = level
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> 'LogContext':
        """Enter context and log start."""
        self.start_time = time.time()
        self.logger.log(self.level, f"╔══ {self.context_name} START ══╗")
        return self
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> bool:
        """Exit context and log completion."""
        elapsed = time.time() - (self.start_time or 0.0)
        if exc_type is None:
            self.logger.log(
                self.level,
                f"╚══ {self.context_name} COMPLETE [{elapsed:.4f}s] ══╝"
            )
        else:
            self.logger.error(
                f"╚══ {self.context_name} FAILED [{elapsed:.4f}s] "
                f"[{exc_type.__name__}: {exc_val}] ══╝"
            )
        return False


def log_data_shape(data: Any, name: str = "data", logger: Optional[logging.Logger] = None) -> None:
    """
    Log the shape/size of data structures (arrays, lists, dicts).
    
    Args:
        data: Data structure to log
        name: Name for the data in logs
        logger: Logger to use (defaults to module logger)
    
    Example:
        >>> log_data_shape(rewards_array, "training_rewards")
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        if hasattr(data, 'shape'):
            # NumPy array or similar
            logger.debug(f"Data '{name}' shape: {data.shape}, dtype: {data.dtype}")
        elif isinstance(data, (list, tuple)):
            logger.debug(f"Data '{name}' length: {len(data)}, type: {type(data).__name__}")
        elif isinstance(data, dict):
            logger.debug(f"Data '{name}' keys: {len(data)}, type: dict")
        else:
            logger.debug(f"Data '{name}' type: {type(data).__name__}")
    except Exception as e:
        logger.warning(f"Could not log shape for '{name}': {e}")
