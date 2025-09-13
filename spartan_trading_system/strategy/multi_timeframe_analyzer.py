"""
Multi-Timeframe Analyzer for Spartan Trading System
Advanced analysis across multiple timeframes for signal confirmation
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..config.strategy_config import StrategyConfig
from ..indicators.indicator_engine import IndicatorEngine
from ..indicators.result_models import MultiTimeframeAnalysis, TrendMagicResult, SqueezeResult
from .signal_types import Direction


class MultiTimeframeAnalyzer:
    """
    Advanced Multi-Timeframe Analysis for Spartan Strategy
    
    Provides sophisticated analysis across multiple timeframes to:
    - Confirm signal direction with higher timeframe context
    - Detect trend alignment across timeframes
    - Calculate overall market structure
    - Provide confluence for signal generation
    """
    
    def __init__(self, config: StrategyConfig, indicator_engine: IndicatorEngine):
        """
        Initialize Multi-Timeframe Analyzer
        
        Args:
            config: Strategy configuration
            indicator_engine: Indicator calculation engine
        """
        self.config = config
        self.indicator_engine = indicator_engine
        self.logger = logging.getLogger("MultiTimeframeAnalyzer")
        
        # Timeframe hierarchy (from lowest to highest)
        self.timeframes = [
            config.monitoring_timeframe,    # 15m - Real-time monitoring
            config.confirmation_timeframe,  # 30m - Entry confirmation
            config.primary_timeframe,       # 1h  - Main signals
            config.context_timeframe        # 4h  - Market context
        ]
        
        self.logger.info("🏛️ Multi-Timeframe Analyzer initialized")
        self.logger.info(f"⏰ Timeframes: {' -> '.join(self.timeframes)}")
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive multi-timeframe analysis for a symbol
        
        Args:
            symbol: Trading pair to analyze
            
        Returns:
            Dictionary with complete multi-timeframe analysis
        """
        try:
            self.logger.debug(f"🔍 Comprehensive analysis for {symbol}")
            
            # Get analysis for each timeframe
            timeframe_data = {}
            for timeframe in self.timeframes:
                try:
                    snapshot = self.indicator_engine.get_indicator_snapshot(symbol, timeframe)
                    timeframe_data[timeframe] = {
                        'trend_magic': snapshot.trend_magic,
                        'squeeze': snapshot.squeeze,
                        'timestamp': snapshot.timestamp
                    }
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get {timeframe} data for {symbol}: {str(e)}")
                    timeframe_data[timeframe] = None
            
            # Analyze trend alignment
            trend_alignment = self._analyze_trend_alignment(timeframe_data)
            
            # Analyze momentum confluence
            momentum_confluence = self._analyze_momentum_confluence(timeframe_data)
            
            # Analyze squeeze conditions across timeframes
            squeeze_analysis = self._analyze_squeeze_conditions(timeframe_data)
            
            # Calculate overall market structure
            market_structure = self._calculate_market_structure(timeframe_data)
            
            # Determine optimal entry timeframe
            optimal_entry_tf = self._determine_optimal_entry_timeframe(timeframe_data)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'timeframe_data': timeframe_data,
                'trend_alignment': trend_alignment,
                'momentum_confluence': momentum_confluence,
                'squeeze_analysis': squeeze_analysis,
                'market_structure': market_structure,
                'optimal_entry_timeframe': optimal_entry_tf,
                'overall_bias': self._calculate_overall_bias(trend_alignment, momentum_confluence),
                'confluence_score': self._calculate_confluence_score(
                    trend_alignment, momentum_confluence, squeeze_analysis
                )
            }
            
        except Exception as e:
            self.logger.error(f"💀 Comprehensive analysis failed for {symbol}: {str(e)}")
            return {}
    
    def _analyze_trend_alignment(self, timeframe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trend alignment across timeframes
        """
        trends = {}
        colors = []
        
        for tf, data in timeframe_data.items():
            if data and data['trend_magic']:
                trend_color = data['trend_magic'].color
                trends[tf] = {
                    'color': trend_color,
                    'value': data['trend_magic'].value,
                    'distance_pct': data['trend_magic'].distance_pct
                }
                colors.append(trend_color)
        
        # Calculate alignment metrics
        if colors:
            bullish_count = colors.count('BLUE')
            bearish_count = colors.count('RED')
            total_count = len(colors)
            
            alignment_score = max(bullish_count, bearish_count) / total_count
            dominant_trend = 'BULLISH' if bullish_count > bearish_count else 'BEARISH'
            
            # Check for perfect alignment
            perfect_alignment = len(set(colors)) == 1
            
            return {
                'trends': trends,
                'dominant_trend': dominant_trend,
                'alignment_score': alignment_score,
                'perfect_alignment': perfect_alignment,
                'bullish_timeframes': bullish_count,
                'bearish_timeframes': bearish_count,
                'total_timeframes': total_count
            }
        
        return {'trends': {}, 'alignment_score': 0.0}
    
    def _analyze_momentum_confluence(self, timeframe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze momentum confluence across timeframes
        """
        momentum_data = {}
        momentum_colors = []
        squeeze_statuses = []
        
        for tf, data in timeframe_data.items():
            if data and data['squeeze']:
                squeeze = data['squeeze']
                momentum_data[tf] = {
                    'momentum_color': squeeze.momentum_color,
                    'momentum_value': squeeze.momentum_value,
                    'squeeze_status': squeeze.squeeze_status,
                    'squeeze_on': squeeze.squeeze_on,
                    'squeeze_off': squeeze.squeeze_off
                }
                momentum_colors.append(squeeze.momentum_color)
                squeeze_statuses.append(squeeze.squeeze_status)
        
        # Analyze momentum alignment
        if momentum_colors:
            bullish_momentum = sum(1 for color in momentum_colors if color in ['GREEN', 'LIME'])
            bearish_momentum = sum(1 for color in momentum_colors if color in ['RED', 'MAROON'])
            
            momentum_alignment = max(bullish_momentum, bearish_momentum) / len(momentum_colors)
            dominant_momentum = 'BULLISH' if bullish_momentum > bearish_momentum else 'BEARISH'
            
            # Check for momentum acceleration (LIME or RED)
            strong_momentum_count = sum(1 for color in momentum_colors if color in ['LIME', 'RED'])
            momentum_strength = strong_momentum_count / len(momentum_colors)
            
            return {
                'momentum_data': momentum_data,
                'dominant_momentum': dominant_momentum,
                'momentum_alignment': momentum_alignment,
                'momentum_strength': momentum_strength,
                'bullish_momentum_count': bullish_momentum,
                'bearish_momentum_count': bearish_momentum,
                'strong_momentum_ratio': momentum_strength
            }
        
        return {'momentum_data': {}, 'momentum_alignment': 0.0}
    
    def _analyze_squeeze_conditions(self, timeframe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze squeeze conditions across timeframes
        """
        squeeze_conditions = {}
        squeeze_on_count = 0
        squeeze_off_count = 0
        
        for tf, data in timeframe_data.items():
            if data and data['squeeze']:
                squeeze = data['squeeze']
                squeeze_conditions[tf] = {
                    'status': squeeze.squeeze_status,
                    'on': squeeze.squeeze_on,
                    'off': squeeze.squeeze_off,
                    'no_squeeze': squeeze.no_squeeze
                }
                
                if squeeze.squeeze_on:
                    squeeze_on_count += 1
                elif squeeze.squeeze_off:
                    squeeze_off_count += 1
        
        total_timeframes = len([tf for tf, data in timeframe_data.items() if data])
        
        # Calculate squeeze metrics
        compression_ratio = squeeze_on_count / total_timeframes if total_timeframes > 0 else 0
        expansion_ratio = squeeze_off_count / total_timeframes if total_timeframes > 0 else 0
        
        # Determine overall squeeze condition
        if compression_ratio >= 0.5:
            overall_condition = "COMPRESSION"
        elif expansion_ratio >= 0.5:
            overall_condition = "EXPANSION"
        else:
            overall_condition = "MIXED"
        
        return {
            'squeeze_conditions': squeeze_conditions,
            'overall_condition': overall_condition,
            'compression_ratio': compression_ratio,
            'expansion_ratio': expansion_ratio,
            'squeeze_on_count': squeeze_on_count,
            'squeeze_off_count': squeeze_off_count,
            'total_timeframes': total_timeframes
        }
    
    def _calculate_market_structure(self, timeframe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall market structure
        """
        # Get higher timeframe bias (context timeframe)
        context_tf = self.config.context_timeframe
        context_data = timeframe_data.get(context_tf)
        
        if context_data and context_data['trend_magic']:
            higher_tf_bias = 'BULLISH' if context_data['trend_magic'].color == 'BLUE' else 'BEARISH'
            higher_tf_strength = abs(context_data['trend_magic'].distance_pct)
        else:
            higher_tf_bias = 'NEUTRAL'
            higher_tf_strength = 0.0
        
        # Get primary timeframe structure
        primary_tf = self.config.primary_timeframe
        primary_data = timeframe_data.get(primary_tf)
        
        if primary_data and primary_data['trend_magic']:
            primary_bias = 'BULLISH' if primary_data['trend_magic'].color == 'BLUE' else 'BEARISH'
            primary_strength = abs(primary_data['trend_magic'].distance_pct)
        else:
            primary_bias = 'NEUTRAL'
            primary_strength = 0.0
        
        # Determine structure alignment
        structure_aligned = higher_tf_bias == primary_bias
        
        # Calculate structure strength
        structure_strength = (higher_tf_strength + primary_strength) / 2
        
        return {
            'higher_timeframe_bias': higher_tf_bias,
            'primary_timeframe_bias': primary_bias,
            'structure_aligned': structure_aligned,
            'structure_strength': structure_strength,
            'overall_structure': higher_tf_bias if structure_aligned else 'CONFLICTED'
        }
    
    def _determine_optimal_entry_timeframe(self, timeframe_data: Dict[str, Any]) -> str:
        """
        Determine the optimal timeframe for entry timing
        """
        # Look for the lowest timeframe with clear signals
        for tf in reversed(self.timeframes):  # Start from lowest timeframe
            data = timeframe_data.get(tf)
            if data and data['trend_magic'] and data['squeeze']:
                trend_magic = data['trend_magic']
                squeeze = data['squeeze']
                
                # Check for clear conditions
                clear_trend = abs(trend_magic.distance_pct) > 0.2
                clear_momentum = squeeze.momentum_color in ['LIME', 'GREEN', 'RED', 'MAROON']
                
                if clear_trend and clear_momentum:
                    return tf
        
        # Default to confirmation timeframe
        return self.config.confirmation_timeframe
    
    def _calculate_overall_bias(self, trend_alignment: Dict[str, Any], 
                              momentum_confluence: Dict[str, Any]) -> str:
        """
        Calculate overall market bias
        """
        trend_bias = trend_alignment.get('dominant_trend', 'NEUTRAL')
        momentum_bias = momentum_confluence.get('dominant_momentum', 'NEUTRAL')
        
        # If both agree, strong bias
        if trend_bias == momentum_bias:
            return trend_bias
        
        # If they conflict, check alignment scores
        trend_score = trend_alignment.get('alignment_score', 0)
        momentum_score = momentum_confluence.get('momentum_alignment', 0)
        
        if trend_score > momentum_score:
            return trend_bias
        elif momentum_score > trend_score:
            return momentum_bias
        else:
            return 'NEUTRAL'
    
    def _calculate_confluence_score(self, trend_alignment: Dict[str, Any],
                                  momentum_confluence: Dict[str, Any],
                                  squeeze_analysis: Dict[str, Any]) -> float:
        """
        Calculate overall confluence score (0.0 to 1.0)
        """
        # Trend alignment score (40% weight)
        trend_score = trend_alignment.get('alignment_score', 0) * 0.4
        
        # Momentum confluence score (40% weight)
        momentum_score = momentum_confluence.get('momentum_alignment', 0) * 0.4
        
        # Squeeze condition score (20% weight)
        squeeze_score = 0.0
        overall_squeeze = squeeze_analysis.get('overall_condition', 'MIXED')
        if overall_squeeze in ['COMPRESSION', 'EXPANSION']:
            squeeze_score = 0.8 * 0.2  # High score for clear squeeze condition
        else:
            squeeze_score = 0.3 * 0.2  # Lower score for mixed conditions
        
        total_score = trend_score + momentum_score + squeeze_score
        return min(1.0, max(0.0, total_score))
    
    def get_entry_confirmation(self, symbol: str, direction: Direction) -> Dict[str, Any]:
        """
        Get entry confirmation for a specific direction
        
        Args:
            symbol: Trading pair
            direction: Intended trade direction
            
        Returns:
            Dictionary with confirmation analysis
        """
        try:
            analysis = self.get_comprehensive_analysis(symbol)
            
            if not analysis:
                return {'confirmed': False, 'reason': 'Analysis failed'}
            
            # Check trend alignment with intended direction
            trend_alignment = analysis.get('trend_alignment', {})
            dominant_trend = trend_alignment.get('dominant_trend', 'NEUTRAL')
            
            trend_confirms = (
                (direction == Direction.LONG and dominant_trend == 'BULLISH') or
                (direction == Direction.SHORT and dominant_trend == 'BEARISH')
            )
            
            # Check momentum confluence
            momentum_confluence = analysis.get('momentum_confluence', {})
            dominant_momentum = momentum_confluence.get('dominant_momentum', 'NEUTRAL')
            
            momentum_confirms = (
                (direction == Direction.LONG and dominant_momentum == 'BULLISH') or
                (direction == Direction.SHORT and dominant_momentum == 'BEARISH')
            )
            
            # Check market structure
            market_structure = analysis.get('market_structure', {})
            structure_bias = market_structure.get('overall_structure', 'NEUTRAL')
            
            structure_confirms = (
                (direction == Direction.LONG and structure_bias == 'BULLISH') or
                (direction == Direction.SHORT and structure_bias == 'BEARISH')
            )
            
            # Calculate confirmation score
            confirmations = [trend_confirms, momentum_confirms, structure_confirms]
            confirmation_score = sum(confirmations) / len(confirmations)
            
            # Overall confirmation
            confirmed = confirmation_score >= 0.67  # At least 2 out of 3 confirm
            
            return {
                'confirmed': confirmed,
                'confirmation_score': confirmation_score,
                'trend_confirms': trend_confirms,
                'momentum_confirms': momentum_confirms,
                'structure_confirms': structure_confirms,
                'confluence_score': analysis.get('confluence_score', 0),
                'optimal_entry_timeframe': analysis.get('optimal_entry_timeframe'),
                'reason': self._get_confirmation_reason(
                    confirmed, trend_confirms, momentum_confirms, structure_confirms
                )
            }
            
        except Exception as e:
            self.logger.error(f"💀 Entry confirmation failed for {symbol}: {str(e)}")
            return {'confirmed': False, 'reason': f'Error: {str(e)}'}
    
    def _get_confirmation_reason(self, confirmed: bool, trend_confirms: bool,
                               momentum_confirms: bool, structure_confirms: bool) -> str:
        """
        Get human-readable confirmation reason
        """
        if confirmed:
            confirmations = []
            if trend_confirms:
                confirmations.append("trend alignment")
            if momentum_confirms:
                confirmations.append("momentum confluence")
            if structure_confirms:
                confirmations.append("market structure")
            
            return f"Confirmed by: {', '.join(confirmations)}"
        else:
            conflicts = []
            if not trend_confirms:
                conflicts.append("trend misalignment")
            if not momentum_confirms:
                conflicts.append("momentum conflict")
            if not structure_confirms:
                conflicts.append("structure conflict")
            
            return f"Rejected due to: {', '.join(conflicts)}"