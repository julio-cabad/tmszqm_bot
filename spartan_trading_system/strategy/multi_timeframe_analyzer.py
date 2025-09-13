"""
Multi-Timeframe Analyzer for Spartan Trading System
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import sys
sys.path.append('.')
from indicators.technical_indicators import TechnicalAnalyzer
from .signal_types import TradingSignal, SignalType, Direction


class MultiTimeframeAnalyzer:
    """
    Analyzes signals across multiple timeframes
    """
    
    def __init__(self, symbol: str, timeframes: List[str] = None):
        """
        Initialize multi-timeframe analyzer
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframes: List of timeframes to analyze
        """
        self.symbol = symbol
        self.timeframes = timeframes or ['1h', '4h', '1d']
        self.logger = logging.getLogger(f"MTFAnalyzer-{symbol}")
        
        # Create analyzers for each timeframe
        self.analyzers = {
            tf: TechnicalAnalyzer(symbol, tf) 
            for tf in self.timeframes
        }
    
    def analyze_all_timeframes(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all configured timeframes
        
        Returns:
            Dictionary with analysis results per timeframe
        """
        results = {}
        
        for timeframe in self.timeframes:
            try:
                analyzer = self.analyzers[timeframe]
                analyzer.fetch_market_data(limit=200)
                
                # Get technical indicators
                tm_result = analyzer.trend_magic_v3(period=100)
                squeeze_result = analyzer.squeeze_momentum()
                
                results[timeframe] = {
                    'trend_magic': tm_result,
                    'squeeze': squeeze_result,
                    'price': tm_result['current_price'] if tm_result else None,
                    'timestamp': datetime.now()
                }
                
            except Exception as e:
                self.logger.error(f"Error analyzing {timeframe}: {str(e)}")
                results[timeframe] = {'error': str(e)}
        
        return results
    
    def get_consensus_signal(self) -> Optional[TradingSignal]:
        """
        Get consensus signal across all timeframes
        
        Returns:
            TradingSignal if consensus found, None otherwise
        """
        try:
            analysis = self.analyze_all_timeframes()
            
            # Simple consensus logic - can be enhanced
            signals = []
            
            for timeframe, data in analysis.items():
                if 'error' in data:
                    continue
                
                tm_data = data.get('trend_magic', {})
                squeeze_data = data.get('squeeze', {})
                
                if tm_data and squeeze_data:
                    # Apply same logic as signal_generator.py
                    tm_value = tm_data.get('magic_trend_value')
                    color = tm_data.get('color')
                    price = tm_data.get('current_price')
                    squeeze_color = squeeze_data.get('momentum_color')
                    
                    if all([tm_value, color, price, squeeze_color]):
                        # Simplified signal detection
                        if color == 'BLUE' and squeeze_color in ['MAROON', 'LIME']:
                            signals.append('LONG')
                        elif color == 'RED' and squeeze_color in ['GREEN', 'RED']:
                            signals.append('SHORT')
            
            # Check for consensus (majority agreement)
            if len(signals) >= 2:
                long_count = signals.count('LONG')
                short_count = signals.count('SHORT')
                
                if long_count > short_count:
                    return self._create_signal(SignalType.LONG, Direction.LONG, analysis)
                elif short_count > long_count:
                    return self._create_signal(SignalType.SHORT, Direction.SHORT, analysis)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting consensus signal: {str(e)}")
            return None
    
    def _create_signal(self, signal_type: SignalType, direction: Direction, 
                      analysis: Dict[str, Any]) -> TradingSignal:
        """Create a trading signal from analysis data"""
        
        # Get primary timeframe data
        primary_tf = self.timeframes[0]
        primary_data = analysis.get(primary_tf, {})
        tm_data = primary_data.get('trend_magic', {})
        
        return TradingSignal(
            symbol=self.symbol,
            signal_type=signal_type,
            direction=direction,
            strength=0.8,  # Default strength
            confidence=0.7,  # Default confidence
            current_price=tm_data.get('current_price', 0.0),
            timestamp=datetime.now(),
            trend_magic_value=tm_data.get('magic_trend_value'),
            trend_magic_color=tm_data.get('color'),
            timeframe=primary_tf,
            metadata={'analysis': analysis}
        )