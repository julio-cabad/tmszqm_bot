"""
Signal Types and Data Models for Spartan Trading System
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class SignalType(Enum):
    """Types of trading signals"""
    LONG = "long"
    SHORT = "short"
    SUPER_BULLISH = "super_bullish"
    SUPER_BEARISH = "super_bearish"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"
    MEDIUM_BUY = "medium_buy"
    MEDIUM_SELL = "medium_sell"


class Direction(Enum):
    """Trading direction"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass
class TradingSignal:
    """Trading signal data model"""
    symbol: str
    signal_type: SignalType
    direction: Direction
    strength: float
    confidence: float
    current_price: float
    timestamp: datetime
    
    # Technical indicator data
    trend_magic_value: Optional[float] = None
    trend_magic_color: Optional[str] = None
    squeeze_color: Optional[str] = None
    open_price: Optional[float] = None
    
    # Additional metadata
    timeframe: str = "1h"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type.value,
            'direction': self.direction.value,
            'strength': self.strength,
            'confidence': self.confidence,
            'current_price': self.current_price,
            'timestamp': self.timestamp.isoformat(),
            'trend_magic_value': self.trend_magic_value,
            'trend_magic_color': self.trend_magic_color,
            'squeeze_color': self.squeeze_color,
            'open_price': self.open_price,
            'timeframe': self.timeframe,
            'metadata': self.metadata
        }