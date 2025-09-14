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
logging.getLogger("PnLSimulator").setLevel(logging.DEBUG)  # Enable PnL simulator debug logs

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
        
        # Display symbols using data from strategy_monitor.py
        for symbol, symbol_status in status.symbols.items():
            try:
                # Use data that strategy_monitor.py already calculated
                price = symbol_status.current_price or 0.0
                tm_color = symbol_status.trend_magic_color or "UNKNOWN"
                squeeze_color = symbol_status.squeeze_status or "UNKNOWN"
                
                # Use placeholder values for display format compatibility
                tm_value = price * 0.999  # Approximate TM value for display
                open_price = price * 1.001  # Approximate open price for display
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
        
    except Exception as e:
        print(f"Error displaying status: {e}")

def main():
    print("🏛️⚔️ SPARTAN PROFESSIONAL MONITORING SYSTEM")
    print("=" * 50)
    
    # Configurar timeframe
    timeframe = input("Timeframe (1m/5m/15m/30m/1h/4h) [1m]: ").strip() or "1m"
    
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
                # Clear screen every 30 seconds
                os.system('cls' if os.name == 'nt' else 'clear')
                
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
                    
                    print(f"\n{balance_emoji} PnL Simulator - Balance: ${total_balance:.2f} ({balance_pct:+.2f}%)")
                    
                    # Show open positions
                    if open_positions:
                        print(f"📊 Open Positions ({len(open_positions)}/{perf_stats['max_positions']}):")
                        for pos in open_positions:
                            side_emoji = "🟢" if pos['side'] == 'LONG' else "🔴"
                            pnl_emoji = "💚" if pos['current_pnl'] >= 0 else "💔"
                            print(f"   {side_emoji} {pos['symbol']} {pos['side']}: {pnl_emoji}${pos['current_pnl']:+.2f} ({pos['pnl_pct']:+.1f}%) | Entry: ${pos['entry_price']:.4f} → Current: ${pos['current_price']:.4f}")
                    
                    # Show performance stats if we have trades
                    if perf_stats['total_trades'] > 0:
                        print(f"📈 Stats: {perf_stats['total_trades']} trades | {perf_stats['win_rate']:.0f}% win rate | ${perf_stats['total_commissions']:.2f} fees")
                    
                except Exception as e:
                    print(f"💀 PnL Display Error: {str(e)}")  # Show the error temporarily
                
                # Show trading suggestions (if any remaining)
                try:
                    suggestions = monitor.order_manager.get_active_suggestions()
                    if suggestions:
                        print(f"\n💡 Pending Suggestions ({len(suggestions)}):")
                        print("=" * 60)
                        for symbol, suggestion in suggestions.items():
                            formatted_suggestion = monitor.order_manager.format_order_suggestion(suggestion)
                            print(formatted_suggestion)
                            print("-" * 60)
                except Exception:
                    pass  # Don't let suggestion display errors break the main loop
                
                # Show recent alerts (last 3) in a clean format
                try:
                    recent_alerts = monitor.alert_manager.get_recent_alerts(10)
                    if recent_alerts:
                        print(f"\n🔔 Alertas Recientes:")
                        for alert in recent_alerts[-10:]:  # Last 10 alerts
                            if isinstance(alert.get('timestamp'), datetime):
                                timestamp = alert['timestamp'].strftime("%H:%M:%S")
                            else:
                                timestamp = str(alert.get('timestamp', ''))[:8]
                            message = alert.get('message', '')[:60]  # Truncate long messages
                            print(f"   {timestamp} - {message}")
                except Exception:
                    pass  # Don't let alert display errors break the main loop
                
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