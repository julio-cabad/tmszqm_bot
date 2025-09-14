#!/usr/bin/env python3
"""
Debug Trades - Verificar estado del sistema de trades
"""

import sys
import os
import logging
from datetime import datetime

sys.path.append('.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from spartan_trading_system.config.strategy_config import StrategyConfig
from spartan_trading_system.monitoring.strategy_monitor import StrategyMonitor

def debug_trades():
    """Debug el estado actual del sistema de trades"""
    print("🔍 DEBUG TRADES SYSTEM")
    print("=" * 50)
    
    # Create monitor
    config = StrategyConfig()
    config.timeframes = ['1m']
    monitor = StrategyMonitor(config)
    
    # Check PnL simulator state
    simulator = monitor.pnl_simulator
    
    print(f"\n📊 PnL Simulator State:")
    print(f"   Open positions: {len(simulator.open_positions)}")
    print(f"   Closed trades: {len(simulator.closed_trades)}")
    print(f"   Total trades: {simulator.total_trades}")
    print(f"   Current balance: ${simulator.current_balance:.3f}")
    
    # Show closed trades in memory
    if simulator.closed_trades:
        print(f"\n💾 Closed Trades in Memory:")
        for i, trade in enumerate(simulator.closed_trades, 1):
            print(f"   {i}. {trade.symbol} {trade.side.value} | "
                  f"PnL: ${trade.real_pnl:.3f} | "
                  f"Reason: {trade.close_reason.value}")
    
    # Check trade logger state
    trade_logger = simulator.trade_logger
    session_stats = trade_logger.get_session_stats()
    
    print(f"\n📝 Trade Logger State:")
    print(f"   Session trades: {len(trade_logger.session_trades)}")
    print(f"   Session stats: {session_stats}")
    
    # Show session trades
    if trade_logger.session_trades:
        print(f"\n💾 Session Trades:")
        for i, trade in enumerate(trade_logger.session_trades, 1):
            print(f"   {i}. {trade.symbol} {trade.side} | "
                  f"PnL: ${trade.real_pnl:.3f} | "
                  f"Timeframe: {trade.timeframe}")
    
    # Check files on disk
    print(f"\n📁 Files on Disk:")
    import os
    from pathlib import Path
    
    trade_logs_dir = Path("trade_logs")
    if trade_logs_dir.exists():
        for tf_dir in trade_logs_dir.iterdir():
            if tf_dir.is_dir():
                json_files = list(tf_dir.glob("*.json"))
                print(f"   {tf_dir.name}/: {len(json_files)} files")
                for json_file in json_files:
                    try:
                        import json
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        print(f"     {json_file.name}: {len(data)} trades")
                    except Exception as e:
                        print(f"     {json_file.name}: ERROR - {e}")
    else:
        print("   No trade_logs directory found")
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_trades()