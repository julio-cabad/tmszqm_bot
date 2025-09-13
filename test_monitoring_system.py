#!/usr/bin/env python3
"""
Multi-Crypto Monitoring System Test - Spartan Real-Time Monitoring
Comprehensive testing of the monitoring system with visual status display
"""

import logging
import sys
import time
import os
from datetime import datetime

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.monitoring.strategy_monitor import StrategyMonitor
from spartan_trading_system.monitoring.monitoring_models import MonitoringState, SymbolState


class MonitoringDisplay:
    """Visual display for monitoring system status"""
    
    def __init__(self):
        self.last_display_time = None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display system header"""
        print("🏛️" + "=" * 80 + "⚔️")
        print("🏛️" + " " * 15 + "SPARTAN MULTI-CRYPTO MONITORING SYSTEM" + " " * 15 + "⚔️")
        print("🏛️" + "=" * 80 + "⚔️")
        print()
    
    def display_monitoring_status(self, monitor: StrategyMonitor):
        """Display overall monitoring status"""
        status = monitor.get_monitoring_status()
        
        print("📊 SYSTEM STATUS")
        print("-" * 50)
        print(f"Status: {status.get_status_emoji()} {status.state.value.upper()}")
        print(f"Uptime: {status.get_uptime_string()}")
        print(f"Health Score: {status.get_health_score():.1%}")
        print(f"Symbols: {status.active_symbols}/{status.total_symbols} active")
        print(f"Total Signals: {status.total_signals}")
        print(f"Memory Usage: {status.memory_usage_mb:.1f} MB")
        print(f"CPU Usage: {status.cpu_usage_percent:.1f}%")
        print()
    
    def display_symbol_status(self, monitor: StrategyMonitor):
        """Display status for all symbols"""
        status = monitor.get_monitoring_status()
        
        print("🎯 SYMBOL STATUS")
        print("-" * 80)
        print(f"{'Symbol':<12} {'Status':<15} {'Signals':<8} {'Price':<12} {'Last Signal':<20}")
        print("-" * 80)
        
        for symbol, symbol_status in status.symbols.items():
            status_text = symbol_status.get_status_summary()
            
            # Format price
            price_text = f"${symbol_status.current_price:.4f}" if symbol_status.current_price else "N/A"
            
            # Format last signal
            if symbol_status.latest_signal_type and symbol_status.latest_signal_time:
                time_diff = datetime.now() - symbol_status.latest_signal_time
                minutes_ago = int(time_diff.total_seconds() / 60)
                last_signal = f"{symbol_status.latest_signal_type} ({minutes_ago}m ago)"
            else:
                last_signal = "None"
            
            print(f"{symbol:<12} {status_text:<35} {symbol_status.signal_count:<8} {price_text:<12} {last_signal:<20}")
        
        print()
    
    def display_performance_metrics(self, monitor: StrategyMonitor):
        """Display performance metrics"""
        perf_summary = monitor.get_performance_summary()
        
        print("⚡ PERFORMANCE METRICS")
        print("-" * 50)
        
        # System performance
        sys_perf = perf_summary.get('system_performance', {})
        print(f"API Calls/min: {sys_perf.get('api_calls_per_minute', 0)}")
        print(f"Avg API Response: {sys_perf.get('avg_api_response_time_ms', 0):.1f}ms")
        print(f"Rate Limit Hits: {sys_perf.get('rate_limit_hits', 0)}")
        
        # Signal performance
        signal_perf = perf_summary.get('signal_performance', {})
        print(f"Avg Signal Strength: {signal_perf.get('avg_signal_strength', 0):.2f}")
        print(f"Avg Detection Time: {signal_perf.get('avg_detection_time_ms', 0):.1f}ms")
        
        # Alert stats
        alert_stats = perf_summary.get('alert_stats', {})
        print(f"Alerts Today: {alert_stats.get('alerts_today', 0)}")
        print(f"Total Alerts: {alert_stats.get('total_alerts', 0)}")
        
        print()
    
    def display_recent_alerts(self, monitor: StrategyMonitor):
        """Display recent alerts"""
        recent_alerts = monitor.alert_manager.get_recent_alerts(5)
        
        if recent_alerts:
            print("🔔 RECENT ALERTS")
            print("-" * 60)
            
            for alert in recent_alerts[-5:]:  # Last 5 alerts
                timestamp = alert['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                time_str = timestamp.strftime("%H:%M:%S")
                priority_emoji = {
                    'critical': '🚨',
                    'high': '⚠️',
                    'medium': '📢',
                    'low': 'ℹ️',
                    'info': '💬'
                }.get(alert['priority'], '📢')
                
                print(f"{time_str} {priority_emoji} {alert['message']}")
            
            print()
    
    def display_controls(self):
        """Display control instructions"""
        print("🎮 CONTROLS")
        print("-" * 30)
        print("Ctrl+C: Stop monitoring")
        print("The display updates every 10 seconds")
        print()


def test_monitoring_display():
    """Test monitoring system with live display"""
    print("🏛️⚔️ SPARTAN MULTI-CRYPTO MONITORING SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring_test.log'),
                logging.StreamHandler()
            ]
        )
        
        # Load configuration
        print("📋 Loading configuration...")
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create monitoring system
        print("🏛️ Initializing Spartan Strategy Monitor...")
        monitor = StrategyMonitor(config)
        
        # Create display
        display = MonitoringDisplay()
        
        # Add some test symbols
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
        print(f"📊 Adding {len(test_symbols)} symbols for monitoring...")
        
        for symbol in test_symbols:
            monitor.add_symbol(symbol)
        
        # Start monitoring
        print("🚀 Starting monitoring system...")
        if not monitor.start_monitoring():
            print("❌ Failed to start monitoring")
            return False
        
        print("✅ Monitoring started successfully!")
        print("📺 Starting live display (Ctrl+C to stop)...")
        time.sleep(2)
        
        # Live display loop
        try:
            while True:
                # Clear screen and display status
                display.clear_screen()
                display.display_header()
                display.display_monitoring_status(monitor)
                display.display_symbol_status(monitor)
                display.display_performance_metrics(monitor)
                display.display_recent_alerts(monitor)
                display.display_controls()
                
                # Wait for next update
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring system...")
            
        finally:
            # Stop monitoring
            monitor.stop_monitoring()
            monitor.shutdown()
            print("✅ Monitoring system stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {str(e)}")
        return False


def test_monitoring_basic():
    """Basic monitoring system test without display"""
    print("🏛️ ═══ BASIC MONITORING SYSTEM TEST ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create monitoring system
        monitor = StrategyMonitor(config)
        
        # Test adding symbols
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        print(f"📊 Testing symbol management...")
        for symbol in test_symbols:
            result = monitor.add_symbol(symbol)
            print(f"   Add {symbol}: {'✅' if result else '❌'}")
        
        # Test monitoring start/stop
        print(f"🚀 Testing monitoring start...")
        start_result = monitor.start_monitoring()
        print(f"   Start monitoring: {'✅' if start_result else '❌'}")
        
        if start_result:
            # Let it run for a few seconds
            print("⏳ Running monitoring for 30 seconds...")
            time.sleep(30)
            
            # Get status
            status = monitor.get_monitoring_status()
            print(f"📊 Monitoring Status:")
            print(f"   State: {status.state.value}")
            print(f"   Active Symbols: {status.active_symbols}/{status.total_symbols}")
            print(f"   Total Signals: {status.total_signals}")
            print(f"   Health Score: {status.get_health_score():.1%}")
            
            # Test symbol operations
            print(f"⏸️ Testing symbol pause/resume...")
            pause_result = monitor.pause_symbol('BTCUSDT')
            print(f"   Pause BTCUSDT: {'✅' if pause_result else '❌'}")
            
            time.sleep(5)
            
            resume_result = monitor.resume_symbol('BTCUSDT')
            print(f"   Resume BTCUSDT: {'✅' if resume_result else '❌'}")
            
            # Test performance summary
            print(f"⚡ Getting performance summary...")
            perf_summary = monitor.get_performance_summary()
            print(f"   Performance data available: {'✅' if perf_summary else '❌'}")
            
            # Stop monitoring
            print(f"🛑 Testing monitoring stop...")
            stop_result = monitor.stop_monitoring()
            print(f"   Stop monitoring: {'✅' if stop_result else '❌'}")
        
        # Test symbol removal
        print(f"🗑️ Testing symbol removal...")
        for symbol in test_symbols:
            result = monitor.remove_symbol(symbol)
            print(f"   Remove {symbol}: {'✅' if result else '❌'}")
        
        # Shutdown
        monitor.shutdown()
        
        print("✅ Basic monitoring test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic monitoring test failed: {str(e)}")
        return False


def main():
    """Run monitoring system tests"""
    print("🏛️⚔️ SPARTAN MONITORING SYSTEM TESTS")
    print("=" * 60)
    
    # Ask user which test to run
    print("Select test to run:")
    print("1. Basic monitoring test (30 seconds)")
    print("2. Live monitoring display (interactive)")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            return test_monitoring_basic()
        elif choice == "2":
            return test_monitoring_display()
        elif choice == "3":
            print("\n" + "="*60)
            print("Running basic test first...")
            basic_result = test_monitoring_basic()
            
            if basic_result:
                print("\n" + "="*60)
                print("Basic test passed! Starting live display...")
                input("Press Enter to continue to live display...")
                return test_monitoring_display()
            else:
                print("❌ Basic test failed, skipping live display")
                return False
        else:
            print("❌ Invalid choice")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)