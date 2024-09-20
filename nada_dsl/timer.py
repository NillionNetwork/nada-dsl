"""
Timer class

This is a timer class used to measure the performance of different stages 
in the compilation process.  
"""

from dataclasses import dataclass
import functools
import time
from typing import Dict


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Clock:
    """NOP implementation of a Clock"""

    def start(self, timer_name: str):
        """Start the timer"""

    def stop(self, timer_name: str):
        """Stop the timer"""

    def report(self) -> Dict[str, float]:
        """Report"""
        return {}


@dataclass
class DefaultClock(Clock):
    """Default implementation for a clock

    The clock keeps a list of timers and implements functions to keep track of
    different timers in a dictionary.

    """

    timers: Dict[str, float]

    def __init__(self):
        self.timers = {}

    def start(self, timer_name: str):
        if timer_name in self.timers:
            raise TimerError(f"timer {timer_name} already running.")
        self.timers[timer_name] = time.perf_counter()

    def stop(self, timer_name: str):
        if self.timers.get(timer_name) is None:
            raise TimerError(
                f"timer {timer_name} is not running, use start() to start it."
            )
        self.timers[timer_name] = time.perf_counter() - self.timers[timer_name]

    def report(self) -> Dict[str, float]:
        return self.timers


@dataclass
class Timer:
    """Timer.

    Basic Timer implementation
    """

    clock: Clock

    def __init__(self):
        self.clock = Clock()

    def enable(self):
        """Enable the timer."""
        self.clock = DefaultClock()

    def is_enabled(self) -> bool:
        """Returns true if the timer is enabled."""
        return isinstance(self.clock, DefaultClock)

    def start(self, timer_name: str):
        """Starts the timer

        Args:
            timer_name (str): The identifier of the timer.
        """
        self.clock.start(timer_name)

    def stop(self, timer_name: str):
        """Stop the timer"""
        self.clock.stop(timer_name)

    def report(self):
        """Returns the report provided by the clock implementation."""
        return self.clock.report()


# Global timer
timer = Timer()


def add_timer(timer_name: str):
    """Add timer decorator.

    Decorator to simplify adding timers.

    Args:
        func (object): The function being decorated
        timer_name (str): The name of the timer

    """

    def decorator_add_timer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer.start(timer_name)
            value = func(*args, **kwargs)
            timer.stop(timer_name)
            return value

        return wrapper

    return decorator_add_timer
