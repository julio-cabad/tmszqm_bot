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
        
        print("🏛️⚔️ SPARTAN CONFLUENCE SIGNALS")
        print("┌─────────┬─────────┬─────────┬─────────┬──────────┬─────────┬──────────────────────┐")
        print("│ Symbol  │ 1m TM   │ 15m TM  │ 1h TM   │ Mom 1m   │Signals  │   Confluence Signal  │")
        print("├─────────┼─────────┼─────────┼─────────┼──────────┼─────────┼──────────────────────┤")
        
        for symbol, symbol_status in status.symbols.items():
            # Skip problematic symbols that were removed from config
            if symbol in ['MATICUSDT', 'FTMUSDT'] or symbol_status.state.value == 'error':
                continue
                
            # Get SPARTAN multi-timeframe data
            tf_data = self._get_multi_timeframe_data(monitor, symbol)
            
            # Format Trend Magic colors for all timeframes
            tm_1m = self._format_trend_magic_color(tf_data.get('1m', {}).get('trend_magic_color', 'UNKNOWN'))
            tm_15m = self._format_trend_magic_color(tf_data.get('15m', {}).get('trend_magic_color', 'UNKNOWN'))
            tm_1h = self._format_trend_magic_color(tf_data.get('1h', {}).get('trend_magic_color', 'UNKNOWN'))
            
            # Format momentum color (1m only)
            momentum_color = self._format_momentum_color(tf_data.get('1m', {}).get('momentum_color', 'UNKNOWN'))
            
            # Check SPARTAN confluence
            confluence_signal = self._check_spartan_confluence(symbol, tf_data)
            
            # Handle error states
            if symbol_status.state.value == 'error':
                tm_1m = tm_15m = tm_1h = "❌ ERR"
                momentum_color = "❌ ERR"
                confluence_signal = "❌ ERROR"
            
            # Shorten TM colors for table
            tm_1m_short = tm_1m.replace(' ', '')[:7]
            tm_15m_short = tm_15m.replace(' ', '')[:7]
            tm_1h_short = tm_1h.replace(' ', '')[:7]
            mom_short = momentum_color.replace(' ', '')[:8]
            
            print(f"│{symbol:<8} │{tm_1m_short:<7} │{tm_15m_short:<7} │{tm_1h_short:<7} │{mom_short:<8} │{symbol_status.signal_count:>6}  │{confluence_signal:<20} │")
        
        print("└─────────┴─────────┴─────────┴─────────┴──────────┴─────────┴──────────────────────┘")
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
    
    def _get_signal_direction(self, tm_color: str) -> str:
        """Determine signal direction based on Trend Magic color"""
        if tm_color == 'BLUE':
            return 'LONG'
        elif tm_color == 'RED':
            return 'SHORT'
        else:
            return 'UNK'
    
    def _is_signal_valid(self, signal_type: str, tm_color: str, signal_time) -> bool:
        """Check if signal is still valid based on current conditions"""
        if not signal_type or not signal_time:
            return False
        
        # Get signal direction when it was generated
        # For now, we'll assume signals were generated correctly at the time
        # In a real implementation, we'd store the original TM color with the signal
        
        # Simple validation: if signal is older than 30 minutes, consider it stale
        from datetime import datetime, timedelta
        if isinstance(signal_time, str):
            return True  # Can't parse time, keep signal for now
        
        time_diff = datetime.now() - signal_time
        if time_diff > timedelta(minutes=30):
            return False  # Signal too old
        
        return True  # Signal is recent enough
    
    def _format_signal_with_direction(self, signal_type: str, signal_time, tm_color: str) -> str:
        """Format signal with direction (LONG/SHORT) and time"""
        if not signal_type:
            return "None"
        
        # Determine direction based on current TM color
        direction = self._get_signal_direction(tm_color)
        
        # Extract time from signal_time
        if signal_time:
            if isinstance(signal_time, str):
                time_str = "0m"  # Default if can't parse
            else:
                from datetime import datetime
                time_diff = datetime.now() - signal_time
                minutes_ago = int(time_diff.total_seconds() / 60)
                time_str = f"{minutes_ago}m"
        else:
            time_str = "0m"
        
        # Format signal type (shorten for display)
        signal_short = signal_type.replace('_', '').upper()[:8]
        
        # Add direction and validation
        if direction == 'UNK':
            return f"{signal_short}({time_str})"
        else:
            return f"{signal_short} {direction}({time_str})"
    
    def _get_multi_timeframe_data(self, monitor: StrategyMonitor, symbol: str) -> dict:
        """Get Trend Magic data for all 3 timeframes - SPARTAN STYLE"""
        try:
            # Suppress logging for clean display
            import logging
            ta_logger = logging.getLogger(f"TechnicalAnalyzer-{symbol}")
            original_level = ta_logger.level
            ta_logger.setLevel(logging.ERROR)
            
            try:
                from indicators.technical_indicators import TechnicalAnalyzer
                
                # Get data for all 3 timeframes
                timeframes = ["1m", "15m", "1h"]
                tm_data = {}
                
                for tf in timeframes:
                    analyzer = TechnicalAnalyzer(symbol, tf)
                    analyzer.fetch_market_data(limit=200)  # More data for CCI 100
                    
                    # Get Trend Magic and Squeeze
                    tm_result = analyzer.trend_magic_v3()
                    squeeze_result = analyzer.squeeze_momentum()
                    
                    tm_data[tf] = {
                        'trend_magic_color': tm_result['color'],
                        'momentum_color': squeeze_result['momentum_color'],
                        'current_price': tm_result['current_price'],
                        'trend_magic_value': tm_result['magic_trend_value'],  # VALOR DEL TM
                        'buy_signal': tm_result['buy_signal'],    # CRUCE ALCISTA
                        'sell_signal': tm_result['sell_signal']   # CRUCE BAJISTA
                    }
                
                return tm_data
                
            finally:
                ta_logger.setLevel(original_level)
                
        except Exception as e:
            print(f"DEBUG: Error getting multi-timeframe data for {symbol}: {str(e)}")
            return {}
    
    def _check_price_crossing(self, symbol: str, tf_data: dict) -> dict:
        """Check if price is crossing Trend Magic - SIMPLE SPARTAN LOGIC"""
        try:
            from indicators.technical_indicators import TechnicalAnalyzer
            
            # Get fresh 1m data with at least 2 candles
            analyzer = TechnicalAnalyzer(symbol, "1m")
            analyzer.fetch_market_data(limit=10)  # Just need recent data
            
            if not hasattr(analyzer, 'data') or len(analyzer.data) < 2:
                return {'buy_cross': False, 'sell_cross': False}
            
            # Get Trend Magic for current analysis
            tm_result = analyzer.trend_magic_v3()
            current_tm_value = tm_result['magic_trend_value']
            
            # Get last 2 prices
            current_price = analyzer.data['close'].iloc[-1]
            previous_price = analyzer.data['close'].iloc[-2]
            
            # SIMPLE CROSSING LOGIC
            buy_cross = (previous_price < current_tm_value and current_price > current_tm_value)
            sell_cross = (previous_price > current_tm_value and current_price < current_tm_value)
            
            return {
                'buy_cross': buy_cross,
                'sell_cross': sell_cross,
                'current_price': current_price,
                'previous_price': previous_price,
                'tm_value': current_tm_value
            }
            
        except Exception as e:
            return {'buy_cross': False, 'sell_cross': False}
    
    def _check_spartan_confluence(self, symbol: str, tf_data: dict) -> str:
        """Check for SPARTAN confluence signals - GODS OF WAR LOGIC WITH MANUAL PRICE CROSSING"""
        if not tf_data or len(tf_data) < 3:
            return "None"
        
        tm_1m = tf_data.get('1m', {}).get('trend_magic_color', 'UNKNOWN')
        tm_15m = tf_data.get('15m', {}).get('trend_magic_color', 'UNKNOWN')
        tm_1h = tf_data.get('1h', {}).get('trend_magic_color', 'UNKNOWN')
        mom_1m = tf_data.get('1m', {}).get('momentum_color', 'UNKNOWN')
        
        # GET MANUAL PRICE CROSSING SIGNALS - SPARTAN STYLE
        crossing_data = self._check_price_crossing(symbol, tf_data)
        buy_cross = crossing_data.get('buy_cross', False)
        sell_cross = crossing_data.get('sell_cross', False)
        
        # 🔥 SUPER BULLISH CONFLUENCE (MÁXIMA SEGURIDAD) - 1m + 15m ALIGNED
        if (tm_1m == 'BLUE' and tm_15m == 'BLUE' and 
            mom_1m in ['MAROON', 'LIME'] and buy_cross):
            return "🔥 SUPER_BULL LONG"
        
        # 🔥 SUPER BEARISH CONFLUENCE (MÁXIMA SEGURIDAD) - 1m + 15m ALIGNED
        if (tm_1m == 'RED' and tm_15m == 'RED' and
            mom_1m in ['MAROON', 'RED'] and sell_cross):
            return "🔥 SUPER_BEAR SHORT"
        
        # 📈 BULL SIGNAL (BUENA OPORTUNIDAD) - 15m AGAINST BUT STILL GOOD
        if (tm_1m == 'BLUE' and tm_15m == 'RED' and 
            mom_1m in ['MAROON', 'LIME'] and buy_cross):
            return "📈 BULL LONG"
        
        # 📉 BEAR SIGNAL (BUENA OPORTUNIDAD) - 15m AGAINST BUT STILL GOOD  
        if (tm_1m == 'RED' and tm_15m == 'BLUE' and
            mom_1m in ['MAROON', 'RED'] and sell_cross):
            return "📉 BEAR SHORT"
        
        # ⚡ TREND CHANGE WITH CROSSING (Early signal with price confirmation)
        if tm_1m == 'BLUE' and tm_15m == 'BLUE' and buy_cross:
            return "⚡ TREND_BULL CROSS"
        if tm_1m == 'RED' and tm_15m == 'RED' and sell_cross:
            return "⚡ TREND_BEAR CROSS"
        
        # 🎯 SUPER SETUP (1m + 15m ALIGNED - WAITING FOR CROSSING)
        if (tm_1m == 'BLUE' and tm_15m == 'BLUE' and 
            mom_1m in ['MAROON', 'LIME']):
            return "🎯 SUPER_BULL SETUP"
        
        if (tm_1m == 'RED' and tm_15m == 'RED' and
            mom_1m in ['MAROON', 'RED']):
            return "🎯 SUPER_BEAR SETUP"
        
        # 📈 BULL SETUP (15m AGAINST - GOOD OPPORTUNITY FORMING)
        if (tm_1m == 'BLUE' and tm_15m == 'RED' and 
            mom_1m in ['MAROON', 'LIME']):
            return "📈 BULL SETUP"
        
        if (tm_1m == 'RED' and tm_15m == 'BLUE' and
            mom_1m in ['MAROON', 'RED']):
            return "📉 BEAR SETUP"
        
        # ⚡ EARLY SIGNALS (Timeframe alignment only)
        if tm_1m == 'BLUE' and tm_15m == 'BLUE':
            return "⚡ TREND_BULL"
        if tm_1m == 'RED' and tm_15m == 'RED':
            return "⚡ TREND_BEAR"
        
        # ⚠️ CONFLICTED (Mixed signals)
        if tm_1m != tm_15m:
            return "⚠️ CONFLICTED"
        
        return "None"
    
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
                         if symbol_status.state.value == 'active' and symbol not in ['MATICUSDT', 'FTMUSDT']][:5]  # Show top 5
        
        for symbol in active_symbols:
            symbol_status = status.symbols[symbol]
            indicator_data = self._get_indicator_data(monitor, symbol)
            
            tm_color = indicator_data.get('trend_magic_color', 'UNKNOWN')
            squeeze_status = indicator_data.get('squeeze_status', 'UNKNOWN')
            momentum_color = indicator_data.get('momentum_color', 'UNKNOWN')
            
            price_text = f"${symbol_status.current_price:.4f}" if symbol_status.current_price else "N/A"
            
            # Format signal for details view
            if symbol_status.latest_signal_type:
                signal_detail = self._format_signal_with_direction(
                    symbol_status.latest_signal_type,
                    symbol_status.latest_signal_time,
                    tm_color
                )
            else:
                signal_detail = "None"
            
            print(f"{symbol:>8}: TM={tm_color:<4} | SQ={squeeze_status:<3} | MOM={momentum_color:<4} | Price={price_text} | Signal={signal_detail}")
        
        print()
        print("🏛️⚔️ SPARTAN CONFLUENCE LEGEND:")
        print("   - 1m/15m/1h TM = Trend Magic colors (🔵BLUE=Bull, 🔴RED=Bear)")
        print("   - Mom 1m = Momentum color (🟢LIME=Strong, 🟤MAR=Weak)")
        print("   - 🔥 SUPER_BULL/BEAR = 1m+15m aligned + momentum + PRICE CROSSING!")
        print("   - 📈📉 BULL/BEAR = 1m good + 15m against + momentum + CROSSING!")
        print("   - 🎯 SUPER_SETUP = 1m+15m aligned + momentum (waiting for cross)")
        print("   - 📈📉 BULL/BEAR SETUP = 1m good + 15m against (waiting for cross)")
        print("   - ⚡ TREND_CROSS = Early signals with crossing")
        print("   - ⚠️ CONFLICTED = Mixed timeframe signals")
        print("   - 🎯 SPARTAN RULE: 🔥SUPER = MÁXIMA SEGURIDAD! 📈BULL = BUENA OPORTUNIDAD!")
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
        print("🏛️ SPARTAN BATTLE INSTRUCTIONS:")
        print("- 🔥 SUPER signals = ENTER IMMEDIATELY! (Price crossed + confluence)")
        print("- ⚡ CROSS signals = Strong entries (Price crossed + timeframes)")
        print("- 📈📉 SETUP signals = GET READY! (Confluence formed, wait for cross)")
        print("- ⚡ TREND signals = Early warnings (No crossing yet)")
        print("- ⚠️ CONFLICTED = AVOID - mixed signals")
        print("- 🎯 STRATEGY: Wait for SUPER or CROSS signals for best entries")
        print("- CCI Period 100 = Quality over quantity")
        print("- REMEMBER: Price must CROSS Trend Magic for valid entry!")
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
        logging.getLogger('StrategyMonitor').setLevel(logging.ERROR)
        logging.getLogger('AlertManager').setLevel(logging.ERROR)
        
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