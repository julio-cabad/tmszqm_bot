#!/usr/bin/env python3
"""
Test Auto Close - Verificar que el cierre automático guarda trades
"""

import sys
import os
import logging
import time
from datetime import datetime

sys.path.append('.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from spartan_trading_system.simulation.pnl_simulator import PnLSimulator

def test_auto_close():
    """Test que el cierre automático funciona y guarda trades"""
    print("🧪 TESTING AUTO CLOSE SYSTEM")
    print("=" * 50)
    
    # Initialize simulator
    simulator = PnLSimulator()
    
    # Test 1: Open a position that will hit TP
    print("\n📈 Test 1: Opening position that will hit TP...")
    
    # Set metadata first
    simulator.set_position_metadata(
        symbol="TESTUSDT",
        timeframe="1m",
        trend_magic_value=100.0,
        trend_magic_color="BLUE",
        squeeze_momentum="LIME"
    )
    
    # Open position with TP very close to entry
    success = simulator.open_position(
        symbol="TESTUSDT",
        side="LONG",
        entry_price=100.0,
        quantity=1.0,  # $100 position
        stop_loss=95.0,   # 5% SL
        take_profit=101.0  # 1% TP (very close)
    )
    
    print(f"Position opened: {success}")
    print(f"Open positions: {len(simulator.open_positions)}")
    
    if success:
        position = simulator.open_positions["TESTUSDT"]
        print(f"Position details: Entry=${position.entry_price}, SL=${position.stop_loss}, TP=${position.take_profit}")
    
    # Test 2: Update with price that hits TP
    print("\n📈 Test 2: Updating with price that hits TP...")
    
    market_data = {"TESTUSDT": 101.5}  # Price above TP
    
    print(f"Updating with price: ${market_data['TESTUSDT']}")
    simulator.update_positions(market_data)
    
    print(f"Open positions after update: {len(simulator.open_positions)}")
    print(f"Closed trades: {len(simulator.closed_trades)}")
    
    # Test 3: Check if trade was logged
    print("\n📝 Test 3: Checking if trade was logged...")
    
    session_stats = simulator.get_trade_logger_stats()
    print(f"Session stats: {session_stats}")
    
    # Test 4: Check files
    print("\n📁 Test 4: Checking files...")
    
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
                        if data:
                            last_trade = data[-1]
                            print(f"       Last trade: {last_trade['symbol']} {last_trade['side']} | "
                                  f"PnL: ${last_trade['real_pnl']:.3f} | "
                                  f"Reason: {last_trade['close_reason']}")
                    except Exception as e:
                        print(f"     {json_file.name}: ERROR - {e}")
    else:
        print("   No trade_logs directory found")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_auto_close()