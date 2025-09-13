"""
Performance Tracker - Spartan Multi-Crypto Monitoring
Professional performance tracking with detailed metrics and statistics
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import json
import psutil
import os

from ..config.strategy_config import StrategyConfig
from ..strategy.signal_types import TradingSignal, SignalType
from .monitoring_models import PerformanceMetrics


class PerformanceTracker:
    """
    Spartan Performance Tracker
    
    Professional performance monitoring with:
    - Signal detection timing and accuracy
    - System resource monitoring
    - API usage tracking
    - Symbol-specific performance metrics
    - Historical performance analysis
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Performance Tracker
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger("PerformanceTracker")
        
        # Performance metrics per symbol
        self.symbol_metrics: Dict[str, PerformanceMetrics] = {}
        
        # System performance tracking
        self.system_metrics = {
            'start_time': datetime.now(),
            'cpu_usage_history': deque(maxlen=100),
            'memory_usage_history': deque(maxlen=100),
            'api_call_times': deque(maxlen=1000),
            'signal_detection_times': deque(maxlen=1000)
        }
        
        # API usage tracking
        self.api_stats = {
            'total_calls': 0,
            'calls_per_minute': deque(maxlen=60),
            'weight_usage': deque(maxlen=60),
            'rate_limit_hits': 0,
            'avg_response_time_ms': 0.0
        }
        
        # Signal performance tracking
        self.signal_stats = {
            'total_signals': 0,
            'signals_by_type': defaultdict(int),
            'signals_by_symbol': defaultdict(int),
            'avg_signal_strength': 0.0,
            'signal_strength_history': deque(maxlen=1000)
        }
        
        # Performance monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        self._initialize_symbol_metrics()
        self._start_monitoring_thread()
        
        self.logger.info("🏛️ Spartan Performance Tracker initialized")
    
    def _initialize_symbol_metrics(self):
        """Initialize performance metrics for configured symbols"""
        from ..config.symbols_config import get_spartan_symbols
        symbols = getattr(self.config, 'symbols', get_spartan_symbols())
        
        for symbol in symbols:
            self.symbol_metrics[symbol] = PerformanceMetrics(
                symbol=symbol,
                timeframe=getattr(self.config, 'primary_timeframe', '1h')
            )
        
        self.logger.info(f"📊 Initialized metrics for {len(symbols)} symbols")
    
    def _start_monitoring_thread(self):
        """Start background thread for system monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._system_monitor, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("🚀 Performance monitoring thread started")
    
    def _system_monitor(self):
        """Background thread to monitor system resources"""
        while self.monitoring_active:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                memory_mb = memory_info.used / (1024 * 1024)
                
                # Store metrics
                self.system_metrics['cpu_usage_history'].append({
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent
                })
                
                self.system_metrics['memory_usage_history'].append({
                    'timestamp': datetime.now(),
                    'memory_mb': memory_mb,
                    'memory_percent': memory_info.percent
                })
                
                # Clean old API call times (older than 1 minute)
                cutoff_time = time.time() - 60
                while (self.api_stats['calls_per_minute'] and 
                       self.api_stats['calls_per_minute'][0]['timestamp'] < cutoff_time):
                    self.api_stats['calls_per_minute'].popleft()
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"💀 System monitoring error: {str(e)}")
                time.sleep(10)  # Longer delay on error
    
    def record_signal(self, signal: TradingSignal, detection_time_ms: float = 0.0):
        """
        Record a trading signal for performance tracking
        
        Args:
            signal: Trading signal to record
            detection_time_ms: Time taken to detect signal in milliseconds
        """
        try:
            # Update symbol-specific metrics
            if signal.symbol in self.symbol_metrics:
                metrics = self.symbol_metrics[signal.symbol]
                metrics.total_signals += 1
                metrics.last_update = datetime.now()
                
                # Update signal type counts
                if signal.signal_type in [SignalType.SUPER_BULLISH, SignalType.SUPER_BEARISH]:
                    metrics.super_signals += 1
                elif signal.strength >= 0.8:
                    metrics.strong_signals += 1
                else:
                    metrics.medium_signals += 1
                
                # Update timing metrics
                if detection_time_ms > 0:
                    if metrics.avg_signal_detection_time_ms == 0:
                        metrics.avg_signal_detection_time_ms = detection_time_ms
                    else:
                        # Running average
                        metrics.avg_signal_detection_time_ms = (
                            (metrics.avg_signal_detection_time_ms * (metrics.total_signals - 1) + detection_time_ms) 
                            / metrics.total_signals
                        )
                    
                    metrics.max_signal_detection_time_ms = max(
                        metrics.max_signal_detection_time_ms, 
                        detection_time_ms
                    )
                
                # Calculate signals per hour
                metrics.calculate_signals_per_hour()
            
            # Update global signal stats
            self.signal_stats['total_signals'] += 1
            self.signal_stats['signals_by_type'][signal.signal_type.value] += 1
            self.signal_stats['signals_by_symbol'][signal.symbol] += 1
            
            # Update average signal strength
            self.signal_stats['signal_strength_history'].append(signal.strength)
            if self.signal_stats['signal_strength_history']:
                self.signal_stats['avg_signal_strength'] = (
                    sum(self.signal_stats['signal_strength_history']) / 
                    len(self.signal_stats['signal_strength_history'])
                )
            
            # Record detection time
            if detection_time_ms > 0:
                self.system_metrics['signal_detection_times'].append({
                    'timestamp': datetime.now(),
                    'symbol': signal.symbol,
                    'detection_time_ms': detection_time_ms,
                    'signal_type': signal.signal_type.value
                })
            
            self.logger.debug(f"📊 Recorded signal: {signal.symbol} {signal.signal_type.value}")
            
        except Exception as e:
            self.logger.error(f"💀 Failed to record signal: {str(e)}")
    
    def record_api_call(self, endpoint: str, response_time_ms: float, weight: int = 1):
        """
        Record API call performance
        
        Args:
            endpoint: API endpoint called
            response_time_ms: Response time in milliseconds
            weight: API weight used
        """
        try:
            current_time = time.time()
            
            # Record API call
            self.api_stats['total_calls'] += 1
            self.api_stats['calls_per_minute'].append({
                'timestamp': current_time,
                'endpoint': endpoint,
                'response_time_ms': response_time_ms,
                'weight': weight
            })
            
            # Update average response time
            self.system_metrics['api_call_times'].append({
                'timestamp': datetime.now(),
                'endpoint': endpoint,
                'response_time_ms': response_time_ms
            })
            
            if self.system_metrics['api_call_times']:
                total_time = sum(call['response_time_ms'] for call in self.system_metrics['api_call_times'])
                self.api_stats['avg_response_time_ms'] = total_time / len(self.system_metrics['api_call_times'])
            
            self.logger.debug(f"📡 API call recorded: {endpoint} ({response_time_ms:.1f}ms)")
            
        except Exception as e:
            self.logger.error(f"💀 Failed to record API call: {str(e)}")
    
    def record_rate_limit_hit(self):
        """Record a rate limit hit"""
        self.api_stats['rate_limit_hits'] += 1
        self.logger.warning("⏳ Rate limit hit recorded")
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # Current system stats
            current_cpu = psutil.cpu_percent()
            current_memory = psutil.virtual_memory()
            
            # Calculate averages
            cpu_history = [entry['cpu_percent'] for entry in self.system_metrics['cpu_usage_history']]
            avg_cpu = sum(cpu_history) / len(cpu_history) if cpu_history else 0
            
            memory_history = [entry['memory_mb'] for entry in self.system_metrics['memory_usage_history']]
            avg_memory_mb = sum(memory_history) / len(memory_history) if memory_history else 0
            
            # API performance
            api_calls_last_minute = len(self.api_stats['calls_per_minute'])
            
            return {
                'uptime_seconds': (datetime.now() - self.system_metrics['start_time']).total_seconds(),
                'current_cpu_percent': current_cpu,
                'avg_cpu_percent': avg_cpu,
                'current_memory_mb': current_memory.used / (1024 * 1024),
                'current_memory_percent': current_memory.percent,
                'avg_memory_mb': avg_memory_mb,
                'api_calls_per_minute': api_calls_last_minute,
                'avg_api_response_time_ms': self.api_stats['avg_response_time_ms'],
                'total_api_calls': self.api_stats['total_calls'],
                'rate_limit_hits': self.api_stats['rate_limit_hits']
            }
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get system performance: {str(e)}")
            return {}
    
    def get_signal_performance(self) -> Dict[str, Any]:
        """Get signal detection performance metrics"""
        try:
            # Calculate detection time stats
            detection_times = [
                entry['detection_time_ms'] 
                for entry in self.system_metrics['signal_detection_times']
            ]
            
            avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0
            max_detection_time = max(detection_times) if detection_times else 0
            
            return {
                'total_signals': self.signal_stats['total_signals'],
                'avg_signal_strength': self.signal_stats['avg_signal_strength'],
                'signals_by_type': dict(self.signal_stats['signals_by_type']),
                'signals_by_symbol': dict(self.signal_stats['signals_by_symbol']),
                'avg_detection_time_ms': avg_detection_time,
                'max_detection_time_ms': max_detection_time,
                'detection_samples': len(detection_times)
            }
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get signal performance: {str(e)}")
            return {}
    
    def get_symbol_performance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific symbol"""
        if symbol not in self.symbol_metrics:
            return None
        
        try:
            metrics = self.symbol_metrics[symbol]
            return metrics.get_performance_summary()
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get symbol performance for {symbol}: {str(e)}")
            return None
    
    def get_all_symbol_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for all symbols"""
        results = {}
        
        for symbol in self.symbol_metrics:
            performance = self.get_symbol_performance(symbol)
            if performance:
                results[symbol] = performance
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            system_perf = self.get_system_performance()
            signal_perf = self.get_signal_performance()
            
            # Top performing symbols
            symbol_signals = [(symbol, metrics.total_signals) 
                            for symbol, metrics in self.symbol_metrics.items()]
            symbol_signals.sort(key=lambda x: x[1], reverse=True)
            top_symbols = symbol_signals[:5]
            
            return {
                'system_performance': system_perf,
                'signal_performance': signal_perf,
                'top_symbols_by_signals': top_symbols,
                'total_symbols_monitored': len(self.symbol_metrics),
                'monitoring_active': self.monitoring_active
            }
            
        except Exception as e:
            self.logger.error(f"💀 Failed to get performance summary: {str(e)}")
            return {}
    
    def reset_symbol_metrics(self, symbol: str):
        """Reset performance metrics for a symbol"""
        if symbol in self.symbol_metrics:
            self.symbol_metrics[symbol] = PerformanceMetrics(
                symbol=symbol,
                timeframe=self.symbol_metrics[symbol].timeframe
            )
            self.logger.info(f"🔄 Reset metrics for {symbol}")
    
    def export_performance_data(self, filepath: str) -> bool:
        """Export performance data to JSON file"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'system_performance': self.get_system_performance(),
                'signal_performance': self.get_signal_performance(),
                'symbol_performance': self.get_all_symbol_performance(),
                'api_stats': {
                    'total_calls': self.api_stats['total_calls'],
                    'avg_response_time_ms': self.api_stats['avg_response_time_ms'],
                    'rate_limit_hits': self.api_stats['rate_limit_hits']
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"📁 Performance data exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to export performance data: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown performance tracker"""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
        
        self.logger.info("🏛️ Spartan Performance Tracker shutdown complete")