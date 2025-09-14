#!/usr/bin/env python3
"""
Trade Analysis Script - Spartan Trading System
Analyze historical trading performance by timeframe
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append('.')

from spartan_trading_system.logging.trade_logger import TradeLogger

def main():
    """Analyze trading performance"""
    print("📊 SPARTAN TRADE ANALYSIS")
    print("=" * 50)
    
    # Initialize trade logger
    trade_logger = TradeLogger()
    
    # Available timeframes
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h']
    
    print("📈 Performance by Timeframe (Last 7 days):")
    print("-" * 80)
    
    for timeframe in timeframes:
        try:
            stats = trade_logger.get_timeframe_summary(timeframe)
            
            if stats.get('total_trades', 0) > 0:
                print(f"\n🕐 {timeframe.upper()} Timeframe:")
                print(f"   Total Trades: {stats['total_trades']}")
                print(f"   Win Rate: {stats['win_rate']:.3f}%")
                print(f"   Total PnL: ${stats['total_pnl']:.3f}")
                print(f"   Avg PnL/Trade: ${stats['avg_pnl_per_trade']:.3f}")
                print(f"   Best Trade: ${stats['best_trade']:.3f}")
                print(f"   Worst Trade: ${stats['worst_trade']:.3f}")
                print(f"   Avg Duration: {stats['avg_duration_minutes']:.3f} minutes")
                
                # Show top performing symbols
                if 'symbol_performance' in stats:
                    print(f"   Top Symbols:")
                    sorted_symbols = sorted(
                        stats['symbol_performance'].items(),
                        key=lambda x: x[1]['pnl'],
                        reverse=True
                    )[:3]
                    
                    for symbol, perf in sorted_symbols:
                        win_rate = (perf['wins'] / perf['trades']) * 100 if perf['trades'] > 0 else 0
                        print(f"     {symbol}: ${perf['pnl']:.3f} ({perf['trades']} trades, {win_rate:.3f}% win)")
            else:
                print(f"\n🕐 {timeframe.upper()}: No trades found")
                
        except Exception as e:
            print(f"\n🕐 {timeframe.upper()}: Error - {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Export options
    print("\n📁 Export Options:")
    print("1. Export specific timeframe to CSV")
    print("2. View detailed trade records")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        timeframe = input("Enter timeframe (1m/5m/15m/30m/1h/4h): ").strip()
        if timeframe in timeframes:
            filename = f"trades_{timeframe}_{datetime.now().strftime('%Y%m%d')}.csv"
            if trade_logger.export_to_csv(timeframe, filename):
                print(f"✅ Exported to {filename}")
            else:
                print("❌ Export failed")
        else:
            print("❌ Invalid timeframe")
    
    elif choice == "2":
        timeframe = input("Enter timeframe (1m/5m/15m/30m/1h/4h): ").strip()
        
        trades = trade_logger.load_trades_by_timeframe(timeframe)
        
        if trades:
            print(f"\n📋 All Trades for {timeframe}:")
            print("-" * 100)
            
            for i, trade in enumerate(trades, 1):
                entry_time = datetime.fromisoformat(trade.entry_time).strftime("%H:%M:%S")
                exit_time = datetime.fromisoformat(trade.exit_time).strftime("%H:%M:%S")
                
                print(f"{i:2d}. {trade.symbol} {trade.side} | "
                      f"{entry_time}-{exit_time} | "
                      f"Entry: ${trade.entry_price:.3f} | "
                      f"Exit: ${trade.exit_price:.3f} | "
                      f"PnL: ${trade.real_pnl:+.3f} | "
                      f"Reason: {trade.close_reason}")
        else:
            print(f"❌ No trades found for {timeframe}")
    
    print("\n👋 Analysis complete!")

if __name__ == "__main__":
    main()