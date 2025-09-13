"""
Monitoring System Data Models
Standardized models for monitoring status, alerts, and performance tracking
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class MonitoringState(Enum):
    """Monitoring system states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class SymbolState(Enum):
    """Individual symbol monitoring states"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    PAUSED = "paused"
    RATE_LIMITED = "rate_limited"


class AlertType(Enum):
    """Alert types for different signal strengths"""
    SUPER_SIGNAL = "super_signal"      # Super Bullish/Bearish
    STRONG_SIGNAL = "strong_signal"    # Strong signals
    MEDIUM_SIGNAL = "medium_signal"    # Medium signals
    SYSTEM_ERROR = "system_error"      # System errors
    CONNECTION_ISSUE = "connection_issue"  # API/Connection issues
    RATE_LIMIT = "rate_limit"          # Rate limit warnings


class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"    # System errors, connection failures
    HIGH = "high"           # Super signals
    MEDIUM = "medium"       # Strong signals
    LOW = "low"            # Medium signals, warnings
    INFO = "info"          # General information


@dataclass
class AlertConfig:
    """Configuration for alerts per symbol"""
    symbol: str
    enabled: bool = True
    
    # Sound settings
    super_signal_sound: Optional[str] = "super_alert.wav"
    strong_signal_sound: Optional[str] = "strong_alert.wav"
    medium_signal_sound: Optional[str] = "medium_alert.wav"
    error_sound: Optional[str] = "error_alert.wav"
    
    # Alert thresholds
    min_signal_strength: float = 0.7
    max_alerts_per_hour: int = 10
    
    # Visual settings
    show_desktop_notifications: bool = True
    log_all_signals: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'enabled': self.enabled,
            'super_signal_sound': self.super_signal_sound,
            'strong_signal_sound': self.strong_signal_sound,
            'medium_signal_sound': self.medium_signal_sound,
            'error_sound': self.error_sound,
            'min_signal_strength': self.min_signal_strength,
            'max_alerts_per_hour': self.max_alerts_per_hour,
            'show_desktop_notifications': self.show_desktop_notifications,
            'log_all_signals': self.log_all_signals
        }


@dataclass
class SymbolStatus:
    """Status information for a monitored symbol"""
    symbol: str
    state: SymbolState
    
    # Monitoring metrics
    last_update: datetime
    update_count: int = 0
    error_count: int = 0
    signal_count: int = 0
    
    # Current market data
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    
    # Latest signal info
    latest_signal_type: Optional[str] = None
    latest_signal_strength: Optional[float] = None
    latest_signal_time: Optional[datetime] = None
    
    # Performance metrics
    avg_update_time_ms: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    # Rate limiting
    api_calls_last_minute: int = 0
    rate_limit_reset_time: Optional[datetime] = None
    
    # Indicator data
    trend_magic_color: Optional[str] = None
    squeeze_status: Optional[str] = None
    momentum_direction: Optional[str] = None
    
    def is_healthy(self) -> bool:
        """Check if symbol monitoring is healthy"""
        if self.state == SymbolState.ERROR:
            return False
        
        # Check if updates are recent (within last 5 minutes)
        if self.last_update:
            minutes_since_update = (datetime.now() - self.last_update).total_seconds() / 60
            if minutes_since_update > 5:
                return False
        
        # Check error rate (less than 10% errors)
        if self.update_count > 10:
            error_rate = self.error_count / self.update_count
            if error_rate > 0.1:
                return False
        
        return True
    
    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        if self.state == SymbolState.ACTIVE:
            if self.latest_signal_type:
                return f"🟢 Active | Last: {self.latest_signal_type} ({self.latest_signal_strength:.2f})"
            else:
                return f"🟢 Active | Price: ${self.current_price:.4f}" if self.current_price else "🟢 Active"
        elif self.state == SymbolState.ERROR:
            return f"🔴 Error | {self.last_error}" if self.last_error else "🔴 Error"
        elif self.state == SymbolState.PAUSED:
            return "⏸️ Paused"
        elif self.state == SymbolState.RATE_LIMITED:
            return "⏳ Rate Limited"
        else:
            return f"⚪ {self.state.value.title()}"


@dataclass
class MonitoringStatus:
    """Overall monitoring system status"""
    state: MonitoringState
    start_time: datetime
    
    # Symbol tracking
    symbols: Dict[str, SymbolStatus] = field(default_factory=dict)
    total_symbols: int = 0
    active_symbols: int = 0
    error_symbols: int = 0
    
    # Performance metrics
    total_updates: int = 0
    total_signals: int = 0
    total_errors: int = 0
    avg_update_time_ms: float = 0.0
    
    # System resources
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # API usage
    api_calls_per_minute: int = 0
    api_weight_usage: int = 0
    rate_limit_warnings: int = 0
    
    # Alert statistics
    alerts_sent_today: int = 0
    last_alert_time: Optional[datetime] = None
    
    def update_symbol_counts(self):
        """Update symbol count statistics"""
        self.total_symbols = len(self.symbols)
        self.active_symbols = sum(1 for s in self.symbols.values() if s.state == SymbolState.ACTIVE)
        self.error_symbols = sum(1 for s in self.symbols.values() if s.state == SymbolState.ERROR)
    
    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_uptime_string(self) -> str:
        """Get human-readable uptime"""
        uptime = self.get_uptime_seconds()
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_health_score(self) -> float:
        """Calculate overall system health score (0.0 to 1.0)"""
        if self.total_symbols == 0:
            return 1.0
        
        # Base score from active symbols
        active_ratio = self.active_symbols / self.total_symbols
        
        # Penalty for errors
        if self.total_updates > 0:
            error_rate = self.total_errors / self.total_updates
            error_penalty = min(0.5, error_rate * 2)  # Max 50% penalty
        else:
            error_penalty = 0
        
        # Penalty for rate limiting
        rate_limit_penalty = min(0.2, self.rate_limit_warnings * 0.05)  # Max 20% penalty
        
        health_score = active_ratio - error_penalty - rate_limit_penalty
        return max(0.0, min(1.0, health_score))
    
    def get_status_emoji(self) -> str:
        """Get status emoji based on health"""
        health = self.get_health_score()
        
        if self.state == MonitoringState.ERROR:
            return "💀"
        elif self.state == MonitoringState.STOPPED:
            return "⏹️"
        elif self.state == MonitoringState.PAUSED:
            return "⏸️"
        elif health >= 0.9:
            return "🟢"
        elif health >= 0.7:
            return "🟡"
        else:
            return "🔴"
    
    def get_summary_line(self) -> str:
        """Get one-line status summary"""
        emoji = self.get_status_emoji()
        uptime = self.get_uptime_string()
        health = self.get_health_score()
        
        return (f"{emoji} {self.state.value.upper()} | "
                f"Symbols: {self.active_symbols}/{self.total_symbols} | "
                f"Signals: {self.total_signals} | "
                f"Health: {health:.1%} | "
                f"Uptime: {uptime}")


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    symbol: str
    timeframe: str
    
    # Signal statistics
    total_signals: int = 0
    super_signals: int = 0
    strong_signals: int = 0
    medium_signals: int = 0
    
    # Signal accuracy (if backtesting data available)
    correct_signals: int = 0
    false_signals: int = 0
    accuracy_percentage: float = 0.0
    
    # Timing metrics
    avg_signal_detection_time_ms: float = 0.0
    max_signal_detection_time_ms: float = 0.0
    
    # Market coverage
    market_hours_monitored: float = 0.0
    signals_per_hour: float = 0.0
    
    # Performance tracking
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    
    def calculate_accuracy(self):
        """Calculate signal accuracy percentage"""
        total_validated = self.correct_signals + self.false_signals
        if total_validated > 0:
            self.accuracy_percentage = (self.correct_signals / total_validated) * 100
        else:
            self.accuracy_percentage = 0.0
    
    def calculate_signals_per_hour(self):
        """Calculate signals per hour rate"""
        if self.market_hours_monitored > 0:
            self.signals_per_hour = self.total_signals / self.market_hours_monitored
        else:
            self.signals_per_hour = 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary dictionary"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'total_signals': self.total_signals,
            'signal_breakdown': {
                'super': self.super_signals,
                'strong': self.strong_signals,
                'medium': self.medium_signals
            },
            'accuracy_percentage': self.accuracy_percentage,
            'signals_per_hour': self.signals_per_hour,
            'avg_detection_time_ms': self.avg_signal_detection_time_ms,
            'market_hours_monitored': self.market_hours_monitored
        }