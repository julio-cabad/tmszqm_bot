#!/usr/bin/env python3
"""
Trend Magic Indicator Test - Spartan Battle Testing
Real market data, no simulations, pure warrior analysis
"""
import logging
from indicators.technical_indicators import TechnicalAnalyzer
from config.settings import SYMBOLS

# Configure logging for battle reports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_trend_magic_single(symbol: str = "BTCUSDT", timeframe: str = "1h"):
    """Test Trend Magic on a single symbol like a focused warrior"""
    print(f"🔮 ═══ TREND MAGIC ANALYSIS: {symbol} ═══")
    
    try:
        analyzer = TechnicalAnalyzer(symbol, timeframe)
        analyzer.fetch_market_data(limit=100)  # Get enough data for calculations
        
        # Get Trend Magic analysis
        magic = analyzer.trend_magic()
        
        print(f"⚔️  Symbol: {symbol}")
        print(f"⏰ Timeframe: {timeframe}")
        print(f"💰 Current Price: ${magic['current_price']:,.4f}")
        print(f"🔮 Magic Trend: ${magic['magic_trend_value']:,.4f}")
        print(f"🎨 Color: {magic['color']}")
        print(f"📊 Status: {magic['trend_status']}")
        print(f"📏 Distance: {magic['distance_pct']:+.2f}%")
        print(f"📈 CCI: {magic['cci_value']:,.2f}")
        print(f"📊 ATR: {magic['atr_value']:,.4f}")
        
        # Signal analysis
        if magic['buy_signal']:
            print(f"🚀 BUY SIGNAL ACTIVE!")
        elif magic['sell_signal']:
            print(f"💀 SELL SIGNAL ACTIVE!")
        else:
            print(f"⚖️  No active signals")
        
        # Quick color check
        color = analyzer.get_trend_magic_color()
        print(f"🎯 Quick Color Check: {color}")
        
        return magic
        
    except Exception as e:
        print(f"💀 Trend Magic test failed: {str(e)}")
        return None

def test_trend_magic_multiple():
    """Test Trend Magic across multiple crypto warriors"""
    print("🏛️ ═══ MULTI-SYMBOL TREND MAGIC BATTLE ═══")
    
    # Test top 5 symbols
    test_symbols = SYMBOLS[:5]
    results = {}
    
    for symbol in test_symbols:
        try:
            print(f"\n🛡️  Testing {symbol}...")
            analyzer = TechnicalAnalyzer(symbol, "1h")
            analyzer.fetch_market_data(limit=100)
            
            # Get just the color for quick assessment
            color = analyzer.get_trend_magic_color()
            magic = analyzer.trend_magic()
            
            results[symbol] = {
                'color': color,
                'price': magic['current_price'],
                'trend_status': magic['trend_status'],
                'distance': magic['distance_pct'],
                'buy_signal': magic['buy_signal'],
                'sell_signal': magic['sell_signal']
            }
            
            # Quick status
            signal_text = ""
            if magic['buy_signal']:
                signal_text = "🚀 BUY"
            elif magic['sell_signal']:
                signal_text = "💀 SELL"
            else:
                signal_text = "⚖️  HOLD"
            
            print(f"   {symbol}: {color} | ${magic['current_price']:,.2f} | {signal_text}")
            
        except Exception as e:
            print(f"   💀 {symbol} failed: {str(e)}")
            results[symbol] = {'error': str(e)}
    
    # Summary report
    print(f"\n📊 BATTLE SUMMARY:")
    bullish_count = sum(1 for r in results.values() if r.get('color') == 'BLUE')
    bearish_count = sum(1 for r in results.values() if r.get('color') == 'RED')
    
    print(f"   🔵 Bullish: {bullish_count}")
    print(f"   🔴 Bearish: {bearish_count}")
    
    # Active signals
    buy_signals = [s for s, r in results.items() if r.get('buy_signal')]
    sell_signals = [s for s, r in results.items() if r.get('sell_signal')]
    
    if buy_signals:
        print(f"   🚀 Buy Signals: {', '.join(buy_signals)}")
    if sell_signals:
        print(f"   💀 Sell Signals: {', '.join(sell_signals)}")
    
    return results

def test_trend_magic_parameters():
    """Test different Trend Magic parameters like a true strategist"""
    print("\n🔮 ═══ TREND MAGIC PARAMETER TESTING ═══")
    
    symbol = "BTCUSDT"
    analyzer = TechnicalAnalyzer(symbol, "1h")
    analyzer.fetch_market_data(limit=200)
    
    # Test different parameter combinations
    test_params = [
        {'period': 20, 'coeff': 1.0, 'atr_period': 5},   # Default
        {'period': 14, 'coeff': 1.5, 'atr_period': 10},  # More sensitive
        {'period': 30, 'coeff': 0.8, 'atr_period': 3},   # Less sensitive
    ]
    
    print(f"⚔️  Testing {symbol} with different parameters:")
    
    for i, params in enumerate(test_params, 1):
        try:
            magic = analyzer.trend_magic(**params)
            
            print(f"\n   Test {i}: Period={params['period']}, Coeff={params['coeff']}, ATR={params['atr_period']}")
            print(f"   Color: {magic['color']} | Trend: ${magic['magic_trend_value']:,.2f}")
            print(f"   Distance: {magic['distance_pct']:+.2f}% | CCI: {magic['cci_value']:,.1f}")
            
            if magic['buy_signal'] or magic['sell_signal']:
                signal = "BUY" if magic['buy_signal'] else "SELL"
                print(f"   🎯 SIGNAL: {signal}")
            
        except Exception as e:
            print(f"   💀 Test {i} failed: {str(e)}")

def test_full_spartan_report():
    """Test the full Spartan report with Trend Magic included"""
    print("\n🏛️ ═══ FULL SPARTAN REPORT WITH TREND MAGIC ═══")
    
    try:
        analyzer = TechnicalAnalyzer("BTCUSDT", "1h")
        analyzer.fetch_market_data(limit=300)
        
        # Full report with Trend Magic
        analyzer.print_spartan_report([20, 50, 200], include_trend_magic=True)
        
    except Exception as e:
        print(f"💀 Full report failed: {str(e)}")

def main():
    """Main battle function"""
    print("🔮 TREND MAGIC INDICATOR - SPARTAN TESTING")
    print("⚔️  Ported from PineScript to Python warrior code!")
    print("=" * 60)
    
    # Test 1: Single symbol detailed analysis
    test_trend_magic_single("BTCUSDT", "1h")
    
    # Test 2: Multiple symbols quick scan
    test_trend_magic_multiple()
    
    # Test 3: Parameter testing
    test_trend_magic_parameters()
    
    # Test 4: Full Spartan report
    test_full_spartan_report()
    
    print("\n🏛️ ═══ TREND MAGIC TESTING COMPLETE ═══")
    print("🔮 The magic of trends revealed through Spartan analysis!")
    print("⚔️  Ready for battle with real market data!")

if __name__ == "__main__":
    main()