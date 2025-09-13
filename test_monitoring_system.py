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
        """Display enhanced status for all symbols with indicator details"""
        status = monitor.get_monitoring_status()
        
        print("🎯 ENHANCED SYMBOL STATUS")
        print("┌─────────┬──────────┬─────────┬──────────┬─────────────┬─────────┬──────────────────┐")
        print("│ Symbol  │TM Color  │Squeeze  │Mom Color │    Price    │Signals  │   Last Signal    │")
        print("├─────────┼──────────┼─────────┼──────────┼─────────────┼─────────┼──────────────────┤")
        
        for symbol, symbol_status in status.symbols.items():
            # Get indicator data from the monitor
            indicator_data = self._get_indicator_data(monitor, symbol)
            
            # Format trend magic color
            tm_color = self._format_trend_magic_color(indicator_data.get('trend_magic_color', 'UNKNOWN'))
            
            # Format squeeze status
            squeeze_status = self._format_squeeze_status(indicator_data.get('squeeze_status', 'UNKNOWN'))
            
            # Format momentum color (instead of direction)
            momentum_color = self._format_momentum_color(indicator_data.get('momentum_color', 'UNKNOWN'))
            
            # Format price
            if symbol_status.current_price:
                if symbol_status.current_price >= 1000:
                    price_text = f"${symbol_status.current_price:,.0f}"
                elif symbol_status.current_price >= 1:
                    price_text = f"${symbol_status.current_price:.2f}"
                else:
                    price_text = f"${symbol_status.current_price:.4f}"
            else:
                price_text = "N/A"
            
            # Format last signal
            if symbol_status.latest_signal_type and symbol_status.latest_signal_time:
                time_diff = datetime.now() - symbol_status.latest_signal_time
                minutes_ago = int(time_diff.total_seconds() / 60)
                signal_short = symbol_status.latest_signal_type.replace('_', '').upper()[:8]
                last_signal = f"{signal_short}({minutes_ago}m)"
            else:
                last_signal = "None"
            
            # Handle error states - NO DEFAULT ASSUMPTIONS, ONLY REAL DATA
            if symbol_status.state.value == 'error':
                tm_color = "❌ ERR"
                squeeze_status = "❌ ERR"
                momentum_color = "❌ ERR"
                price_text = "N/A"
            # If data is UNKNOWN, keep it as UNKNOWN - NO FAKE DATA
            
            print(f"│{symbol:<8} │{tm_color:<9} │{squeeze_status:<8} │{momentum_color:<9} │{price_text:>11} │{symbol_status.signal_count:>6}  │{last_signal:<16} │")
        
        print("└─────────┴──────────┴─────────┴──────────┴─────────────┴─────────┴──────────────────┘")
        print()
    
    def _get_indicator_data(self, monitor: StrategyMonitor, symbol: str) -> dict:
        """Get current indicator data for a symbol"""
        try:
            symbol_status = monitor.get_symbol_status(symbol)
            if not symbol_status:
                return {
                    'trend_magic_color': 'UNKNOWN',
                    'squeeze_status': 'UNKNOWN',
                    'momentum_direction': 'UNKNOWN',
                    'momentum_color': 'UNKNOWN'
                }
            
            # ALWAYS get REAL indicator data from IndicatorEngine (ignore cached symbol_status)
            real_data = self._get_real_indicator_data(monitor, symbol)
            
            tm_color = real_data.get('trend_magic_color', 'UNKNOWN')
            squeeze_status = real_data.get('squeeze_status', 'UNKNOWN')
            momentum_dir = real_data.get('momentum_direction', 'UNKNOWN')
            momentum_color = real_data.get('momentum_color', 'UNKNOWN')
            
            return {
                'trend_magic_color': tm_color,
                'squeeze_status': squeeze_status,
                'momentum_direction': momentum_dir,
                'momentum_color': momentum_color
            }
            
        except Exception as e:
            return {
                'trend_magic_color': 'UNKNOWN',
                'squeeze_status': 'UNKNOWN',
                'momentum_direction': 'UNKNOWN',
                'momentum_color': 'UNKNOWN'
            }
    
    def _format_trend_magic_color(self, color: str) -> str:
        """Format trend magic color with emoji"""
        color_map = {
            'BLUE': '🔵 BLUE',
            'RED': '🔴 RED',
            'UNKNOWN': '⚪ UNK'
        }
        return color_map.get(color.upper(), '⚪ UNK')
    
    def _format_squeeze_status(self, status: str) -> str:
        """Format squeeze status with emoji"""
        status_map = {
            'ON': '🔴 ON',
            'OFF': '🟢 OFF',
            'UNKNOWN': '⚪ UNK'
        }
        return status_map.get(status.upper(), '⚪ UNK')
    
    def _format_momentum_direction(self, direction: str) -> str:
        """Format momentum direction with emoji"""
        direction_map = {
            'UP': '⬆️ UP',
            'DOWN': '⬇️ DOWN',
            'UNKNOWN': '➡️ UNK'
        }
        return direction_map.get(direction.upper(), '➡️ UNK')
    
    def _format_momentum_color(self, color: str) -> str:
        """Format momentum color with emoji"""
        color_map = {
            'LIME': '🟢 LIME',
            'GREEN': '🟢 GRN',
            'RED': '🔴 RED',
            'MAROON': '🟤 MAR',
            'UNKNOWN': '⚪ UNK'
        }
        return color_map.get(color.upper(), '⚪ UNK')
    
    def _get_real_indicator_data(self, monitor: StrategyMonitor, symbol: str) -> dict:
        """Get REAL indicator data using the same method as trend_magic_continuous_compare.py"""
        try:
            # Temporarily suppress TechnicalAnalyzer logging to avoid cluttering the display
            import logging
            ta_logger = logging.getLogger(f"TechnicalAnalyzer-{symbol}")
            original_level = ta_logger.level
            ta_logger.setLevel(logging.ERROR)
            
            try:
                # Force fresh data by using the TechnicalAnalyzer directly like trend_magic_continuous_compare.py
                from indicators.technical_indicators import TechnicalAnalyzer
                
                # Create fresh analyzer instance (no caching)
                analyzer = TechnicalAnalyzer(symbol, "1m")  # Use 1m like your working script
                
                # Fetch fresh market data (50 candles like your script)
                analyzer.fetch_market_data(limit=50)
                
                # Calculate Trend Magic V3 (same as your script)
                tm_result = analyzer.trend_magic_v3()
                
                # Calculate Squeeze Momentum
                squeeze_result = analyzer.squeeze_momentum()
                
                return {
                    'trend_magic_color': tm_result['color'],
                    'squeeze_status': 'ON' if squeeze_result['squeeze_on'] else 'OFF',
                    'momentum_direction': 'UP' if squeeze_result['momentum_value'] > 0 else 'DOWN',
                    'momentum_color': squeeze_result['momentum_color']  # RED, MAROON, LIME, GREEN
                }

            finally:
                # Restore original logging level
                ta_logger.setLevel(original_level)
            
        except Exception as e:
            return {
                'trend_magic_color': 'UNKNOWN',
                'squeeze_status': 'UNKNOWN',
                'momentum_direction': 'UNKNOWN',
                'momentum_color': 'UNKNOWN'
            }
    
    def display_indicator_details(self, monitor: StrategyMonitor):
        """Display detailed indicator information for comparison with TradingView"""
        status = monitor.get_monitoring_status()
        
        print("📊 INDICATOR DETAILS (for TradingView comparison)")
        print("-" * 70)
        
        active_symbols = [symbol for symbol, symbol_status in status.symbols.items() 
                         if symbol_status.state.value == 'active'][:5]  # Show top 5
        
        for symbol in active_symbols:
            symbol_status = status.symbols[symbol]
            indicator_data = self._get_indicator_data(monitor, symbol)
            
            tm_color = indicator_data.get('trend_magic_color', 'UNKNOWN')
            squeeze_status = indicator_data.get('squeeze_status', 'UNKNOWN')
            momentum_color = indicator_data.get('momentum_color', 'UNKNOWN')
            
            price_text = f"${symbol_status.current_price:.4f}" if symbol_status.current_price else "N/A"
            
            print(f"{symbol:>8}: TM={tm_color:<4} | SQ={squeeze_status:<3} | MOM={momentum_color:<4} | Price={price_text}")
        
        print()
        print("💡 Compare with TradingView:")
        print("   - TM = Trend Magic color (BLUE=Bullish, RED=Bearish)")
        print("   - SQ = Squeeze status (ON=Compressed, OFF=Expanded)")  
        print("   - MOM = Momentum color (LIME=Strong Up, GREEN=Up, RED=Down, MAROON=Strong Down)")
        print()
        print("ℹ️  Note: If showing UNKNOWN, the system is still gathering indicator data.")
        print("   Wait a few update cycles for accurate indicator readings.")
        print()
        print("ℹ️  Note: If showing UNKNOWN, the system is still gathering indicator data.")
        print("   Wait a few update cycles for accurate indicator readings.")
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
        print("🔧 TROUBLESHOOTING:")
        print("- If indicators show UNKNOWN, wait 1-2 update cycles")
        print("- Check that primary_timeframe is set to '1m' in config")
        print("- Verify API connectivity and data quality")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("- If indicators show UNKNOWN, wait 1-2 update cycles")
        print("- Check that primary_timeframe is set to '1m' in config")
        print("- Verify API connectivity and data quality")
        print()


