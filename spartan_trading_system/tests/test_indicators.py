"""
Unit Tests for Indicator Integration
Test all indicator calculations with various parameters
"""

import unittest
import sys
import os
from datetime import datetime

# Add spartan_trading_system to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from spartan_trading_system.config.strategy_config import StrategyConfig
from spartan_trading_system.indicators.indicator_engine import IndicatorEngine
from spartan_trading_system.indicators.result_models import TrendMagicResult, SqueezeResult


class TestIndicatorIntegration(unittest.TestCase):
    """Test indicator integration with configuration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StrategyConfig(
            symbols=["BTCUSDT", "ETHUSDT"],
            candles_limit=50,  # Smaller for faster tests
            trend_magic_version="v3"
        )
        self.engine = IndicatorEngine(self.config)
    
    def test_trend_magic_v1_calculation(self):
        """Test Trend Magic V1 calculation"""
        # Test with V1
        self.config.trend_magic_version = "v1"
        self.engine.update_config(self.config)
        
        result = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        self.assertIsInstance(result, TrendMagicResult)
        self.assertIn(result.color, ["BLUE", "RED"])
        self.assertIsInstance(result.value, float)
        self.assertIsInstance(result.distance_pct, float)
        self.assertIsInstance(result.buy_signal, bool)
        self.assertIsInstance(result.sell_signal, bool)
        self.assertEqual(result.version, "V1")
    
    def test_trend_magic_v2_calculation(self):
        """Test Trend Magic V2 calculation"""
        # Test with V2
        self.config.trend_magic_version = "v2"
        self.engine.update_config(self.config)
        
        result = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        self.assertIsInstance(result, TrendMagicResult)
        self.assertIn(result.color, ["BLUE", "RED"])
        self.assertEqual(result.version, "V2")
    
    def test_trend_magic_v3_calculation(self):
        """Test Trend Magic V3 calculation (TA-Lib)"""
        # Test with V3
        self.config.trend_magic_version = "v3"
        self.engine.update_config(self.config)
        
        result = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        self.assertIsInstance(result, TrendMagicResult)
        self.assertIn(result.color, ["BLUE", "RED"])
        self.assertEqual(result.version, "V3_TALIB")
    
    def test_squeeze_momentum_calculation(self):
        """Test Squeeze Momentum calculation"""
        result = self.engine.calculate_squeeze_momentum("BTCUSDT", "1h")
        
        self.assertIsInstance(result, SqueezeResult)
        self.assertIn(result.momentum_color, ["LIME", "GREEN", "RED", "MAROON"])
        self.assertIn(result.squeeze_color, ["BLUE", "BLACK", "GRAY"])
        self.assertIsInstance(result.squeeze_on, bool)
        self.assertIsInstance(result.squeeze_off, bool)
        self.assertIsInstance(result.no_squeeze, bool)
        self.assertIsInstance(result.momentum_value, float)
    
    def test_parameter_configuration(self):
        """Test different parameter configurations"""
        # Test with custom parameters
        custom_config = StrategyConfig(
            trend_magic_cci_period=14,
            trend_magic_atr_multiplier=1.5,
            trend_magic_atr_period=10,
            squeeze_bb_length=14,
            squeeze_bb_multiplier=2.5,
            candles_limit=50
        )
        
        custom_engine = IndicatorEngine(custom_config)
        
        # Test Trend Magic with custom params
        tm_result = custom_engine.calculate_trend_magic("BTCUSDT", "1h")
        self.assertIsInstance(tm_result, TrendMagicResult)
        
        # Test Squeeze with custom params
        sq_result = custom_engine.calculate_squeeze_momentum("BTCUSDT", "1h")
        self.assertIsInstance(sq_result, SqueezeResult)
    
    def test_multiple_symbols(self):
        """Test calculations with multiple symbols"""
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                # Test Trend Magic
                tm_result = self.engine.calculate_trend_magic(symbol, "1h")
                self.assertIsInstance(tm_result, TrendMagicResult)
                self.assertEqual(tm_result.current_price > 0, True)
                
                # Test Squeeze
                sq_result = self.engine.calculate_squeeze_momentum(symbol, "1h")
                self.assertIsInstance(sq_result, SqueezeResult)
                self.assertEqual(sq_result.current_price > 0, True)
    
    def test_multiple_timeframes(self):
        """Test calculations with multiple timeframes"""
        timeframes = ["15m", "30m", "1h", "4h"]
        
        for timeframe in timeframes:
            with self.subTest(timeframe=timeframe):
                # Test Trend Magic
                tm_result = self.engine.calculate_trend_magic("BTCUSDT", timeframe)
                self.assertIsInstance(tm_result, TrendMagicResult)
                
                # Test Squeeze
                sq_result = self.engine.calculate_squeeze_momentum("BTCUSDT", timeframe)
                self.assertIsInstance(sq_result, SqueezeResult)
    
    def test_indicator_snapshot(self):
        """Test complete indicator snapshot"""
        snapshot = self.engine.get_indicator_snapshot("BTCUSDT", "1h")
        
        self.assertEqual(snapshot.symbol, "BTCUSDT")
        self.assertEqual(snapshot.timeframe, "1h")
        self.assertIsInstance(snapshot.trend_magic, TrendMagicResult)
        self.assertIsInstance(snapshot.squeeze, SqueezeResult)
        self.assertIsInstance(snapshot.timestamp, datetime)
        
        # Test snapshot to_dict conversion
        snapshot_dict = snapshot.to_dict()
        self.assertIsInstance(snapshot_dict, dict)
        self.assertIn('symbol', snapshot_dict)
        self.assertIn('trend_magic', snapshot_dict)
        self.assertIn('squeeze', snapshot_dict)
    
    def test_multi_timeframe_analysis(self):
        """Test multi-timeframe analysis"""
        analysis = self.engine.get_multi_timeframe_analysis("BTCUSDT")
        
        self.assertEqual(analysis.symbol, "BTCUSDT")
        self.assertEqual(analysis.primary_timeframe, self.config.primary_timeframe)
        self.assertEqual(analysis.confirmation_timeframe, self.config.confirmation_timeframe)
        self.assertEqual(analysis.context_timeframe, self.config.context_timeframe)
        
        # Check all timeframe results exist
        self.assertIsInstance(analysis.primary_trend_magic, TrendMagicResult)
        self.assertIsInstance(analysis.primary_squeeze, SqueezeResult)
        self.assertIsInstance(analysis.confirmation_trend_magic, TrendMagicResult)
        self.assertIsInstance(analysis.confirmation_squeeze, SqueezeResult)
        self.assertIsInstance(analysis.context_trend_magic, TrendMagicResult)
        self.assertIsInstance(analysis.context_squeeze, SqueezeResult)
        
        # Check analysis results
        self.assertIn(analysis.overall_trend, ["BULLISH", "BEARISH"])
        self.assertGreaterEqual(analysis.trend_strength, 0.0)
        self.assertLessEqual(analysis.trend_strength, 1.0)
        self.assertIsInstance(analysis.timeframes_aligned, bool)
    
    def test_quick_color_check(self):
        """Test quick color check functionality"""
        color = self.engine.get_trend_magic_color_quick("BTCUSDT", "1h")
        self.assertIn(color, ["BLUE", "RED"])
    
    def test_analyzer_caching(self):
        """Test analyzer caching functionality"""
        # First call should create analyzer
        result1 = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        # Second call should use cached analyzer
        result2 = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        # Results should be consistent (same timestamp within reasonable range)
        self.assertEqual(result1.color, result2.color)
        self.assertEqual(result1.version, result2.version)
    
    def test_config_update(self):
        """Test configuration update and cache clearing"""
        # Get initial result
        initial_result = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        # Update config
        new_config = StrategyConfig(
            trend_magic_cci_period=30,  # Different from default
            trend_magic_version="v2",
            candles_limit=50
        )
        
        self.engine.update_config(new_config)
        
        # Get new result with updated config
        updated_result = self.engine.calculate_trend_magic("BTCUSDT", "1h")
        
        # Version should be different
        self.assertEqual(updated_result.version, "V2")
        self.assertNotEqual(initial_result.version, updated_result.version)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with invalid symbol (should raise exception)
        with self.assertRaises(Exception):
            self.engine.calculate_trend_magic("INVALID", "1h")
        
        # Test with invalid timeframe (should raise exception)
        with self.assertRaises(Exception):
            self.engine.calculate_trend_magic("BTCUSDT", "invalid")


class TestIndicatorParameterValidation(unittest.TestCase):
    """Test parameter validation for indicators"""
    
    def test_trend_magic_parameter_ranges(self):
        """Test Trend Magic parameter validation"""
        # Test valid parameters
        valid_config = StrategyConfig(
            trend_magic_cci_period=20,
            trend_magic_atr_multiplier=1.0,
            trend_magic_atr_period=5
        )
        
        errors = valid_config.validate()
        trend_magic_errors = [e for e in errors if 'trend_magic' in e.lower()]
        self.assertEqual(len(trend_magic_errors), 0)
        
        # Test invalid parameters
        invalid_config = StrategyConfig(
            trend_magic_cci_period=300,  # Too high
            trend_magic_atr_multiplier=15.0,  # Too high
            trend_magic_atr_period=100  # Too high
        )
        
        errors = invalid_config.validate()
        self.assertGreater(len(errors), 0)
    
    def test_squeeze_parameter_ranges(self):
        """Test Squeeze Momentum parameter validation"""
        # Test valid parameters
        valid_config = StrategyConfig(
            squeeze_bb_length=20,
            squeeze_bb_multiplier=2.0,
            squeeze_kc_length=20,
            squeeze_kc_multiplier=1.5
        )
        
        errors = valid_config.validate()
        squeeze_errors = [e for e in errors if 'squeeze' in e.lower()]
        self.assertEqual(len(squeeze_errors), 0)
        
        # Test invalid parameters
        invalid_config = StrategyConfig(
            squeeze_bb_length=200,  # Too high
            squeeze_bb_multiplier=10.0  # Too high
        )
        
        errors = invalid_config.validate()
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    # Setup logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run tests
    unittest.main(verbosity=2)