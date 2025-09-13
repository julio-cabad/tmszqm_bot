#!/usr/bin/env python3
"""
Simple Trend Magic Values Display
Shows Trend Magic values for all configured cryptocurrencies
"""

import sys
import os
import time
from datetime import datetime, timezone, timedelta
sys.path.append('.')

from indicators.technical_indicators import TechnicalAnalyzer


def play_alert_sound(signal_type):
    """Play alert sound for signals using os.system()"""
    try:
        if signal_type == "BUY":
            # Play 3 quick beeps for LONG signals
            for _ in range(3):
                os.system("afplay /System/Library/Sounds/Glass.aiff")
                time.sleep(0.2)
        elif signal_type == "SELL":
            # Play 2 long beeps for SHORT signals
            for _ in range(2):
                os.system("afplay /System/Library/Sounds/Basso.aiff")
                time.sleep(0.5)
    except:
        pass  # Ignore sound errors

def show_trend_magic_values():
    """Show Trend Magic values for all configured symbols"""
    
    # Symbols from config
    symbols = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", 
        "BNBUSDT", "XRPUSDT", "AVAXUSDT", "LINKUSDT", "ATOMUSDT",
        "ALGOUSDT", "VETUSDT", "NEARUSDT", "SANDUSDT", "MANAUSDT",
        "CHZUSDT", "ENJUSDT", "GALAUSDT", "TIAUSDT", "DOGEUSDT",
        "SUIUSDT", "HBARUSDT"
    ]
    
    # Get current time in UTC-5
    utc_minus_5 = timezone(timedelta(hours=-5))
    current_time = datetime.now(utc_minus_5).strftime("%Y-%m-%d %H:%M:%S UTC-5")
    
    print("🏛️⚔️ SPARTAN TREND MAGIC VALUES")
    print(f"⏰ Time: {current_time}")
    print("=" * 130)
    print(f"{'Symbol':<10} {'TM Value':<12} {'Color':<6} {'Price':<12} {'Open Price':<12} {'Open Time':<16} {'Squeeze':<10} {'Signal':<10}")
    print("-" * 130)
    
    # Store alerts to show after table
    alerts = []
    
    for symbol in symbols:
        try:
            # Create analyzer
            analyzer = TechnicalAnalyzer(symbol, "30m")
            analyzer.fetch_market_data(limit=200)
            
            # Get Trend Magic V3
            tm_result = analyzer.trend_magic_v3(period=100)
            
            # Get Squeeze Momentum
            squeeze_result = analyzer.squeeze_momentum()
            
            tm_value = tm_result['magic_trend_value']
            color = tm_result['color']
            price = tm_result['current_price']
            squeeze_color = squeeze_result['momentum_color']
            
            # Get open price of current candle
            open_price = analyzer.df['open'].iloc[-1]
            
            # Get open time of current candle in UTC-5
            open_timestamp = analyzer.df.index[-1]
            open_time_utc5 = open_timestamp.tz_convert(utc_minus_5).strftime("%H:%M:%S")
            
            # Format with emojis
            color_emoji = "🔵" if color == 'BLUE' else "🔴"
            
            squeeze_emoji_map = {
                'LIME': '🟢',
                'GREEN': '💠', 
                'RED': '🔴',
                'MAROON': '🟤'
            }
            squeeze_emoji = squeeze_emoji_map.get(squeeze_color, '⚪')
            
            # SPARTAN SIGNAL LOGIC
            signal = "🟡 NONE"
            
            # BUY CONDITION (LONG)
            if (open_price < tm_value and price > tm_value and 
                color == 'BLUE' and squeeze_color in ['MAROON', 'LIME']):
                signal = "🟢 LONG"
                alerts.append({
                    'type': 'LONG',
                    'symbol': symbol,
                    'price': price,
                    'tm_value': tm_value,
                    'open_time': open_time_utc5
                })
                play_alert_sound("BUY")
            
            # SELL CONDITION (SHORT)
            elif (open_price > tm_value and price < tm_value and 
                  color == 'RED' and squeeze_color in ['GREEN', 'RED']):
                signal = "🔴 SHORT"
                alerts.append({
                    'type': 'SHORT',
                    'symbol': symbol,
                    'price': price,
                    'tm_value': tm_value,
                    'open_time': open_time_utc5
                })
                play_alert_sound("SELL")
            
            print(f"{symbol:<10} ${tm_value:<11.4f} {color_emoji}{color:<5} ${price:<11.2f} ${open_price:<11.2f} {open_time_utc5:<16} {squeeze_emoji}{squeeze_color:<9} {signal:<10}")
            
        except Exception as e:
            print(f"{symbol:<10} ERROR: {str(e)[:30]}")
    
    print("-" * 130)
    
    # Show alerts after table
    if alerts:
        print("\n🚨 ALERTAS DETECTADAS:")
        print("=" * 80)
        for alert in alerts:
            if alert['type'] == 'LONG':
                print(f"🟢 ALERTA LONG: {alert['symbol']} - {alert['open_time']} UTC-5")
                print(f"💰 Precio cruzó hacia arriba del Trend Magic!")
                print(f"📈 Precio: ${alert['price']:.4f} | TM: ${alert['tm_value']:.4f}")
                
            else:
                print(f"🔴 ALERTA SHORT: {alert['symbol']} - {alert['open_time']} UTC-5")
                print(f"📉 Precio cruzó hacia abajo del Trend Magic!")
                print(f"📊 Precio: ${alert['price']:.4f} | TM: ${alert['tm_value']:.4f}")
                
            print("-" * 40)
        print("=" * 80)
    else:
        print("\n✅ No hay alertas en este momento")


def run_continuous_monitoring():
    """Run continuous monitoring with alerts"""
    print("🏛️⚔️ SPARTAN CONTINUOUS SIGNAL MONITOR")
    print("⚡ Monitoring for BUY/SELL signals...")
    print("🔊 Sound alerts enabled")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    scan_count = 0
    
    try:
        while True:  # BUCLE INFINITO
            scan_count += 1
            
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Get current time in UTC-5 for scan
            utc_minus_5 = timezone(timedelta(hours=-5))
            scan_time = datetime.now(utc_minus_5).strftime('%H:%M:%S')
            print(f"🔄 Scan #{scan_count} - {scan_time} UTC-5")
            print()
            
            # Show current values
            show_trend_magic_values()
            
            print(f"\n⏳ Próximo scan en 10 segundos... (Scan #{scan_count + 1})")
            print("🔊 Alertas sonoras activas para señales LONG/SHORT")
            
            # Wait 30 seconds before next update
            for i in range(10, 0, -1):
                print(f"\r⏱️  Esperando: {i:2d}s", end="", flush=True)
                time.sleep(1)
            
            print()  # New line after countdown
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user after {scan_count} scans")

# Clase SignalGenerator para compatibilidad con el sistema profesional
class SignalGenerator:
    """
    Signal Generator class - Wrapper para tu lógica existente
    """
    
    def __init__(self, config, indicator_engine):
        """Initialize SignalGenerator"""
        self.config = config
        self.indicator_engine = indicator_engine
    
    def generate_signals(self, symbol):
        """
        Generate signals using your exact LONG/SHORT logic
        
        Args:
            symbol: Symbol to analyze
            
        Returns:
            List of signals (empty list for now, signals handled in monitor)
        """
        # Tu lógica exacta está implementada directamente en el strategy_monitor.py
        # Esta función existe solo para compatibilidad
        return []


if __name__ == "__main__":
    run_continuous_monitoring()