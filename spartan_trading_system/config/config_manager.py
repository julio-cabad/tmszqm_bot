"""
Configuration Manager for Spartan Trading System
Handles loading, saving, and validation of strategy configurations
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .strategy_config import StrategyConfig


class ConfigurationError(Exception):
    """Configuration related errors"""
    pass


class ConfigManager:
    """
    Spartan Configuration Manager
    
    Handles all configuration operations with validation, backup, and error recovery
    """
    
    def __init__(self, config_dir: str = "configs"):
        """
        Initialize Configuration Manager
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("ConfigManager")
        self.logger.info(f"🏛️ Spartan Config Manager initialized: {self.config_dir}")
    
    def load_config(self, config_path: str) -> StrategyConfig:
        """
        Load configuration from file with validation
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            StrategyConfig instance
            
        Raises:
            ConfigurationError: If config is invalid or file not found
        """
        try:
            config_file = self.config_dir / config_path
            
            if not config_file.exists():
                self.logger.warning(f"⚠️ Config file not found: {config_file}")
                self.logger.info("🔧 Creating default configuration...")
                return self.get_default_config()
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            config = StrategyConfig.from_dict(config_data)
            
            # Validate configuration
            errors = self.validate_config(config)
            if errors:
                error_msg = f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
                self.logger.error(f"💀 {error_msg}")
                raise ConfigurationError(error_msg)
            
            self.logger.info(f"✅ Configuration loaded successfully: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file {config_path}: {str(e)}"
            self.logger.error(f"💀 {error_msg}")
            raise ConfigurationError(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to load config {config_path}: {str(e)}"
            self.logger.error(f"💀 {error_msg}")
            raise ConfigurationError(error_msg)
    
    def save_config(self, config: StrategyConfig, config_path: str, create_backup: bool = True) -> bool:
        """
        Save configuration to file with backup
        
        Args:
            config: StrategyConfig to save
            config_path: Path to save configuration
            create_backup: Whether to create backup of existing file
            
        Returns:
            True if successful
            
        Raises:
            ConfigurationError: If save fails
        """
        try:
            config_file = self.config_dir / config_path
            
            # Validate before saving
            errors = self.validate_config(config)
            if errors:
                error_msg = f"Cannot save invalid configuration:\n" + "\n".join(f"  - {error}" for error in errors)
                self.logger.error(f"💀 {error_msg}")
                raise ConfigurationError(error_msg)
            
            # Create backup if file exists
            if create_backup and config_file.exists():
                backup_path = config_file.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                config_file.rename(backup_path)
                self.logger.info(f"📦 Backup created: {backup_path.name}")
            
            # Save configuration
            with open(config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            self.logger.info(f"✅ Configuration saved: {config_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save config {config_path}: {str(e)}"
            self.logger.error(f"💀 {error_msg}")
            raise ConfigurationError(error_msg)
    
    def validate_config(self, config: StrategyConfig) -> List[str]:
        """
        Validate configuration parameters
        
        Args:
            config: StrategyConfig to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        return config.validate()
    
    def get_default_config(self) -> StrategyConfig:
        """
        Get default configuration
        
        Returns:
            Default StrategyConfig
        """
        return StrategyConfig()
    
    def create_default_configs(self) -> None:
        """
        Create default configuration files for different trading styles
        """
        try:
            # Default configuration
            default_config = self.get_default_config()
            self.save_config(default_config, "default.json", create_backup=False)
            
            # Conservative configuration
            conservative_config = StrategyConfig(
                risk_percentage=1.0,
                max_positions=2,
                min_signal_strength=0.8,
                primary_timeframe="4h",
                confirmation_timeframe="1h",
                context_timeframe="1d",
                symbols=[
                    "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT"
                ]
            )
            self.save_config(conservative_config, "conservative.json", create_backup=False)
            
            # Aggressive configuration
            aggressive_config = StrategyConfig(
                risk_percentage=3.0,
                max_positions=5,
                min_signal_strength=0.6,
                primary_timeframe="30m",
                confirmation_timeframe="15m",
                context_timeframe="1h",
                update_interval=15,
                symbols=[
                    "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT",
                    "BNBUSDT", "XRPUSDT", "MATICUSDT", "AVAXUSDT", "LINKUSDT",
                    "ATOMUSDT", "ALGOUSDT", "VETUSDT", "FTMUSDT", "NEARUSDT"
                ]
            )
            self.save_config(aggressive_config, "aggressive.json", create_backup=False)
            
            # Scalping configuration (shorter timeframes)
            scalping_config = StrategyConfig(
                risk_percentage=1.5,
                max_positions=3,
                min_signal_strength=0.75,
                primary_timeframe="15m",
                confirmation_timeframe="5m",
                context_timeframe="30m",
                monitoring_timeframe="1m",
                update_interval=10,
                candles_limit=50,  # Faster for scalping
                symbols=[
                    "BTCUSDT", "ETHUSDT", "BNBUSDT"  # High volume pairs only
                ]
            )
            self.save_config(scalping_config, "scalping.json", create_backup=False)
            
            self.logger.info("✅ Default configuration files created")
            
        except Exception as e:
            self.logger.error(f"💀 Failed to create default configs: {str(e)}")
            raise ConfigurationError(f"Failed to create default configs: {str(e)}")
    
    def list_configs(self) -> List[str]:
        """
        List available configuration files
        
        Returns:
            List of configuration file names
        """
        try:
            config_files = [f.name for f in self.config_dir.glob("*.json") if not f.name.startswith("backup_")]
            return sorted(config_files)
        except Exception as e:
            self.logger.error(f"💀 Failed to list configs: {str(e)}")
            return []
    
    def delete_config(self, config_path: str, create_backup: bool = True) -> bool:
        """
        Delete configuration file
        
        Args:
            config_path: Path to configuration file
            create_backup: Whether to create backup before deletion
            
        Returns:
            True if successful
        """
        try:
            config_file = self.config_dir / config_path
            
            if not config_file.exists():
                self.logger.warning(f"⚠️ Config file not found: {config_path}")
                return False
            
            if create_backup:
                backup_path = config_file.with_suffix(f".deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                config_file.rename(backup_path)
                self.logger.info(f"🗑️ Config deleted with backup: {config_path} -> {backup_path.name}")
            else:
                config_file.unlink()
                self.logger.info(f"🗑️ Config deleted: {config_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to delete config {config_path}: {str(e)}")
            return False
    
    def copy_config(self, source_path: str, dest_path: str) -> bool:
        """
        Copy configuration file
        
        Args:
            source_path: Source configuration file
            dest_path: Destination configuration file
            
        Returns:
            True if successful
        """
        try:
            config = self.load_config(source_path)
            self.save_config(config, dest_path, create_backup=False)
            self.logger.info(f"📋 Config copied: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to copy config: {str(e)}")
            return False
    
    def export_config(self, config: StrategyConfig, export_path: str) -> bool:
        """
        Export configuration to external file
        
        Args:
            config: StrategyConfig to export
            export_path: External file path
            
        Returns:
            True if successful
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            self.logger.info(f"📤 Config exported: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to export config: {str(e)}")
            return False
    
    def import_config(self, import_path: str, config_name: str) -> StrategyConfig:
        """
        Import configuration from external file
        
        Args:
            import_path: External file path
            config_name: Name for imported config
            
        Returns:
            Imported StrategyConfig
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                raise ConfigurationError(f"Import file not found: {import_path}")
            
            with open(import_file, 'r') as f:
                config_data = json.load(f)
            
            config = StrategyConfig.from_dict(config_data)
            
            # Validate imported config
            errors = self.validate_config(config)
            if errors:
                error_msg = f"Imported configuration is invalid:\n" + "\n".join(f"  - {error}" for error in errors)
                raise ConfigurationError(error_msg)
            
            # Save imported config
            self.save_config(config, config_name, create_backup=False)
            
            self.logger.info(f"📥 Config imported: {import_path} -> {config_name}")
            return config
            
        except Exception as e:
            error_msg = f"Failed to import config from {import_path}: {str(e)}"
            self.logger.error(f"💀 {error_msg}")
            raise ConfigurationError(error_msg)
    
    def get_config_info(self, config_path: str) -> Dict[str, Any]:
        """
        Get information about a configuration file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary with config information
        """
        try:
            config_file = self.config_dir / config_path
            
            if not config_file.exists():
                return {"exists": False}
            
            config = self.load_config(config_path)
            stat = config_file.stat()
            
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "symbols_count": len(config.symbols),
                "primary_timeframe": config.primary_timeframe,
                "trend_magic_version": config.trend_magic_version,
                "risk_percentage": config.risk_percentage,
                "validation_errors": self.validate_config(config)
            }
            
        except Exception as e:
            return {
                "exists": True,
                "error": str(e)
            }