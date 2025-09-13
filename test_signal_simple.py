#!/usr/bin/env python3
"""
Simple Signal Generation Test
Quick test of the core signal generation functionality
"""

import logging
import sys
import os

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.indicators.indicator_engine import IndicatorEngine
from spartan_trading_system.strategy.signal_generator import SignalGenerator

def main():
    """Simple signal generation test"""
    # Setup logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise
    
    print("🏛️ SPARTAN SIGNAL GENERATION - QUICK TEST")
    print("=" * 50)
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        print(f"✅ Config loaded: {config.primary_timeframe} timeframe")
        
        # Initialize components
        indicator_engine = IndicatorEngine(config)
        signal_generator = SignalGenerator(config, indicator_engine)
        print("✅ Signal Generator initialized")
        
        # Test BTC signal generation
        symbol = "BTCUSDT"
        print(f"\n🎯 Generating signals for {symbol}...")
        
        signals = signal_generator.generate_signals(symbol)
        
        if signals:
            signal = signals[0]  # Take first signal
            print(f"\n🚀 SIGNAL DETECTED!")
            print(f"   Type: {signal.signal_type.value.upper()}")
            print(f"   Direction: {signal.direction.value.upper()}")
            print(f"   Strength: {signal.strength:.2f}")
            print(f"   Entry: ${signal.entry_price:,.2f}")
            print(f"   Stop: ${signal.stop_loss:,.2f}")
            print(f"   TP1: ${signal.take_profit_levels[0]:,.2f}")
            print(f"   R:R: {signal.get_risk_reward_ratio():.2f}")
            print(f"   Reason: {signal.trigger_reason}")
            
            print(f"\n✅ SIGNAL GENERATION WORKING!")
        else:
            print("   No signals (market conditions not met)")
            print("   ✅ System working - just no entry conditions")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 SPARTAN SIGNAL SYSTEM OPERATIONAL! ⚔️")
    sys.exit(0 if success else 1)