"""
SQLite Trade Logger - Spartan Trading System
Reliable database storage for all trade data
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class SQLiteTradeLogger:
    """
    SQLite Trade Logger - 100% Reliable
    
    Stores all trade data in SQLite database with:
    - Symbol, side, timeframe
    - Entry/exit times and prices
    - Stop loss, take profit
    - PnL calculations
    - Market conditions (TM color, squeeze)
    - All data we agreed on
    """
    
    def __init__(self, db_path: str = "trade_logs/spartan_trades.db"):
        """Initialize SQLite Trade Logger"""
        self.logger = logging.getLogger("SQLiteTradeLogger")
        self.db_path = Path(db_path)
        
        # Create directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Session stats cache
        self.session_trades = []
        
        self.logger.info(f"📊 SQLite Trade Logger initialized - DB: {self.db_path}")
    
    def _init_database(self):
        """Create trades table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        
                        -- Basic trade info
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        
                        -- Timing
                        entry_time TEXT NOT NULL,
                        exit_time TEXT NOT NULL,
                        duration_minutes REAL NOT NULL,
                        
                        -- Prices
                        entry_price REAL NOT NULL,
                        exit_price REAL NOT NULL,
                        stop_loss REAL NOT NULL,
                        take_profit REAL NOT NULL,
                        trend_magic_value REAL NOT NULL,
                        
                        -- Position details
                        quantity REAL NOT NULL,
                        position_value REAL NOT NULL,
                        
                        -- PnL
                        gross_pnl REAL NOT NULL,
                        real_pnl REAL NOT NULL,
                        pnl_percentage REAL NOT NULL,
                        total_commissions REAL NOT NULL,
                        
                        -- Trade outcome
                        close_reason TEXT NOT NULL,
                        is_winner INTEGER NOT NULL,
                        
                        -- Market conditions
                        trend_magic_color TEXT NOT NULL,
                        squeeze_momentum TEXT NOT NULL,
                        
                        -- Additional analysis
                        price_change_pct REAL NOT NULL,
                        risk_reward_ratio REAL NOT NULL,
                        
                        -- Metadata
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON trades(symbol)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_timeframe ON trades(timeframe)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_entry_time ON trades(entry_time)')
                
                conn.commit()
                
            print(f"🔥 SQLite database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"🔥 Database init error: {e}")
            raise
    
    def log_trade(self, closed_trade, timeframe: str, trend_magic_value: float = 0.0, 
                  trend_magic_color: str = "UNKNOWN", squeeze_momentum: str = "UNKNOWN") -> bool:
        """Log trade to SQLite database"""
        try:
            print(f"🔥 SQLITE: Logging {closed_trade.symbol} {closed_trade.side.value}")
            
            # Calculate additional metrics
            duration = (closed_trade.exit_time - closed_trade.entry_time).total_seconds() / 60
            position_value = closed_trade.entry_price * closed_trade.quantity
            pnl_percentage = (closed_trade.real_pnl / position_value) * 100
            
            # Calculate price change percentage
            if closed_trade.side.value == 'LONG':
                price_change_pct = ((closed_trade.exit_price - closed_trade.entry_price) / closed_trade.entry_price) * 100
            else:
                price_change_pct = ((closed_trade.entry_price - closed_trade.exit_price) / closed_trade.entry_price) * 100
            
            # Calculate risk/reward ratio
            if closed_trade.side.value == 'LONG':
                risk = closed_trade.entry_price - closed_trade.stop_loss
                reward = closed_trade.take_profit - closed_trade.entry_price
            else:
                risk = closed_trade.stop_loss - closed_trade.entry_price
                reward = closed_trade.entry_price - closed_trade.take_profit
            
            risk_reward_ratio = (reward / risk) if risk > 0 else 0.0
            
            # Insert into database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO trades (
                        symbol, side, timeframe,
                        entry_time, exit_time, duration_minutes,
                        entry_price, exit_price, stop_loss, take_profit, trend_magic_value,
                        quantity, position_value,
                        gross_pnl, real_pnl, pnl_percentage, total_commissions,
                        close_reason, is_winner,
                        trend_magic_color, squeeze_momentum,
                        price_change_pct, risk_reward_ratio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    closed_trade.symbol,
                    closed_trade.side.value,
                    timeframe,
                    closed_trade.entry_time.isoformat(),
                    closed_trade.exit_time.isoformat(),
                    round(duration, 3),
                    round(closed_trade.entry_price, 3),
                    round(closed_trade.exit_price, 3),
                    round(closed_trade.stop_loss, 3),
                    round(closed_trade.take_profit, 3),
                    round(trend_magic_value, 3),
                    round(closed_trade.quantity, 6),
                    round(position_value, 3),
                    round(closed_trade.gross_pnl, 3),
                    round(closed_trade.real_pnl, 3),
                    round(pnl_percentage, 3),
                    round(closed_trade.total_commissions, 3),
                    closed_trade.close_reason.value,
                    1 if closed_trade.is_winner else 0,
                    trend_magic_color,
                    squeeze_momentum,
                    round(price_change_pct, 3),
                    round(risk_reward_ratio, 3)
                ))
                conn.commit()
            
            # Add to session cache
            self.session_trades.append({
                'symbol': closed_trade.symbol,
                'side': closed_trade.side.value,
                'real_pnl': closed_trade.real_pnl,
                'is_winner': closed_trade.is_winner
            })
            
            print(f"🔥 SQLITE: Trade saved successfully")
            return True
            
        except Exception as e:
            print(f"🔥 SQLITE ERROR: {str(e)}")
            self.logger.error(f"💀 Failed to log trade: {str(e)}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        if not self.session_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0
            }
        
        winning_trades = [t for t in self.session_trades if t['is_winner']]
        total_pnl = sum(t['real_pnl'] for t in self.session_trades)
        win_rate = (len(winning_trades) / len(self.session_trades)) * 100
        
        return {
            'total_trades': len(self.session_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(self.session_trades) - len(winning_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(self.session_trades),
            'best_trade': max(t['real_pnl'] for t in self.session_trades),
            'worst_trade': min(t['real_pnl'] for t in self.session_trades),
        }
    
    def get_trades_by_timeframe(self, timeframe: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get trades for specific timeframe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Return rows as dictionaries
                
                query = "SELECT * FROM trades WHERE timeframe = ? ORDER BY entry_time DESC"
                params = [timeframe]
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                trades = [dict(row) for row in cursor.fetchall()]
                
            return trades
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get trades: {str(e)}")
            return []
    
    def get_timeframe_summary(self, timeframe: str) -> Dict[str, Any]:
        """Get summary statistics for a timeframe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic stats
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN is_winner = 1 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(real_pnl) as total_pnl,
                        AVG(real_pnl) as avg_pnl,
                        MAX(real_pnl) as best_trade,
                        MIN(real_pnl) as worst_trade,
                        AVG(duration_minutes) as avg_duration
                    FROM trades 
                    WHERE timeframe = ?
                ''', [timeframe])
                
                stats = cursor.fetchone()
                
                if stats[0] == 0:  # No trades
                    return {'timeframe': timeframe, 'total_trades': 0}
                
                # Get symbol performance
                cursor = conn.execute('''
                    SELECT 
                        symbol,
                        COUNT(*) as trades,
                        SUM(real_pnl) as pnl,
                        SUM(CASE WHEN is_winner = 1 THEN 1 ELSE 0 END) as wins
                    FROM trades 
                    WHERE timeframe = ?
                    GROUP BY symbol
                    ORDER BY pnl DESC
                ''', [timeframe])
                
                symbol_stats = {}
                for row in cursor.fetchall():
                    symbol_stats[row[0]] = {
                        'trades': row[1],
                        'pnl': row[2],
                        'wins': row[3]
                    }
                
                win_rate = (stats[1] / stats[0]) * 100 if stats[0] > 0 else 0
                
                return {
                    'timeframe': timeframe,
                    'total_trades': stats[0],
                    'winning_trades': stats[1],
                    'losing_trades': stats[0] - stats[1],
                    'win_rate': win_rate,
                    'total_pnl': stats[2] or 0,
                    'avg_pnl_per_trade': stats[3] or 0,
                    'best_trade': stats[4] or 0,
                    'worst_trade': stats[5] or 0,
                    'avg_duration_minutes': stats[6] or 0,
                    'symbol_performance': symbol_stats
                }
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get timeframe summary: {str(e)}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def export_to_csv(self, timeframe: str, output_file: str) -> bool:
        """Export trades to CSV"""
        try:
            trades = self.get_trades_by_timeframe(timeframe)
            
            if not trades:
                print(f"No trades found for {timeframe}")
                return False
            
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if trades:
                    fieldnames = trades[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(trades)
            
            print(f"📊 Exported {len(trades)} trades to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to export CSV: {str(e)}")
            return False
    
    def get_all_timeframes(self) -> List[str]:
        """Get list of all timeframes with trades"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT DISTINCT timeframe FROM trades ORDER BY timeframe')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"💀 Failed to get timeframes: {str(e)}")
            return []
    
    def get_all_trades(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get ALL trades from all timeframes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM trades ORDER BY entry_time DESC"
                params = []
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                trades = [dict(row) for row in cursor.fetchall()]
                
            return trades
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get all trades: {str(e)}")
            return []
    
    def get_total_summary(self) -> Dict[str, Any]:
        """Get total summary across ALL timeframes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get overall stats
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN is_winner = 1 THEN 1 ELSE 0 END) as winning_trades,
                        SUM(real_pnl) as total_pnl,
                        AVG(real_pnl) as avg_pnl,
                        MAX(real_pnl) as best_trade,
                        MIN(real_pnl) as worst_trade,
                        AVG(duration_minutes) as avg_duration
                    FROM trades
                ''')
                
                stats = cursor.fetchone()
                
                if stats[0] == 0:
                    return {'total_trades': 0}
                
                # Get stats by timeframe
                cursor = conn.execute('''
                    SELECT 
                        timeframe,
                        COUNT(*) as trades,
                        SUM(real_pnl) as pnl,
                        SUM(CASE WHEN is_winner = 1 THEN 1 ELSE 0 END) as wins
                    FROM trades 
                    GROUP BY timeframe
                    ORDER BY pnl DESC
                ''')
                
                timeframe_stats = {}
                for row in cursor.fetchall():
                    win_rate = (row[3] / row[1]) * 100 if row[1] > 0 else 0
                    timeframe_stats[row[0]] = {
                        'trades': row[1],
                        'pnl': row[2],
                        'wins': row[3],
                        'win_rate': win_rate
                    }
                
                win_rate = (stats[1] / stats[0]) * 100 if stats[0] > 0 else 0
                
                return {
                    'total_trades': stats[0],
                    'winning_trades': stats[1],
                    'losing_trades': stats[0] - stats[1],
                    'win_rate': win_rate,
                    'total_pnl': stats[2] or 0,
                    'avg_pnl_per_trade': stats[3] or 0,
                    'best_trade': stats[4] or 0,
                    'worst_trade': stats[5] or 0,
                    'avg_duration_minutes': stats[6] or 0,
                    'timeframe_breakdown': timeframe_stats
                }
                
        except Exception as e:
            self.logger.error(f"💀 Failed to get total summary: {str(e)}")
            return {'error': str(e)}