def test_monitoring_display():
    """Test monitoring system with live display"""
    print("🏛️⚔️ SPARTAN MULTI-CRYPTO MONITORING SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Setup logging - Reduce console noise for clean display
        logging.basicConfig(
            level=logging.WARNING,  # Only show warnings and errors on console
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring_test.log'),  # Full logs to file
                logging.StreamHandler()  # Only warnings/errors to console
            ]
        )
        
        # Set specific loggers to reduce noise
        logging.getLogger('MarketDataProvider').setLevel(logging.ERROR)
        logging.getLogger('IndicatorEngine').setLevel(logging.ERROR)
        logging.getLogger('StrategyMonitor').setLevel(logging.WARNING)
        
        # Suppress TechnicalAnalyzer logs during display updates
        for symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']:
            logging.getLogger(f"TechnicalAnalyzer-{symbol}").setLevel(logging.ERROR)
        
        # Load configuration
        print("📋 Loading configuration...")
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create monitoring system
        print("🏛️ Initializing Spartan Strategy Monitor...")
        monitor = StrategyMonitor(config)
        
        # Create display
        display = MonitoringDisplay()
        
        # Add some test symbols (removed FTMUSDT and MATICUSDT due to data issues)
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
                display.display_indicator_details(monitor)
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
        # Suppress TechnicalAnalyzer logs for clean output
        import logging
        for symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
            logging.getLogger(f"TechnicalAnalyzer-{symbol}").setLevel(logging.ERROR)
        
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