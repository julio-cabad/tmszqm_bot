#!/usr/bin/env python3
"""
Quick test of the enhanced display
"""

import sys
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.monitoring.strategy_monitor import StrategyMonitor
from test_monitoring_system import MonitoringDisplay
import time

def quick_test():
    print("🏛️⚔️ QUICK TEST - ENHANCED DISPLAY")
    print("=" * 50)
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create monitor
        monitor = StrategyMonitor(config)
        
        # Add a few symbols
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        for symbol in test_symbols:
            monitor.add_symbol(symbol)
        
        # Start monitoring
        print("🚀 Starting monitoring...")
        if monitor.start_monitoring():
            print("✅ Monitoring started")
            
            # Wait a bit for data
            print("⏳ Waiting 30 seconds for indicator data...")
            time.sleep(30)
            
            # Display enhanced status
            display = MonitoringDisplay()
            display.clear_screen()
            display.display_header()
            display.display_monitoring_status(monitor)
            display.display_symbol_status(monitor)
            display.display_indicator_details(monitor)
            
            # Stop monitoring
            monitor.stop_monitoring()
            monitor.shutdown()
            
            print("✅ Test completed successfully!")
        else:
            print("❌ Failed to start monitoring")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    quick_test()