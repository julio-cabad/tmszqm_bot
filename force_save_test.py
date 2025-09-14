#!/usr/bin/env python3
"""
Force Save Test - Forzar guardado para diagnosticar el problema
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

sys.path.append('.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from spartan_trading_system.logging.trade_logger import TradeLogger, TradeRecord

def test_direct_save():
    """Test directo de guardado de archivo"""
    print("🔧 FORCE SAVE TEST")
    print("=" * 50)
    
    # Test 1: Create TradeLogger directly
    print("\n📝 Test 1: Creating TradeLogger...")
    
    trade_logger = TradeLogger()
    
    # Test 2: Create a test trade record manually
    print("\n📊 Test 2: Creating test trade record...")
    
    test_trade = TradeRecord(
        symbol="TESTUSDT",
        side="LONG",
        timeframe="1m",
        entry_time=datetime.now().isoformat(),
        exit_time=datetime.now().isoformat(),
        duration_minutes=5.0,
        entry_price=100.0,
        exit_price=101.0,
        stop_loss=95.0,
        take_profit=105.0,
        trend_magic_value=100.0,
        quantity=1.0,
        position_value=100.0,
        gross_pnl=1.0,
        real_pnl=0.91,
        pnl_percentage=0.91,
        total_commissions=0.09,
        close_reason="TAKE_PROFIT",
        is_winner=True,
        trend_magic_color="BLUE",
        squeeze_momentum="LIME",
        price_change_pct=1.0,
        risk_reward_ratio=2.0
    )
    
    print(f"Test trade created: {test_trade.symbol} {test_trade.side}")
    
    # Test 3: Try to save directly
    print("\n💾 Test 3: Attempting direct save...")
    
    try:
        # Create directory structure manually
        base_path = Path("trade_logs")
        timeframe_dir = base_path / "1m"
        timeframe_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = "trades_1m.json"
        filepath = timeframe_dir / filename
        
        print(f"Target file: {filepath}")
        print(f"Directory exists: {timeframe_dir.exists()}")
        print(f"Directory writable: {os.access(timeframe_dir, os.W_OK)}")
        
        # Try to write directly
        trades = [test_trade.to_dict()]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trades, f, indent=2, ensure_ascii=False, separators=(',', ': '))
        
        print(f"✅ File written successfully!")
        print(f"File exists: {filepath.exists()}")
        print(f"File size: {filepath.stat().st_size} bytes")
        
        # Verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Content verified: {len(data)} trades")
        print(f"First trade: {data[0]['symbol']} {data[0]['side']} PnL: ${data[0]['real_pnl']}")
        
    except Exception as e:
        print(f"❌ Direct save failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Try using TradeLogger._save_trade_to_file
    print("\n🔧 Test 4: Using TradeLogger._save_trade_to_file...")
    
    try:
        trade_logger._save_trade_to_file(test_trade, "1m")
        print("✅ TradeLogger save successful!")
        
        # Check if file exists
        filepath = Path("trade_logs/1m/trades_1m.json")
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            print(f"File contains: {len(data)} trades")
        else:
            print("❌ File not found after TradeLogger save")
            
    except Exception as e:
        print(f"❌ TradeLogger save failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Force save test completed!")

if __name__ == "__main__":
    test_direct_save()