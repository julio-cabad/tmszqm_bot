"""
Alert Manager - Spartan Multi-Crypto Monitoring
Professional alert system with configurable audio and visual notifications
"""

import logging
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import json

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

from ..config.strategy_config import StrategyConfig
from ..strategy.signal_types import TradingSignal, SignalType
from .monitoring_models import AlertConfig, AlertType, AlertPriority


class AlertManager:
    """
    Spartan Alert Manager
    
    Professional alert system with:
    - Configurable audio alerts per symbol
    - Desktop notifications
    - Rate limiting and priority management
    - Alert history and statistics
    - Multi-threading for non-blocking alerts
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Alert Manager
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger("AlertManager")
        
        # Alert configurations per symbol
        self.alert_configs: Dict[str, AlertConfig] = {}
        
        # Alert history and rate limiting
        self.alert_history: deque = deque(maxlen=1000)  # Keep last 1000 alerts
        self.alert_counts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Sound system
        self.sound_enabled = True
        self.sound_volume = 0.7
        self.sound_files_path = "sounds/"
        
        # Threading for non-blocking alerts
        self.alert_queue = deque()
        self.alert_thread = None
        self.alert_thread_running = False
        
        # Statistics
        self.stats = {
            'total_alerts': 0,
            'alerts_by_type': defaultdict(int),
            'alerts_by_symbol': defaultdict(int),
            'alerts_today': 0,
            'last_reset_date': datetime.now().date()
        }
        
        self._initialize_sound_system()
        self._load_default_alert_configs()
        self._start_alert_thread()
        
        self.logger.info("🏛️ Spartan Alert Manager initialized")
        self.logger.info(f"🔊 Sound system: {'Enabled' if self.sound_enabled else 'Disabled'}")
        self.logger.info(f"📱 Desktop notifications: {'Available' if PLYER_AVAILABLE else 'Not available'}")
    
    def _initialize_sound_system(self):
        """Initialize pygame sound system"""
        if not PYGAME_AVAILABLE:
            self.logger.warning("⚠️ pygame not available - audio alerts disabled")
            self.sound_enabled = False
            return
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sound_enabled = True
            self.logger.info("✅ Sound system initialized")
        except Exception as e:
            self.logger.error(f"💀 Failed to initialize sound system: {str(e)}")
            self.sound_enabled = False
    
    def _load_default_alert_configs(self):
        """Load default alert configurations for symbols"""
        # Get symbols from config or use defaults
        from ..config.symbols_config import get_spartan_symbols
        symbols = getattr(self.config, 'symbols', get_spartan_symbols())
        
        for symbol in symbols:
            self.alert_configs[symbol] = AlertConfig(
                symbol=symbol,
                enabled=True,
                min_signal_strength=getattr(self.config, 'min_signal_strength', 0.7)
            )
        
        self.logger.info(f"📋 Loaded alert configs for {len(symbols)} symbols")
    
    def _start_alert_thread(self):
        """Start background thread for processing alerts"""
        self.alert_thread_running = True
        self.alert_thread = threading.Thread(target=self._alert_processor, daemon=True)
        self.alert_thread.start()
        self.logger.info("🚀 Alert processing thread started")
    
    def _alert_processor(self):
        """Background thread to process alert queue"""
        while self.alert_thread_running:
            try:
                if self.alert_queue:
                    alert_data = self.alert_queue.popleft()
                    self._process_alert(alert_data)
                else:
                    time.sleep(0.1)  # Small delay when queue is empty
            except Exception as e:
                self.logger.error(f"💀 Alert processor error: {str(e)}")
                time.sleep(1)  # Longer delay on error
    
    def send_signal_alert(self, signal: TradingSignal) -> bool:
        """
        Send alert for a trading signal
        
        Args:
            signal: Trading signal to alert on
            
        Returns:
            True if alert was sent, False if filtered out
        """
        try:
            # Check if alerts are enabled for this symbol
            alert_config = self.alert_configs.get(signal.symbol)
            if not alert_config or not alert_config.enabled:
                return False
            
            # Check signal strength threshold
            if signal.strength < alert_config.min_signal_strength:
                return False
            
            # Check rate limiting
            if not self._check_rate_limit(signal.symbol, alert_config):
                self.logger.debug(f"⏳ Rate limited alert for {signal.symbol}")
                return False
            
            # Determine alert type and priority
            alert_type, priority = self._get_alert_type_and_priority(signal)
            
            # Create alert data
            alert_data = {
                'type': 'signal',
                'signal': signal,
                'alert_type': alert_type,
                'priority': priority,
                'timestamp': datetime.now(),
                'config': alert_config
            }
            
            # Queue alert for processing
            self.alert_queue.append(alert_data)
            
            # Update statistics
            self._update_stats(signal.symbol, alert_type)
            
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to send signal alert: {str(e)}")
            return False
    
    def send_system_alert(self, message: str, alert_type: AlertType = AlertType.SYSTEM_ERROR, 
                         priority: AlertPriority = AlertPriority.HIGH) -> bool:
        """
        Send system alert (errors, warnings, etc.)
        
        Args:
            message: Alert message
            alert_type: Type of alert
            priority: Alert priority
            
        Returns:
            True if alert was sent
        """
        try:
            alert_data = {
                'type': 'system',
                'message': message,
                'alert_type': alert_type,
                'priority': priority,
                'timestamp': datetime.now()
            }
            
            self.alert_queue.append(alert_data)
            self._update_stats('SYSTEM', alert_type)
            
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to send system alert: {str(e)}")
            return False
    
    def _process_alert(self, alert_data: Dict[str, Any]):
        """Process a single alert"""
        try:
            alert_type = alert_data['alert_type']
            priority = alert_data['priority']
            timestamp = alert_data['timestamp']
            
            if alert_data['type'] == 'signal':
                signal = alert_data['signal']
                config = alert_data['config']
                
                # Create alert message
                message = self._format_signal_message(signal)
                
                # Play sound
                if self.sound_enabled:
                    self._play_alert_sound(alert_type, config)
                
                # Show desktop notification
                if config.show_desktop_notifications:
                    self._show_desktop_notification(signal.symbol, message, priority)
                
                # Log alert
                if config.log_all_signals:
                    self._log_alert(signal.symbol, message, alert_type, priority)
                
            elif alert_data['type'] == 'system':
                message = alert_data['message']
                
                # Play error sound
                if self.sound_enabled:
                    self._play_system_sound(alert_type)
                
                # Show desktop notification
                self._show_desktop_notification("System Alert", message, priority)
                
                # Log alert
                self._log_alert("SYSTEM", message, alert_type, priority)
            
            # Add to history
            self.alert_history.append({
                'timestamp': timestamp,
                'type': alert_data['type'],
                'alert_type': alert_type.value,
                'priority': priority.value,
                'message': message if alert_data['type'] == 'system' else f"{signal.symbol}: {message}"
            })
            
        except Exception as e:
            self.logger.error(f"💀 Failed to process alert: {str(e)}")
    
    def _get_alert_type_and_priority(self, signal: TradingSignal) -> tuple[AlertType, AlertPriority]:
        """Determine alert type and priority based on signal"""
        if signal.signal_type in [SignalType.SUPER_BULLISH, SignalType.SUPER_BEARISH]:
            return AlertType.SUPER_SIGNAL, AlertPriority.HIGH
        elif signal.strength >= 0.8:
            return AlertType.STRONG_SIGNAL, AlertPriority.MEDIUM
        else:
            return AlertType.MEDIUM_SIGNAL, AlertPriority.LOW
    
    def _check_rate_limit(self, symbol: str, config: AlertConfig) -> bool:
        """Check if alert is within rate limits"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old alerts
        symbol_alerts = self.alert_counts[symbol]
        while symbol_alerts and symbol_alerts[0] < hour_ago:
            symbol_alerts.popleft()
        
        # Check limit
        if len(symbol_alerts) >= config.max_alerts_per_hour:
            return False
        
        # Add current alert
        symbol_alerts.append(now)
        return True
    
    def _format_signal_message(self, signal: TradingSignal) -> str:
        """Format signal into readable message"""
        direction_emoji = "🟢" if signal.direction.value == "long" else "🔴"
        strength_stars = "⭐" * min(5, int(signal.strength * 5))
        
        return (f"{direction_emoji} {signal.signal_type.value.upper()} "
                f"| Strength: {signal.strength:.2f} {strength_stars} "
                f"| Price: ${signal.current_price:.4f} "
                f"| Confidence: {signal.confidence:.1%}")
    
    def _play_alert_sound(self, alert_type: AlertType, config: AlertConfig):
        """Play appropriate sound for alert type"""
        if not self.sound_enabled:
            return
        
        try:
            sound_file = None
            
            if alert_type == AlertType.SUPER_SIGNAL:
                sound_file = config.super_signal_sound
            elif alert_type == AlertType.STRONG_SIGNAL:
                sound_file = config.strong_signal_sound
            elif alert_type == AlertType.MEDIUM_SIGNAL:
                sound_file = config.medium_signal_sound
            
            if sound_file:
                self._play_sound_file(sound_file)
                
        except Exception as e:
            self.logger.error(f"💀 Failed to play alert sound: {str(e)}")
    
    def _play_system_sound(self, alert_type: AlertType):
        """Play system sound for errors/warnings"""
        if not self.sound_enabled:
            return
        
        try:
            if alert_type in [AlertType.SYSTEM_ERROR, AlertType.CONNECTION_ISSUE]:
                self._play_sound_file("error_alert.wav")
            elif alert_type == AlertType.RATE_LIMIT:
                self._play_sound_file("warning_alert.wav")
                
        except Exception as e:
            self.logger.error(f"💀 Failed to play system sound: {str(e)}")
    
    def _play_sound_file(self, filename: str):
        """Play a sound file or system sound"""
        try:
            filepath = os.path.join(self.sound_files_path, filename)
            
            # Try to play custom sound file first
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sound_volume)
                sound.play()
                return
            
            # Fallback to system sound on macOS
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                self._play_system_beep(filename)
            else:
                self.logger.debug(f"⚠️ Sound file not found: {filepath}")
                
        except Exception as e:
            self.logger.debug(f"Sound playback failed for {filename}: {str(e)}")
    
    def _play_system_beep(self, sound_type: str):
        """Play system beep sound on macOS"""
        try:
            import subprocess
            
            # Map sound types to system sounds
            sound_map = {
                'error_alert.wav': 'Basso',
                'warning_alert.wav': 'Ping',
                'bullish_alert.wav': 'Glass',
                'bearish_alert.wav': 'Sosumi',
                'breakout_alert.wav': 'Hero'
            }
            
            system_sound = sound_map.get(sound_type, 'Ping')
            subprocess.run(['afplay', f'/System/Library/Sounds/{system_sound}.aiff'], 
                         capture_output=True, timeout=2)
            
        except Exception as e:
            self.logger.debug(f"System sound failed: {str(e)}")
    
    def _show_desktop_notification(self, title: str, message: str, priority: AlertPriority):
        """Show desktop notification"""
        try:
            # Try native macOS notification first
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                self._show_macos_notification(title, message)
                return
            
            # Fallback to plyer if available
            if PLYER_AVAILABLE:
                timeout_map = {
                    AlertPriority.CRITICAL: 10,
                    AlertPriority.HIGH: 8,
                    AlertPriority.MEDIUM: 5,
                    AlertPriority.LOW: 3,
                    AlertPriority.INFO: 2
                }
                
                timeout = timeout_map.get(priority, 5)
                
                plyer.notification.notify(
                    title=f"Spartan Trading - {title}",
                    message=message,
                    timeout=timeout,
                    app_name="Spartan Trading System"
                )
            else:
                # Log notification if no system available
                self.logger.info(f"📱 NOTIFICATION: {title} - {message}")
                
        except Exception as e:
            self.logger.error(f"💀 Failed to show desktop notification: {str(e)}")
    
    def _show_macos_notification(self, title: str, message: str):
        """Show native macOS notification using osascript"""
        try:
            import subprocess
            
            # Escape quotes in title and message
            title = title.replace('"', '\\"')
            message = message.replace('"', '\\"')
            
            # Use osascript to show notification
            script = f'''
            display notification "{message}" with title "🏛️⚔️ Spartan Trading" subtitle "{title}"
            '''
            
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, text=True, timeout=5)
            
        except Exception as e:
            self.logger.debug(f"macOS notification failed: {str(e)}")
            # Fallback to console log
            self.logger.info(f"📱 NOTIFICATION: {title} - {message}")
    
    def _log_alert(self, symbol: str, message: str, alert_type: AlertType, priority: AlertPriority):
        """Log alert to console and file"""
        # Only log critical alerts to avoid interfering with display
        if priority == AlertPriority.CRITICAL:
            priority_emoji = "🚨"
            log_message = f"{priority_emoji} [{symbol}] {message}"
            self.logger.error(log_message)
        else:
            # Store in history but don't log to console to keep display clean
            pass
    
    def _update_stats(self, symbol: str, alert_type: AlertType):
        """Update alert statistics"""
        now = datetime.now()
        
        # Reset daily count if new day
        if now.date() > self.stats['last_reset_date']:
            self.stats['alerts_today'] = 0
            self.stats['last_reset_date'] = now.date()
        
        self.stats['total_alerts'] += 1
        self.stats['alerts_today'] += 1
        self.stats['alerts_by_type'][alert_type.value] += 1
        self.stats['alerts_by_symbol'][symbol] += 1
    
    def configure_symbol_alerts(self, symbol: str, config: AlertConfig):
        """Configure alerts for a specific symbol"""
        self.alert_configs[symbol] = config
        self.logger.info(f"📋 Updated alert config for {symbol}")
    
    def enable_symbol_alerts(self, symbol: str, enabled: bool = True):
        """Enable/disable alerts for a symbol"""
        if symbol in self.alert_configs:
            self.alert_configs[symbol].enabled = enabled
            status = "enabled" if enabled else "disabled"
            self.logger.info(f"🔔 Alerts {status} for {symbol}")
    
    def set_sound_volume(self, volume: float):
        """Set sound volume (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        self.logger.info(f"🔊 Sound volume set to {self.sound_volume:.1%}")
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return {
            'total_alerts': self.stats['total_alerts'],
            'alerts_today': self.stats['alerts_today'],
            'alerts_by_type': dict(self.stats['alerts_by_type']),
            'alerts_by_symbol': dict(self.stats['alerts_by_symbol']),
            'alert_history_size': len(self.alert_history),
            'sound_enabled': self.sound_enabled,
            'sound_volume': self.sound_volume,
            'configured_symbols': len(self.alert_configs)
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return list(self.alert_history)[-limit:]
    
    def shutdown(self):
        """Shutdown alert manager"""
        self.alert_thread_running = False
        
        if self.alert_thread and self.alert_thread.is_alive():
            self.alert_thread.join(timeout=2)
        
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            pygame.mixer.quit()
        
        self.logger.info("🏛️ Spartan Alert Manager shutdown complete")