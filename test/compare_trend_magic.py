#!/usr/bin/env python3
"""
Trend Magic Comparison Test - V1 vs V2
Compare both implementations to see which matches TradingView better
"""
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.technical_indicators import TechnicalAnalyzer

def compare_trend_magic_versions(symbol: str = "BTCUSDT", timeframe: str = "1m"):
    """Compare all three Trend Magic implementations"""
    print(f"🔮 ═══ TREND MAGIC COMPARISON: {symbol} ═══")
    
    try:
        analyzer = TechnicalAnalyzer(symbol, timeframe)
        analyzer.fetch_market_data(limit=100)
        
        # Get all three versions
        magic_v1 = analyzer.trend_magic()  # Current version (pandas_ta)
        magic_v2 = analyzer.trend_magic_v2()  # Previous version (pandas_ta)
        magic_v3 = analyzer.trend_magic_v3()  # TA-Lib version
        
        print(f"⚔️  Symbol: {symbol}")
        print(f"⏰ Timeframe: {timeframe}")
        print(f"💰 Current Price: ${magic_v1['current_price']:,.4f}")
        
        print(f"\n🔮 TREND MAGIC V1 (pandas_ta - Current):")
        print(f"   Value: ${magic_v1['magic_trend_value']:,.4f}")
        print(f"   Color: {magic_v1['color']}")
        print(f"   Status: {magic_v1['trend_status']}")
        print(f"   Distance: {magic_v1['distance_pct']:+.2f}%")
        print(f"   CCI: {magic_v1['cci_value']:,.2f}")
        
        print(f"\n🔮 TREND MAGIC V2 (pandas_ta - Previous):")
        print(f"   Value: ${magic_v2['magic_trend_value']:,.4f}")
        print(f"   Color: {magic_v2['color']}")
        print(f"   Status: {magic_v2['trend_status']}")
        print(f"   Distance: {magic_v2['distance_pct']:+.2f}%")
        print(f"   CCI: {magic_v2['cci_value']:,.2f}")
        
        print(f"\n🔮 TREND MAGIC V3 (TA-Lib - Original):")
        print(f"   Value: ${magic_v3['magic_trend_value']:,.4f}")
        print(f"   Color: {magic_v3['color']}")
        print(f"   Status: {magic_v3['trend_status']}")
        print(f"   Distance: {magic_v3['distance_pct']:+.2f}%")
        print(f"   CCI: {magic_v3['cci_value']:,.2f}")
        
        # Compare results
        print(f"\n📊 COMPARISON:")
        v1_v2_match = "✅ MATCH" if magic_v1['color'] == magic_v2['color'] else "❌ DIFFERENT"
        v1_v3_match = "✅ MATCH" if magic_v1['color'] == magic_v3['color'] else "❌ DIFFERENT"
        v2_v3_match = "✅ MATCH" if magic_v2['color'] == magic_v3['color'] else "❌ DIFFERENT"
        
        print(f"   V1 vs V2 Colors: {magic_v1['color']} vs {magic_v2['color']} - {v1_v2_match}")
        print(f"   V1 vs V3 Colors: {magic_v1['color']} vs {magic_v3['color']} - {v1_v3_match}")
        print(f"   V2 vs V3 Colors: {magic_v2['color']} vs {magic_v3['color']} - {v2_v3_match}")
        
        v1_v2_diff = abs(magic_v1['magic_trend_value'] - magic_v2['magic_trend_value'])
        v1_v3_diff = abs(magic_v1['magic_trend_value'] - magic_v3['magic_trend_value'])
        v2_v3_diff = abs(magic_v2['magic_trend_value'] - magic_v3['magic_trend_value'])
        
        print(f"   V1 vs V2 Value Diff: ${v1_v2_diff:.4f}")
        print(f"   V1 vs V3 Value Diff: ${v1_v3_diff:.4f}")
        print(f"   V2 vs V3 Value Diff: ${v2_v3_diff:.4f}")
        
        # Quick color checks
        v1_color = analyzer.get_trend_magic_color()
        v2_color = analyzer.get_trend_magic_v2_color()
        v3_color = analyzer.get_trend_magic_v3_color()
        
        print(f"\n🎯 Quick Color Checks:")
        print(f"   V1 (pandas_ta): {v1_color}")
        print(f"   V2 (pandas_ta): {v2_color}")
        print(f"   V3 (TA-Lib): {v3_color}")
        
        # Determine which version matches TradingView best
        all_match = magic_v1['color'] == magic_v2['color'] == magic_v3['color']
        if all_match:
            print(f"\n🏆 ALL VERSIONS AGREE: {magic_v1['color']}")
        else:
            print(f"\n⚠️  VERSIONS DISAGREE - Test against TradingView to choose!")
        
        return {
            'v1': magic_v1,
            'v2': magic_v2,
            'v3': magic_v3,
            'all_match': all_match,
            'v1_v2_diff': v1_v2_diff,
            'v1_v3_diff': v1_v3_diff,
            'v2_v3_diff': v2_v3_diff
        }
        
    except Exception as e:
        print(f"💀 Comparison failed: {str(e)}")
        return None

def test_multiple_timeframes():
    """Test both versions across different timeframes"""
    print("\n🏛️ ═══ MULTI-TIMEFRAME COMPARISON ═══")
    
    timeframes = ["1m", "5m", "15m", "1h"]
    
    for tf in timeframes:
        try:
            print(f"\n⏰ Testing {tf} timeframe:")
            result = compare_trend_magic_versions("BTCUSDT", tf)
            
            if result:
                match_status = "✅ COLORS MATCH" if result['colors_match'] else "❌ COLORS DIFFER"
                print(f"   Result: {match_status} | Value Diff: ${result['value_diff']:.4f}")
            
        except Exception as e:
            print(f"   💀 {tf} failed: {str(e)}")

def main():
    """Main comparison function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔮 TREND MAGIC VERSION COMPARISON")
    print("⚔️  Testing V1 (Current) vs V2 (Previous) implementations")
    print("🎯 Goal: Find which version matches TradingView better")
    print("=" * 60)
    
    # Test 1: Single detailed comparison
    compare_trend_magic_versions("BTCUSDT", "1m")
    
    # Test 2: Multiple timeframes
    test_multiple_timeframes()
    
    print("\n🏛️ ═══ COMPARISON COMPLETE ═══")
    print("🔮 Use the version that matches TradingView colors better!")
    print("⚔️  Monitor both versions to see which detects changes faster!")

if __name__ == "__main__":
    main()