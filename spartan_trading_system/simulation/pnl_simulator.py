"""
PnL Simulator - Spartan Trading System
Real-time P&L simulation with commission calculations
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from config.settings import maker_fee, taker_fee, MAX_OPEN_POSITIONS, INITIAL_BALANCE, AUTO_CLOSE_ON_TARGET
from ..logging.sqlite_trade_logger import SQLiteTradeLogger

class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class CloseReason(Enum):
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    MANUAL = "MANUAL"

@dataclass
class Position:
    """Represents an open trading position"""
    symbol: str
    side: PositionSide
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    entry_commission: float  # Commission paid on entry
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current PnL without commissions"""
        if self.side == PositionSide.LONG:
            price_diff = current_price - self.entry_price
            gross_pnl = price_diff * self.quantity
        else:  # SHORT
            price_diff = self.entry_price - current_price
            gross_pnl = price_diff * self.quantity
        
        # Calculation completed - debug logging removed for cleaner console
        
        return gross_pnl
    
    def calculate_real_pnl(self, current_price: float, exit_commission: float = 0.0) -> float:
        """Calculate real PnL including all commissions"""
        gross_pnl = self.calculate_pnl(current_price)
        total_commissions = self.entry_commission + exit_commission
        return gross_pnl - total_commissions
    
    def should_close(self, current_price: float) -> Optional[CloseReason]:
        """Check if position should be closed based on stop loss or take profit"""
        if not AUTO_CLOSE_ON_TARGET:
            return None
        
        # Debug logging
        import logging
        logger = logging.getLogger("PnLSimulator")
        
        if self.side == PositionSide.LONG:
            if current_price <= self.stop_loss:
                logger.info(f"🔍 DEBUG: {self.symbol} LONG hit SL - Price: ${current_price:.4f} <= SL: ${self.stop_loss:.4f}")
                return CloseReason.STOP_LOSS
            elif current_price >= self.take_profit:
                logger.info(f"🔍 DEBUG: {self.symbol} LONG hit TP - Price: ${current_price:.4f} >= TP: ${self.take_profit:.4f}")
                return CloseReason.TAKE_PROFIT
        else:  # SHORT
            if current_price >= self.stop_loss:
                logger.info(f"🔍 DEBUG: {self.symbol} SHORT hit SL - Price: ${current_price:.4f} >= SL: ${self.stop_loss:.4f}")
                return CloseReason.STOP_LOSS
            elif current_price <= self.take_profit:
                logger.info(f"🔍 DEBUG: {self.symbol} SHORT hit TP - Price: ${current_price:.4f} <= TP: ${self.take_profit:.4f}")
                return CloseReason.TAKE_PROFIT
        
        return None

@dataclass
class ClosedTrade:
    """Represents a closed trading position"""
    symbol: str
    side: PositionSide
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime
    exit_time: datetime
    gross_pnl: float
    real_pnl: float
    total_commissions: float
    close_reason: CloseReason
    stop_loss: float
    take_profit: float
    
    @property
    def is_winner(self) -> bool:
        return self.real_pnl > 0

