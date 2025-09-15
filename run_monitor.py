#!/usr/bin/env python3
"""
Monitor Spartan - Sistema Profesional
Usa el sistema completo de /spartan_trading_system/monitoring
"""

import sys
import os
import time
import logging
from datetime import datetime, timezone, timedelta

sys.path.append('.')

# Configure logging - suppress verbose logs
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress specific loggers that are too verbose
logging.getLogger("TechnicalAnalyzer").setLevel(logging.CRITICAL)
logging.getLogger("MarketDataProvider").setLevel(logging.CRITICAL)
logging.getLogger("IndicatorEngine").setLevel(logging.CRITICAL)
logging.getLogger("RobotBinance").setLevel(logging.CRITICAL)
logging.getLogger("StrategyMonitor").setLevel(logging.CRITICAL)  # Disable debug logs
logging.getLogger("AlertManager").setLevel(logging.CRITICAL)  # Suppress alert logs during display
logging.getLogger("TradeLogger").setLevel(logging.INFO)  # Enable trade logger logs
logging.getLogger("PnLSimulator").setLevel(logging.WARNING)  # Disable debug logs

from spartan_trading_system.config.strategy_config import StrategyConfig
from spartan_trading_system.config.symbols_config import get_spartan_symbols
from spartan_trading_system.monitoring.strategy_monitor import StrategyMonitor

def display_spartan_monitoring_status(monitor, timeframe="1m"):
    """Display monitoring status using YOUR FORMAT"""
    try:
        status = monitor.get_monitoring_status()
        
        # Get current time in UTC-5
        utc_minus_5 = timezone(timedelta(hours=-5))
        current_time = datetime.now(utc_minus_5).strftime("%Y-%m-%d %H:%M:%S UTC-5")
        
        print("🏛️⚔️ SPARTAN PROFESSIONAL MONITORING SYSTEM")
        print(f"⏰ Time: {current_time}")
        print(f"🔄 Estado: {status.get_status_emoji()} {status.state.value.upper()}")
        print(f"⏱️ Uptime: {status.get_uptime_string()}")
        print(f"💚 Health: {status.get_health_score():.1%}")
        print(f"📊 Señales: {status.total_signals}")
        print("=" * 130)
        print(f"{'Symbol':<10} {'TM Value':<12} {'Color':<6} {'Price':<12} {'Open Price':<12} {'Open Time':<16} {'Squeeze':<10} {'Signal':<10}")
        print("-" * 130)
        
        # Display symbols using data from strategy_monitor.py (FAST VERSION)
        for symbol, symbol_status in status.symbols.items():
            try:
                # Use data that strategy_monitor.py already calculated
                price = symbol_status.current_price or 0.0
                tm_color = symbol_status.trend_magic_color or "UNKNOWN"
                squeeze_color = symbol_status.squeeze_status or "UNKNOWN"
                
                # Get REAL TM value with CACHE for speed
                cache_key = f"{symbol}_{timeframe}"
                
                # Check if we have cached data (refresh every 30 seconds)
                current_time = time.time()
                if not hasattr(display_spartan_monitoring_status, 'cache'):
                    display_spartan_monitoring_status.cache = {}
                
                if (cache_key in display_spartan_monitoring_status.cache and 
                    current_time - display_spartan_monitoring_status.cache[cache_key]['timestamp'] < 30):
                    # Use cached data
                    cached_data = display_spartan_monitoring_status.cache[cache_key]
                    tm_value = cached_data['tm_value']
                    open_price = cached_data['open_price']
                else:
                    # Calculate new data and cache it
                    try:
                        from indicators.technical_indicators import TechnicalAnalyzer
                        analyzer = TechnicalAnalyzer(symbol, timeframe)
                        analyzer.fetch_market_data(limit=50)  # Very small limit for speed
                        tm_result = analyzer.trend_magic_v3(period=100)
                        
                        if tm_result and hasattr(analyzer, 'df') and not analyzer.df.empty:
                            tm_value = tm_result['magic_trend_value']
                            open_price = analyzer.df['open'].iloc[-1]
                        else:
                            tm_value = price * 0.999
                            open_price = price
                        
                        # Cache the results
                        display_spartan_monitoring_status.cache[cache_key] = {
                            'tm_value': tm_value,
                            'open_price': open_price,
                            'timestamp': current_time
                        }
                    except:
                        tm_value = price * 0.999
                        open_price = price
                open_time_utc5 = datetime.now(utc_minus_5).strftime("%H:%M:%S")
                
                # Format with emojis
                color_emoji = "🔵" if tm_color == 'BLUE' else "🔴" if tm_color == 'RED' else "⚪"
                
                squeeze_emoji_map = {
                    'LIME': '🟢',
                    'GREEN': '💠', 
                    'RED': '🔴',
                    'MAROON': '🟤'
                }
                squeeze_emoji = squeeze_emoji_map.get(squeeze_color, '⚪')
                
                # Use signal from strategy_monitor.py
                signal = "🟡 NONE"
                if symbol_status.latest_signal_type == 'LONG':
                    signal = "🟢 LONG"
                elif symbol_status.latest_signal_type == 'SHORT':
                    signal = "🔴 SHORT"
                
                print(f"{symbol:<10} ${tm_value:<11.4f} {color_emoji}{tm_color:<5} ${price:<11.2f} ${open_price:<11.2f} {open_time_utc5:<16} {squeeze_emoji}{squeeze_color:<9} {signal:<10}")
                    
            except Exception as e:
                print(f"{symbol:<10} ERROR: {str(e)[:30]}")
        
        print("-" * 130)
        
        # Force flush output to ensure immediate display
        sys.stdout.flush()
        
    except Exception as e:
        print(f"Error displaying status: {e}")
        sys.stdout.flush()

