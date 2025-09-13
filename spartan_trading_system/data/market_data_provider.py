"""
Market Data Provider for Spartan Trading System
Professional Binance integration with error handling and rate limiting
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.strategy_config import StrategyConfig
from .data_models import MarketData, CandleData, SymbolInfo, DataRequest, DataSource, DataQuality
from .data_cache import DataCache


class BinanceAPIError(Exception):
    """Binance API related errors"""
    pass


class RateLimitError(Exception):
    """Rate limit exceeded error"""
    pass


class MarketDataProvider:
    """
    Spartan Market Data Provider
    
    Professional Binance integration with:
    - Rate limiting and retry logic
    - Data caching and optimization
    - Multi-timeframe support
    - Error handling and recovery
    - Data quality validation
    """
    
    def __init__(self, config: StrategyConfig, cache: Optional[DataCache] = None):
        """
        Initialize Market Data Provider
        
        Args:
            config: Strategy configuration
            cache: Data cache instance (creates new if None)
        """
        self.config = config
        self.cache = cache or DataCache()
        
        # Binance API configuration
        self.base_url = "https://api.binance.com"
        self.api_key = getattr(config, 'binance_api_key', None)
        self.api_secret = getattr(config, 'binance_api_secret', None)
        
        # Rate limiting
        self.rate_limit_requests_per_minute = 1200  # Binance limit
        self.rate_limit_weight_per_minute = 6000    # Binance weight limit
        self.request_timestamps = []
        self.weight_usage = []
        
        # Session with retry strategy
        self.session = self._create_session()
        
        # Symbol information cache
        self.symbol_info_cache: Dict[str, SymbolInfo] = {}
        self.symbol_info_last_update = None
        
        self.logger = logging.getLogger("MarketDataProvider")
        self.logger.info("🏛️ Spartan Market Data Provider initialized")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers
        session.headers.update({
            'User-Agent': 'SpartanTradingSystem/1.0',
            'Content-Type': 'application/json'
        })
        
        return session    

    def _check_rate_limit(self, weight: int = 1):
        """Check and enforce rate limits"""
        now = time.time()
        
        # Clean old timestamps (older than 1 minute)
        cutoff = now - 60
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]
        self.weight_usage = [(ts, w) for ts, w in self.weight_usage if ts > cutoff]
        
        # Check request rate limit
        if len(self.request_timestamps) >= self.rate_limit_requests_per_minute:
            sleep_time = 60 - (now - self.request_timestamps[0])
            if sleep_time > 0:
                self.logger.warning(f"⏳ Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Check weight limit
        current_weight = sum(w for _, w in self.weight_usage)
        if current_weight + weight > self.rate_limit_weight_per_minute:
            sleep_time = 60 - (now - self.weight_usage[0][0])
            if sleep_time > 0:
                self.logger.warning(f"⏳ Weight limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Record this request
        self.request_timestamps.append(now)
        self.weight_usage.append((now, weight))
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, weight: int = 1) -> Dict[str, Any]:
        """Make API request with rate limiting and error handling"""
        self._check_rate_limit(weight)
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            # Check for rate limit headers
            if 'X-MBX-USED-WEIGHT-1M' in response.headers:
                used_weight = int(response.headers['X-MBX-USED-WEIGHT-1M'])
                if used_weight > self.rate_limit_weight_per_minute * 0.8:
                    self.logger.warning(f"⚠️ High API weight usage: {used_weight}")
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"⏳ Rate limited, waiting {retry_after}s")
                time.sleep(retry_after)
                raise RateLimitError("Rate limit exceeded")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"💀 API request failed: {str(e)}")
            raise BinanceAPIError(f"API request failed: {str(e)}")
    
    def get_symbol_info(self, symbol: str, force_refresh: bool = False) -> Optional[SymbolInfo]:
        """Get symbol information from Binance"""
        # Check cache first
        if not force_refresh and symbol in self.symbol_info_cache:
            info = self.symbol_info_cache[symbol]
            if (datetime.now() - info.last_update).total_seconds() < 3600:  # 1 hour cache
                return info
        
        try:
            # Get exchange info
            data = self._make_request("/api/v3/exchangeInfo", weight=10)
            
            # Find symbol
            symbol_data = None
            for s in data.get('symbols', []):
                if s['symbol'] == symbol:
                    symbol_data = s
                    break
            
            if not symbol_data:
                self.logger.warning(f"⚠️ Symbol {symbol} not found")
                return None
            
            # Parse filters
            filters = {f['filterType']: f for f in symbol_data.get('filters', [])}
            
            price_filter = filters.get('PRICE_FILTER', {})
            lot_size_filter = filters.get('LOT_SIZE', {})
            notional_filter = filters.get('NOTIONAL', {})
            
            # Create SymbolInfo
            symbol_info = SymbolInfo(
                symbol=symbol,
                base_asset=symbol_data['baseAsset'],
                quote_asset=symbol_data['quoteAsset'],
                status=symbol_data['status'],
                is_trading=symbol_data['status'] == 'TRADING',
                price_precision=symbol_data['quotePrecision'],
                quantity_precision=symbol_data['baseAssetPrecision'],
                base_precision=symbol_data['baseAssetPrecision'],
                quote_precision=symbol_data['quotePrecision'],
                min_price=float(price_filter.get('minPrice', 0)),
                max_price=float(price_filter.get('maxPrice', 999999999)),
                tick_size=float(price_filter.get('tickSize', 0.01)),
                min_qty=float(lot_size_filter.get('minQty', 0)),
                max_qty=float(lot_size_filter.get('maxQty', 999999999)),
                step_size=float(lot_size_filter.get('stepSize', 0.001)),
                min_notional=float(notional_filter.get('minNotional', 0))
            )
            
            # Cache the info
            self.symbol_info_cache[symbol] = symbol_info
            
            self.logger.debug(f"📊 Symbol info updated: {symbol}")
            return symbol_info
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get symbol info for {symbol}: {str(e)}")
            return None    

    def get_klines(self, request: DataRequest) -> Optional[MarketData]:
        """
        Get candlestick data from Binance
        
        Args:
            request: Data request specification
            
        Returns:
            MarketData with candlestick data
        """
        try:
            # Check cache first
            cached_data = self.cache.get(request)
            if cached_data:
                return cached_data
            
            # Prepare API parameters
            # Fix timeframe format for Binance API
            interval = request.timeframe
            if interval.isdigit():  # If it's just a number like "30"
                interval = f"{interval}m"  # Make it "30m"
            
            # Ensure correct format for Binance API (30m not 30min)
            if interval.endswith('min'):
                interval = interval.replace('min', 'm')
            
            params = {
                'symbol': request.symbol,
                'interval': interval,
                'limit': min(request.limit, 1000)  # Binance max is 1000
            }
            
            # Don't send timestamps - let Binance use default behavior with just limit
            # This avoids timestamp calculation errors
            
            # Use the same method as your working TechnicalAnalyzer
            self.logger.debug(f"📊 Fetching {request.symbol} {request.timeframe} data using RobotBinance")
            
            try:
                from bnb.binance import RobotBinance
                
                # Create client same as your TechnicalAnalyzer
                client = RobotBinance(pair=request.symbol, temporality=interval)
                df = client.get_historical_data(limit=params['limit'])
                
                if df is None or df.empty:
                    raise Exception(f"No data returned for {request.symbol}")
                
                # Convert DataFrame to candles
                candles = []
                for index, row in df.iterrows():
                    candle = CandleData(
                        symbol=request.symbol,
                        timestamp=index,
                        timeframe=request.timeframe,
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume'])
                    )
                    candles.append(candle)
                
            except Exception as e:
                self.logger.error(f"💀 RobotBinance failed, trying direct API: {str(e)}")
                
                # Fallback to direct API
                data = self._make_request("/api/v3/klines", params, weight=1)
                
                # Parse candlestick data
                candles = []
                for kline in data:
                    candle = CandleData(
                        symbol=request.symbol,
                        timestamp=datetime.fromtimestamp(kline[0] / 1000),
                        timeframe=request.timeframe,
                        open=float(kline[1]),
                        high=float(kline[2]),
                        low=float(kline[3]),
                        close=float(kline[4]),
                        volume=float(kline[5]),
                        quote_volume=float(kline[7]),
                        trades_count=int(kline[8]),
                        taker_buy_base_volume=float(kline[9]),
                        taker_buy_quote_volume=float(kline[10]),
                        source=DataSource.BINANCE
                    )
                    candles.append(candle)
            
            # Create MarketData
            market_data = MarketData(
                symbol=request.symbol,
                timeframe=request.timeframe,
                candles=candles,
                last_update=datetime.now(),
                data_source=DataSource.BINANCE
            )
            
            # Validate data quality if requested
            if request.validate_data:
                quality = self._validate_data_quality(market_data, request)
                if quality.quality_score < 0.7:
                    self.logger.warning(f"⚠️ Poor data quality for {request.symbol}: {quality.get_quality_rating()}")
            
            # Cache the data
            self.cache.put(request, market_data)
            
            self.logger.info(f"✅ Fetched {len(candles)} candles for {request.symbol} {request.timeframe}")
            return market_data
            
        except Exception as e:
            self.logger.error(f"💀 Failed to fetch klines for {request.symbol}: {str(e)}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        try:
            data = self._make_request("/api/v3/ticker/price", {'symbol': symbol}, weight=1)
            return float(data['price'])
        except Exception as e:
            self.logger.error(f"💀 Failed to get latest price for {symbol}: {str(e)}")
            return None
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get 24h ticker statistics"""
        try:
            data = self._make_request("/api/v3/ticker/24hr", {'symbol': symbol}, weight=1)
            return {
                'symbol': data['symbol'],
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'weighted_avg_price': float(data['weightedAvgPrice']),
                'prev_close_price': float(data['prevClosePrice']),
                'last_price': float(data['lastPrice']),
                'bid_price': float(data['bidPrice']),
                'ask_price': float(data['askPrice']),
                'open_price': float(data['openPrice']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'open_time': datetime.fromtimestamp(data['openTime'] / 1000),
                'close_time': datetime.fromtimestamp(data['closeTime'] / 1000),
                'count': int(data['count'])
            }
        except Exception as e:
            self.logger.error(f"💀 Failed to get 24h ticker for {symbol}: {str(e)}")
            return None
    
    def get_multi_symbol_data(self, symbols: List[str], timeframe: str, limit: int = 100) -> Dict[str, MarketData]:
        """
        Get data for multiple symbols efficiently
        
        Args:
            symbols: List of symbols to fetch
            timeframe: Timeframe for all symbols
            limit: Number of candles per symbol
            
        Returns:
            Dictionary mapping symbol to MarketData
        """
        results = {}
        
        for symbol in symbols:
            try:
                request = DataRequest(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit,
                    use_cache=True
                )
                
                data = self.get_klines(request)
                if data:
                    results[symbol] = data
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"💀 Failed to fetch data for {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Fetched data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def _validate_data_quality(self, market_data: MarketData, request: DataRequest) -> DataQuality:
        """Validate data quality and generate metrics"""
        candles = market_data.candles
        
        if not candles:
            return DataQuality(
                symbol=request.symbol,
                timeframe=request.timeframe,
                total_expected=request.limit,
                total_received=0,
                completeness_ratio=0.0,
                missing_periods=[],
                gaps_count=0,
                largest_gap_minutes=0,
                invalid_candles=0,
                duplicate_candles=0,
                out_of_order_candles=0,
                latest_timestamp=datetime.now(),
                data_age_minutes=0.0,
                is_stale=True,
                quality_score=0.0
            )
        
        # Calculate expected vs received
        total_received = len(candles)
        total_expected = request.limit
        completeness_ratio = min(1.0, total_received / total_expected)
        
        # Check for gaps and missing periods
        missing_periods = []
        gaps_count = 0
        largest_gap_minutes = 0
        
        if len(candles) > 1:
            timeframe_minutes = self._get_timeframe_minutes(request.timeframe)
            
            for i in range(1, len(candles)):
                prev_time = candles[i-1].timestamp
                curr_time = candles[i].timestamp
                expected_diff = timedelta(minutes=timeframe_minutes)
                actual_diff = curr_time - prev_time
                
                if actual_diff > expected_diff * 1.5:  # Allow some tolerance
                    gaps_count += 1
                    gap_minutes = int(actual_diff.total_seconds() / 60)
                    largest_gap_minutes = max(largest_gap_minutes, gap_minutes)
                    
                    # Add missing periods
                    missing_time = prev_time + expected_diff
                    while missing_time < curr_time:
                        missing_periods.append(missing_time)
                        missing_time += expected_diff
        
        # Check for invalid candles
        invalid_candles = 0
        duplicate_candles = 0
        out_of_order_candles = 0
        
        seen_timestamps = set()
        prev_timestamp = None
        
        for candle in candles:
            # Check for invalid OHLC data
            if not (candle.low <= candle.open <= candle.high and 
                   candle.low <= candle.close <= candle.high):
                invalid_candles += 1
            
            # Check for duplicates
            if candle.timestamp in seen_timestamps:
                duplicate_candles += 1
            seen_timestamps.add(candle.timestamp)
            
            # Check for out of order
            if prev_timestamp and candle.timestamp < prev_timestamp:
                out_of_order_candles += 1
            prev_timestamp = candle.timestamp
        
        # Check data freshness
        latest_timestamp = candles[-1].timestamp
        data_age_minutes = (datetime.now() - latest_timestamp).total_seconds() / 60
        is_stale = data_age_minutes > 60  # Consider stale if older than 1 hour
        
        return DataQuality(
            symbol=request.symbol,
            timeframe=request.timeframe,
            total_expected=total_expected,
            total_received=total_received,
            completeness_ratio=completeness_ratio,
            missing_periods=missing_periods,
            gaps_count=gaps_count,
            largest_gap_minutes=largest_gap_minutes,
            invalid_candles=invalid_candles,
            duplicate_candles=duplicate_candles,
            out_of_order_candles=out_of_order_candles,
            latest_timestamp=latest_timestamp,
            data_age_minutes=data_age_minutes,
            is_stale=is_stale,
            quality_score=0.0  # Will be calculated in __post_init__
        )
    
    def _get_timeframe_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
            '1d': 1440, '3d': 4320, '1w': 10080, '1M': 43200
        }
        return timeframe_map.get(timeframe, 60)
    
    def get_server_time(self) -> Optional[datetime]:
        """Get Binance server time"""
        try:
            data = self._make_request("/api/v3/time", weight=1)
            return datetime.fromtimestamp(data['serverTime'] / 1000)
        except Exception as e:
            self.logger.error(f"💀 Failed to get server time: {str(e)}")
            return None
    
    def test_connectivity(self) -> bool:
        """Test API connectivity"""
        try:
            self._make_request("/api/v3/ping", weight=1)
            self.logger.info("✅ Binance API connectivity test passed")
            return True
        except Exception as e:
            self.logger.error(f"💀 Binance API connectivity test failed: {str(e)}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        now = time.time()
        cutoff = now - 60
        
        # Clean old entries
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]
        self.weight_usage = [(ts, w) for ts, w in self.weight_usage if ts > cutoff]
        
        current_requests = len(self.request_timestamps)
        current_weight = sum(w for _, w in self.weight_usage)
        
        return {
            'requests_per_minute': current_requests,
            'max_requests_per_minute': self.rate_limit_requests_per_minute,
            'requests_utilization_pct': (current_requests / self.rate_limit_requests_per_minute * 100),
            'weight_per_minute': current_weight,
            'max_weight_per_minute': self.rate_limit_weight_per_minute,
            'weight_utilization_pct': (current_weight / self.rate_limit_weight_per_minute * 100)
        }
    
    def shutdown(self):
        """Shutdown provider and cleanup resources"""
        if self.session:
            self.session.close()
        
        if self.cache:
            self.cache.shutdown()
        
        self.logger.info("🏛️ Spartan Market Data Provider shutdown complete")