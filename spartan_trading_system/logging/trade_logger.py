"""
Trade Logger - Spartan Trading System
SIMPLIFIED VERSION - FORCE SAVE TO DISK
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

@dataclass
class TradeRecord:
    """Complete trade record for analysis"""
    # Basic trade info
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    timeframe: str
    
    # Timing
    entry_time: str
    exit_time: str
    duration_minutes: float
    
    # Prices
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    trend_magic_value: float
    
    # Position details
    quantity: float
    position_value: float
    
    # PnL
    gross_pnl: float
    real_pnl: float
    pnl_percentage: float
    total_commissions: float
    
    # Trade outcome
    close_reason: str  # 'TAKE_PROFIT', 'STOP_LOSS', 'MANUAL'
    is_winner: bool
    
    # Market conditions at entry
    trend_magic_color: str
    squeeze_momentum: str
    
    # Additional analysis data
    price_change_pct: float
    risk_reward_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class TradeLogger:
    """SIMPLIFIED Trade Logger - FORCE SAVE"""
    
    def __init__(self, base_path: str = "trade_logs"):
        """Initialize trade logger"""
        self.logger = logging.getLogger("TradeLogger")
        self.base_path = Path(base_path)
        
        # Create directory structure
        self.base_path.mkdir(exist_ok=True)
        
        # Cache for current session data
        self.session_trades: List[TradeRecord] = []
        
        self.logger.info(f"📊 Trade Logger initialized - Path: {self.base_path}")
    
    def log_trade(self, closed_trade, timeframe: str, trend_magic_value: float = 0.0, 
                  trend_magic_color: str = "UNKNOWN", squeeze_momentum: str = "UNKNOWN") -> bool:
        """FORCE LOG TRADE TO DISK"""
        try:
            print(f"🔥 STARTING TRADE LOG: {closed_trade.symbol} {closed_trade.side.value}")
            
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
            
            # Create trade record with rounded values (3 decimals)
            trade_record = TradeRecord(
                symbol=closed_trade.symbol,
                side=closed_trade.side.value,
                timeframe=timeframe,
                entry_time=closed_trade.entry_time.isoformat(),
                exit_time=closed_trade.exit_time.isoformat(),
                duration_minutes=round(duration, 3),
                entry_price=round(closed_trade.entry_price, 3),
                exit_price=round(closed_trade.exit_price, 3),
                stop_loss=round(closed_trade.stop_loss, 3),
                take_profit=round(closed_trade.take_profit, 3),
                trend_magic_value=round(trend_magic_value, 3),
                quantity=round(closed_trade.quantity, 6),  # Keep more precision for quantity
                position_value=round(position_value, 3),
                gross_pnl=round(closed_trade.gross_pnl, 3),
                real_pnl=round(closed_trade.real_pnl, 3),
                pnl_percentage=round(pnl_percentage, 3),
                total_commissions=round(closed_trade.total_commissions, 3),
                close_reason=closed_trade.close_reason.value,
                is_winner=closed_trade.is_winner,
                trend_magic_color=trend_magic_color,
                squeeze_momentum=squeeze_momentum,
                price_change_pct=round(price_change_pct, 3),
                risk_reward_ratio=round(risk_reward_ratio, 3)
            )
            
            print(f"🔥 TRADE RECORD CREATED: {trade_record.symbol}")
            
            # Add to session cache
            self.session_trades.append(trade_record)
            
            # FORCE SAVE TO FILE
            success = self._force_save_to_file(trade_record, timeframe)
            
            print(f"🔥 SAVE RESULT: {success}")
            
            return success
            
        except Exception as e:
            print(f"🔥 TRADE LOG ERROR: {str(e)}")
            self.logger.error(f"💀 Failed to log trade: {str(e)}")
            return False
    
    def _force_save_to_file(self, trade_record: TradeRecord, timeframe: str) -> bool:
        """FORCE SAVE TO FILE WITH VERIFICATION"""
        try:
            print(f"🔥 FORCE SAVE START: {timeframe}")
            
            # Create timeframe directory
            timeframe_dir = self.base_path / timeframe
            timeframe_dir.mkdir(exist_ok=True)
            
            print(f"🔥 DIRECTORY: {timeframe_dir} | EXISTS: {timeframe_dir.exists()}")
            
            # Generate filename by timeframe only (no date)
            filename = f"trades_{timeframe}.json"
            filepath = timeframe_dir / filename
            
            print(f"🔥 TARGET FILE: {filepath}")
            
            # Load existing trades or create new list
            trades = []
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        trades = json.load(f)
                    print(f"🔥 LOADED EXISTING: {len(trades)} trades")
                except json.JSONDecodeError as e:
                    print(f"🔥 CORRUPTED FILE, STARTING FRESH: {e}")
                    trades = []
            else:
                print(f"🔥 NEW FILE")
            
            # Add new trade
            trades.append(trade_record.to_dict())
            print(f"🔥 TOTAL TRADES TO SAVE: {len(trades)}")
            
            # ULTRA SIMPLE - WRITE AS TEXT FILE
            txt_filepath = timeframe_dir / f"trades_{timeframe}.txt"
            
            with open(txt_filepath, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()},{trade_record.symbol},{trade_record.side},{trade_record.real_pnl:.3f},{trade_record.close_reason}\n")
                f.flush()
                os.fsync(f.fileno())
            
            print(f"🔥 FILE WRITTEN")
            
            # VERIFY FILE EXISTS
            if not filepath.exists():
                print(f"🔥 ERROR: FILE NOT FOUND AFTER WRITE")
                return False
            
            # VERIFY FILE CONTENT
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                print(f"🔥 VERIFICATION: {len(verify_data)} trades in file")
                
                if len(verify_data) == 0:
                    print(f"🔥 ERROR: FILE IS EMPTY")
                    return False
                    
                # Show last trade
                last_trade = verify_data[-1]
                print(f"🔥 LAST TRADE: {last_trade['symbol']} {last_trade['side']} PnL: ${last_trade['real_pnl']}")
                
            except Exception as e:
                print(f"🔥 VERIFICATION ERROR: {e}")
                return False
            
            print(f"🔥 SUCCESS: File saved and verified")
            return True
            
        except Exception as e:
            print(f"🔥 FORCE SAVE ERROR: {str(e)}")
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
        
        winning_trades = [t for t in self.session_trades if t.is_winner]
        losing_trades = [t for t in self.session_trades if not t.is_winner]
        
        total_pnl = sum(t.real_pnl for t in self.session_trades)
        win_rate = (len(winning_trades) / len(self.session_trades)) * 100
        
        return {
            'total_trades': len(self.session_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(self.session_trades),
            'best_trade': max(t.real_pnl for t in self.session_trades),
            'worst_trade': min(t.real_pnl for t in self.session_trades),
            'avg_duration': sum(t.duration_minutes for t in self.session_trades) / len(self.session_trades)
        }
    
    def load_trades_by_timeframe(self, timeframe: str) -> List[TradeRecord]:
        """Load all trades from file by timeframe"""
        try:
            timeframe_dir = self.base_path / timeframe
            filename = f"trades_{timeframe}.json"
            filepath = timeframe_dir / filename
            
            if not filepath.exists():
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                trades_data = json.load(f)
            
            # Convert back to TradeRecord objects
            trades = []
            for trade_data in trades_data:
                trades.append(TradeRecord(**trade_data))
            
            return trades
            
        except Exception as e:
            self.logger.error(f"💀 Failed to load trades: {str(e)}")
            return []
    
    def get_timeframe_summary(self, timeframe: str) -> Dict[str, Any]:
        """Get summary statistics for a timeframe (all trades)"""
        try:
            # Load all trades for this timeframe
            all_trades = self.load_trades_by_timeframe(timeframe)
            
            if not all_trades:
                return {'timeframe': timeframe, 'total_trades': 0}
            
            # Calculate statistics
            winning_trades = [t for t in all_trades if t.is_winner]
            losing_trades = [t for t in all_trades if not t.is_winner]
            
            total_pnl = sum(t.real_pnl for t in all_trades)
            win_rate = (len(winning_trades) / len(all_trades)) * 100
            
            # Group by symbol
            symbol_stats = {}
            for trade in all_trades:
                if trade.symbol not in symbol_stats:
                    symbol_stats[trade.symbol] = {'trades': 0, 'pnl': 0.0, 'wins': 0}
                symbol_stats[trade.symbol]['trades'] += 1
                symbol_stats[trade.symbol]['pnl'] += trade.real_pnl
                if trade.is_winner:
                    symbol_stats[trade.symbol]['wins'] += 1
            
            return {
                'timeframe': timeframe,
                'total_trades': len(all_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl_per_trade': total_pnl / len(all_trades),
                'best_trade': max(t.real_pnl for t in all_trades),
                'worst_trade': min(t.real_pnl for t in all_trades),
                'avg_duration_minutes': sum(t.duration_minutes for t in all_trades) / len(all_trades),
                'symbol_performance': symbol_stats
            }
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get timeframe summary: {str(e)}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def export_to_csv(self, timeframe: str, output_file: str) -> bool:
        """Export trades to CSV for external analysis"""
        try:
            import pandas as pd
            
            # Load all trades for this timeframe
            all_trades = self.load_trades_by_timeframe(timeframe)
            
            if not all_trades:
                self.logger.warning(f"No trades found for {timeframe}")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame([trade.to_dict() for trade in all_trades])
            
            # Save to CSV
            df.to_csv(output_file, index=False)
            
            self.logger.info(f"📊 Exported {len(all_trades)} trades to {output_file}")
            return True
            
        except ImportError:
            self.logger.error("💀 pandas not available for CSV export")
            return False
        except Exception as e:
            self.logger.error(f"💀 Failed to export to CSV: {str(e)}")
            return False