def main():
    print("🏛️⚔️ SPARTAN PROFESSIONAL MONITORING SYSTEM")
    print("=" * 50)
    
    # Configurar timeframe
    timeframe = input("Timeframe (1m/5m/15m/30m/1h/2h/4h) [1m]: ").strip() or "1m"
    
    # Crear configuración
    config = StrategyConfig()
    config.timeframes = [timeframe]
    config.primary_timeframe = timeframe
    
    # Símbolos centralizados desde symbols_config.py
    config.symbols = get_spartan_symbols()
    
    print(f"🕐 Timeframe: {timeframe}")
    print(f"📊 Símbolos: {len(config.symbols)}")
    print("🚀 Iniciando sistema profesional de /monitoring...")
    
    # Crear monitor profesional
    monitor = StrategyMonitor(config)
    
    try:
        # Iniciar monitoreo
        if monitor.start_monitoring():
            print("✅ Sistema profesional iniciado")
            print("🔊 AlertManager activo")
            print("📊 PerformanceTracker activo") 
            print("🎯 Detectando señales LONG/SHORT")
            print("🛑 Presiona Ctrl+C para detener")
            print()
            
            # Loop de monitoreo con TU FORMATO
            while True:
                # FORCE CLEAR SCREEN - Multiple methods
                try:
                    # Method 1: Standard clear
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    # Method 2: ANSI escape sequences (more reliable)
                    print('\033[2J\033[H', end='')
                    
                    # Method 3: Print newlines to push old content up
                    print('\n' * 50)
                    
                except:
                    # Fallback: Just print many newlines
                    print('\n' * 100)
                
                # Display usando TU FORMATO
                display_spartan_monitoring_status(monitor, timeframe)
                
                # Show performance summary
                perf_summary = monitor.get_performance_summary()
                print(f"\n📈 Performance: CPU {perf_summary.get('system_performance', {}).get('current_cpu_percent', 0):.1f}% | Memory {perf_summary.get('system_performance', {}).get('current_memory_mb', 0):.1f}MB | API {perf_summary.get('system_performance', {}).get('api_calls_per_minute', 0)}/min")
                
                # Show PnL Simulator Status
                try:
                    # Get current market data for PnL calculation
                    market_data = {}
                    status = monitor.get_monitoring_status()
                    for symbol, symbol_status in status.symbols.items():
                        if symbol_status.current_price:
                            market_data[symbol] = symbol_status.current_price
                    
                    # Get simulator stats
                    perf_stats = monitor.pnl_simulator.get_performance_stats()
                    open_positions = monitor.pnl_simulator.get_open_positions_summary(market_data)
                    total_balance = monitor.pnl_simulator.get_total_balance(market_data)
                    
                    # Display PnL Summary
                    balance_change = total_balance - perf_stats['initial_balance']
                    balance_pct = (balance_change / perf_stats['initial_balance']) * 100
                    balance_emoji = "💚" if balance_change >= 0 else "💔"
                    
                    print(f"\n{balance_emoji} PnL Simulator - Balance: ${total_balance:.3f} ({balance_pct:+.3f}%)")
                    
                    # Show open positions with TP/SL and proximity
                    if open_positions:
                        print(f"📊 Open Positions ({len(open_positions)}/{perf_stats['max_positions']}):")
                        for pos in open_positions:
                            side_emoji = "🟢" if pos['side'] == 'LONG' else "🔴"
                            pnl_emoji = "💚" if pos['current_pnl'] >= 0 else "💔"
                            
                            # Calculate proximity to TP and SL
                            current_price = pos['current_price']
                            entry_price = pos['entry_price']
                            tp_price = pos['take_profit']
                            sl_price = pos['stop_loss']
                            
                            if pos['side'] == 'LONG':
                                # For LONG: TP is above, SL is below
                                tp_distance = ((tp_price - current_price) / (tp_price - entry_price)) * 100
                                sl_distance = ((current_price - sl_price) / (entry_price - sl_price)) * 100
                            else:
                                # For SHORT: TP is below, SL is above  
                                tp_distance = ((entry_price - current_price) / (entry_price - tp_price)) * 100
                                sl_distance = ((sl_price - current_price) / (sl_price - entry_price)) * 100
                            
                            # Clamp distances to 0-100%
                            tp_distance = max(0, min(100, tp_distance))
                            sl_distance = max(0, min(100, sl_distance))
                            
                            # Get current time
                            current_time = datetime.now().strftime("%H:%M:%S")
                            
                            print(f"   {side_emoji} {pos['symbol']} {pos['side']}: {pnl_emoji}${pos['current_pnl']:+.3f} ({pos['pnl_pct']:+.3f}%) | "
                                  f"TP: {tp_distance:.3f}% | SL: {sl_distance:.3f}% | Time: {current_time}")
                    
                    # Show performance stats if we have trades
                    if perf_stats['total_trades'] > 0:
                        print(f"📈 Stats: {perf_stats['total_trades']} trades | {perf_stats['win_rate']:.3f}% win rate | ${perf_stats['total_commissions']:.3f} fees")
                        
                        # Show trade logger session stats
                        try:
                            session_stats = monitor.pnl_simulator.get_trade_logger_stats()
                            if session_stats['total_trades'] > 0:
                                print(f"📊 Session: {session_stats['total_trades']} logged | Avg PnL: ${session_stats['avg_pnl']:.3f} | Best: ${session_stats['best_trade']:.3f} | Worst: ${session_stats['worst_trade']:.3f}")
                        except Exception:
                            pass
                    
                except Exception as e:
                    print(f"💀 PnL Display Error: {str(e)}")  # Show the error temporarily
                
                # Trading suggestions are now shown above in the main display
                
                # Show recent alerts in a cleaner format
                try:
                    recent_alerts = monitor.alert_manager.get_recent_alerts(5)
                    if recent_alerts:
                        print(f"\n🔔 Alertas Recientes:")
                        for alert in recent_alerts[-5:]:  # Last 5 alerts only
                            if isinstance(alert.get('timestamp'), datetime):
                                timestamp = alert['timestamp'].strftime("%H:%M:%S")
                            else:
                                timestamp = str(alert.get('timestamp', ''))[:8]
                            message = alert.get('message', '')[:80]  # Slightly longer messages
                            print(f"   {timestamp} - {message}")
                except Exception:
                    pass
                
                # Wait 5 seconds with countdown (faster updates)
                print(f"\n⏳ Próxima actualización en:")
                for i in range(5, 0, -1):
                    print(f"\r⏱️  {i:2d}s", end="", flush=True)
                    time.sleep(1)
                print()
                
        else:
            print("❌ Error al iniciar el sistema profesional")
            
    except KeyboardInterrupt:
        print("\n� Detneniendo sistema profesional...")
        monitor.stop_monitoring()
        monitor.shutdown()
        print("✅ Sistema detenido correctamente")

if __name__ == "__main__":
    main()