# Design Document - Spartan Squeeze Magic Strategy

## Overview

The Spartan Squeeze Magic Strategy system is designed as a modular, configurable, and scalable trading platform. The architecture follows clean code principles with clear separation of concerns, making it maintainable and extensible for future enhancements.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SPARTAN TRADING SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface  │  Web Dashboard  │  API Endpoints          │
├─────────────────────────────────────────────────────────────┤
│                    Strategy Engine                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Signal    │ │    Risk     │ │     Portfolio       │   │
│  │  Generator  │ │  Manager    │ │     Manager         │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Indicator Engine                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Trend Magic │ │   Squeeze   │ │   Multi-Timeframe   │   │
│  │  Calculator │ │  Momentum   │ │     Analyzer        │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Market    │ │ Historical  │ │    Configuration    │   │
│  │    Data     │ │    Data     │ │      Storage        │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                 External Services                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Binance   │ │   Logging   │ │      Alerts         │   │
│  │     API     │ │   System    │ │      System         │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Configuration Management (`config/`)

#### ConfigManager Class
```python
class ConfigManager:
    def load_config(self, config_path: str) -> StrategyConfig
    def save_config(self, config: StrategyConfig, config_path: str) -> bool
    def validate_config(self, config: StrategyConfig) -> List[str]
    def get_default_config(self) -> StrategyConfig
```

#### StrategyConfig Class
```python
@dataclass
class StrategyConfig:
    # Trend Magic Parameters
    trend_magic_cci_period: int = 20
    trend_magic_atr_multiplier: float = 1.0
    trend_magic_atr_period: int = 5
    
    # Squeeze Momentum Parameters
    squeeze_bb_length: int = 20
    squeeze_bb_multiplier: float = 2.0
    squeeze_kc_length: int = 20
    squeeze_kc_multiplier: float = 1.5
    squeeze_use_true_range: bool = True
    
    # Timeframe Configuration
    primary_timeframe: str = "1h"
    confirmation_timeframe: str = "30m"
    context_timeframe: str = "4h"
    
    # Risk Management
    risk_percentage: float = 2.0
    max_positions: int = 3
    
    # Alert Settings
    enable_audio_alerts: bool = True
    alert_sound_bullish: str = "sounds/bullish.wav"
    alert_sound_bearish: str = "sounds/bearish.wav"
```

### 2. Indicator Engine (`indicators/`)

#### Enhanced TechnicalAnalyzer
```python
class TechnicalAnalyzer:
    def __init__(self, config: StrategyConfig)
    def calculate_trend_magic(self, data: pd.DataFrame) -> TrendMagicResult
    def calculate_squeeze_momentum(self, data: pd.DataFrame) -> SqueezeResult
    def get_multi_timeframe_analysis(self, symbol: str) -> MultiTimeframeAnalysis
```

#### Result Classes
```python
@dataclass
class TrendMagicResult:
    value: float
    color: str
    trend_status: str
    distance_pct: float
    buy_signal: bool
    sell_signal: bool

@dataclass
class SqueezeResult:
    momentum_value: float
    momentum_color: str
    squeeze_status: str
    squeeze_on: bool
    squeeze_off: bool
```

### 3. Strategy Engine (`strategy/`)

#### SignalGenerator Class
```python
class SignalGenerator:
    def __init__(self, config: StrategyConfig, analyzer: TechnicalAnalyzer)
    def generate_signals(self, symbol: str) -> List[TradingSignal]
    def calculate_signal_strength(self, trend_magic: TrendMagicResult, 
                                squeeze: SqueezeResult) -> float
    def classify_signal_type(self, trend_magic: TrendMagicResult, 
                           squeeze: SqueezeResult) -> SignalType
```

#### TradingSignal Class
```python
@dataclass
class TradingSignal:
    symbol: str
    timestamp: datetime
    signal_type: SignalType
    direction: Direction
    strength: float
    entry_price: float
    stop_loss: float
    take_profit_levels: List[float]
    timeframe: str
    confidence: float
```

#### SignalType Enum
```python
class SignalType(Enum):
    SUPER_BULLISH = "super_bullish"
    SUPER_BEARISH = "super_bearish"
    BREAKOUT_BULLISH = "breakout_bullish"
    BREAKOUT_BEARISH = "breakout_bearish"
    TREND_CHANGE_BULLISH = "trend_change_bullish"
    TREND_CHANGE_BEARISH = "trend_change_bearish"
    NO_SIGNAL = "no_signal"
```

### 4. Risk Management (`risk/`)

#### RiskManager Class
```python
class RiskManager:
    def __init__(self, config: StrategyConfig)
    def calculate_position_size(self, account_balance: float, 
                              entry_price: float, stop_loss: float) -> float
    def calculate_stop_loss(self, trend_magic_value: float, 
                          direction: Direction) -> float
    def calculate_take_profit_levels(self, entry_price: float, 
                                   stop_loss: float, direction: Direction) -> List[float]
    def validate_risk_parameters(self, signal: TradingSignal) -> bool
```

### 5. Monitoring System (`monitoring/`)

#### StrategyMonitor Class
```python
class StrategyMonitor:
    def __init__(self, config: StrategyConfig, signal_generator: SignalGenerator)
    def start_monitoring(self, symbols: List[str]) -> None
    def stop_monitoring(self) -> None
    def get_current_status(self) -> MonitoringStatus
    def handle_new_signal(self, signal: TradingSignal) -> None
```

