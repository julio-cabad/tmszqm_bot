"""
Strategy Configuration Dataclass
Comprehensive configuration for all Spartan Trading System parameters
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json


@dataclass
class StrategyConfig:
    """
    Comprehensive configuration for Spartan Squeeze Magic Strategy
    All parameters are configurable for maximum flexibility
    """
    
    # Multi-Crypto Configuration
    symbols: List[str] = field(default_factory=lambda: [
        # Top Tier - Major Cryptos
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT",
        # Tier 1 - Established Altcoins
        "BNBUSDT", "XRPUSDT", "MATICUSDT", "AVAXUSDT", "LINKUSDT",
        # Tier 2 - Promising Projects
        "ATOMUSDT", "ALGOUSDT", "VETUSDT", "FTMUSDT", "NEARUSDT",
        # Tier 3 - Emerging Opportunities
        "SANDUSDT", "MANAUSDT", "CHZUSDT", "ENJUSDT", "GALAUSDT"
    ])
    max_concurrent_symbols: int = 20
    
    # Trend Magic Parameters (Fully Configurable)
    trend_magic_cci_period: int = 20
    trend_magic_atr_multiplier: float = 1.0
    trend_magic_atr_period: int = 5
    trend_magic_version: str = "v3"  # v1, v2, v3 (TA-Lib)
    
    # Squeeze Momentum Parameters
    squeeze_bb_length: int = 20
    squeeze_bb_multiplier: float = 2.0
    squeeze_kc_length: int = 20
    squeeze_kc_multiplier: float = 1.5
    squeeze_use_true_range: bool = True
    
    # Timeframe Configuration (Fully Configurable)
    primary_timeframe: str = "1h"
    confirmation_timeframe: str = "30m"
    context_timeframe: str = "4h"
    monitoring_timeframe: str = "15m"  # For real-time monitoring
    
    # Data Management
    candles_limit: int = 100  # Optimized for speed
    update_interval: int = 30  # Seconds between updates
    
    # Risk Management
    risk_percentage: float = 2.0
    max_positions: int = 3
    max_positions_per_symbol: int = 1
    
    # Signal Configuration
    min_signal_strength: float = 0.7  # Minimum signal strength (0-1)
    require_multi_timeframe_confirmation: bool = True
    
    # Alert Settings
    enable_audio_alerts: bool = True
    alert_sound_bullish: str = "sounds/bullish_alert.wav"
    alert_sound_bearish: str = "sounds/bearish_alert.wav"
    alert_sound_breakout: str = "sounds/breakout_alert.wav"
    alert_sound_notification: str = "sounds/notification.wav"
    
    # Performance Settings
    enable_performance_tracking: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Database Configuration
    database_path: str = "data/spartan_trading.db"
    
    # API Configuration
    api_rate_limit: int = 1200  # Requests per minute
    api_timeout: int = 30  # Seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyConfig':
        """Create configuration from dictionary"""
        # Filter only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StrategyConfig':
        """Create configuration from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """
        Validate configuration parameters
        Returns list of validation errors
        """
        errors = []
        
        # Validate symbols
        if not self.symbols:
            errors.append("At least one symbol must be configured")
        
        if len(self.symbols) > self.max_concurrent_symbols:
            errors.append(f"Number of symbols ({len(self.symbols)}) exceeds max_concurrent_symbols ({self.max_concurrent_symbols})")
        
        # Validate Trend Magic parameters
        if self.trend_magic_cci_period < 1 or self.trend_magic_cci_period > 200:
            errors.append("trend_magic_cci_period must be between 1 and 200")
        
        if self.trend_magic_atr_multiplier < 0.1 or self.trend_magic_atr_multiplier > 10.0:
            errors.append("trend_magic_atr_multiplier must be between 0.1 and 10.0")
        
        if self.trend_magic_atr_period < 1 or self.trend_magic_atr_period > 50:
            errors.append("trend_magic_atr_period must be between 1 and 50")
        
        if self.trend_magic_version not in ["v1", "v2", "v3"]:
            errors.append("trend_magic_version must be 'v1', 'v2', or 'v3'")
        

        
        # Validate Squeeze parameters
        if self.squeeze_bb_length < 5 or self.squeeze_bb_length > 100:
            errors.append("squeeze_bb_length must be between 5 and 100")
        
        if self.squeeze_bb_multiplier < 0.5 or self.squeeze_bb_multiplier > 5.0:
            errors.append("squeeze_bb_multiplier must be between 0.5 and 5.0")
        
        # Validate timeframes
        valid_timeframes = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
        
        if self.primary_timeframe not in valid_timeframes:
            errors.append(f"primary_timeframe must be one of: {valid_timeframes}")
        
        if self.confirmation_timeframe not in valid_timeframes:
            errors.append(f"confirmation_timeframe must be one of: {valid_timeframes}")
        
        if self.context_timeframe not in valid_timeframes:
            errors.append(f"context_timeframe must be one of: {valid_timeframes}")
        
        # Validate risk parameters
        if self.risk_percentage < 0.1 or self.risk_percentage > 10.0:
            errors.append("risk_percentage must be between 0.1 and 10.0")
        
        if self.max_positions < 1 or self.max_positions > 20:
            errors.append("max_positions must be between 1 and 20")
        
        # Validate signal parameters
        if self.min_signal_strength < 0.0 or self.min_signal_strength > 1.0:
            errors.append("min_signal_strength must be between 0.0 and 1.0")
        
        # Validate performance parameters
        if self.candles_limit < 20 or self.candles_limit > 1500:
            errors.append("candles_limit must be between 20 and 1500")
        
        if self.update_interval < 5 or self.update_interval > 300:
            errors.append("update_interval must be between 5 and 300 seconds")
        
        return errors
    
    def get_trend_magic_params(self) -> Dict[str, Any]:
        """Get Trend Magic parameters as dictionary"""
        return {
            'period': self.trend_magic_cci_period,
            'coeff': self.trend_magic_atr_multiplier,
            'atr_period': self.trend_magic_atr_period
        }
    
    def get_squeeze_params(self) -> Dict[str, Any]:
        """Get Squeeze Momentum parameters as dictionary"""
        return {
            'bb_length': self.squeeze_bb_length,
            'bb_mult': self.squeeze_bb_multiplier,
            'kc_length': self.squeeze_kc_length,
            'kc_mult': self.squeeze_kc_multiplier,
            'use_true_range': self.squeeze_use_true_range
        }