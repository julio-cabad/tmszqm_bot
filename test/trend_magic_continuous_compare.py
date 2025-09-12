#!/usr/bin/env python3
"""
Trend Magic Continuous Comparison Monitor - 1min Optimized
Real-time comparison of all 3 versions with speed optimizations
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

class TrendMagicCompareMonitor:
    """
    Continuous Trend Magic comparison monitor - All 3 versions
    Optimized for speed with reduced data and faster updates
    """
    
    def __init__(self, symbol: str = "BTCUSDT", timeframe: str = "1m", update_interval: int = 15):
        """
        Initialize the Comparison Monitor
        
        Args:
            symbol: Trading pair to monitor
            timeframe: Chart timeframe (fixed to 1m)
            update_interval: Seconds between updates (optimized to 15s)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.update_interval = update_interval
        self.running = False
        
        # Setup logging
        self.logger = logging.getLogger(f"TrendMagicCompare-{symbol}")
        
        # Initialize analyzer
        self.analyzer = TechnicalAnalyzer(symbol, timeframe)
        
        # Track previous states for change detection
        self.previous_colors = {'v1': None, 'v2': None, 'v3': None}
        
        # Statistics
        self.stats = {
            'updates': 0,
            'v1_changes': 0,
            'v2_changes': 0,
            'v3_changes': 0,
            'agreements': 0,
            'disagreements': 0,
            'start_time': None
        }
        
        self.logger.info(f"🔮 Trend Magic Compare Monitor initialized for {symbol} on {timeframe}")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            self.logger.info("🛡️ Shutdown signal received - Stopping monitor gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def play_sound_alert(self, alert_type: str):
        """Play sound alert for important changes"""
        try:
            if alert_type == "all_agree_change":
                # All versions changed to same color
                for _ in range(2):
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                    time.sleep(0.1)
                self.logger.info("🎯 ALL VERSIONS AGREE CHANGE!")
                
            elif alert_type == "disagreement":
                # Versions disagree
                for _ in range(3):
                    os.system("afplay /System/Library/Sounds/Basso.aiff")
                    time.sleep(0.2)
                self.logger.info("⚠️ VERSIONS DISAGREE!")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Sound alert failed: {str(e)}")

    def get_all_versions_analysis(self) -> Dict[str, Any]:
        """Get analysis from all 3 Trend Magic versions - OPTIMIZED"""
        try:
            # Fetch REDUCED market data for speed (50 candles instead of 500)
            self.analyzer.fetch_market_data(limit=50)
            
            # Calculate all versions
            v1 = self.analyzer.trend_magic()
            v2 = self.analyzer.trend_magic_v2()
            v3 = self.analyzer.trend_magic_v3()
            
            return {
                'success': True,
                'v1': v1,
                'v2': v2,
                'v3': v3,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"💀 Analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def detect_changes(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes from previous analysis"""
        changes = {
            'v1_changed': False,
            'v2_changed': False,
            'v3_changed': False,
            'all_agree': False,
            'disagreement': False,
            'agreement_change': False
        }
        
        if not analysis['success']:
            return changes
        
        v1_color = analysis['v1']['color']
        v2_color = analysis['v2']['color']
        v3_color = analysis['v3']['color']
        
        # Check individual changes
        if self.previous_colors['v1'] and self.previous_colors['v1'] != v1_color:
            changes['v1_changed'] = True
            self.stats['v1_changes'] += 1
        
        if self.previous_colors['v2'] and self.previous_colors['v2'] != v2_color:
            changes['v2_changed'] = True
            self.stats['v2_changes'] += 1
        
        if self.previous_colors['v3'] and self.previous_colors['v3'] != v3_color:
            changes['v3_changed'] = True
            self.stats['v3_changes'] += 1
        
        # Check agreement
        all_agree = v1_color == v2_color == v3_color
        changes['all_agree'] = all_agree
        
        if all_agree:
            self.stats['agreements'] += 1
            # Check if all changed to same new color
            if (changes['v1_changed'] or changes['v2_changed'] or changes['v3_changed']):
                changes['agreement_change'] = True
                self.play_sound_alert('all_agree_change')
        else:
            self.stats['disagreements'] += 1
            changes['disagreement'] = True
            self.play_sound_alert('disagreement')
        
        # Update previous state
        self.previous_colors = {
            'v1': v1_color,
            'v2': v2_color,
            'v3': v3_color
        }
        
        return changes
    
    def print_analysis(self, analysis: Dict[str, Any], changes: Dict[str, Any]):
        """Print formatted comparison analysis"""
        timestamp = analysis['timestamp'].strftime("%H:%M:%S")
        
        if not analysis['success']:
            print(f"[{timestamp}] 💀 ERROR: {analysis['error']}")
            return
        
        v1 = analysis['v1']
        v2 = analysis['v2']
        v3 = analysis['v3']
        
        # Color emojis
        color_emoji = {"BLUE": "🔵", "RED": "🔴"}
        
        v1_emoji = color_emoji.get(v1['color'], "❓")
        v2_emoji = color_emoji.get(v2['color'], "❓")
        v3_emoji = color_emoji.get(v3['color'], "❓")
        
        # Agreement status
        if changes['all_agree']:
            agreement = "✅ AGREE"
            if changes['agreement_change']:
                agreement += " 🔄🔊"
        else:
            agreement = "❌ DISAGREE 🔊"
        
        # Change indicators
        v1_change = " 🔄" if changes['v1_changed'] else ""
        v2_change = " 🔄" if changes['v2_changed'] else ""
        v3_change = " 🔄" if changes['v3_changed'] else ""
        
        # Value differences
        v1_v3_diff = abs(v1['magic_trend_value'] - v3['magic_trend_value'])
        v2_v3_diff = abs(v2['magic_trend_value'] - v3['magic_trend_value'])
        
        # Main display line
        print(f"[{timestamp}] ${v1['current_price']:8,.0f} | "
              f"V1:{v1_emoji}{v1_change} V2:{v2_emoji}{v2_change} V3:{v3_emoji}{v3_change} | "
              f"{agreement} | "
              f"Diff: V1-V3=${v1_v3_diff:.4f} V2-V3=${v2_v3_diff:.4f}")
    
    def print_header(self):
        """Print monitor header"""
        print(f"\n🔮 ═══ TREND MAGIC CONTINUOUS COMPARISON ═══")
        print(f"⚔️  Symbol: {self.symbol}")
        print(f"⏰ Timeframe: {self.timeframe}")
        print(f"🔄 Update Interval: {self.update_interval}s")
        print(f"⚡ Optimized: 50 candles (fast detection)")
        print(f"🔊 Sound Alerts: Agreement changes & Disagreements")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🛡️  Press Ctrl+C to stop gracefully")
        print(f"═══════════════════════════════════════")
        print(f"\n🔮 VERSIONS:")
        print(f"   V1: pandas_ta (Current implementation)")
        print(f"   V2: pandas_ta (Previous implementation)")
        print(f"   V3: TA-Lib (Original - most accurate)")
        print(f"─────────────────────────────────────────────────────────────────────────────")
        print(f"{'Time':>8} | {'Price':>10} | {'Colors':>15} | {'Agreement':>12} | {'Differences':>20}")
        print(f"─────────────────────────────────────────────────────────────────────────────")
    
    def print_statistics(self):
        """Print session statistics"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            duration_str = str(duration).split('.')[0]
            
            total_checks = self.stats['agreements'] + self.stats['disagreements']
            agreement_pct = (self.stats['agreements'] / total_checks * 100) if total_checks > 0 else 0
            
            print(f"\n📊 SESSION STATISTICS:")
            print(f"   Duration: {duration_str}")
            print(f"   Updates: {self.stats['updates']}")
            print(f"   V1 Changes: {self.stats['v1_changes']}")
            print(f"   V2 Changes: {self.stats['v2_changes']}")
            print(f"   V3 Changes: {self.stats['v3_changes']}")
            print(f"   Agreements: {self.stats['agreements']} ({agreement_pct:.1f}%)")
            print(f"   Disagreements: {self.stats['disagreements']}")
    
    def run(self):
        """Start the continuous monitoring"""
        self.setup_signal_handlers()
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.print_header()
        
        try:
            while self.running:
                # Get analysis
                analysis = self.get_all_versions_analysis()
                
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
        print(f"\n🔮 Trend Magic Comparison stopped. Choose the best version! ⚔️")

def main():
    """Main function for running the monitor"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔮 TREND MAGIC CONTINUOUS COMPARISON MONITOR")
    print("⚔️  Real-time BTC analysis - All 3 versions")
    print("⚡ Optimized for speed: 50 candles, 15s updates")
    print("🎯 Goal: Find which version detects changes fastest!")
    
    # Create and run monitor
    monitor = TrendMagicCompareMonitor(
        symbol="BTCUSDT",
        timeframe="1m",
        update_interval=15  # Optimized for faster detection
    )
    
    monitor.run()

if __name__ == "__main__":
    main()