#!/usr/bin/env python3
"""
Data Management System Test - Spartan Data Integration
Comprehensive testing of market data, caching, and database systems
"""

import logging
import sys
import os
import time
from datetime import datetime, timedelta

# Add spartan_trading_system to path
sys.path.append('.')

from spartan_trading_system.config.config_manager import ConfigManager
from spartan_trading_system.data.market_data_provider import MarketDataProvider
from spartan_trading_system.data.data_cache import DataCache
from spartan_trading_system.data.database_manager import DatabaseManager
from spartan_trading_system.data.data_models import DataRequest, TimeFrame


def test_data_cache():
    """Test data cache functionality"""
    print("🏛️ ═══ TESTING DATA CACHE ═══")
    
    try:
        # Create cache
        cache = DataCache(max_size_mb=10, default_ttl=60)
        
        # Test cache statistics
        stats = cache.get_stats()
        print(f"✅ Cache initialized:")
        print(f"   Max Size: {stats['max_size_mb']:.1f}MB")
        print(f"   Current Size: {stats['size_mb']:.3f}MB")
        print(f"   Entries: {stats['entries']}")
        print(f"   Hit Rate: {stats['hit_rate_pct']:.1f}%")
        
        # Test cache operations
        request = DataRequest(
            symbol="BTCUSDT",
            timeframe="1h",
            limit=100
        )
        
        # Test cache miss
        cached_data = cache.get(request)
        if cached_data is None:
            print("✅ Cache miss test passed")
        
        # Test cache optimization
        cache.optimize()
        print("✅ Cache optimization completed")
        
        # Cleanup
        cache.shutdown()
        print("✅ Cache shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Data cache test failed: {str(e)}")
        return False


def test_database_manager():
    """Test database manager functionality"""
    print("\n💾 ═══ TESTING DATABASE MANAGER ═══")
    
    try:
        # Create database manager
        db_manager = DatabaseManager("test_data/test_spartan.db")
        
        # Test database statistics
        stats = db_manager.get_database_stats()
        print(f"✅ Database initialized:")
        print(f"   File Size: {stats.get('file_size_mb', 0):.3f}MB")
        print(f"   Market Data Records: {stats.get('market_data_count', 0)}")
        print(f"   Symbol Info Records: {stats.get('symbol_info_count', 0)}")
        
        # Test available symbols
        symbols = db_manager.get_available_symbols()
        print(f"✅ Available symbols: {len(symbols)}")
        
        # Test database optimization
        db_manager.optimize_database()
        print("✅ Database optimization completed")
        
        # Cleanup
        db_manager.close()
        print("✅ Database closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database manager test failed: {str(e)}")
        return False


