#!/usr/bin/env python3
"""
Squeeze Momentum Continuous Monitor - LazyBear's Beast
Real-time monitoring with sound alerts for all changes
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

class SqueezeMonitor:
    """
    Continuous Squeeze Momentum monitor with sound alerts
    Built for warriors who track volatility compression 🎯⚔️
    """
    
    def __init__(self, symbol: str = "BTCUSDT", timeframe: str = "1m", update_interval: int = 30):
        """
        Initialize the Squeeze Monitor
        
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
        self.logger = logging.getLogger(f"SqueezeMonitor-{symbol}")
        
        # Initialize analyzer
        self.analyzer = TechnicalAnalyzer(symbol, timeframe)
        
        # Track previous state for change detection
        self.previous_momentum_color = None
        self.previous_squeeze_status = None
        
        # Statistics
        self.stats = {
            'updates': 0,
            'momentum_changes': 0,
            'squeeze_changes': 0,
            'start_time': None
        }
        
        self.logger.info(f"🎯 Squeeze Monitor initialized for {symbol} on {timeframe}")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            self.logger.info("🛡️ Shutdown signal received - Stopping monitor gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def play_sound_alert(self, alert_type: str):
        """Play sound alert for changes"""
        try:
            if alert_type == "momentum_bullish_up":
                # GREEN to LIME - Bullish momentum increasing
                for _ in range(2):
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                    time.sleep(0.1)
                self.logger.info("🟢➡️🟢 MOMENTUM BULLISH UP ALERT!")
                
            elif alert_type == "momentum_bullish_down":
                # LIME to GREEN - Bullish momentum decreasing
                os.system("afplay /System/Library/Sounds/Tink.aiff")
                self.logger.info("🟢➡️🟢 MOMENTUM BULLISH DOWN ALERT!")
                
            elif alert_type == "momentum_bearish_down":
                # RED - Bearish momentum decreasing (more bearish)
                for _ in range(2):
                    os.system("afplay /System/Library/Sounds/Sosumi.aiff")
                    time.sleep(0.1)
                self.logger.info("🔴➡️🔴 MOMENTUM BEARISH DOWN ALERT!")
                
            elif alert_type == "momentum_bearish_up":
                # MAROON - Bearish momentum increasing (less bearish)
                os.system("afplay /System/Library/Sounds/Funk.aiff")
                self.logger.info("🔴➡️🔴 MOMENTUM BEARISH UP ALERT!")
                
            elif alert_type == "momentum_bull_to_bear":
                # Bullish to Bearish
                for _ in range(3):
                    os.system("afplay /System/Library/Sounds/Basso.aiff")
                    time.sleep(0.2)
                self.logger.info("🟢➡️🔴 MOMENTUM BULL TO BEAR ALERT!")
                
            elif alert_type == "momentum_bear_to_bull":
                # Bearish to Bullish
                for _ in range(3):
                    os.system("afplay /System/Library/Sounds/Hero.aiff")
                    time.sleep(0.2)
                self.logger.info("🔴➡️🟢 MOMENTUM BEAR TO BULL ALERT!")
                
            elif alert_type == "squeeze_on":
                # Squeeze activated
                for _ in range(4):
                    os.system("afplay /System/Library/Sounds/Ping.aiff")
                    time.sleep(0.15)
                self.logger.info("🔴 SQUEEZE ON ALERT!")
                
            elif alert_type == "squeeze_off":
                # Squeeze released
                for _ in range(4):
                    os.system("afplay /System/Library/Sounds/Pop.aiff")
                    time.sleep(0.15)
                self.logger.info("🟢 SQUEEZE OFF ALERT!")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Sound alert failed: {str(e)}")

    def get_squeeze_analysis(self) -> Dict[str, Any]:
        """Get current Squeeze Momentum analysis"""
        try:
            # Fetch fresh market data
            self.analyzer.fetch_market_data(limit=50)
            
            # Calculate Squeeze Momentum
            squeeze = self.analyzer.squeeze_momentum()
            
            return {
                'success': True,
                'data': squeeze,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"💀 Analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def detect_changes(self, current_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes from previous analysis"""
        changes = {
            'momentum_changed': False,
            'squeeze_changed': False,
            'momentum_change_type': None,
            'squeeze_change_type': None
        }
        
        if not current_analysis['success']:
            return changes
        
        data = current_analysis['data']
        
        # Check momentum color changes
        if self.previous_momentum_color and self.previous_momentum_color != data['momentum_color']:
            changes['momentum_changed'] = True
            self.stats['momentum_changes'] += 1
            
            # Determine specific momentum change type
            prev = self.previous_momentum_color
            curr = data['momentum_color']
            
            # Bullish changes
            if prev == "GREEN" and curr == "LIME":
                changes['momentum_change_type'] = 'momentum_bullish_up'
                self.play_sound_alert('momentum_bullish_up')
            elif prev == "LIME" and curr == "GREEN":
                changes['momentum_change_type'] = 'momentum_bullish_down'
                self.play_sound_alert('momentum_bullish_down')
            
            # Bearish changes
            elif prev == "MAROON" and curr == "RED":
                changes['momentum_change_type'] = 'momentum_bearish_down'
                self.play_sound_alert('momentum_bearish_down')
            elif prev == "RED" and curr == "MAROON":
                changes['momentum_change_type'] = 'momentum_bearish_up'
                self.play_sound_alert('momentum_bearish_up')
            
            # Bull/Bear transitions
            elif prev in ["GREEN", "LIME"] and curr in ["RED", "MAROON"]:
                changes['momentum_change_type'] = 'momentum_bull_to_bear'
                self.play_sound_alert('momentum_bull_to_bear')
            elif prev in ["RED", "MAROON"] and curr in ["GREEN", "LIME"]:
                changes['momentum_change_type'] = 'momentum_bear_to_bull'
                self.play_sound_alert('momentum_bear_to_bull')
        
        # Check squeeze status changes
        if self.previous_squeeze_status and self.previous_squeeze_status != data['squeeze_status']:
            changes['squeeze_changed'] = True
            self.stats['squeeze_changes'] += 1
            
            # Determine squeeze change type
            if "SQUEEZE ON" in data['squeeze_status']:
                changes['squeeze_change_type'] = 'squeeze_on'
                self.play_sound_alert('squeeze_on')
            elif "SQUEEZE OFF" in data['squeeze_status']:
                changes['squeeze_change_type'] = 'squeeze_off'
                self.play_sound_alert('squeeze_off')
        
        # Update previous state
        self.previous_momentum_color = data['momentum_color']
        self.previous_squeeze_status = data['squeeze_status']
        
        return changes
    
    def print_analysis(self, analysis: Dict[str, Any], changes: Dict[str, Any]):
        """Print formatted analysis with change indicators"""
        timestamp = analysis['timestamp'].strftime("%H:%M:%S")
        
        if not analysis['success']:
            print(f"[{timestamp}] 💀 ERROR: {analysis['error']}")
            return
        
        data = analysis['data']
        
        # Momentum color emoji mapping
        color_emojis = {
            "LIME": "🟢⬆️",
            "GREEN": "🟢⬇️", 
            "RED": "🔴⬇️",
            "MAROON": "🔴⬆️"
        }
        
        # Squeeze status emoji mapping
        squeeze_emojis = {
            "🔴 SQUEEZE ON": "🔴",
            "🟢 SQUEEZE OFF": "🟢",
            "🔵 NO SQUEEZE": "🔵"
        }
        
        momentum_emoji = color_emojis.get(data['momentum_color'], "❓")
        squeeze_emoji = squeeze_emojis.get(data['squeeze_status'], "❓")
        
        # Change indicators
        momentum_change = ""
        squeeze_change = ""
        
        if changes['momentum_changed']:
            momentum_change = f" 🔄🔊 {changes['momentum_change_type'].upper()}"
        
        if changes['squeeze_changed']:
            squeeze_change = f" 🔄🔊 {changes['squeeze_change_type'].upper()}"
        
        # Main display line
        print(f"[{timestamp}] {momentum_emoji} ${data['current_price']:8,.0f} | "
              f"Mom: {data['momentum_value']:8.2f} | "
              f"Squeeze: {squeeze_emoji} | "
              f"Color: {data['momentum_color']:6s}{momentum_change}{squeeze_change}")
    
    def print_header(self):
        """Print monitor header"""
        print(f"\n🎯 ═══ SQUEEZE MOMENTUM MONITOR ═══")
        print(f"⚔️  Symbol: {self.symbol}")
        print(f"⏰ Timeframe: {self.timeframe}")
        print(f"🔄 Update Interval: {self.update_interval}s")
        print(f"🔊 Sound Alerts: ENABLED (All changes)")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🛡️  Press Ctrl+C to stop gracefully")
        print(f"═══════════════════════════════════════")
        print(f"{'Time':>8} | {'Momentum':>10} | {'Price':>10} | {'Value':>10} | {'Squeeze':>8} | {'Color':>6} | Changes")
        print(f"─────────────────────────────────────────────────────────────────────────────")
        print(f"\n🎨 MOMENTUM COLORS:")
        print(f"   🟢⬆️ LIME: Bullish momentum increasing")
        print(f"   🟢⬇️ GREEN: Bullish momentum decreasing") 
        print(f"   🔴⬇️ RED: Bearish momentum decreasing")
        print(f"   🔴⬆️ MAROON: Bearish momentum increasing")
        print(f"\n🎯 SQUEEZE STATUS:")
        print(f"   🔴 SQUEEZE ON: Volatility compressed (prepare for breakout)")
        print(f"   🟢 SQUEEZE OFF: Volatility expanding")
        print(f"   🔵 NO SQUEEZE: Normal volatility")
        print(f"─────────────────────────────────────────────────────────────────────────────")
    
    def print_statistics(self):
        """Print session statistics"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            duration_str = str(duration).split('.')[0]
            
            print(f"\n📊 SESSION STATISTICS:")
            print(f"   Duration: {duration_str}")
            print(f"   Updates: {self.stats['updates']}")
            print(f"   Momentum Changes: {self.stats['momentum_changes']}")
            print(f"   Squeeze Changes: {self.stats['squeeze_changes']}")
    
    def run(self):
        """Start the continuous monitoring"""
        self.setup_signal_handlers()
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.print_header()
        
        try:
            while self.running:
                # Get analysis
                analysis = self.get_squeeze_analysis()
                
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
        print(f"\n🎯 Squeeze Monitor stopped. May the volatility be with you! ⚔️")

def main():
    """Main function for running the monitor"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 SQUEEZE MOMENTUM CONTINUOUS MONITOR")
    print("⚔️  Real-time BTC analysis with LazyBear's indicator")
    print("🔊 Sound alerts for all momentum and squeeze changes")
    
    # Create and run monitor
    monitor = SqueezeMonitor(
        symbol="BTCUSDT",
        timeframe="1m",
        update_interval=30  # Update every 30 seconds
    )
    
    monitor.run()

if __name__ == "__main__":
    main()