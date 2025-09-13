#!/usr/bin/env python3
"""
Risk Management System Test - Spartan Risk Controls
Comprehensive testing of position sizing, stop losses, and portfolio risk
"""

import logging
import sys
import os

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.indicators.indicator_engine import IndicatorEngine
from spartan_trading_system.strategy.signal_generator import SignalGenerator
from spartan_trading_system.risk.risk_manager import RiskManager
from spartan_trading_system.strategy.signal_types import SignalType, TradingSignal, Direction
from spartan_trading_system.risk.risk_models import Direction as RiskDirection
from datetime import datetime

def test_position_calculator():
    """Test position size calculations"""
    print("🏛️ ═══ TESTING POSITION CALCULATOR ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create risk manager
        risk_manager = RiskManager(config)
        
        # Test position calculation
        account_balance = 10000.0  # $10,000 account
        entry_price = 116000.0  # BTC entry
        stop_loss_price = 115000.0  # $1000 stop
        
        position_size = risk_manager.position_calculator.calculate_position_size(
            symbol="BTCUSDT",
            direction=RiskDirection.LONG,
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price
        )
        
        print(f"✅ Position Size Calculation:")
        print(f"   Account Balance: ${account_balance:,.2f}")
        print(f"   Risk Percentage: {position_size.risk_percentage}%")
        print(f"   Risk Amount: ${position_size.risk_amount:,.2f}")
        print(f"   Position Size: ${position_size.position_size_usd:,.2f}")
        print(f"   Position Base: {position_size.position_size_base:.6f} BTC")
        print(f"   Max Loss: {position_size.max_loss_percentage:.2f}%")
        
        # Validate position
        is_valid, errors = risk_manager.position_calculator.validate_position_size(position_size)
        if is_valid:
            print(f"✅ Position validation: PASSED")
        else:
            print(f"❌ Position validation: FAILED - {len(errors)} errors")
            for error in errors:
                print(f"     - {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Position calculator test failed: {str(e)}")
        return False

def test_stop_loss_calculation():
    """Test stop loss calculations"""
    print("\n🛡️ ═══ TESTING STOP LOSS CALCULATION ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create risk manager
        risk_manager = RiskManager(config)
        
        # Test stop loss calculation
        entry_price = 116000.0
        trend_magic_value = 115500.0
        atr_value = 800.0
        
        stop_loss = risk_manager.position_calculator.calculate_stop_loss(
            symbol="BTCUSDT",
            direction=RiskDirection.LONG,
            entry_price=entry_price,
            trend_magic_value=trend_magic_value,
            atr_value=atr_value
        )
        
        print(f"✅ Stop Loss Calculation:")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   Trend Magic Stop: ${stop_loss.trend_magic_stop:,.2f}")
        print(f"   ATR Stop: ${stop_loss.atr_stop:,.2f}")
        print(f"   Percentage Stop: ${stop_loss.percentage_stop:,.2f}")
        print(f"   Recommended: ${stop_loss.recommended_stop:,.2f} ({stop_loss.stop_type})")
        print(f"   Stop Distance: {stop_loss.stop_distance_percentage:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Stop loss test failed: {str(e)}")
        return False

def test_take_profit_calculation():
    """Test take profit calculations"""
    print("\n🎯 ═══ TESTING TAKE PROFIT CALCULATION ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create risk manager
        risk_manager = RiskManager(config)
        
        # Test take profit calculation
        entry_price = 116000.0
        stop_loss_price = 115000.0  # Stop loss below entry for LONG position
        
        take_profit = risk_manager.position_calculator.calculate_take_profit(
            symbol="BTCUSDT",
            direction=RiskDirection.LONG,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price
        )
        
        print(f"✅ Take Profit Calculation:")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   Stop Loss: ${stop_loss_price:,.2f}")
        print(f"   TP1 (1:1): ${take_profit.tp1_price:,.2f} ({take_profit.tp1_allocation*100:.0f}% allocation)")
        print(f"   TP2 (1:2): ${take_profit.tp2_price:,.2f} ({take_profit.tp2_allocation*100:.0f}% allocation)")
        print(f"   TP3 (1:3): ${take_profit.tp3_price:,.2f} ({take_profit.tp3_allocation*100:.0f}% allocation)")
        
        return True
        
    except Exception as e:
        print(f"❌ Take profit test failed: {str(e)}")
        return False

def test_comprehensive_risk_assessment():
    """Test comprehensive risk assessment"""
    print("\n⚔️ ═══ TESTING COMPREHENSIVE RISK ASSESSMENT ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create components
        indicator_engine = IndicatorEngine(config)
        signal_generator = SignalGenerator(config, indicator_engine)
        risk_manager = RiskManager(config)
        
        # Create a mock trading signal
        mock_signal = TradingSignal(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            signal_type=SignalType.SUPER_BULLISH,
            direction=Direction.LONG,
            strength=0.85,
            confidence=0.9,
            entry_price=116000.0,
            current_price=116000.0,
            stop_loss=0.0,  # Will be calculated
            take_profit_levels=[],
            position_size_pct=2.0,
            trend_magic_value=115500.0,
            trend_magic_color="BLUE",
            squeeze_status="ON",
            momentum_color="GREEN",
            momentum_value=0.75,
            timeframe="1h",
            context_timeframe_trend="BULLISH",
            confirmation_timeframe_trend="BULLISH",
            timeframes_aligned=True,
            trigger_reason="Super Bullish: Squeeze ON + Trend Magic BLUE + Momentum GREEN",
            supporting_factors=["Strong momentum", "Trend alignment", "Squeeze compression"],
            risk_factors=["Market volatility"]
        )
        
        # Test comprehensive risk assessment
        account_balance = 10000.0
        trend_magic_value = 115500.0
        atr_value = 800.0
        
        risk_assessment = risk_manager.assess_signal_risk(
            signal=mock_signal,
            account_balance=account_balance,
            trend_magic_value=trend_magic_value,
            atr_value=atr_value
        )
        
        print(f"✅ Risk Assessment Results:")
        print(f"   Symbol: {risk_assessment.symbol}")
        print(f"   Direction: {risk_assessment.direction.value}")
        print(f"   Risk Level: {risk_assessment.risk_level.value}")
        print(f"   Risk Score: {risk_assessment.risk_score:.3f}")
        print(f"   Position Size: ${risk_assessment.position_size.position_size_usd:,.2f}")
        print(f"   Risk Amount: ${risk_assessment.position_size.risk_amount:,.2f}")
        print(f"   R:R Ratio: {risk_assessment.position_size.risk_reward_ratio:.2f}")
        print(f"   Valid: {risk_assessment.is_valid}")
        
        if risk_assessment.validation_errors:
            print(f"   Errors: {len(risk_assessment.validation_errors)}")
            for error in risk_assessment.validation_errors:
                print(f"     - {error}")
        
        if risk_assessment.validation_warnings:
            print(f"   Warnings: {len(risk_assessment.validation_warnings)}")
            for warning in risk_assessment.validation_warnings:
                print(f"     - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment test failed: {str(e)}")
        return False

def test_portfolio_risk_management():
    """Test portfolio-level risk management"""
    print("\n🏛️ ═══ TESTING PORTFOLIO RISK MANAGEMENT ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create risk manager
        risk_manager = RiskManager(config)
        
        # Test portfolio risk with no positions
        account_balance = 10000.0
        portfolio_risk = risk_manager.get_portfolio_risk(account_balance)
        
        print(f"✅ Portfolio Risk (Empty):")
        print(f"   Total Risk: ${portfolio_risk.total_risk_amount:,.2f} ({portfolio_risk.total_risk_percentage:.2f}%)")
        print(f"   Active Positions: {portfolio_risk.active_positions}/{portfolio_risk.max_positions}")
        print(f"   Risk Level: {portfolio_risk.risk_level.value}")
        print(f"   Can Take New Position: {portfolio_risk.can_take_new_position}")
        print(f"   Position Size Multiplier: {portfolio_risk.recommended_position_size_multiplier:.2f}")
        
        # Add some mock positions
        mock_signal1 = TradingSignal(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            signal_type=SignalType.SUPER_BULLISH,
            direction=Direction.LONG,
            strength=0.85,
            confidence=0.9,
            entry_price=116000.0,
            current_price=116000.0,
            stop_loss=0.0,
            take_profit_levels=[],
            position_size_pct=2.0,
            trend_magic_value=115500.0,
            trend_magic_color="BLUE",
            squeeze_status="ON",
            momentum_color="GREEN",
            momentum_value=0.75,
            timeframe="1h",
            context_timeframe_trend="BULLISH",
            confirmation_timeframe_trend="BULLISH",
            timeframes_aligned=True,
            trigger_reason="Super Bullish: Squeeze ON + Trend Magic BLUE + Momentum GREEN",
            supporting_factors=["Strong momentum", "Trend alignment", "Squeeze compression"],
            risk_factors=["Market volatility"]
        )
        
        # Assess and add first position
        risk_assessment1 = risk_manager.assess_signal_risk(
            signal=mock_signal1,
            account_balance=account_balance,
            trend_magic_value=115500.0,
            atr_value=800.0
        )
        
        if risk_assessment1.is_valid:
            risk_manager.add_position(risk_assessment1)
            print(f"✅ Added position: {risk_assessment1.symbol}")
        
        # Test portfolio risk with positions
        portfolio_risk = risk_manager.get_portfolio_risk(account_balance)
        
        print(f"\n✅ Portfolio Risk (With Positions):")
        print(f"   Total Risk: ${portfolio_risk.total_risk_amount:,.2f} ({portfolio_risk.total_risk_percentage:.2f}%)")
        print(f"   Active Positions: {portfolio_risk.active_positions}/{portfolio_risk.max_positions}")
        print(f"   Risk Level: {portfolio_risk.risk_level.value}")
        print(f"   Can Take New Position: {portfolio_risk.can_take_new_position}")
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio risk test failed: {str(e)}")
        return False

def main():
    """Run all risk management tests"""
    print("🏛️⚔️ SPARTAN RISK MANAGEMENT SYSTEM TESTS")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tests = [
        test_position_calculator,
        test_stop_loss_calculation,
        test_take_profit_calculation,
        test_comprehensive_risk_assessment,
        test_portfolio_risk_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print(f"\n🏛️ ═══ TEST RESULTS ═══")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎯 ALL TESTS PASSED! SPARTAN RISK SYSTEM IS READY FOR BATTLE! ⚔️")
        return True
    else:
        print("💀 SOME TESTS FAILED! REVIEW AND FIX BEFORE DEPLOYMENT!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)