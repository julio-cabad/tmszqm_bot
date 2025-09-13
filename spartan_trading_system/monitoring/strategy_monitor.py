"""
Strategy Monitor - Spartan Multi-Crypto Real-Time Monitoring
Professional concurrent monitoring system for multiple cryptocurrencies
"""

import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from ..config.strategy_config import StrategyConfig
from ..data.market_data_provider import MarketDataProvider
from ..data.data_models import DataRequest
from ..indicators.indicator_engine import IndicatorEngine
from ..strategy.signal_generator import SignalGenerator
from ..risk.risk_manager import RiskManager
from .alert_manager import AlertManager
from .performance_tracker import PerformanceTracker
from .monitoring_models import (
    MonitoringStatus, SymbolStatus, MonitoringState, SymbolState
)


class StrategyMonitor:
    """
    Spartan Strategy Monitor
    
    Professional multi-cryptocurrency monitoring system with:
    - Concurrent monitoring of 20+ symbols
    - Real-time signal detection and processing
    - Comprehensive performance tracking
    - Intelligent error handling and recovery
    - Dynamic symbol management
    - Resource optimization and rate limiting
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Strategy Monitor
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger("StrategyMonitor")
        
        # Core components
        self.market_data_provider = MarketDataProvider(config)
        self.indicator_engine = IndicatorEngine(config)
        self.signal_generator = SignalGenerator(config, self.indicator_engine)
        self.risk_manager = RiskManager(config)
        self.alert_manager = AlertManager(config)
        self.performance_tracker = PerformanceTracker(config)
        
        # Monitoring state
        self.monitoring_status = MonitoringStatus(
            state=MonitoringState.STOPPED,
            start_time=datetime.now()
        )
        
        # Symbol management
        self.active_symbols: Set[str] = set()
        self.symbol_configs: Dict[str, Dict[str, Any]] = {}
        
        # Threading and concurrency
        self.monitor_thread = None
        self.symbol_threads: Dict[str, threading.Thread] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.monitoring_active = False
        
        # Performance optimization
        self.update_intervals = {
            '1m': 60,    # 1 minute
            '5m': 300,   # 5 minutes  
            '15m': 900,  # 15 minutes
            '1h': 3600,  # 1 hour
            '4h': 14400, # 4 hours
            '1d': 86400  # 1 day
        }
        
        # Error handling
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
        self.max_errors_per_symbol = 5
        self.error_reset_time = timedelta(minutes=30)
        
        self._initialize_symbols()
        
        self.logger.info("🏛️ Spartan Strategy Monitor initialized")
        self.logger.info(f"⚔️ Configured for {len(self.active_symbols)} symbols")
    
    def _initialize_symbols(self):
        """Initialize symbols from configuration"""
        symbols = getattr(self.config, 'symbols', [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'BCHUSDT',
            'AVAXUSDT', 'MATICUSDT', 'ATOMUSDT', 'NEARUSDT', 'FTMUSDT',
            'SANDUSDT', 'MANAUSDT', 'AXSUSDT', 'CHZUSDT', 'ENJUSDT'
        ])
        
        for symbol in symbols:
            self.add_symbol(symbol)
        
        self.logger.info(f"📋 Initialized {len(self.active_symbols)} symbols for monitoring")
    
    def add_symbol(self, symbol: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a symbol to monitoring
        
        Args:
            symbol: Symbol to add (e.g., 'BTCUSDT')
            config: Optional symbol-specific configuration
            
        Returns:
            True if symbol was added successfully
        """
        try:
            if symbol in self.active_symbols:
                self.logger.warning(f"⚠️ Symbol {symbol} already being monitored")
                return False
            
            # Default symbol configuration
            symbol_config = {
                'timeframes': getattr(self.config, 'timeframes', ['1h']),
                'update_interval': 60,  # seconds
                'enabled': True,
                'max_errors': self.max_errors_per_symbol
            }
            
            # Override with provided config
            if config:
                symbol_config.update(config)
            
            # Add to active symbols
            self.active_symbols.add(symbol)
            self.symbol_configs[symbol] = symbol_config
            
            # Initialize symbol status
            self.monitoring_status.symbols[symbol] = SymbolStatus(
                symbol=symbol,
                state=SymbolState.INACTIVE,
                last_update=datetime.now()
            )
            
            # Initialize error tracking
            self.error_counts[symbol] = 0
            
            self.logger.info(f"✅ Added symbol {symbol} to monitoring")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to add symbol {symbol}: {str(e)}")
            return False
    
    def remove_symbol(self, symbol: str) -> bool:
        """
        Remove a symbol from monitoring
        
        Args:
            symbol: Symbol to remove
            
        Returns:
            True if symbol was removed successfully
        """
        try:
            if symbol not in self.active_symbols:
                self.logger.warning(f"⚠️ Symbol {symbol} not being monitored")
                return False
            
            # Stop symbol thread if running
            if symbol in self.symbol_threads:
                # Symbol threads will check monitoring_active flag
                pass
            
            # Remove from active symbols
            self.active_symbols.discard(symbol)
            self.symbol_configs.pop(symbol, None)
            self.monitoring_status.symbols.pop(symbol, None)
            self.error_counts.pop(symbol, None)
            self.last_errors.pop(symbol, None)
            
            self.logger.info(f"✅ Removed symbol {symbol} from monitoring")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to remove symbol {symbol}: {str(e)}")
            return False
    
    def start_monitoring(self) -> bool:
        """
        Start real-time monitoring for all symbols
        
        Returns:
            True if monitoring started successfully
        """
        try:
            if self.monitoring_active:
                self.logger.warning("⚠️ Monitoring already active")
                return False
            
            self.logger.info("🚀 Starting Spartan multi-crypto monitoring...")
            
            # Update monitoring state
            self.monitoring_status.state = MonitoringState.STARTING
            self.monitoring_status.start_time = datetime.now()
            
            # Test connectivity
            if not self.market_data_provider.test_connectivity():
                self.logger.error("💀 Market data provider connectivity test failed")
                self.monitoring_status.state = MonitoringState.ERROR
                return False
            
            # Start monitoring
            self.monitoring_active = True
            self.monitoring_status.state = MonitoringState.RUNNING
            
            # Start main monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            # Send system alert
            from .monitoring_models import AlertType, AlertPriority
            self.alert_manager.send_system_alert(
                f"🏛️ Spartan monitoring started for {len(self.active_symbols)} symbols",
                alert_type=AlertType.SYSTEM_ERROR,
                priority=AlertPriority.INFO
            )
            
            self.logger.info(f"✅ Monitoring started for {len(self.active_symbols)} symbols")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to start monitoring: {str(e)}")
            self.monitoring_status.state = MonitoringState.ERROR
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop monitoring for all symbols
        
        Returns:
            True if monitoring stopped successfully
        """
        try:
            if not self.monitoring_active:
                self.logger.warning("⚠️ Monitoring not active")
                return False
            
            self.logger.info("🛑 Stopping Spartan monitoring...")
            
            # Update state
            self.monitoring_status.state = MonitoringState.SHUTTING_DOWN
            
            # Stop monitoring
            self.monitoring_active = False
            
            # Wait for main thread to finish
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            
            # Update symbol states
            for symbol_status in self.monitoring_status.symbols.values():
                symbol_status.state = SymbolState.INACTIVE
            
            # Update monitoring state
            self.monitoring_status.state = MonitoringState.STOPPED
            
            # Send system alert
            from .monitoring_models import AlertType, AlertPriority
            self.alert_manager.send_system_alert(
                "🏛️ Spartan monitoring stopped",
                alert_type=AlertType.SYSTEM_ERROR,
                priority=AlertPriority.INFO
            )
            
            self.logger.info("✅ Monitoring stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to stop monitoring: {str(e)}")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("🔄 Main monitoring loop started")
        
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Process all symbols concurrently
                futures = []
                
                for symbol in list(self.active_symbols):  # Create copy to avoid modification during iteration
                    if not self.monitoring_active:
                        break
                    
                    # Submit symbol processing to thread pool
                    future = self.thread_pool.submit(self._process_symbol, symbol)
                    futures.append((symbol, future))
                
                # Wait for all symbols to complete (with timeout)
                for symbol, future in futures:
                    try:
                        future.result(timeout=30)  # 30 second timeout per symbol
                    except Exception as e:
                        self.logger.error(f"💀 Symbol processing failed for {symbol}: {str(e)}")
                        self._handle_symbol_error(symbol, str(e))
                
                # Update monitoring statistics
                self._update_monitoring_stats()
                
                # Calculate sleep time to maintain update interval
                processing_time = time.time() - start_time
                sleep_time = max(1, 60 - processing_time)  # Minimum 1 second, target 60 seconds
                
                self.logger.debug(f"🔄 Monitoring cycle completed in {processing_time:.2f}s, sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"💀 Monitoring loop error: {str(e)}")
                time.sleep(5)  # Short delay on error
        
        self.logger.info("🔄 Main monitoring loop stopped")
    
    def _process_symbol(self, symbol: str):
        """
        Process a single symbol for signals
        
        Args:
            symbol: Symbol to process
        """
        try:
            start_time = time.time()
            
            # Check if symbol is enabled
            symbol_config = self.symbol_configs.get(symbol, {})
            if not symbol_config.get('enabled', True):
                return
            
            # Get symbol status
            symbol_status = self.monitoring_status.symbols.get(symbol)
            if not symbol_status:
                return
            
            # Update symbol state
            symbol_status.state = SymbolState.ACTIVE
            symbol_status.last_update = datetime.now()
            symbol_status.update_count += 1
            
            # Get market data for all timeframes
            timeframes = symbol_config.get('timeframes', ['1h'])
            market_data = {}
            
            for timeframe in timeframes:
                request = DataRequest(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=100,
                    use_cache=True
                )
                
                data = self.market_data_provider.get_klines(request)
                if data and data.candles:
                    market_data[timeframe] = data
                    
                    # Update symbol status with latest price
                    latest_candle = data.candles[-1]
                    symbol_status.current_price = latest_candle.close
            
            if not market_data:
                raise Exception(f"No market data available for {symbol}")
            
            # Record API call performance
            api_time = (time.time() - start_time) * 1000
            self.performance_tracker.record_api_call(f"klines_{symbol}", api_time)
            
            # Generate signals for primary timeframe
            primary_timeframe = timeframes[0]
            if primary_timeframe in market_data:
                signal_start_time = time.time()
                
                signals = self.signal_generator.generate_signals(symbol)
                
                signal_detection_time = (time.time() - signal_start_time) * 1000
                
                # Process signals
                for signal in signals:
                    # Record signal performance
                    self.performance_tracker.record_signal(signal, signal_detection_time)
                    
                    # Update symbol status
                    symbol_status.signal_count += 1
                    symbol_status.latest_signal_type = signal.signal_type.value
                    symbol_status.latest_signal_strength = signal.strength
                    symbol_status.latest_signal_time = signal.timestamp
                    
                    # Send alert
                    self.alert_manager.send_signal_alert(signal)
                    
                    # Log signal
                    self.logger.info(
                        f"🎯 {symbol}: {signal.signal_type.value} "
                        f"| Strength: {signal.strength:.2f} "
                        f"| Price: ${signal.current_price:.4f}"
                    )
            
            # Update performance metrics
            total_time = (time.time() - start_time) * 1000
            symbol_status.avg_update_time_ms = (
                (symbol_status.avg_update_time_ms * (symbol_status.update_count - 1) + total_time) 
                / symbol_status.update_count
            )
            
            # Reset error count on successful processing
            self.error_counts[symbol] = 0
            
        except Exception as e:
            self._handle_symbol_error(symbol, str(e))
    
    def _handle_symbol_error(self, symbol: str, error_message: str):
        """Handle error for a specific symbol"""
        try:
            # Update error tracking
            self.error_counts[symbol] = self.error_counts.get(symbol, 0) + 1
            self.last_errors[symbol] = datetime.now()
            
            # Update symbol status
            symbol_status = self.monitoring_status.symbols.get(symbol)
            if symbol_status:
                symbol_status.error_count += 1
                symbol_status.last_error = error_message
                symbol_status.last_error_time = datetime.now()
            
            # Check if symbol should be paused
            if self.error_counts[symbol] >= self.max_errors_per_symbol:
                if symbol_status:
                    symbol_status.state = SymbolState.ERROR
                
                self.logger.error(f"💀 Symbol {symbol} paused due to excessive errors: {error_message}")
                
                # Send error alert
                from .monitoring_models import AlertType, AlertPriority
                self.alert_manager.send_system_alert(
                    f"Symbol {symbol} paused due to errors: {error_message}",
                    alert_type=AlertType.SYSTEM_ERROR,
                    priority=AlertPriority.HIGH
                )
            else:
                self.logger.warning(f"⚠️ Error processing {symbol} ({self.error_counts[symbol]}/{self.max_errors_per_symbol}): {error_message}")
        
        except Exception as e:
            self.logger.error(f"💀 Error handling failed for {symbol}: {str(e)}")
    
    def _update_monitoring_stats(self):
        """Update overall monitoring statistics"""
        try:
            # Update symbol counts
            self.monitoring_status.update_symbol_counts()
            
            # Update performance metrics
            system_perf = self.performance_tracker.get_system_performance()
            self.monitoring_status.memory_usage_mb = system_perf.get('current_memory_mb', 0)
            self.monitoring_status.cpu_usage_percent = system_perf.get('current_cpu_percent', 0)
            self.monitoring_status.api_calls_per_minute = system_perf.get('api_calls_per_minute', 0)
            
            # Update signal statistics
            signal_perf = self.performance_tracker.get_signal_performance()
            self.monitoring_status.total_signals = signal_perf.get('total_signals', 0)
            
            # Reset error counts for symbols that haven't had errors recently
            current_time = datetime.now()
            for symbol in list(self.error_counts.keys()):
                last_error_time = self.last_errors.get(symbol)
                if last_error_time and (current_time - last_error_time) > self.error_reset_time:
                    self.error_counts[symbol] = 0
                    
                    # Reactivate symbol if it was in error state
                    symbol_status = self.monitoring_status.symbols.get(symbol)
                    if symbol_status and symbol_status.state == SymbolState.ERROR:
                        symbol_status.state = SymbolState.ACTIVE
                        self.logger.info(f"✅ Symbol {symbol} reactivated after error recovery period")
        
        except Exception as e:
            self.logger.error(f"💀 Failed to update monitoring stats: {str(e)}")
    
    def get_monitoring_status(self) -> MonitoringStatus:
        """Get current monitoring status"""
        return self.monitoring_status
    
    def get_symbol_status(self, symbol: str) -> Optional[SymbolStatus]:
        """Get status for a specific symbol"""
        return self.monitoring_status.symbols.get(symbol)
    
    def get_active_symbols(self) -> List[str]:
        """Get list of active symbols"""
        return list(self.active_symbols)
    
    def pause_symbol(self, symbol: str) -> bool:
        """Pause monitoring for a specific symbol"""
        if symbol in self.monitoring_status.symbols:
            self.monitoring_status.symbols[symbol].state = SymbolState.PAUSED
            self.logger.info(f"⏸️ Paused monitoring for {symbol}")
            return True
        return False
    
    def resume_symbol(self, symbol: str) -> bool:
        """Resume monitoring for a specific symbol"""
        if symbol in self.monitoring_status.symbols:
            self.monitoring_status.symbols[symbol].state = SymbolState.ACTIVE
            self.error_counts[symbol] = 0  # Reset error count
            self.logger.info(f"▶️ Resumed monitoring for {symbol}")
            return True
        return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'monitoring_status': {
                'state': self.monitoring_status.state.value,
                'uptime': self.monitoring_status.get_uptime_string(),
                'health_score': self.monitoring_status.get_health_score(),
                'summary': self.monitoring_status.get_summary_line()
            },
            'system_performance': self.performance_tracker.get_system_performance(),
            'signal_performance': self.performance_tracker.get_signal_performance(),
            'alert_stats': self.alert_manager.get_alert_stats(),
            'symbol_count': {
                'total': self.monitoring_status.total_symbols,
                'active': self.monitoring_status.active_symbols,
                'error': self.monitoring_status.error_symbols
            }
        }
    
    def export_monitoring_data(self, filepath: str) -> bool:
        """Export monitoring data to file"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'monitoring_status': {
                    'state': self.monitoring_status.state.value,
                    'start_time': self.monitoring_status.start_time.isoformat(),
                    'uptime_seconds': self.monitoring_status.get_uptime_seconds(),
                    'health_score': self.monitoring_status.get_health_score()
                },
                'symbols': {
                    symbol: {
                        'state': status.state.value,
                        'update_count': status.update_count,
                        'signal_count': status.signal_count,
                        'error_count': status.error_count,
                        'current_price': status.current_price,
                        'latest_signal_type': status.latest_signal_type,
                        'latest_signal_strength': status.latest_signal_strength,
                        'avg_update_time_ms': status.avg_update_time_ms,
                        'is_healthy': status.is_healthy()
                    }
                    for symbol, status in self.monitoring_status.symbols.items()
                },
                'performance_summary': self.get_performance_summary()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"📁 Monitoring data exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to export monitoring data: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown monitoring system"""
        try:
            self.logger.info("🛑 Shutting down Spartan Strategy Monitor...")
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Shutdown components
            self.alert_manager.shutdown()
            self.performance_tracker.shutdown()
            self.market_data_provider.shutdown()
            
            self.logger.info("🏛️ Spartan Strategy Monitor shutdown complete")
            
        except Exception as e:
            self.logger.error(f"💀 Error during shutdown: {str(e)}")