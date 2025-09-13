"""
Database Manager for Spartan Trading System
SQLite-based persistence with performance optimization
"""

import logging
import sqlite3
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pandas as pd

from .data_models import MarketData, CandleData, SymbolInfo, DataSource


class DatabaseError(Exception):
    """Database related errors"""
    pass


class DatabaseManager:
    """
    Spartan Database Manager
    
    SQLite-based data persistence with:
    - Optimized schema for time-series data
    - Automatic indexing and partitioning
    - Data compression and cleanup
    - Thread-safe operations
    - Performance monitoring
    """
    
    def __init__(self, db_path: str = "data/spartan_trading.db"):
        """
        Initialize Database Manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.RLock()
        self._connection_pool = {}
        
        self.logger = logging.getLogger("DatabaseManager")
        
        # Initialize database
        self._initialize_database()
        
        self.logger.info(f"🏛️ Spartan Database Manager initialized: {db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        thread_id = threading.get_ident()
        
        if thread_id not in self._connection_pool:
            conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Row factory for easier data access
            conn.row_factory = sqlite3.Row
            
            self._connection_pool[thread_id] = conn
        
        return self._connection_pool[thread_id]
    
    def _initialize_database(self):
        """Initialize database schema"""
        with self._lock:
            conn = self._get_connection()
            
            # Create tables
            self._create_tables(conn)
            
            # Create indexes
            self._create_indexes(conn)
            
            conn.commit()
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables"""
        
        # Market data table (partitioned by symbol and timeframe)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                quote_volume REAL DEFAULT 0,
                trades_count INTEGER DEFAULT 0,
                taker_buy_base_volume REAL DEFAULT 0,
                taker_buy_quote_volume REAL DEFAULT 0,
                source TEXT DEFAULT 'binance',
                fetched_at INTEGER NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                UNIQUE(symbol, timeframe, timestamp)
            )
        """)
        
        # Symbol information table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS symbol_info (
                symbol TEXT PRIMARY KEY,
                base_asset TEXT NOT NULL,
                quote_asset TEXT NOT NULL,
                status TEXT NOT NULL,
                is_trading BOOLEAN NOT NULL,
                price_precision INTEGER NOT NULL,
                quantity_precision INTEGER NOT NULL,
                base_precision INTEGER NOT NULL,
                quote_precision INTEGER NOT NULL,
                min_price REAL NOT NULL,
                max_price REAL NOT NULL,
                tick_size REAL NOT NULL,
                min_qty REAL NOT NULL,
                max_qty REAL NOT NULL,
                step_size REAL NOT NULL,
                min_notional REAL NOT NULL,
                last_price REAL DEFAULT 0,
                price_change_24h REAL DEFAULT 0,
                price_change_percent_24h REAL DEFAULT 0,
                volume_24h REAL DEFAULT 0,
                last_update INTEGER NOT NULL
            )
        """)
        
        # Trading signals table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                signal_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                strength REAL NOT NULL,
                confidence REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit_levels TEXT,  -- JSON array
                position_size_pct REAL NOT NULL,
                trend_magic_value REAL NOT NULL,
                trend_magic_color TEXT NOT NULL,
                squeeze_status TEXT NOT NULL,
                momentum_color TEXT NOT NULL,
                momentum_value REAL NOT NULL,
                timeframe TEXT NOT NULL,
                context_timeframe_trend TEXT NOT NULL,
                confirmation_timeframe_trend TEXT NOT NULL,
                timeframes_aligned BOOLEAN NOT NULL,
                trigger_reason TEXT NOT NULL,
                supporting_factors TEXT,  -- JSON array
                risk_factors TEXT,        -- JSON array
                created_by TEXT DEFAULT 'SpartanSignalGenerator',
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Performance tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                date TEXT NOT NULL,  -- YYYY-MM-DD format
                signals_generated INTEGER DEFAULT 0,
                signals_executed INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_win REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                UNIQUE(symbol, timeframe, date)
            )
        """)
        
        # System logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                level TEXT NOT NULL,
                logger TEXT NOT NULL,
                message TEXT NOT NULL,
                extra_data TEXT,  -- JSON
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance"""
        
        indexes = [
            # Market data indexes
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timeframe ON market_data(symbol, timeframe)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp)",
            
            # Trading signals indexes
            "CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON trading_signals(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_signals_type ON trading_signals(signal_type)",
            
            # Performance metrics indexes
            "CREATE INDEX IF NOT EXISTS idx_performance_symbol_date ON performance_metrics(symbol, date)",
            "CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)",
            
            # System logs indexes
            "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)    

    def store_market_data(self, market_data: MarketData) -> bool:
        """
        Store market data in database
        
        Args:
            market_data: MarketData to store
            
        Returns:
            True if successful
        """
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Prepare data for bulk insert
                data_rows = []
                for candle in market_data.candles:
                    data_rows.append((
                        candle.symbol,
                        candle.timeframe,
                        int(candle.timestamp.timestamp()),
                        candle.open,
                        candle.high,
                        candle.low,
                        candle.close,
                        candle.volume,
                        candle.quote_volume,
                        candle.trades_count,
                        candle.taker_buy_base_volume,
                        candle.taker_buy_quote_volume,
                        candle.source.value,
                        int(candle.fetched_at.timestamp())
                    ))
                
                # Bulk insert with conflict resolution
                conn.executemany("""
                    INSERT OR REPLACE INTO market_data (
                        symbol, timeframe, timestamp, open, high, low, close, volume,
                        quote_volume, trades_count, taker_buy_base_volume, 
                        taker_buy_quote_volume, source, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data_rows)
                
                conn.commit()
                
                self.logger.debug(f"💾 Stored {len(data_rows)} candles for {market_data.symbol}")
                return True
                
        except Exception as e:
            self.logger.error(f"💀 Failed to store market data: {str(e)}")
            return False
    
    def load_market_data(self, symbol: str, timeframe: str, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: Optional[int] = None) -> Optional[MarketData]:
        """
        Load market data from database
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            start_time: Start time (optional)
            end_time: End time (optional)
            limit: Maximum number of candles (optional)
            
        Returns:
            MarketData or None if not found
        """
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Build query
                query = """
                    SELECT * FROM market_data 
                    WHERE symbol = ? AND timeframe = ?
                """
                params = [symbol, timeframe]
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(int(start_time.timestamp()))
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(int(end_time.timestamp()))
                
                query += " ORDER BY timestamp ASC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                # Execute query
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Convert to CandleData objects
                candles = []
                for row in rows:
                    candle = CandleData(
                        symbol=row['symbol'],
                        timestamp=datetime.fromtimestamp(row['timestamp']),
                        timeframe=row['timeframe'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['volume'],
                        quote_volume=row['quote_volume'],
                        trades_count=row['trades_count'],
                        taker_buy_base_volume=row['taker_buy_base_volume'],
                        taker_buy_quote_volume=row['taker_buy_quote_volume'],
                        source=DataSource(row['source']),
                        fetched_at=datetime.fromtimestamp(row['fetched_at'])
                    )
                    candles.append(candle)
                
                # Create MarketData
                market_data = MarketData(
                    symbol=symbol,
                    timeframe=timeframe,
                    candles=candles,
                    last_update=datetime.now(),
                    data_source=DataSource.DATABASE
                )
                
                self.logger.debug(f"📊 Loaded {len(candles)} candles for {symbol} {timeframe}")
                return market_data
                
        except Exception as e:
            self.logger.error(f"💀 Failed to load market data: {str(e)}")
            return None
    
    def store_symbol_info(self, symbol_info: SymbolInfo) -> bool:
        """Store symbol information"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                conn.execute("""
                    INSERT OR REPLACE INTO symbol_info (
                        symbol, base_asset, quote_asset, status, is_trading,
                        price_precision, quantity_precision, base_precision, quote_precision,
                        min_price, max_price, tick_size, min_qty, max_qty, step_size, min_notional,
                        last_price, price_change_24h, price_change_percent_24h, volume_24h, last_update
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol_info.symbol, symbol_info.base_asset, symbol_info.quote_asset,
                    symbol_info.status, symbol_info.is_trading,
                    symbol_info.price_precision, symbol_info.quantity_precision,
                    symbol_info.base_precision, symbol_info.quote_precision,
                    symbol_info.min_price, symbol_info.max_price, symbol_info.tick_size,
                    symbol_info.min_qty, symbol_info.max_qty, symbol_info.step_size, symbol_info.min_notional,
                    symbol_info.last_price, symbol_info.price_change_24h,
                    symbol_info.price_change_percent_24h, symbol_info.volume_24h,
                    int(symbol_info.last_update.timestamp())
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"💀 Failed to store symbol info: {str(e)}")
            return False
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols in database"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                cursor = conn.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol")
                rows = cursor.fetchall()
                
                return [row['symbol'] for row in rows]
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get available symbols: {str(e)}")
            return []
    
    def get_available_timeframes(self, symbol: str) -> List[str]:
        """Get available timeframes for a symbol"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                cursor = conn.execute(
                    "SELECT DISTINCT timeframe FROM market_data WHERE symbol = ? ORDER BY timeframe",
                    (symbol,)
                )
                rows = cursor.fetchall()
                
                return [row['timeframe'] for row in rows]
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get available timeframes: {str(e)}")
            return []
    
    def get_data_range(self, symbol: str, timeframe: str) -> Optional[Tuple[datetime, datetime]]:
        """Get data range (first and last timestamp) for symbol/timeframe"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                cursor = conn.execute("""
                    SELECT MIN(timestamp) as first_ts, MAX(timestamp) as last_ts
                    FROM market_data 
                    WHERE symbol = ? AND timeframe = ?
                """, (symbol, timeframe))
                
                row = cursor.fetchone()
                if row and row['first_ts'] and row['last_ts']:
                    return (
                        datetime.fromtimestamp(row['first_ts']),
                        datetime.fromtimestamp(row['last_ts'])
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get data range: {str(e)}")
            return None  
  
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Clean up old data to save space
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Number of records deleted
        """
        try:
            with self._lock:
                conn = self._get_connection()
                
                cutoff_timestamp = int((datetime.now() - timedelta(days=days_to_keep)).timestamp())
                
                # Delete old market data
                cursor = conn.execute(
                    "DELETE FROM market_data WHERE timestamp < ?",
                    (cutoff_timestamp,)
                )
                deleted_market_data = cursor.rowcount
                
                # Delete old signals
                cursor = conn.execute(
                    "DELETE FROM trading_signals WHERE timestamp < ?",
                    (cutoff_timestamp,)
                )
                deleted_signals = cursor.rowcount
                
                # Delete old logs
                cursor = conn.execute(
                    "DELETE FROM system_logs WHERE timestamp < ?",
                    (cutoff_timestamp,)
                )
                deleted_logs = cursor.rowcount
                
                conn.commit()
                
                total_deleted = deleted_market_data + deleted_signals + deleted_logs
                
                # Vacuum to reclaim space
                conn.execute("VACUUM")
                
                self.logger.info(f"🧹 Cleaned up {total_deleted} old records (kept {days_to_keep} days)")
                return total_deleted
                
        except Exception as e:
            self.logger.error(f"💀 Failed to cleanup old data: {str(e)}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                stats = {}
                
                # Table sizes
                tables = ['market_data', 'symbol_info', 'trading_signals', 'performance_metrics', 'system_logs']
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()['count']
                
                # Database file size
                stats['file_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
                
                # Data range
                cursor = conn.execute("""
                    SELECT 
                        MIN(timestamp) as first_data,
                        MAX(timestamp) as last_data,
                        COUNT(DISTINCT symbol) as unique_symbols,
                        COUNT(DISTINCT timeframe) as unique_timeframes
                    FROM market_data
                """)
                row = cursor.fetchone()
                
                if row['first_data']:
                    stats['first_data'] = datetime.fromtimestamp(row['first_data']).isoformat()
                    stats['last_data'] = datetime.fromtimestamp(row['last_data']).isoformat()
                    stats['unique_symbols'] = row['unique_symbols']
                    stats['unique_timeframes'] = row['unique_timeframes']
                
                return stats
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get database stats: {str(e)}")
            return {}
    
    def export_to_csv(self, symbol: str, timeframe: str, output_path: str) -> bool:
        """Export market data to CSV file"""
        try:
            market_data = self.load_market_data(symbol, timeframe)
            if not market_data:
                return False
            
            df = market_data.to_dataframe()
            df.to_csv(output_path)
            
            self.logger.info(f"📊 Exported {len(df)} records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to export to CSV: {str(e)}")
            return False
    
    def import_from_csv(self, csv_path: str, symbol: str, timeframe: str) -> bool:
        """Import market data from CSV file"""
        try:
            df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            
            candles = []
            for timestamp, row in df.iterrows():
                candle = CandleData(
                    symbol=symbol,
                    timestamp=timestamp,
                    timeframe=timeframe,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume'],
                    source=DataSource.DATABASE
                )
                candles.append(candle)
            
            market_data = MarketData(
                symbol=symbol,
                timeframe=timeframe,
                candles=candles,
                last_update=datetime.now(),
                data_source=DataSource.DATABASE
            )
            
            return self.store_market_data(market_data)
            
        except Exception as e:
            self.logger.error(f"💀 Failed to import from CSV: {str(e)}")
            return False
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            with self._lock:
                conn = self._get_connection()
                
                # Analyze tables for query optimization
                conn.execute("ANALYZE")
                
                # Rebuild indexes
                conn.execute("REINDEX")
                
                # Update statistics
                conn.execute("PRAGMA optimize")
                
                conn.commit()
                
                self.logger.info("🔧 Database optimization complete")
                
        except Exception as e:
            self.logger.error(f"💀 Database optimization failed: {str(e)}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            
            with self._lock:
                # Close all connections
                for conn in self._connection_pool.values():
                    conn.close()
                self._connection_pool.clear()
                
                # Copy database file
                shutil.copy2(self.db_path, backup_path)
                
                self.logger.info(f"💾 Database backup created: {backup_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"💀 Database backup failed: {str(e)}")
            return False
    
    def close(self):
        """Close all database connections"""
        with self._lock:
            for conn in self._connection_pool.values():
                conn.close()
            self._connection_pool.clear()
        
        self.logger.info("🏛️ Database connections closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.close()
        except Exception:
            pass