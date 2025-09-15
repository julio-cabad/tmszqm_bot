#!/usr/bin/env python3
"""
Test Telegram Notifications - Spartan Trading System
"""

import sys
import os
from datetime import datetime

sys.path.append('.')

from spartan_trading_system.notifications.telegram_notifier import TelegramNotifier
from spartan_trading_system.notifications.telegram_config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def test_telegram_notifications():
    """Test Telegram notifications"""
    print("📱 TESTING TELEGRAM NOTIFICATIONS")
    print("=" * 50)
    
    # Initialize notifier
    try:
        notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        print("✅ Telegram notifier initialized")
    except Exception as e:
        print(f"❌ Failed to initialize notifier: {e}")
        return
    
    # Test 1: Position Opened
    print("\n📈 Test 1: Position Opened Notification")
    success = notifier.notify_position_opened(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=50000.0,
        quantity=0.002,
        stop_loss=49000.0,
        take_profit=52000.0,
        timeframe="15m"
    )
    print(f"Position opened notification: {'✅ Sent' if success else '❌ Failed'}")
    
    # Test 2: Position Closed (Winner)
    print("\n💚 Test 2: Position Closed (Winner) Notification")
    success = notifier.notify_position_closed(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=50000.0,
        exit_price=51000.0,
        quantity=0.002,
        gross_pnl=2.0,
        real_pnl=1.91,
        total_commissions=0.09,
        close_reason="TAKE_PROFIT",
        entry_time=datetime(2025, 9, 14, 10, 30, 0),
        exit_time=datetime(2025, 9, 14, 11, 15, 0),
        timeframe="15m"
    )
    print(f"Position closed (winner) notification: {'✅ Sent' if success else '❌ Failed'}")
    
    # Test 3: Position Closed (Loser)
    print("\n💔 Test 3: Position Closed (Loser) Notification")
    success = notifier.notify_position_closed(
        symbol="ETHUSDT",
        side="SHORT",
        entry_price=4000.0,
        exit_price=4050.0,
        quantity=0.025,
        gross_pnl=-1.25,
        real_pnl=-1.34,
        total_commissions=0.09,
        close_reason="STOP_LOSS",
        entry_time=datetime(2025, 9, 14, 12, 0, 0),
        exit_time=datetime(2025, 9, 14, 12, 20, 0),
        timeframe="15m"
    )
    print(f"Position closed (loser) notification: {'✅ Sent' if success else '❌ Failed'}")
    
    # Test 4: General Alert
    print("\n🚨 Test 4: General Alert Notification")
    success = notifier.notify_alert(
        title="System Alert",
        message="Spartan Trading System is running smoothly! 🚀"
    )
    print(f"Alert notification: {'✅ Sent' if success else '❌ Failed'}")
    
    print("\n✅ Telegram notification tests completed!")
    print("📱 Check your Telegram chat for the test messages")

if __name__ == "__main__":
    test_telegram_notifications()