#!/usr/bin/env python3
"""
Trend Magic Continuous Monitor - BTC 1min Analysis
Real-time Spartan monitoring system for battlefield conditions
"""
import time
import logging
import signal
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.technical_indicators import TechnicalAnalyzer

class TrendMagicMonitor:
    """
    Continuous Trend Magic monitor for real-time market analysis
    Built for warriors who never sleep 🏛️⚔️
    """
    
    def __init__(self, symbol: str = "BTCUSDT", timeframe: str = "1m", update_interval: int = 60):
        """
        Initialize the Spartan monitor
        
        Args:
            symbol: Trading pair to monitor
            timeframe: Chart timeframe
            update_interval: Seconds between updates
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.update_interval = update_interval
        self.running = False
        
        # Setup logging
        self.logger = logging.getLogger(f"TrendMagicMonitor-{symbol}")
        
        # Initialize analyzer
        self.analyzer = TechnicalAnalyzer(symbol, timeframe)
        
        # Track previous state for change detection
        self.previous_color = None
        self.previous_signals = {'buy': False, 'sell': False}
        
        # Statistics
        self.stats = {
            'updates': 0,
            'color_changes': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'start_time': None
        }
        
        self.logger.info(f"🏛️ Spartan Monitor initialized for {symbol} on {timeframe}")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            self.logger.info("🛡️ Shutdown signal received - Stopping monitor gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def get_trend_magic_analysis(self) -> Dict[str, Any]:
        """Get current Trend Magic analysis"""
        try:
            # Fetch fresh market data
            self.analyzer.fetch_market_data(limit=500)  # Enough for calculations
            
            # Calculate Trend Magic
            magic = self.analyzer.trend_magic()
            
            return {
                'success': True,
                'data': magic,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"💀 Analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def play_sound_alert(self, alert_type: str):
        """Play sound alert for color changes"""
        try:
            if alert_type == "red_to_blue":
                # Bullish alert - 3 beeps
                for _ in range(3):
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                    time.sleep(0.2)
                self.logger.info("🔵 BULLISH ALERT SOUND PLAYED!")
                
            elif alert_type == "blue_to_red":
                # Bearish alert - 2 beeps
                for _ in range(2):
                    os.system("afplay /System/Library/Sounds/Sosumi.aiff")
                    time.sleep(0.3)
                self.logger.info("🔴 BEARISH ALERT SOUND PLAYED!")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Sound alert failed: {str(e)}")

    def detect_changes(self, current_analysis: Dict[str, Any]) -> Dict[str, bool]:
        """Detect changes from previous analysis"""
        changes = {
            'color_changed': False,
            'new_buy_signal': False,
            'new_sell_signal': False,
            'change_type': None
        }
        
        if not current_analysis['success']:
            return changes
        
        data = current_analysis['data']
        
        # Check color change
        if self.previous_color and self.previous_color != data['color']:
            changes['color_changed'] = True
            self.stats['color_changes'] += 1
            
            # Determine change type for sound alert
            if self.previous_color == 'RED' and data['color'] == 'BLUE':
                changes['change_type'] = 'red_to_blue'
                self.play_sound_alert('red_to_blue')
            elif self.previous_color == 'BLUE' and data['color'] == 'RED':
                changes['change_type'] = 'blue_to_red'
                self.play_sound_alert('blue_to_red')
        
        # Check new signals
        if data['buy_signal'] and not self.previous_signals['buy']:
            changes['new_buy_signal'] = True
            self.stats['buy_signals'] += 1
        
        if data['sell_signal'] and not self.previous_signals['sell']:
            changes['new_sell_signal'] = True
            self.stats['sell_signals'] += 1
        
        # Update previous state
        self.previous_color = data['color']
        self.previous_signals = {
            'buy': data['buy_signal'],
            'sell': data['sell_signal']
        }
        
        return changes
    
    def print_analysis(self, analysis: Dict[str, Any], changes: Dict[str, bool]):
        """Print formatted analysis with change indicators"""
        timestamp = analysis['timestamp'].strftime("%H:%M:%S")
        
        if not analysis['success']:
            print(f"[{timestamp}] 💀 ERROR: {analysis['error']}")
            return
        
        data = analysis['data']
        
        # Color indicator with change detection
        color_indicator = "🔵" if data['color'] == 'BLUE' else "🔴"
        change_indicator = ""
        
        if changes['color_changed']:
            if changes['change_type'] == 'red_to_blue':
                change_indicator = " 🔄🔵 BULLISH CHANGE! 🔊"
            elif changes['change_type'] == 'blue_to_red':
                change_indicator = " 🔄🔴 BEARISH CHANGE! 🔊"
            else:
                change_indicator = " 🔄"
        
        # Signal indicators
        signal_text = ""
        if changes['new_buy_signal']:
            signal_text = " 🚀 NEW BUY!"
        elif changes['new_sell_signal']:
            signal_text = " 💀 NEW SELL!"
        elif data['buy_signal']:
            signal_text = " 🚀 BUY"
        elif data['sell_signal']:
            signal_text = " 💀 SELL"
        else:
            signal_text = " ⚖️ HOLD"
        
        # Main display line
        print(f"[{timestamp}] {color_indicator} ${data['current_price']:8,.0f} | "
              f"Trend: ${data['magic_trend_value']:8,.0f} | "
              f"Dist: {data['distance_pct']:+5.2f}% | "
              f"CCI: {data['cci_value']:8,.0f}{change_indicator}{signal_text}")
    
    def print_header(self):
        """Print monitor header"""
        print(f"\n🏛️ ═══ SPARTAN TREND MAGIC MONITOR ═══")
        print(f"⚔️  Symbol: {self.symbol}")
        print(f"⏰ Timeframe: {self.timeframe}")
        print(f"🔄 Update Interval: {self.update_interval}s")
        print(f"� Soaund Alerts: ENABLED (RED↔BLUE changes)")
        print(f"� Startsed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🛡️  Press Ctrl+C to stop gracefully")
        print(f"═══════════════════════════════════════")
        print(f"{'Time':>8} | {'Color':>5} | {'Price':>10} | {'Trend':>10} | {'Distance':>8} | {'CCI':>10} | Status")
        print(f"─────────────────────────────────────────────────────────────────────────────")
    
    def print_statistics(self):
        """Print session statistics"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            duration_str = str(duration).split('.')[0]  # Remove microseconds
            
            print(f"\n📊 SESSION STATISTICS:")
            print(f"   Duration: {duration_str}")
            print(f"   Updates: {self.stats['updates']}")
            print(f"   Color Changes: {self.stats['color_changes']}")
            print(f"   Buy Signals: {self.stats['buy_signals']}")
            print(f"   Sell Signals: {self.stats['sell_signals']}")
    
    def run(self):
        """Start the continuous monitoring"""
        self.setup_signal_handlers()
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.print_header()
        
        try:
            while self.running:
                # Get analysis
                analysis = self.get_trend_magic_analysis()
                
                # Detect changes
                changes = self.detect_changes(analysis)
                
                # Print results
                self.print_analysis(analysis, changes)
                
                # Update stats
                self.stats['updates'] += 1
                
                # Wait for next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛡️ Monitor stopped by user")
        except Exception as e:
            self.logger.error(f"💀 Monitor crashed: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the monitor gracefully"""
        self.running = False
        self.print_statistics()
        print(f"\n🏛️ Spartan Monitor stopped. May the trends be with you! ⚔️")

def main():
    """Main function for running the monitor"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🏛️ SPARTAN TREND MAGIC CONTINUOUS MONITOR")
    print("⚔️  Real-time BTC analysis on 1-minute timeframe")
    print("🔮 Monitoring Trend Magic indicator changes...")
    
    # Create and run monitor
    monitor = TrendMagicMonitor(
        symbol="BTCUSDT",
        timeframe="1m",
        update_interval=15  # Update every 60 seconds
    )
    
    monitor.run()

if __name__ == "__main__":
    main()