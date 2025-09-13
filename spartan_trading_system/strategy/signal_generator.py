"""
Signal Generator - The Heart of Spartan Trading System
Implements the complete Spartan Squeeze Magic Strategy
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from ..config.strategy_config import StrategyConfig
from ..indicators.indicator_engine import IndicatorEngine
from ..indicators.result_models import TrendMagicResult, SqueezeResult, MultiTimeframeAnalysis
from .signal_types import (
    SignalType, Direction, TradingSignal, SignalContext, 
    SIGNAL_PRIORITY, SIGNAL_WIN_RATES, SignalStrength
)


class SignalGenerator:
    """
    Spartan Signal Generator - The God of Trading Signals
    
    Implements the complete Spartan Squeeze Magic Strategy:
    - SUPER_BULLISH: Squeeze ON + Trend Magic BLUE + Momentum GREEN
    - SUPER_BEARISH: Squeeze ON + Trend Magic RED + Momentum RED  
    - BREAKOUT signals: Squeeze OFF + direction confirmation
    - TREND_CHANGE signals: Trend Magic color changes
    - Multi-timeframe confirmation and filtering
    """
    
    def __init__(self, config: StrategyConfig, indicator_engine: IndicatorEngine):
        """
        Initialize Signal Generator
        
        Args:
            config: Strategy configuration
            indicator_engine: Indicator calculation engine
        """
        self.config = config
        self.indicator_engine = indicator_engine
        self.logger = logging.getLogger("SignalGenerator")
        
        # Signal history for change detection
        self._signal_history: Dict[str, List[TradingSignal]] = {}
        self._previous_indicators: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("🏛️ Spartan Signal Generator initialized")
        self.logger.info(f"⚔️ Min Signal Strength: {config.min_signal_strength}")
        self.logger.info(f"🎯 Multi-timeframe confirmation: {config.require_multi_timeframe_confirmation}")
    
    def generate_signals(self, symbol: str) -> List[TradingSignal]:
        """
        Generate trading signals for a symbol using Spartan Squeeze Magic Strategy
        
        Args:
            symbol: Trading pair to analyze
            
        Returns:
            List of trading signals (usually 0-1 signals)
        """
        try:
            self.logger.debug(f"🔍 Generating signals for {symbol}")
            
            # Get multi-timeframe analysis
            analysis = self.indicator_engine.get_multi_timeframe_analysis(symbol)
            
            # Create signal context
            context = self._create_signal_context(symbol, analysis)
            
            # Generate all possible signals
            signals = []
            
            # 1. SUPER SIGNALS (Highest Priority)
            super_signal = self._detect_super_signals(context, analysis)
            if super_signal:
                signals.append(super_signal)
            
            # 2. BREAKOUT SIGNALS
            if not signals:  # Only if no super signal
                breakout_signal = self._detect_breakout_signals(context, analysis)
                if breakout_signal:
                    signals.append(breakout_signal)
            
            # 3. TREND CHANGE SIGNALS
            if not signals:  # Only if no higher priority signal
                trend_change_signal = self._detect_trend_change_signals(context, analysis)
                if trend_change_signal:
                    signals.append(trend_change_signal)
            
            # 4. CONTINUATION SIGNALS
            if not signals:  # Only if no other signals
                continuation_signal = self._detect_continuation_signals(context, analysis)
                if continuation_signal:
                    signals.append(continuation_signal)
            
            # Filter signals by strength and multi-timeframe confirmation
            filtered_signals = self._filter_signals(signals, analysis)
            
            # Update signal history
            if filtered_signals:
                self._update_signal_history(symbol, filtered_signals)
            
            # Update previous indicators for next iteration
            self._update_previous_indicators(symbol, analysis)
            
            return filtered_signals
            
        except Exception as e:
            self.logger.error(f"💀 Signal generation failed for {symbol}: {str(e)}")
            return []
    
    def _create_signal_context(self, symbol: str, analysis: MultiTimeframeAnalysis) -> SignalContext:
        """Create signal context from multi-timeframe analysis"""
        return SignalContext(
            symbol=symbol,
            timeframe=self.config.primary_timeframe,
            trend_magic_current=analysis.primary_trend_magic.__dict__,
            squeeze_current=analysis.primary_squeeze.__dict__,
            trend_magic_previous=self._previous_indicators.get(symbol, {}).get('trend_magic'),
            squeeze_previous=self._previous_indicators.get(symbol, {}).get('squeeze'),
            context_timeframe_data=analysis.context_trend_magic.__dict__,
            confirmation_timeframe_data=analysis.confirmation_trend_magic.__dict__,
            current_price=analysis.primary_trend_magic.current_price,
            timestamp=analysis.timestamp
        )
    
    def _detect_super_signals(self, context: SignalContext, analysis: MultiTimeframeAnalysis) -> Optional[TradingSignal]:
        """
        Detect SUPER signals - Highest probability (85%+)
        
        SUPER_BULLISH: Squeeze ON + Trend Magic BLUE + Momentum GREEN/LIME
        SUPER_BEARISH: Squeeze ON + Trend Magic RED + Momentum RED/MAROON
        """
        squeeze = analysis.primary_squeeze
        trend_magic = analysis.primary_trend_magic
        
        # Must have squeeze compression (volatility building up)
        if not squeeze.squeeze_on:
            return None
        
        # SUPER BULLISH CONDITIONS
        if (trend_magic.color == 'BLUE' and 
            squeeze.momentum_color in ['GREEN', 'LIME']):
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.SUPER_BULLISH,
                direction=Direction.LONG,
                base_strength=0.90,  # Very high base strength
                trigger_reason="Squeeze compression with bullish trend and momentum alignment",
                supporting_factors=[
                    f"Squeeze ON (volatility compressed)",
                    f"Trend Magic BLUE (${trend_magic.value:,.2f})",
                    f"Momentum {squeeze.momentum_color} ({squeeze.momentum_value:,.2f})",
                    f"Price above trend line ({trend_magic.distance_pct:+.2f}%)"
                ],
                analysis=analysis
            )
        
        # SUPER BEARISH CONDITIONS  
        elif (trend_magic.color == 'RED' and 
              squeeze.momentum_color in ['RED', 'MAROON']):
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.SUPER_BEARISH,
                direction=Direction.SHORT,
                base_strength=0.90,  # Very high base strength
                trigger_reason="Squeeze compression with bearish trend and momentum alignment",
                supporting_factors=[
                    f"Squeeze ON (volatility compressed)",
                    f"Trend Magic RED (${trend_magic.value:,.2f})",
                    f"Momentum {squeeze.momentum_color} ({squeeze.momentum_value:,.2f})",
                    f"Price below trend line ({trend_magic.distance_pct:+.2f}%)"
                ],
                analysis=analysis
            )
        
        return None
    
    def _detect_breakout_signals(self, context: SignalContext, analysis: MultiTimeframeAnalysis) -> Optional[TradingSignal]:
        """
        Detect BREAKOUT signals - High probability (75%+)
        
        Squeeze OFF (volatility expanding) + Trend Magic direction + Momentum confirmation
        """
        squeeze = analysis.primary_squeeze
        trend_magic = analysis.primary_trend_magic
        
        # Must have squeeze release (volatility expanding)
        if not squeeze.squeeze_off:
            return None
        
        # Check if this is a fresh breakout (squeeze was ON recently)
        previous_squeeze = context.squeeze_previous
        if not (previous_squeeze and previous_squeeze.get('squeeze_on', False)):
            return None  # Not a fresh breakout
        
        # BULLISH BREAKOUT
        if (trend_magic.color == 'BLUE' and 
            squeeze.momentum_color in ['GREEN', 'LIME']):
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.BREAKOUT_BULLISH,
                direction=Direction.LONG,
                base_strength=0.80,
                trigger_reason="Bullish breakout from squeeze compression",
                supporting_factors=[
                    f"Squeeze OFF (volatility expanding from compression)",
                    f"Trend Magic BLUE (${trend_magic.value:,.2f})",
                    f"Momentum {squeeze.momentum_color} (bullish)",
                    f"Fresh breakout detected"
                ],
                analysis=analysis
            )
        
        # BEARISH BREAKOUT
        elif (trend_magic.color == 'RED' and 
              squeeze.momentum_color in ['RED', 'MAROON']):
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.BREAKOUT_BEARISH,
                direction=Direction.SHORT,
                base_strength=0.80,
                trigger_reason="Bearish breakout from squeeze compression",
                supporting_factors=[
                    f"Squeeze OFF (volatility expanding from compression)",
                    f"Trend Magic RED (${trend_magic.value:,.2f})",
                    f"Momentum {squeeze.momentum_color} (bearish)",
                    f"Fresh breakout detected"
                ],
                analysis=analysis
            )
        
        return None
    
    def _detect_trend_change_signals(self, context: SignalContext, analysis: MultiTimeframeAnalysis) -> Optional[TradingSignal]:
        """
        Detect TREND CHANGE signals - Medium-High probability (65%+)
        
        Trend Magic color change + Momentum confirmation
        """
        trend_magic = analysis.primary_trend_magic
        squeeze = analysis.primary_squeeze
        
        # Check for trend magic color change
        previous_trend = context.trend_magic_previous
        if not previous_trend:
            return None
        
        previous_color = previous_trend.get('color')
        current_color = trend_magic.color
        
        if previous_color == current_color:
            return None  # No color change
        
        # BULLISH TREND CHANGE (RED -> BLUE)
        if previous_color == 'RED' and current_color == 'BLUE':
            
            # Momentum should support the change
            momentum_support = squeeze.momentum_color in ['GREEN', 'LIME']
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.TREND_CHANGE_BULLISH,
                direction=Direction.LONG,
                base_strength=0.70 if momentum_support else 0.60,
                trigger_reason="Bullish trend change detected",
                supporting_factors=[
                    f"Trend Magic changed RED -> BLUE",
                    f"New trend line: ${trend_magic.value:,.2f}",
                    f"Momentum: {squeeze.momentum_color}",
                    f"Squeeze status: {squeeze.squeeze_status}"
                ] + (["Momentum supports trend change"] if momentum_support else []),
                risk_factors=[] if momentum_support else ["Momentum not fully aligned"],
                analysis=analysis
            )
        
        # BEARISH TREND CHANGE (BLUE -> RED)
        elif previous_color == 'BLUE' and current_color == 'RED':
            
            # Momentum should support the change
            momentum_support = squeeze.momentum_color in ['RED', 'MAROON']
            
            return self._create_signal(
                context=context,
                signal_type=SignalType.TREND_CHANGE_BEARISH,
                direction=Direction.SHORT,
                base_strength=0.70 if momentum_support else 0.60,
                trigger_reason="Bearish trend change detected",
                supporting_factors=[
                    f"Trend Magic changed BLUE -> RED",
                    f"New trend line: ${trend_magic.value:,.2f}",
                    f"Momentum: {squeeze.momentum_color}",
                    f"Squeeze status: {squeeze.squeeze_status}"
                ] + (["Momentum supports trend change"] if momentum_support else []),
                risk_factors=[] if momentum_support else ["Momentum not fully aligned"],
                analysis=analysis
            )
        
        return None
    
    def _detect_continuation_signals(self, context: SignalContext, analysis: MultiTimeframeAnalysis) -> Optional[TradingSignal]:
        """
        Detect CONTINUATION signals - Medium probability (60%+)
        
        Strong trend + Momentum acceleration
        """
        trend_magic = analysis.primary_trend_magic
        squeeze = analysis.primary_squeeze
        
        # Check for momentum acceleration
        previous_squeeze = context.squeeze_previous
        if not previous_squeeze:
            return None
        
        previous_momentum = previous_squeeze.get('momentum_color')
        current_momentum = squeeze.momentum_color
        
        # BULLISH CONTINUATION
        if trend_magic.color == 'BLUE':
            # Look for momentum acceleration (GREEN -> LIME)
            momentum_acceleration = (
                previous_momentum == 'GREEN' and current_momentum == 'LIME'
            )
            
            # Or strong momentum with good distance from trend line
            strong_momentum = (
                current_momentum == 'LIME' and 
                trend_magic.distance_pct > 0.5  # Price well above trend line
            )
            
            if momentum_acceleration or strong_momentum:
                return self._create_signal(
                    context=context,
                    signal_type=SignalType.CONTINUATION_BULLISH,
                    direction=Direction.LONG,
                    base_strength=0.65,
                    trigger_reason="Bullish trend continuation with momentum acceleration",
                    supporting_factors=[
                        f"Trend Magic BLUE (strong trend)",
                        f"Momentum: {current_momentum}",
                        f"Distance from trend: {trend_magic.distance_pct:+.2f}%",
                        f"Squeeze: {squeeze.squeeze_status}"
                    ] + (["Momentum acceleration detected"] if momentum_acceleration else []),
                    analysis=analysis
                )
        
        # BEARISH CONTINUATION
        elif trend_magic.color == 'RED':
            # Look for momentum acceleration (MAROON -> RED)
            momentum_acceleration = (
                previous_momentum == 'MAROON' and current_momentum == 'RED'
            )
            
            # Or strong momentum with good distance from trend line
            strong_momentum = (
                current_momentum == 'RED' and 
                trend_magic.distance_pct < -0.5  # Price well below trend line
            )
            
            if momentum_acceleration or strong_momentum:
                return self._create_signal(
                    context=context,
                    signal_type=SignalType.CONTINUATION_BEARISH,
                    direction=Direction.SHORT,
                    base_strength=0.65,
                    trigger_reason="Bearish trend continuation with momentum acceleration",
                    supporting_factors=[
                        f"Trend Magic RED (strong trend)",
                        f"Momentum: {current_momentum}",
                        f"Distance from trend: {trend_magic.distance_pct:+.2f}%",
                        f"Squeeze: {squeeze.squeeze_status}"
                    ] + (["Momentum acceleration detected"] if momentum_acceleration else []),
                    analysis=analysis
                )
        
        return None
    
    def _create_signal(self, context: SignalContext, signal_type: SignalType, 
                      direction: Direction, base_strength: float, trigger_reason: str,
                      supporting_factors: List[str], analysis: MultiTimeframeAnalysis,
                      risk_factors: List[str] = None) -> TradingSignal:
        """
        Create a complete trading signal with all parameters
        """
        if risk_factors is None:
            risk_factors = []
        
        # Calculate final strength with multi-timeframe adjustment
        final_strength = self._calculate_signal_strength(
            base_strength, analysis, signal_type
        )
        
        # Calculate confidence based on timeframe alignment
        confidence = self._calculate_confidence(analysis, signal_type)
        
        # Calculate risk management parameters
        entry_price = context.current_price
        stop_loss = self._calculate_stop_loss(analysis.primary_trend_magic, direction)
        take_profit_levels = self._calculate_take_profit_levels(
            entry_price, stop_loss, direction
        )
        position_size = self._calculate_position_size(final_strength)
        
        return TradingSignal(
            signal_id=str(uuid.uuid4()),
            symbol=context.symbol,
            timestamp=context.timestamp,
            signal_type=signal_type,
            direction=direction,
            strength=final_strength,
            confidence=confidence,
            entry_price=entry_price,
            current_price=context.current_price,
            stop_loss=stop_loss,
            take_profit_levels=take_profit_levels,
            position_size_pct=position_size,
            trend_magic_value=analysis.primary_trend_magic.value,
            trend_magic_color=analysis.primary_trend_magic.color,
            squeeze_status=analysis.primary_squeeze.squeeze_status,
            momentum_color=analysis.primary_squeeze.momentum_color,
            momentum_value=analysis.primary_squeeze.momentum_value,
            timeframe=context.timeframe,
            context_timeframe_trend=analysis.overall_trend,
            confirmation_timeframe_trend=analysis.confirmation_trend_magic.trend_status,
            timeframes_aligned=analysis.timeframes_aligned,
            trigger_reason=trigger_reason,
            supporting_factors=supporting_factors,
            risk_factors=risk_factors
        )
    
    def _calculate_signal_strength(self, base_strength: float, 
                                 analysis: MultiTimeframeAnalysis, 
                                 signal_type: SignalType) -> float:
        """
        Calculate final signal strength with multi-timeframe adjustments
        """
        strength = base_strength
        
        # Multi-timeframe alignment bonus
        if analysis.timeframes_aligned:
            strength += 0.05  # 5% bonus for alignment
        
        # Trend strength bonus
        if analysis.trend_strength >= 0.8:
            strength += 0.03  # 3% bonus for strong trend
        
        # Signal type base adjustment
        expected_win_rate = SIGNAL_WIN_RATES.get(signal_type, 0.5)
        strength = (strength + expected_win_rate) / 2  # Average with expected win rate
        
        # Ensure within bounds
        return max(0.0, min(1.0, strength))
    
    def _calculate_confidence(self, analysis: MultiTimeframeAnalysis, 
                            signal_type: SignalType) -> float:
        """
        Calculate signal confidence based on various factors
        """
        confidence = 0.5  # Base confidence
        
        # Timeframe alignment
        if analysis.timeframes_aligned:
            confidence += 0.2
        
        # Trend strength
        confidence += analysis.trend_strength * 0.2
        
        # Signal type confidence
        if signal_type in [SignalType.SUPER_BULLISH, SignalType.SUPER_BEARISH]:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_stop_loss(self, trend_magic: TrendMagicResult, direction: Direction) -> float:
        """
        Calculate stop loss based on Trend Magic line
        """
        if direction == Direction.LONG:
            # For long positions, stop below Trend Magic line
            return trend_magic.value * 0.995  # 0.5% below trend line
        else:
            # For short positions, stop above Trend Magic line
            return trend_magic.value * 1.005  # 0.5% above trend line
    
    def _calculate_take_profit_levels(self, entry_price: float, stop_loss: float, 
                                    direction: Direction) -> List[float]:
        """
        Calculate multiple take profit levels
        """
        risk = abs(entry_price - stop_loss)
        
        if direction == Direction.LONG:
            return [
                entry_price + risk * 1.5,  # TP1: 1.5R
                entry_price + risk * 2.5,  # TP2: 2.5R
                entry_price + risk * 4.0   # TP3: 4.0R
            ]
        else:
            return [
                entry_price - risk * 1.5,  # TP1: 1.5R
                entry_price - risk * 2.5,  # TP2: 2.5R
                entry_price - risk * 4.0   # TP3: 4.0R
            ]
    
    def _calculate_position_size(self, signal_strength: float) -> float:
        """
        Calculate position size based on signal strength and risk settings
        """
        base_risk = self.config.risk_percentage
        
        # Adjust position size based on signal strength
        if signal_strength >= 0.85:
            return base_risk * 1.2  # 20% larger position for very strong signals
        elif signal_strength >= 0.75:
            return base_risk * 1.0  # Normal position for strong signals
        elif signal_strength >= 0.65:
            return base_risk * 0.8  # 20% smaller position for medium signals
        else:
            return base_risk * 0.5  # 50% smaller position for weak signals
    
    def _filter_signals(self, signals: List[TradingSignal], 
                       analysis: MultiTimeframeAnalysis) -> List[TradingSignal]:
        """
        Filter signals based on configuration requirements
        """
        filtered = []
        
        for signal in signals:
            # Minimum strength filter
            if signal.strength < self.config.min_signal_strength:
                self.logger.debug(f"Signal filtered: strength {signal.strength:.2f} < {self.config.min_signal_strength}")
                continue
            
            # Multi-timeframe confirmation filter
            if self.config.require_multi_timeframe_confirmation:
                if not analysis.timeframes_aligned:
                    self.logger.debug(f"Signal filtered: timeframes not aligned")
                    continue
            
            filtered.append(signal)
        
        return filtered
    
    def _update_signal_history(self, symbol: str, signals: List[TradingSignal]):
        """Update signal history for the symbol"""
        if symbol not in self._signal_history:
            self._signal_history[symbol] = []
        
        self._signal_history[symbol].extend(signals)
        
        # Keep only last 10 signals per symbol
        self._signal_history[symbol] = self._signal_history[symbol][-10:]
    
    def _update_previous_indicators(self, symbol: str, analysis: MultiTimeframeAnalysis):
        """Update previous indicator values for change detection"""
        self._previous_indicators[symbol] = {
            'trend_magic': analysis.primary_trend_magic.__dict__,
            'squeeze': analysis.primary_squeeze.__dict__
        }
    
    def get_signal_history(self, symbol: str) -> List[TradingSignal]:
        """Get signal history for a symbol"""
        return self._signal_history.get(symbol, [])
    
    def clear_signal_history(self, symbol: str = None):
        """Clear signal history for a symbol or all symbols"""
        if symbol:
            self._signal_history.pop(symbol, None)
        else:
            self._signal_history.clear()