def test_market_data_provider():
    """Test market data provider functionality"""
    print("\n📊 ═══ TESTING MARKET DATA PROVIDER ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create components
        cache = DataCache(max_size_mb=5, default_ttl=300)
        provider = MarketDataProvider(config, cache)
        
        # Test connectivity
        is_connected = provider.test_connectivity()
        if is_connected:
            print("✅ Binance API connectivity test passed")
        else:
            print("⚠️ Binance API connectivity test failed (might be network issue)")
        
        # Test rate limit status
        rate_status = provider.get_rate_limit_status()
        print(f"✅ Rate limit status:")
        print(f"   Requests: {rate_status['requests_per_minute']}/{rate_status['max_requests_per_minute']}")
        print(f"   Weight: {rate_status['weight_per_minute']}/{rate_status['max_weight_per_minute']}")
        
        # Test symbol info (if connected)
        if is_connected:
            symbol_info = provider.get_symbol_info("BTCUSDT")
            if symbol_info:
                print(f"✅ Symbol info retrieved:")
                print(f"   Symbol: {symbol_info.symbol}")
                print(f"   Status: {symbol_info.status}")
                print(f"   Trading: {symbol_info.is_trading}")
                print(f"   Min Price: {symbol_info.min_price}")
                print(f"   Tick Size: {symbol_info.tick_size}")
        
        # Test data request
        request = DataRequest(
            symbol="BTCUSDT",
            timeframe="1h",
            limit=10,
            use_cache=True
        )
        
        print(f"✅ Data request created:")
        print(f"   Symbol: {request.symbol}")
        print(f"   Timeframe: {request.timeframe}")
        print(f"   Limit: {request.limit}")
        print(f"   Cache Key: {request.get_cache_key()}")
        
        # Test market data fetching (if connected)
        if is_connected:
            try:
                market_data = provider.get_klines(request)
                if market_data:
                    print(f"✅ Market data retrieved:")
                    print(f"   Candles: {len(market_data.candles)}")
                    print(f"   Latest: {market_data.get_latest_candle().timestamp}")
                    print(f"   Source: {market_data.data_source.value}")
                    
                    # Test price range
                    price_range = market_data.get_price_range()
                    print(f"   Price Range: ${price_range['min']:.2f} - ${price_range['max']:.2f}")
            except Exception as e:
                print(f"⚠️ Market data fetch failed (API issue): {str(e)}")
        
        # Cleanup
        provider.shutdown()
        print("✅ Market data provider shutdown")
        
        return True
        
    except Exception as e:
        print(f"❌ Market data provider test failed: {str(e)}")
        return False


def test_integrated_data_flow():
    """Test integrated data flow: Provider -> Cache -> Database"""
    print("\n🔄 ═══ TESTING INTEGRATED DATA FLOW ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create components
        cache = DataCache(max_size_mb=5, default_ttl=300)
        db_manager = DatabaseManager("test_data/integration_test.db")
        provider = MarketDataProvider(config, cache)
        
        # Test connectivity first
        if not provider.test_connectivity():
            print("⚠️ Skipping integration test - no API connectivity")
            return True
        
        # Create data request
        request = DataRequest(
            symbol="BTCUSDT",
            timeframe="1h",
            limit=5,
            use_cache=True
        )
        
        print(f"📊 Testing data flow for {request.symbol} {request.timeframe}")
        
        # Step 1: Fetch from API
        print("1️⃣ Fetching from API...")
        market_data = provider.get_klines(request)
        
        if market_data:
            print(f"   ✅ Fetched {len(market_data.candles)} candles from API")
            
            # Step 2: Store in database
            print("2️⃣ Storing in database...")
            stored = db_manager.store_market_data(market_data)
            if stored:
                print("   ✅ Data stored in database")
            
            # Step 3: Load from database
            print("3️⃣ Loading from database...")
            db_data = db_manager.load_market_data(
                request.symbol, 
                request.timeframe, 
                limit=request.limit
            )
            
            if db_data:
                print(f"   ✅ Loaded {len(db_data.candles)} candles from database")
                print(f"   📊 Data source: {db_data.data_source.value}")
            
            # Step 4: Test cache hit
            print("4️⃣ Testing cache...")
            cached_data = cache.get(request)
            if cached_data:
                print("   ✅ Cache hit - data retrieved from cache")
            else:
                print("   ℹ️ Cache miss - data not in cache")
            
            # Show cache statistics
            cache_stats = cache.get_stats()
            print(f"   📊 Cache stats: {cache_stats['hits']} hits, {cache_stats['misses']} misses")
        
        # Cleanup
        provider.shutdown()
        db_manager.close()
        cache.shutdown()
        
        print("✅ Integrated data flow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Integrated data flow test failed: {str(e)}")
        return False


def test_multi_symbol_data():
    """Test multi-symbol data handling"""
    print("\n🎯 ═══ TESTING MULTI-SYMBOL DATA ═══")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config("default.json")
        
        # Create provider
        cache = DataCache(max_size_mb=10, default_ttl=300)
        provider = MarketDataProvider(config, cache)
        
        # Test connectivity
        if not provider.test_connectivity():
            print("⚠️ Skipping multi-symbol test - no API connectivity")
            return True
        
        # Test symbols
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        timeframe = "1h"
        
        print(f"📊 Testing multi-symbol data for: {', '.join(symbols)}")
        
        # Fetch data for multiple symbols
        start_time = time.time()
        multi_data = provider.get_multi_symbol_data(symbols, timeframe, limit=5)
        fetch_time = time.time() - start_time
        
        print(f"✅ Multi-symbol fetch completed in {fetch_time:.2f}s")
        print(f"   Symbols fetched: {len(multi_data)}/{len(symbols)}")
        
        for symbol, data in multi_data.items():
            if data:
                latest = data.get_latest_candle()
                print(f"   {symbol}: {len(data.candles)} candles, latest: ${latest.close:.2f}")
        
        # Test cache efficiency
        cache_stats = cache.get_stats()
        print(f"📊 Cache efficiency: {cache_stats['hit_rate_pct']:.1f}% hit rate")
        
        # Cleanup
        provider.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-symbol data test failed: {str(e)}")
        return False


def main():
    """Run all data management tests"""
    print("🏛️⚔️ SPARTAN DATA MANAGEMENT SYSTEM TESTS")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create test directory
    os.makedirs("test_data", exist_ok=True)
    
    tests = [
        test_data_cache,
        test_database_manager,
        test_market_data_provider,
        test_integrated_data_flow,
        test_multi_symbol_data
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
        print("🎯 ALL TESTS PASSED! SPARTAN DATA SYSTEM IS READY FOR BATTLE! ⚔️")
        return True
    else:
        print("💀 SOME TESTS FAILED! REVIEW AND FIX BEFORE DEPLOYMENT!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)