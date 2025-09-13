"""
Indicator Engine - Configuration Bridge to Existing Indicators
Uses existing TechnicalAnalyzer with Spartan configuration system
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Add the parent indicators directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'indicators'))

from technical_indicators import TechnicalAnalyzer
from ..config.strategy_config import StrategyConfig
from .result_models import TrendMagicResult, SqueezeResult, MultiTimeframeAnalysis, IndicatorSnapshot


class IndicatorEngine:
    """
    Spartan Indicator Engine - Bridge between configuration and existing indicators
    
    This class wraps the existing TechnicalAnalyzer with configuration support,
    providing a clean interface for the Spartan Trading System while reusing
    all the battle-tested indicator code.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Indicator Engine with configuration
        
        Args:
            config: StrategyConfig with all parameters
        """
        self.config = config
        self.logger = logging.getLogger("IndicatorEngine")
        
        # Cache for analyzers per symbol/timeframe
        self._analyzers: Dict[str, TechnicalAnalyzer] = {}
        
        self.logger.info(f"🏛️ Spartan Indicator Engine initialized")
        self.logger.info(f"⚔️ Trend Magic Version: {config.trend_magic_version.upper()}")
        self.logger.info(f"🎯 Monitoring {len(config.symbols)} symbols")
    
    def _get_analyzer(self, symbol: str, timeframe: str) -> TechnicalAnalyzer:
        """
        Get or create TechnicalAnalyzer for symbol/timeframe combination
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Timeframe (e.g., '1h')
            
        Returns:
            TechnicalAnalyzer instance
        """
        key = f"{symbol}_{timeframe}"
        
        if key not in self._analyzers:
            self._analyzers[key] = TechnicalAnalyzer(symbol, timeframe)
            self.logger.debug(f"📊 Created analyzer for {symbol} on {timeframe}")
        
        return self._analyzers[key]
    
    def calculate_trend_magic(self, symbol: str, timeframe: str) -> TrendMagicResult:
        """
        Calculate Trend Magic using existing indicator with configuration
        
        Args:
            symbol: Trading pair
            timeframe: Chart timeframe
            
        Returns:
            TrendMagicResult with standardized output
        """
        try:
            analyzer = self._get_analyzer(symbol, timeframe)
            
            # Fetch data with configured limit
            analyzer.fetch_market_data(limit=self.config.candles_limit)
            
            # Get Trend Magic parameters from config
            tm_params = self.config.get_trend_magic_params()
            
            # Use V3 (TA-Lib) - Stable and accurate version
            result = analyzer.trend_magic_v3(**tm_params)
            
            # Convert to standardized result
            return TrendMagicResult(
                value=result['magic_trend_value'],
                color=result['color'],
                trend_status=result['trend_status'],
                trend_emoji=result['trend_emoji'],
                distance_pct=result['distance_pct'],
                buy_signal=bool(result['buy_signal']),
                sell_signal=bool(result['sell_signal']),
                cci_value=result['cci_value'],
                atr_value=result['atr_value'],
                current_price=result['current_price'],
                timestamp=datetime.now(),
                version="V3_TALIB"
            )
            
        except Exception as e:
            self.logger.error(f"💀 Trend Magic calculation failed for {symbol}: {str(e)}")
            raise
    
    def calculate_squeeze_momentum(self, symbol: str, timeframe: str) -> SqueezeResult:
        """
        Calculate Squeeze Momentum using existing indicator with configuration
        
        Args:
            symbol: Trading pair
            timeframe: Chart timeframe
            
        Returns:
            SqueezeResult with standardized output
        """
        try:
            analyzer = self._get_analyzer(symbol, timeframe)
            
            # Fetch data with configured limit
            analyzer.fetch_market_data(limit=self.config.candles_limit)
            
            # Get Squeeze parameters from config
            squeeze_params = self.config.get_squeeze_params()
            
            # Calculate Squeeze Momentum
            result = analyzer.squeeze_momentum(**squeeze_params)
            
            # Convert to standardized result
            return SqueezeResult(
                momentum_value=result['momentum_value'],
                momentum_color=result['momentum_color'],
                momentum_trend=result['momentum_trend'],
                squeeze_color=result['squeeze_color'],
                squeeze_status=result['squeeze_status'],
                squeeze_on=bool(result['squeeze_on']),
                squeeze_off=bool(result['squeeze_off']),
                no_squeeze=bool(result['no_squeeze']),
                bb_upper=result['bb_upper'],
                bb_lower=result['bb_lower'],
                kc_upper=result['kc_upper'],
                kc_lower=result['kc_lower'],
                current_price=result['current_price'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"💀 Squeeze Momentum calculation failed for {symbol}: {str(e)}")
            raise
    
    def get_indicator_snapshot(self, symbol: str, timeframe: str) -> IndicatorSnapshot:
        """
        Get complete indicator snapshot for a symbol/timeframe
        
        Args:
            symbol: Trading pair
            timeframe: Chart timeframe
            
        Returns:
            IndicatorSnapshot with both indicators
        """
        try:
            trend_magic = self.calculate_trend_magic(symbol, timeframe)
            squeeze = self.calculate_squeeze_momentum(symbol, timeframe)
            
            return IndicatorSnapshot(
                symbol=symbol,
                timeframe=timeframe,
                trend_magic=trend_magic,
                squeeze=squeeze,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"💀 Indicator snapshot failed for {symbol}: {str(e)}")
            raise
    
    def get_multi_timeframe_analysis(self, symbol: str) -> MultiTimeframeAnalysis:
        """
        Get multi-timeframe analysis for a symbol using configured timeframes
        
        Args:
            symbol: Trading pair
            
        Returns:
            MultiTimeframeAnalysis with all timeframes
        """
        try:
            # Get snapshots for all configured timeframes
            primary_snapshot = self.get_indicator_snapshot(symbol, self.config.primary_timeframe)
            confirmation_snapshot = self.get_indicator_snapshot(symbol, self.config.confirmation_timeframe)
            context_snapshot = self.get_indicator_snapshot(symbol, self.config.context_timeframe)
            
            # Analyze overall trend alignment
            trend_colors = [
                primary_snapshot.trend_magic.color,
                confirmation_snapshot.trend_magic.color,
                context_snapshot.trend_magic.color
            ]
            
            bullish_count = sum(1 for color in trend_colors if color == 'BLUE')
            timeframes_aligned = len(set(trend_colors)) == 1
            
            # Determine overall trend
            if bullish_count == 3:
                overall_trend = "BULLISH"
                trend_strength = 1.0
            elif bullish_count == 2:
                overall_trend = "BULLISH"
                trend_strength = 0.7
            elif bullish_count == 1:
                overall_trend = "BEARISH"
                trend_strength = 0.7
            else:
                overall_trend = "BEARISH"
                trend_strength = 1.0
            
            return MultiTimeframeAnalysis(
                symbol=symbol,
                primary_timeframe=self.config.primary_timeframe,
                confirmation_timeframe=self.config.confirmation_timeframe,
                context_timeframe=self.config.context_timeframe,
                primary_trend_magic=primary_snapshot.trend_magic,
                primary_squeeze=primary_snapshot.squeeze,
                confirmation_trend_magic=confirmation_snapshot.trend_magic,
                confirmation_squeeze=confirmation_snapshot.squeeze,
                context_trend_magic=context_snapshot.trend_magic,
                context_squeeze=context_snapshot.squeeze,
                overall_trend=overall_trend,
                trend_strength=trend_strength,
                timeframes_aligned=timeframes_aligned,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"💀 Multi-timeframe analysis failed for {symbol}: {str(e)}")
            raise
    
    def get_trend_magic_color_quick(self, symbol: str, timeframe: str) -> str:
        """
        Quick Trend Magic color check using existing indicator
        
        Args:
            symbol: Trading pair
            timeframe: Chart timeframe
            
        Returns:
            'BLUE' or 'RED'
        """
        try:
            analyzer = self._get_analyzer(symbol, timeframe)
            analyzer.fetch_market_data(limit=self.config.candles_limit)
            
            tm_params = self.config.get_trend_magic_params()
            
            # Use V3 (TA-Lib) - Stable version
            return analyzer.get_trend_magic_v3_color(**tm_params)
                
        except Exception as e:
            self.logger.error(f"💀 Quick color check failed for {symbol}: {str(e)}")
            return "RED"  # Safe default
    
    def update_config(self, new_config: StrategyConfig):
        """
        Update configuration and clear analyzer cache
        
        Args:
            new_config: New StrategyConfig
        """
        self.config = new_config
        self._analyzers.clear()  # Clear cache to use new parameters
        self.logger.info(f"🔄 Configuration updated: Trend Magic {new_config.trend_magic_version.upper()}")
        self.logger.info("🔄 Analyzer cache cleared")