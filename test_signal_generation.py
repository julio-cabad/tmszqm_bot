#!/usr/bin/env python3
"""
Test Signal Generation System - The Heart of Spartan Strategy
Complete test of signal generation with real market data
"""

import logging
import sys
import os
from datetime import datetime

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.indicators.indicator_engine import IndicatorEngine
from spartan_trading_system.strategy.signal_generator import SignalGenerator
from spartan_trading_system.strategy.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from spartan_trading_system.strategy.signal_types import SignalType, Direction


def test_signal_generation():
    """Test complete signal generation system"""
    print("🏛️ ═══ TESTING SIGNAL GENERATION SYSTEM ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        print(f"✅ Configuration loaded: {len(config.symbols)} symbols")
        
        # Initialize components
        indicator_engine = IndicatorEngine(config)
        signal_generator = SignalGenerator(config, indicator_engine)
        
        print("✅ Signal Generator initialized")
        
        # Test signal generation for BTC
        symbol = "BTCUSDT"
        print(f"\n🎯 Generating signals for {symbol}...")
        
        signals = signal_generator.generate_signals(symbol)
        
        if signals:
            for signal in signals:
                print(f"\n🚀 SIGNAL DETECTED:")
                print(f"   Type: {signal.signal_type.value.upper()}")
                print(f"   Direction: {signal.direction.value.upper()}")
                print(f"   Strength: {signal.strength:.2f} ({signal.get_strength_classification().value})")
                print(f"   Confidence: {signal.confidence:.2f}")
                print(f"   Entry: ${signal.entry_price:,.2f}")
                print(f"   Stop Loss: ${signal.stop_loss:,.2f}")
                print(f"   Take Profits: {[f'${tp:,.2f}' for tp in signal.take_profit_levels]}")
                print(f"   R:R Ratio: {signal.get_risk_reward_ratio():.2f}")
                print(f"   Position Size: {signal.position_size_pct:.1f}%")
                print(f"   Trigger: {signal.trigger_reason}")
                print(f"   Supporting Factors:")
                for factor in signal.supporting_factors:
                    print(f"     - {factor}")
                if signal.risk_factors:
                    print(f"   Risk Factors:")
                    for risk in signal.risk_factors:
                        print(f"     - {risk}")
        else:
            print("   No signals generated (conditions not met)")
        
        return True
        
    except Exception as e:
        print(f"❌ Signal generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_timeframe_analyzer():
    """Test multi-timeframe analysis system"""
    print("\n⏰ ═══ TESTING MULTI-TIMEFRAME ANALYZER ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Initialize components
        indicator_engine = IndicatorEngine(config)
        mtf_analyzer = MultiTimeframeAnalyzer(config, indicator_engine)
        
        print("✅ Multi-Timeframe Analyzer initialized")
        
        # Test comprehensive analysis
        symbol = "BTCUSDT"
        print(f"\n🔍 Comprehensive analysis for {symbol}...")
        
        analysis = mtf_analyzer.get_comprehensive_analysis(symbol)
        
        if analysis:
            print(f"✅ Analysis completed:")
            
            # Trend alignment
            trend_alignment = analysis.get('trend_alignment', {})
            print(f"   Trend Alignment:")
            print(f"     Dominant: {trend_alignment.get('dominant_trend', 'N/A')}")
            print(f"     Score: {trend_alignment.get('alignment_score', 0):.2f}")
            print(f"     Perfect: {trend_alignment.get('perfect_alignment', False)}")
            
            # Momentum confluence
            momentum_confluence = analysis.get('momentum_confluence', {})
            print(f"   Momentum Confluence:")
            print(f"     Dominant: {momentum_confluence.get('dominant_momentum', 'N/A')}")
            print(f"     Alignment: {momentum_confluence.get('momentum_alignment', 0):.2f}")
            print(f"     Strength: {momentum_confluence.get('momentum_strength', 0):.2f}")
            
            # Squeeze analysis
            squeeze_analysis = analysis.get('squeeze_analysis', {})
            print(f"   Squeeze Analysis:")
            print(f"     Overall: {squeeze_analysis.get('overall_condition', 'N/A')}")
            print(f"     Compression Ratio: {squeeze_analysis.get('compression_ratio', 0):.2f}")
            print(f"     Expansion Ratio: {squeeze_analysis.get('expansion_ratio', 0):.2f}")
            
            # Market structure
            market_structure = analysis.get('market_structure', {})
            print(f"   Market Structure:")
            print(f"     Higher TF Bias: {market_structure.get('higher_timeframe_bias', 'N/A')}")
            print(f"     Primary TF Bias: {market_structure.get('primary_timeframe_bias', 'N/A')}")
            print(f"     Aligned: {market_structure.get('structure_aligned', False)}")
            
            # Overall metrics
            print(f"   Overall Bias: {analysis.get('overall_bias', 'N/A')}")
            print(f"   Confluence Score: {analysis.get('confluence_score', 0):.2f}")
            print(f"   Optimal Entry TF: {analysis.get('optimal_entry_timeframe', 'N/A')}")
        
        # Test entry confirmation
        print(f"\n🎯 Testing entry confirmation...")
        
        for direction in [Direction.LONG, Direction.SHORT]:
            confirmation = mtf_analyzer.get_entry_confirmation(symbol, direction)
            status = "✅ CONFIRMED" if confirmation['confirmed'] else "❌ REJECTED"
            print(f"   {direction.value.upper()}: {status} ({confirmation['confirmation_score']:.2f})")
            print(f"     Reason: {confirmation['reason']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-timeframe analyzer test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_types_and_strength():
    """Test different signal types and strength calculations"""
    print("\n🎯 ═══ TESTING SIGNAL TYPES AND STRENGTH ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("aggressive.json")  # Use aggressive config for more signals
        
        # Initialize components
        indicator_engine = IndicatorEngine(config)
        signal_generator = SignalGenerator(config, indicator_engine)
        
        print("✅ Signal Generator initialized with aggressive config")
        
        # Test multiple symbols to find different signal types
        test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT"]
        
        all_signals = []
        
        for symbol in test_symbols:
            try:
                print(f"\n📊 Testing {symbol}...")
                signals = signal_generator.generate_signals(symbol)
                
                if signals:
                    for signal in signals:
                        all_signals.append(signal)
                        print(f"   {signal.signal_type.value.upper()}: {signal.strength:.2f} strength")
                else:
                    print(f"   No signals for {symbol}")
                    
            except Exception as e:
                print(f"   ❌ Error with {symbol}: {str(e)}")
        
        # Summary of signal types found
        if all_signals:
            print(f"\n📈 SIGNAL SUMMARY:")
            signal_types = {}
            for signal in all_signals:
                signal_type = signal.signal_type.value
                if signal_type not in signal_types:
                    signal_types[signal_type] = []
                signal_types[signal_type].append(signal.strength)
            
            for signal_type, strengths in signal_types.items():
                avg_strength = sum(strengths) / len(strengths)
                print(f"   {signal_type.upper()}: {len(strengths)} signals, avg strength {avg_strength:.2f}")
        else:
            print("   No signals generated across all symbols")
        
        return True
        
    except Exception as e:
        print(f"❌ Signal types test failed: {str(e)}")
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
    
    print("🏛️ SPARTAN SIGNAL GENERATION SYSTEM - COMPREHENSIVE TEST")
    print("⚔️ Testing the heart of the trading strategy")
    print("=" * 70)
    
    # Run tests
    tests = [
        ("Signal Generation System", test_signal_generation),
        ("Multi-Timeframe Analyzer", test_multi_timeframe_analyzer),
        ("Signal Types and Strength", test_signal_types_and_strength)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 70)
    print("🏛️ SIGNAL GENERATION TEST RESULTS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🏆 ALL TESTS PASSED! Signal generation system is ready for battle! ⚔️")
        print("🚀 The heart of the Spartan strategy is beating strong!")
        return True
    else:
        print("💀 Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)