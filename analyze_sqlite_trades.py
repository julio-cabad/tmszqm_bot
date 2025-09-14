#!/usr/bin/env python3
"""
SQLite Trade Analysis - Spartan Trading System
Analyze trades stored in SQLite database
"""

import sys
import os
from datetime import datetime

sys.path.append('.')

from spartan_trading_system.logging.sqlite_trade_logger import SQLiteTradeLogger

def main():
    """Analyze trading performance from SQLite database"""
    print("📊 SPARTAN SQLITE TRADE ANALYSIS")
    print("=" * 50)
    
    # Initialize SQLite trade logger
    trade_logger = SQLiteTradeLogger()
    
    # Get all available timeframes
    timeframes = trade_logger.get_all_timeframes()
    
    if not timeframes:
        print("❌ No trades found in database")
        return
    
    print(f"📈 Available timeframes: {', '.join(timeframes)}")
    print("📈 Performance by Timeframe:")
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
                if 'symbol_performance' in stats and stats['symbol_performance']:
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
    print("\n📁 Options:")
    print("1. Export specific timeframe to CSV")
    print("2. View recent trades for timeframe")
    print("3. View ALL trades (all timeframes)")
    print("4. Show total PnL summary")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print(f"Available timeframes: {', '.join(timeframes)}")
        timeframe = input("Enter timeframe: ").strip()
        if timeframe in timeframes:
            filename = f"trades_{timeframe}_{datetime.now().strftime('%Y%m%d')}.csv"
            if trade_logger.export_to_csv(timeframe, filename):
                print(f"✅ Exported to {filename}")
            else:
                print("❌ Export failed")
        else:
            print("❌ Invalid timeframe")
    
    elif choice == "2":
        print(f"Available timeframes: {', '.join(timeframes)}")
        timeframe = input("Enter timeframe: ").strip()
        limit = input("Number of recent trades (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        if timeframe in timeframes:
            trades = trade_logger.get_trades_by_timeframe(timeframe, limit)
            
            if trades:
                print(f"\n📋 Recent {len(trades)} trades for {timeframe}:")
                print("-" * 100)
                
                for i, trade in enumerate(trades, 1):
                    entry_time = datetime.fromisoformat(trade['entry_time']).strftime("%H:%M:%S")
                    exit_time = datetime.fromisoformat(trade['exit_time']).strftime("%H:%M:%S")
                    
                    print(f"{i:2d}. {trade['symbol']} {trade['side']} | "
                          f"{entry_time}-{exit_time} | "
                          f"Entry: ${trade['entry_price']:.3f} | "
                          f"Exit: ${trade['exit_price']:.3f} | "
                          f"TM: ${trade['trend_magic_value']:.3f} | "
                          f"PnL: ${trade['real_pnl']:+.3f} | "
                          f"Reason: {trade['close_reason']}")
            else:
                print(f"❌ No trades found for {timeframe}")
        else:
            print("❌ Invalid timeframe")
    
    elif choice == "3":
        limit = input("Number of recent trades (default 20): ").strip()
        limit = int(limit) if limit.isdigit() else 20
        
        trades = trade_logger.get_all_trades(limit)
        
        if trades:
            print(f"\n📋 Recent {len(trades)} trades (ALL timeframes):")
            print("-" * 120)
            
            for i, trade in enumerate(trades, 1):
                entry_time = datetime.fromisoformat(trade['entry_time']).strftime("%H:%M:%S")
                exit_time = datetime.fromisoformat(trade['exit_time']).strftime("%H:%M:%S")
                
                print(f"{i:2d}. {trade['symbol']} {trade['side']} ({trade['timeframe']}) | "
                      f"{entry_time}-{exit_time} | "
                      f"Entry: ${trade['entry_price']:.3f} | "
                      f"Exit: ${trade['exit_price']:.3f} | "
                      f"TM: ${trade['trend_magic_value']:.3f} | "
                      f"PnL: ${trade['real_pnl']:+.3f} | "
                      f"Reason: {trade['close_reason']}")
        else:
            print("❌ No trades found")
    
    elif choice == "4":
        summary = trade_logger.get_total_summary()
        
        if summary.get('total_trades', 0) > 0:
            print(f"\n💰 TOTAL PnL SUMMARY (ALL TIMEFRAMES):")
            print("=" * 60)
            print(f"📊 Total Trades: {summary['total_trades']}")
            print(f"📈 Win Rate: {summary['win_rate']:.3f}%")
            print(f"💵 TOTAL PnL: ${summary['total_pnl']:+.3f}")
            print(f"📊 Avg PnL/Trade: ${summary['avg_pnl_per_trade']:+.3f}")
            print(f"🏆 Best Trade: ${summary['best_trade']:+.3f}")
            print(f"💔 Worst Trade: ${summary['worst_trade']:+.3f}")
            print(f"⏱️ Avg Duration: {summary['avg_duration_minutes']:.1f} minutes")
            
            if 'timeframe_breakdown' in summary:
                print(f"\n📊 Breakdown by Timeframe:")
                print("-" * 60)
                for tf, stats in summary['timeframe_breakdown'].items():
                    print(f"   {tf}: ${stats['pnl']:+.3f} ({stats['trades']} trades, {stats['win_rate']:.1f}% win)")
        else:
            print("❌ No trades found")
    
    print("\n👋 Analysis complete!")

if __name__ == "__main__":
    main()