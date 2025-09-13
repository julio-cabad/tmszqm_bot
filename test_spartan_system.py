#!/usr/bin/env python3
"""
Test Spartan Trading System - Configuration and Indicators
Quick test to verify the system is working correctly
"""

import logging
import sys
import os

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.config.strategy_config import StrategyConfig
from spartan_trading_system.indicators.indicator_engine import IndicatorEngine

def test_configuration_system():
    """Test configuration loading and validation"""
    print("🏛️ ═══ TESTING CONFIGURATION SYSTEM ═══")
    
    try:
        # Test ConfigManager
        config_manager = ConfigManager()
        
        # Create default configs
        config_manager.create_default_configs()
        print("✅ Default configurations created")
        
        # Load default config
        config = config_manager.load_config("default.json")
        print(f"✅ Default config loaded: {len(config.symbols)} symbols")
        
        # Validate config
        errors = config_manager.validate_config(config)
        if errors:
            print(f"❌ Validation errors: {errors}")
            return False
        else:
            print("✅ Configuration validation passed")
        
        # Test config info
        info = config_manager.get_config_info("default.json")
        if 'symbols_count' in info:
            print(f"✅ Config info: {info['symbols_count']} symbols, {info['primary_timeframe']} timeframe")
        else:
            print(f"✅ Config info retrieved: {len(config.symbols)} symbols, {config.primary_timeframe} timeframe")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_indicator_engine():
    """Test indicator engine with existing indicators"""
    print("\n🎯 ═══ TESTING INDICATOR ENGINE ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create indicator engine
        indicator_engine = IndicatorEngine(config)
        print("✅ Indicator Engine initialized")
        
        # Test with BTC
        symbol = "BTCUSDT"
        timeframe = config.primary_timeframe
        
        print(f"📊 Testing indicators for {symbol} on {timeframe}...")
        
        # Test Trend Magic
        trend_magic = indicator_engine.calculate_trend_magic(symbol, timeframe)
        print(f"✅ Trend Magic: {trend_magic.color} | Value: ${trend_magic.value:,.2f} | Version: {trend_magic.version}")
        
        # Test Squeeze Momentum
        squeeze = indicator_engine.calculate_squeeze_momentum(symbol, timeframe)
        print(f"✅ Squeeze: {squeeze.squeeze_status} | Momentum: {squeeze.momentum_color}")
        
        # Test complete snapshot
        snapshot = indicator_engine.get_indicator_snapshot(symbol, timeframe)
        print(f"✅ Snapshot created for {snapshot.symbol} at {snapshot.timestamp}")
        
        # Test quick color check
        quick_color = indicator_engine.get_trend_magic_color_quick(symbol, timeframe)
        print(f"✅ Quick color check: {quick_color}")
        
        return True
        
    except Exception as e:
        print(f"❌ Indicator engine test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_timeframe_analysis():
    """Test multi-timeframe analysis"""
    print("\n⏰ ═══ TESTING MULTI-TIMEFRAME ANALYSIS ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create indicator engine
        indicator_engine = IndicatorEngine(config)
        
        # Test multi-timeframe analysis
        symbol = "BTCUSDT"
        analysis = indicator_engine.get_multi_timeframe_analysis(symbol)
        
        print(f"✅ Multi-timeframe analysis for {symbol}:")
        print(f"   Primary ({analysis.primary_timeframe}): {analysis.primary_trend_magic.color}")
        print(f"   Confirmation ({analysis.confirmation_timeframe}): {analysis.confirmation_trend_magic.color}")
        print(f"   Context ({analysis.context_timeframe}): {analysis.context_trend_magic.color}")
        print(f"   Overall Trend: {analysis.overall_trend} (Strength: {analysis.trend_strength:.2f})")
        print(f"   Timeframes Aligned: {analysis.timeframes_aligned}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-timeframe test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🏛️ SPARTAN TRADING SYSTEM - INTEGRATION TEST")
    print("⚔️ Testing configuration and indicator integration")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Configuration System", test_configuration_system),
        ("Indicator Engine", test_indicator_engine),
        ("Multi-Timeframe Analysis", test_multi_timeframe_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("🏛️ TEST RESULTS SUMMARY:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🏆 ALL TESTS PASSED! Spartan system is ready for battle! ⚔️")
        return True
    else:
        print("💀 Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)