class PnLSimulator:
    """
    Real-time P&L Simulator with commission calculations
    
    Features:
    - Real commission calculations (maker + taker fees)
    - Maximum position limits
    - Automatic stop loss / take profit
    - Performance tracking
    """
    
    def __init__(self):
        """Initialize PnL Simulator"""
        self.logger = logging.getLogger("PnLSimulator")
        
        # Account state
        self.initial_balance = INITIAL_BALANCE
        self.current_balance = INITIAL_BALANCE
        
        # Positions
        self.open_positions: Dict[str, Position] = {}
        self.closed_trades: List[ClosedTrade] = []
        
        # Configuration
        self.max_positions = MAX_OPEN_POSITIONS
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.total_commissions_paid = 0.0
        
        # Trade logging with SQLite
        self.trade_logger = SQLiteTradeLogger()
        
        # Store additional data for logging
        self.position_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Debug: Track if positions are being closed
        self.debug_mode = False  # Set to True for debugging
        
        self.logger.info(f"🏛️ PnL Simulator initialized - Balance: ${self.initial_balance}")
        self.logger.info(f"⚙️ Max positions: {self.max_positions} | Fees: {self.maker_fee:.4f}/{self.taker_fee:.4f}")
        self.logger.info(f"📊 Trade logging enabled - Path: trade_logs/")
    
    def can_open_position(self) -> bool:
        """Check if we can open a new position"""
        return len(self.open_positions) < self.max_positions
    
    def set_position_metadata(self, symbol: str, timeframe: str, trend_magic_value: float = 0.0,
                             trend_magic_color: str = "UNKNOWN", squeeze_momentum: str = "UNKNOWN"):
        """Set additional metadata for position logging"""
        if symbol not in self.position_metadata:
            self.position_metadata[symbol] = {}
        
        self.position_metadata[symbol].update({
            'timeframe': timeframe,
            'trend_magic_value': trend_magic_value,
            'trend_magic_color': trend_magic_color,
            'squeeze_momentum': squeeze_momentum
        })
    
    def open_position(self, symbol: str, side: str, entry_price: float, 
                     quantity: float, stop_loss: float, take_profit: float) -> bool:
        """
        Open a new position
        
        Args:
            symbol: Trading symbol
            side: 'LONG' or 'SHORT'
            entry_price: Entry price
            quantity: Position size
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            True if position opened successfully
        """
        try:
            # Check if we can open more positions
            if not self.can_open_position():
                self.logger.warning(f"⚠️ Cannot open {symbol} - Max positions ({self.max_positions}) reached")
                return False
            
            # Check if position already exists
            if symbol in self.open_positions:
                self.logger.warning(f"⚠️ Position for {symbol} already exists")
                return False
            
            # Calculate entry commission (use maker fee for entry)
            position_value = entry_price * quantity
            entry_commission = position_value * self.maker_fee
            
            # Validate position value is close to target ($100)
            from config.settings import POSITION_SIZE
            value_diff = abs(position_value - POSITION_SIZE)
            if value_diff > 0.01:  # More than $0.01 difference
                self.logger.warning(
                    f"⚠️ Position value deviation for {symbol}: "
                    f"Expected=${POSITION_SIZE:.3f}, Actual=${position_value:.3f}, "
                    f"Diff=${value_diff:.3f}"
                )
            
            # Create position
            position = Position(
                symbol=symbol,
                side=PositionSide.LONG if side == 'LONG' else PositionSide.SHORT,
                entry_price=entry_price,
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=datetime.now(),
                entry_commission=entry_commission
            )
            
            # Add to open positions
            self.open_positions[symbol] = position
            self.total_commissions_paid += entry_commission
            
            self.logger.info(f"📈 Opened {side} position: {symbol} @ ${entry_price:.3f} | Qty: {quantity:.6f} | Commission: ${entry_commission:.3f}")
            self.logger.info(f"🔍 Position details: SL=${stop_loss:.3f} | TP=${take_profit:.3f} | Capital=${position_value:.3f}")
            self.logger.info(f"🔍 Quantity calculation: ${POSITION_SIZE:.3f} / ${entry_price:.3f} = {quantity:.6f}")
            self.logger.info(f"🔍 Total open positions: {len(self.open_positions)}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to open position for {symbol}: {str(e)}")
            return False
    
    def close_position(self, symbol: str, exit_price: float, reason: CloseReason = CloseReason.MANUAL) -> Optional[ClosedTrade]:
        """
        Close an existing position
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Reason for closing
            
        Returns:
            ClosedTrade object if successful
        """
        try:
            if symbol not in self.open_positions:
                self.logger.warning(f"⚠️ No open position found for {symbol}")
                return None
            
            position = self.open_positions[symbol]
            
            # Calculate exit commission
            position_value = exit_price * position.quantity
            exit_commission = position_value * self.taker_fee
            
            # Calculate PnL
            gross_pnl = position.calculate_pnl(exit_price)
            real_pnl = position.calculate_real_pnl(exit_price, exit_commission)
            total_commissions = position.entry_commission + exit_commission
            
            # Create closed trade
            closed_trade = ClosedTrade(
                symbol=symbol,
                side=position.side,
                entry_price=position.entry_price,
                exit_price=exit_price,
                quantity=position.quantity,
                entry_time=position.entry_time,
                exit_time=datetime.now(),
                gross_pnl=gross_pnl,
                real_pnl=real_pnl,
                total_commissions=total_commissions,
                close_reason=reason,
                stop_loss=position.stop_loss,
                take_profit=position.take_profit
            )
            
            # Update statistics
            self.closed_trades.append(closed_trade)
            self.total_trades += 1
            self.total_commissions_paid += exit_commission
            self.current_balance += real_pnl
            
            if closed_trade.is_winner:
                self.winning_trades += 1
            
            # Log trade with metadata
            metadata = self.position_metadata.get(symbol, {})
            
            # Debug logging
            if self.debug_mode:
                self.logger.info(f"🔍 DEBUG: Logging trade for {symbol} | Metadata: {metadata}")
            
            trade_logged = self.trade_logger.log_trade(
                closed_trade=closed_trade,
                timeframe=metadata.get('timeframe', 'unknown'),
                trend_magic_value=metadata.get('trend_magic_value', 0.0),
                trend_magic_color=metadata.get('trend_magic_color', 'UNKNOWN'),
                squeeze_momentum=metadata.get('squeeze_momentum', 'UNKNOWN')
            )
            
            if self.debug_mode:
                self.logger.info(f"🔍 DEBUG: Trade logged successfully: {trade_logged}")
            
            # Clean up metadata
            self.position_metadata.pop(symbol, None)
            
            # Remove from open positions
            del self.open_positions[symbol]
            
            result_emoji = "💚" if closed_trade.is_winner else "💔"
            
            # FORCE PRINT TO CONSOLE
            print(f"🔥 POSITION CLOSED: {symbol} {position.side.value} | PnL: ${real_pnl:.3f} | Reason: {reason.value}")
            
            self.logger.info(f"{result_emoji} Closed {position.side.value} {symbol}: PnL ${real_pnl:.3f} | Reason: {reason.value}")
            
            return closed_trade
            
        except Exception as e:
            self.logger.error(f"💀 Failed to close position for {symbol}: {str(e)}")
            return None
    
    def update_positions(self, market_data: Dict[str, float]):
        """
        Update all positions with current market prices
        
        Args:
            market_data: Dictionary of symbol -> current_price
        """
        try:
            if self.debug_mode and self.open_positions:
                self.logger.info(f"🔍 DEBUG: Updating {len(self.open_positions)} positions with market data")
            
            positions_to_close = []
            
            for symbol, position in self.open_positions.items():
                if symbol in market_data:
                    current_price = market_data[symbol]
                    
                    # Check if position should be closed
                    close_reason = position.should_close(current_price)
                    if close_reason:
                        positions_to_close.append((symbol, current_price, close_reason))
                        if self.debug_mode:
                            self.logger.info(f"🔍 DEBUG: {symbol} should close - Reason: {close_reason.value} | Price: ${current_price:.4f}")
            
            # Close positions that hit stop loss or take profit
            for symbol, price, reason in positions_to_close:
                if self.debug_mode:
                    self.logger.info(f"🔍 DEBUG: Closing {symbol} - Reason: {reason.value}")
                self.close_position(symbol, price, reason)
                
        except Exception as e:
            self.logger.error(f"💀 Failed to update positions: {str(e)}")
    
    def get_current_pnl(self, market_data: Dict[str, float]) -> float:
        """Get current unrealized PnL for all open positions"""
        total_pnl = 0.0
        
        for symbol, position in self.open_positions.items():
            if symbol in market_data:
                current_price = market_data[symbol]
                # Calculate real PnL (including entry commission, but not exit commission yet)
                exit_commission = current_price * position.quantity * self.taker_fee
                pnl = position.calculate_real_pnl(current_price, exit_commission)
                total_pnl += pnl
        
        return total_pnl
    
    def get_total_balance(self, market_data: Dict[str, float]) -> float:
        """Get total balance including unrealized PnL"""
        unrealized_pnl = self.get_current_pnl(market_data)
        return self.current_balance + unrealized_pnl
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0.0
        
        total_profit = sum(trade.real_pnl for trade in self.closed_trades if trade.is_winner)
        total_loss = abs(sum(trade.real_pnl for trade in self.closed_trades if not trade.is_winner))
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_return': self.current_balance - self.initial_balance,
            'total_return_pct': ((self.current_balance - self.initial_balance) / self.initial_balance) * 100,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.total_trades - self.winning_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_commissions': self.total_commissions_paid,
            'open_positions': len(self.open_positions),
            'max_positions': self.max_positions
        }
    
    def get_open_positions_summary(self, market_data: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get summary of all open positions with current PnL"""
        positions_summary = []
        
        for symbol, position in self.open_positions.items():
            if symbol in market_data:
                current_price = market_data[symbol]
                # Calculate PnL
                gross_pnl = position.calculate_pnl(current_price)
                exit_commission = current_price * position.quantity * self.taker_fee
                real_pnl = position.calculate_real_pnl(current_price, exit_commission)
                
                # Calculate percentage based on fixed position size ($100)
                from config.settings import POSITION_SIZE
                pnl_pct = (real_pnl / POSITION_SIZE) * 100
                
                # PnL calculation completed - debug logging removed for cleaner console
                
                positions_summary.append({
                    'symbol': symbol,
                    'side': position.side.value,
                    'entry_price': position.entry_price,
                    'current_price': current_price,
                    'quantity': position.quantity,
                    'current_pnl': real_pnl,
                    'pnl_pct': pnl_pct,
                    'stop_loss': position.stop_loss,
                    'take_profit': position.take_profit
                })
        
        return positions_summary
    
    def get_trade_logger_stats(self) -> Dict[str, Any]:
        """Get trade logging statistics"""
        return self.trade_logger.get_session_stats()
    
    def get_timeframe_performance(self, timeframe: str) -> Dict[str, Any]:
        """Get performance statistics for a specific timeframe"""
        return self.trade_logger.get_timeframe_summary(timeframe)
    
    def export_trades_to_csv(self, timeframe: str, output_file: str) -> bool:
        """Export trades to CSV for analysis"""
        return self.trade_logger.export_to_csv(timeframe, output_file)
    
    def force_close_position(self, symbol: str) -> bool:
        """Force close a position for testing (manual close)"""
        if symbol not in self.open_positions:
            self.logger.warning(f"⚠️ No position found for {symbol}")
            return False
        
        position = self.open_positions[symbol]
        # Use current entry price as exit price for testing
        exit_price = position.entry_price * 1.01  # Simulate small profit
        
        closed_trade = self.close_position(symbol, exit_price, CloseReason.MANUAL)
        return closed_trade is not None
    
    def clear_all_positions(self):
        """Clear all positions (for testing/reset)"""
        self.open_positions.clear()
        self.closed_trades.clear()
        self.current_balance = self.initial_balance
        self.total_trades = 0
        self.winning_trades = 0
        self.total_commissions_paid = 0.0
        self.position_metadata.clear()
        self.logger.info("🔄 All positions cleared - Simulator reset")