#### AlertManager Class
```python
class AlertManager:
    def __init__(self, config: StrategyConfig)
    def send_audio_alert(self, signal_type: SignalType) -> None
    def send_notification(self, message: str, priority: Priority) -> None
    def log_signal(self, signal: TradingSignal) -> None
```

### 6. Data Management (`data/`)

#### MarketDataProvider Class
```python
class MarketDataProvider:
    def __init__(self, config: StrategyConfig)
    def get_realtime_data(self, symbol: str, timeframe: str) -> pd.DataFrame
    def get_historical_data(self, symbol: str, timeframe: str, 
                          start_date: datetime, end_date: datetime) -> pd.DataFrame
    def get_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]
```

### 7. Backtesting Engine (`backtesting/`)

#### BacktestEngine Class
```python
class BacktestEngine:
    def __init__(self, config: StrategyConfig, signal_generator: SignalGenerator)
    def run_backtest(self, symbol: str, start_date: datetime, 
                    end_date: datetime) -> BacktestResult
    def optimize_parameters(self, symbol: str, parameter_ranges: Dict) -> OptimizationResult
    def generate_report(self, result: BacktestResult) -> BacktestReport
```

## Data Models

### Database Schema (SQLite for simplicity)

```sql
-- Signals Table
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,
    timestamp DATETIME NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    strength FLOAT NOT NULL,
    entry_price FLOAT NOT NULL,
    stop_loss FLOAT NOT NULL,
    take_profit_1 FLOAT,
    take_profit_2 FLOAT,
    take_profit_3 FLOAT,
    timeframe VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance Table
CREATE TABLE performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER REFERENCES signals(id),
    exit_price FLOAT,
    exit_timestamp DATETIME,
    pnl FLOAT,
    pnl_percentage FLOAT,
    duration_minutes INTEGER,
    exit_reason VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Configuration History
CREATE TABLE config_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name VARCHAR(100) NOT NULL,
    config_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);
```

## Error Handling

### Exception Hierarchy
```python
class SpartanTradingException(Exception):
    """Base exception for Spartan Trading System"""
    pass

class ConfigurationError(SpartanTradingException):
    """Configuration related errors"""
    pass

class DataProviderError(SpartanTradingException):
    """Market data provider errors"""
    pass

class IndicatorCalculationError(SpartanTradingException):
    """Indicator calculation errors"""
    pass

class RiskManagementError(SpartanTradingException):
    """Risk management validation errors"""
    pass
```

### Error Handling Strategy
1. **Graceful Degradation**: System continues with reduced functionality
2. **Retry Logic**: Automatic retry for transient failures
3. **Fallback Mechanisms**: Alternative data sources and calculations
4. **Comprehensive Logging**: Detailed error logs for debugging
5. **User Notifications**: Clear error messages for configuration issues

## Testing Strategy

### Unit Tests
- Individual indicator calculations
- Signal generation logic
- Risk management calculations
- Configuration validation

### Integration Tests
- Multi-timeframe analysis
- Signal generation pipeline
- Alert system functionality
- Data provider integration

### Performance Tests
- Real-time monitoring performance
- Large dataset processing
- Memory usage optimization
- Concurrent symbol monitoring

### Backtesting Validation
- Historical signal accuracy
- Strategy performance metrics
- Parameter optimization validation
- Edge case handling

## Security Considerations

### API Security
- Secure storage of API keys
- Rate limiting for external APIs
- Input validation and sanitization
- Encrypted configuration storage

### Data Protection
- Local data encryption
- Secure logging practices
- Personal information protection
- Audit trail maintenance

## Deployment Architecture

### Directory Structure
```
spartan_trading_system/
├── config/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── strategy_config.py
│   └── default_config.json
├── indicators/
│   ├── __init__.py
│   ├── technical_analyzer.py
│   ├── trend_magic.py
│   └── squeeze_momentum.py
├── strategy/
│   ├── __init__.py
│   ├── signal_generator.py
│   ├── signal_types.py
│   └── multi_timeframe_analyzer.py
├── risk/
│   ├── __init__.py
│   ├── risk_manager.py
│   └── position_calculator.py
├── monitoring/
│   ├── __init__.py
│   ├── strategy_monitor.py
│   ├── alert_manager.py
│   └── performance_tracker.py
├── data/
│   ├── __init__.py
│   ├── market_data_provider.py
│   ├── data_cache.py
│   └── database_manager.py
├── backtesting/
│   ├── __init__.py
│   ├── backtest_engine.py
│   ├── optimization_engine.py
│   └── report_generator.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   └── helpers.py
├── cli/
│   ├── __init__.py
│   ├── main_cli.py
│   ├── monitor_cli.py
│   └── backtest_cli.py
├── sounds/
│   ├── bullish_alert.wav
│   ├── bearish_alert.wav
│   └── notification.wav
├── logs/
├── data/
│   └── spartan_trading.db
├── configs/
│   ├── default.json
│   ├── conservative.json
│   └── aggressive.json
├── requirements.txt
├── setup.py
└── README.md
```

This architecture ensures modularity, configurability, and maintainability while providing a robust foundation for the Spartan Squeeze Magic Strategy system.