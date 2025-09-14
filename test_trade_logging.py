#!/usr/bin/env python3
"""
Test Trade Logging - Verificar que el sistema de logging funciona
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

from spartan_trading_system.simulation.pnl_simulator import PnLSimulator, CloseReason

def test_trade_logging():
    """Test que el sistema de logging de trades funciona"""
    print("🧪 TESTING TRADE LOGGING SYSTEM")
    print("=" * 50)
    
    # Initialize simulator
    simulator = PnLSimulator()
    
    # Test 1: Open a position
    print("\n📈 Test 1: Opening position...")
    
    # Set metadata first
    simulator.set_position_metadata(
        symbol="BTCUSDT",
        timeframe="1h",
        trend_magic_value=50000.0,
        trend_magic_color="BLUE",
        squeeze_momentum="LIME"
    )
    
    # Open position
    success = simulator.open_position(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=50000.0,
        quantity=0.002,  # $100 position
        stop_loss=49000.0,
        take_profit=52000.0
    )
    
    print(f"Position opened: {success}")
    print(f"Open positions: {len(simulator.open_positions)}")
    
    # Test 2: Force close position
    print("\n📉 Test 2: Closing position...")
    
    closed = simulator.force_close_position("BTCUSDT")
    print(f"Position closed: {closed}")
    print(f"Open positions: {len(simulator.open_positions)}")
    print(f"Closed trades: {len(simulator.closed_trades)}")
    
    # Test 3: Check if file was created
    print("\n📁 Test 3: Checking files...")
    
    import os
    from pathlib import Path
    
    trade_logs_dir = Path("trade_logs")
    if trade_logs_dir.exists():
        print(f"✅ trade_logs directory exists")
        
        # Check for timeframe directories
        timeframe_dirs = list(trade_logs_dir.iterdir())
        print(f"Timeframe directories: {[d.name for d in timeframe_dirs if d.is_dir()]}")
        
        # Check for JSON files
        for tf_dir in timeframe_dirs:
            if tf_dir.is_dir():
                json_files = list(tf_dir.glob("*.json"))
                print(f"JSON files in {tf_dir.name}: {[f.name for f in json_files]}")
                
                # Read and display content
                for json_file in json_files:
                    try:
                        import json
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        print(f"📄 Content of {json_file.name}: {len(data)} trades")
                        if data:
                            print(f"   First trade: {data[0]['symbol']} {data[0]['side']} PnL: ${data[0]['real_pnl']:.2f}")
                    except Exception as e:
                        print(f"❌ Error reading {json_file}: {e}")
    else:
        print("❌ trade_logs directory not found")
    
    # Test 4: Get session stats
    print("\n📊 Test 4: Session statistics...")
    
    stats = simulator.get_trade_logger_stats()
    print(f"Session stats: {stats}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_trade_logging()