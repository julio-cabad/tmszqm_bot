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
logging.getLogger("StrategyMonitor").setLevel(logging.CRITICAL)
logging.getLogger("AlertManager").setLevel(logging.CRITICAL)  # Suppress alert logs during display

from spartan_trading_system.config.strategy_config import StrategyConfig
from spartan_trading_system.config.symbols_config import get_spartan_symbols
from spartan_trading_system.monitoring.strategy_monitor import StrategyMonitor

def display_spartan_monitoring_status(monitor):
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
        
        # Display symbols in your format
        for symbol, symbol_status in status.symbols.items():
            try:
                # Get real-time data using TechnicalAnalyzer
                from indicators.technical_indicators import TechnicalAnalyzer
                
                analyzer = TechnicalAnalyzer(symbol, "30m")  # Use same timeframe
                analyzer.fetch_market_data(limit=200)
                
                # Get indicators - same as your code
                tm_result = analyzer.trend_magic_v3(period=100)
                squeeze_result = analyzer.squeeze_momentum()
                
                if tm_result and squeeze_result:
                    tm_value = tm_result['magic_trend_value']
                    color = tm_result['color']
                    price = tm_result['current_price']
                    squeeze_color = squeeze_result['momentum_color']
                    
                    # Get open price and time
                    open_price = analyzer.df['open'].iloc[-1]
                    open_timestamp = analyzer.df.index[-1]
                    open_time_utc5 = open_timestamp.tz_convert(utc_minus_5).strftime("%H:%M:%S")
                    
                    # Format with emojis - same as your code
                    color_emoji = "🔵" if color == 'BLUE' else "🔴"
                    
                    squeeze_emoji_map = {
                        'LIME': '🟢',
                        'GREEN': '💠', 
                        'RED': '🔴',
                        'MAROON': '🟤'
                    }
                    squeeze_emoji = squeeze_emoji_map.get(squeeze_color, '⚪')
                    
                    # Determine signal
                    signal = "🟡 NONE"
                    if symbol_status.latest_signal_type == 'LONG':
                        signal = "🟢 LONG"
                    elif symbol_status.latest_signal_type == 'SHORT':
                        signal = "🔴 SHORT"
                    
                    print(f"{symbol:<10} ${tm_value:<11.4f} {color_emoji}{color:<5} ${price:<11.2f} ${open_price:<11.2f} {open_time_utc5:<16} {squeeze_emoji}{squeeze_color:<9} {signal:<10}")
                else:
                    print(f"{symbol:<10} ERROR: No indicator data")
                    
            except Exception as e:
                print(f"{symbol:<10} ERROR: {str(e)[:30]}")
        
        print("-" * 130)
        
    except Exception as e:
        print(f"Error displaying status: {e}")

def main():
    print("🏛️⚔️ SPARTAN PROFESSIONAL MONITORING SYSTEM")
    print("=" * 50)
    
    # Configurar timeframe
    timeframe = input("Timeframe (1m/5m/15m/30m/1h/4h) [30m]: ").strip() or "30m"
    
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
                display_spartan_monitoring_status(monitor)
                
                # Show performance summary
                perf_summary = monitor.get_performance_summary()
                print(f"\n📈 Performance: CPU {perf_summary.get('system_performance', {}).get('current_cpu_percent', 0):.1f}% | Memory {perf_summary.get('system_performance', {}).get('current_memory_mb', 0):.1f}MB | API {perf_summary.get('system_performance', {}).get('api_calls_per_minute', 0)}/min")
                
                # Show recent alerts (last 3) in a clean format
                try:
                    recent_alerts = monitor.alert_manager.get_recent_alerts(3)
                    if recent_alerts:
                        print(f"\n🔔 Alertas Recientes:")
                        for alert in recent_alerts[-3:]:  # Last 3 alerts
                            if isinstance(alert.get('timestamp'), datetime):
                                timestamp = alert['timestamp'].strftime("%H:%M:%S")
                            else:
                                timestamp = str(alert.get('timestamp', ''))[:8]
                            message = alert.get('message', '')[:60]  # Truncate long messages
                            print(f"   {timestamp} - {message}")
                except Exception:
                    pass  # Don't let alert display errors break the main loop
                
                # Wait 30 seconds with countdown
                print(f"\n⏳ Próxima actualización en:")
                for i in range(10, 0, -1):
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