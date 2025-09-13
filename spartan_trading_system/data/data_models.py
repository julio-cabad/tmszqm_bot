"""
Data Models for Spartan Trading System
Standardized data structures for market data and analysis
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import pandas as pd


class TimeFrame(Enum):
    """Supported timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class DataSource(Enum):
    """Data source providers"""
    BINANCE = "binance"
    CACHE = "cache"
    DATABASE = "database"


@dataclass
class CandleData:
    """Single candlestick data point"""
    symbol: str
    timestamp: datetime
    timeframe: str
    
    # OHLCV data
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    # Additional data
    quote_volume: float = 0.0
    trades_count: int = 0
    taker_buy_base_volume: float = 0.0
    taker_buy_quote_volume: float = 0.0
    
    # Data source tracking
    source: DataSource = DataSource.BINANCE
    fetched_at: datetime = None
    
    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'timeframe': self.timeframe,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'quote_volume': self.quote_volume,
            'trades_count': self.trades_count,
            'taker_buy_base_volume': self.taker_buy_base_volume,
            'taker_buy_quote_volume': self.taker_buy_quote_volume,
            'source': self.source.value,
            'fetched_at': self.fetched_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandleData':
        """Create from dictionary"""
        return cls(
            symbol=data['symbol'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            timeframe=data['timeframe'],
            open=float(data['open']),
            high=float(data['high']),
            low=float(data['low']),
            close=float(data['close']),
            volume=float(data['volume']),
            quote_volume=float(data.get('quote_volume', 0.0)),
            trades_count=int(data.get('trades_count', 0)),
            taker_buy_base_volume=float(data.get('taker_buy_base_volume', 0.0)),
            taker_buy_quote_volume=float(data.get('taker_buy_quote_volume', 0.0)),
            source=DataSource(data.get('source', 'binance')),
            fetched_at=datetime.fromisoformat(data['fetched_at'])
        )


@dataclass
class MarketData:
    """Complete market data for a symbol and timeframe"""
    symbol: str
    timeframe: str
    candles: List[CandleData]
    
    # Metadata
    last_update: datetime
    data_source: DataSource
    is_complete: bool = True
    missing_periods: List[datetime] = None
    
    def __post_init__(self):
        if self.missing_periods is None:
            self.missing_periods = []
        
        # Sort candles by timestamp
        self.candles.sort(key=lambda x: x.timestamp)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis"""
        if not self.candles:
            return pd.DataFrame()
        
        data = []
        for candle in self.candles:
            data.append({
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def get_latest_candle(self) -> Optional[CandleData]:
        """Get the most recent candle"""
        return self.candles[-1] if self.candles else None
    
    def get_candles_since(self, since: datetime) -> List[CandleData]:
        """Get candles since a specific timestamp"""
        return [candle for candle in self.candles if candle.timestamp >= since]
    
    def add_candle(self, candle: CandleData) -> None:
        """Add a new candle and maintain sorting"""
        self.candles.append(candle)
        self.candles.sort(key=lambda x: x.timestamp)
        self.last_update = datetime.now()
    
    def get_price_range(self) -> Dict[str, float]:
        """Get price range statistics"""
        if not self.candles:
            return {'min': 0.0, 'max': 0.0, 'range': 0.0}
        
        prices = [candle.close for candle in self.candles]
        min_price = min(prices)
        max_price = max(prices)
        
        return {
            'min': min_price,
            'max': max_price,
            'range': max_price - min_price,
            'current': prices[-1]
        }


@dataclass
class SymbolInfo:
    """Symbol information and metadata"""
    symbol: str
    base_asset: str
    quote_asset: str
    
    # Trading info
    status: str
    is_trading: bool
    
    # Price precision
    price_precision: int
    quantity_precision: int
    base_precision: int
    quote_precision: int
    
    # Filters
    min_price: float
    max_price: float
    tick_size: float
    min_qty: float
    max_qty: float
    step_size: float
    min_notional: float
    
    # Market data
    last_price: float = 0.0
    price_change_24h: float = 0.0
    price_change_percent_24h: float = 0.0
    volume_24h: float = 0.0
    
    # Metadata
    last_update: datetime = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'base_asset': self.base_asset,
            'quote_asset': self.quote_asset,
            'status': self.status,
            'is_trading': self.is_trading,
            'price_precision': self.price_precision,
            'quantity_precision': self.quantity_precision,
            'base_precision': self.base_precision,
            'quote_precision': self.quote_precision,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'tick_size': self.tick_size,
            'min_qty': self.min_qty,
            'max_qty': self.max_qty,
            'step_size': self.step_size,
            'min_notional': self.min_notional,
            'last_price': self.last_price,
            'price_change_24h': self.price_change_24h,
            'price_change_percent_24h': self.price_change_percent_24h,
            'volume_24h': self.volume_24h,
            'last_update': self.last_update.isoformat()
        }
    
    def is_valid_price(self, price: float) -> bool:
        """Check if price is within valid range"""
        return self.min_price <= price <= self.max_price
    
    def is_valid_quantity(self, quantity: float) -> bool:
        """Check if quantity is within valid range"""
        return self.min_qty <= quantity <= self.max_qty
    
    def round_price(self, price: float) -> float:
        """Round price to valid tick size"""
        return round(price / self.tick_size) * self.tick_size
    
    def round_quantity(self, quantity: float) -> float:
        """Round quantity to valid step size"""
        return round(quantity / self.step_size) * self.step_size


@dataclass
class DataRequest:
    """Data request specification"""
    symbol: str
    timeframe: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 1000
    
    # Request options
    use_cache: bool = True
    cache_timeout: int = 300  # 5 minutes
    force_refresh: bool = False
    
    # Validation
    validate_data: bool = True
    fill_missing: bool = False
    
    def __post_init__(self):
        if self.end_time is None:
            self.end_time = datetime.now()
        
        if self.start_time is None:
            # Default to 1000 periods back
            from datetime import timedelta
            timeframe_minutes = self._get_timeframe_minutes()
            self.start_time = self.end_time - timedelta(minutes=timeframe_minutes * self.limit)
    
    def _get_timeframe_minutes(self) -> int:
        """Get timeframe in minutes"""
        timeframe_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }
        return timeframe_map.get(self.timeframe, 60)
    
    def get_cache_key(self) -> str:
        """Generate cache key for this request"""
        start_str = self.start_time.strftime('%Y%m%d_%H%M') if self.start_time else 'none'
        end_str = self.end_time.strftime('%Y%m%d_%H%M') if self.end_time else 'none'
        return f"{self.symbol}_{self.timeframe}_{start_str}_{end_str}_{self.limit}"


@dataclass
class DataQuality:
    """Data quality metrics"""
    symbol: str
    timeframe: str
    
    # Completeness
    total_expected: int
    total_received: int
    completeness_ratio: float
    
    # Missing data
    missing_periods: List[datetime]
    gaps_count: int
    largest_gap_minutes: int
    
    # Data validation
    invalid_candles: int
    duplicate_candles: int
    out_of_order_candles: int
    
    # Freshness
    latest_timestamp: datetime
    data_age_minutes: float
    is_stale: bool
    
    # Quality score (0.0 to 1.0)
    quality_score: float
    
    def __post_init__(self):
        # Calculate quality score
        completeness_weight = 0.4
        freshness_weight = 0.3
        validity_weight = 0.3
        
        completeness_score = self.completeness_ratio
        freshness_score = 1.0 if not self.is_stale else max(0.0, 1.0 - (self.data_age_minutes / 60.0))
        validity_score = 1.0 - ((self.invalid_candles + self.duplicate_candles) / max(1, self.total_received))
        
        self.quality_score = (
            completeness_score * completeness_weight +
            freshness_score * freshness_weight +
            validity_score * validity_weight
        )
    
    def get_quality_rating(self) -> str:
        """Get human-readable quality rating"""
        if self.quality_score >= 0.9:
            return "EXCELLENT"
        elif self.quality_score >= 0.8:
            return "GOOD"
        elif self.quality_score >= 0.7:
            return "FAIR"
        elif self.quality_score >= 0.6:
            return "POOR"
        else:
            return "CRITICAL"
    
    def get_issues(self) -> List[str]:
        """Get list of data quality issues"""
        issues = []
        
        if self.completeness_ratio < 0.95:
            issues.append(f"Data incomplete: {self.completeness_ratio:.1%} received")
        
        if self.gaps_count > 0:
            issues.append(f"{self.gaps_count} data gaps found")
        
        if self.invalid_candles > 0:
            issues.append(f"{self.invalid_candles} invalid candles")
        
        if self.duplicate_candles > 0:
            issues.append(f"{self.duplicate_candles} duplicate candles")
        
        if self.is_stale:
            issues.append(f"Data is stale ({self.data_age_minutes:.1f} minutes old)")
        
        return issues