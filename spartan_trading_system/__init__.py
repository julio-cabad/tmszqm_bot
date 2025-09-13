"""
Spartan Squeeze Magic Trading System
A professional multi-cryptocurrency trading system combining Squeeze Momentum and Trend Magic indicators.
"""

__version__ = "1.0.0"
__author__ = "Spartan Trading Gods"
__description__ = "Multi-crypto trading system with Squeeze Momentum and Trend Magic indicators"

from .config.strategy_config import StrategyConfig
from .config.config_manager import ConfigManager

__all__ = ['StrategyConfig', 'ConfigManager']