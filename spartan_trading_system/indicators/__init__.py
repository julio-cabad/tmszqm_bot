"""
Indicator Integration for Spartan Trading System
Wraps existing indicators with configuration support
"""

from .indicator_engine import IndicatorEngine
from .result_models import TrendMagicResult, SqueezeResult, MultiTimeframeAnalysis

__all__ = ['IndicatorEngine', 'TrendMagicResult', 'SqueezeResult', 'MultiTimeframeAnalysis']