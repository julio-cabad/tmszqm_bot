"""
Data Cache System for Spartan Trading
High-performance caching with TTL and memory management
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import pickle
import hashlib
from collections import OrderedDict

from .data_models import MarketData, CandleData, DataRequest, DataSource


class CacheEntry:
    """Cache entry with metadata"""
    
    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.access_count = 0
        self.last_accessed = self.created_at
        self.size_bytes = self._calculate_size()
    
    def _calculate_size(self) -> int:
        """Estimate memory size of cached data"""
        try:
            return len(pickle.dumps(self.data))
        except Exception:
            return 1024  # Default estimate
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() > self.expires_at
    
    def is_stale(self, max_age_seconds: int = 60) -> bool:
        """Check if data is considered stale"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > max_age_seconds
    
    def access(self) -> Any:
        """Access cached data and update statistics"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.data
    
    def get_age_seconds(self) -> float:
        """Get age of cache entry in seconds"""
        return (datetime.now() - self.created_at).total_seconds()


class DataCache:
    """
    Spartan Data Cache System
    
    High-performance in-memory cache with:
    - TTL (Time To Live) support
    - LRU (Least Recently Used) eviction
    - Memory management
    - Thread-safe operations
    - Cache statistics
    """
    
    def __init__(self, max_size_mb: int = 100, default_ttl: int = 300):
        """
        Initialize Data Cache
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            default_ttl: Default TTL in seconds
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        
        # Cache storage (OrderedDict for LRU)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.current_size_bytes = 0
        
        # Cleanup thread
        self._cleanup_interval = 60  # 1 minute
        self._cleanup_thread = None
        self._stop_cleanup = False
        
        self.logger = logging.getLogger("DataCache")
        self.logger.info(f"🏛️ Spartan Data Cache initialized: {max_size_mb}MB max, {default_ttl}s TTL")
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while not self._stop_cleanup:
                try:
                    self._cleanup_expired()
                    time.sleep(self._cleanup_interval)
                except Exception as e:
                    self.logger.error(f"💀 Cache cleanup error: {str(e)}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _generate_key(self, request: DataRequest) -> str:
        """Generate cache key from data request"""
        return request.get_cache_key()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                self.logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    def _remove_entry(self, key: str):
        """Remove cache entry and update size"""
        if key in self._cache:
            entry = self._cache.pop(key)
            self.current_size_bytes -= entry.size_bytes
            self.evictions += 1
    
    def _evict_lru(self):
        """Evict least recently used entries to free space"""
        target_size = self.max_size_bytes * 0.8  # Evict to 80% capacity
        
        while self.current_size_bytes > target_size and self._cache:
            # Remove oldest entry (LRU)
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)
    
    def _ensure_capacity(self, new_entry_size: int):
        """Ensure cache has capacity for new entry"""
        if self.current_size_bytes + new_entry_size > self.max_size_bytes:
            self._evict_lru()
    
    def get(self, request: DataRequest) -> Optional[MarketData]:
        """
        Get cached market data
        
        Args:
            request: Data request specification
            
        Returns:
            Cached MarketData or None if not found/expired
        """
        if not request.use_cache:
            return None
        
        key = self._generate_key(request)
        
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.misses += 1
                return None
            
            # Check if force refresh is requested
            if request.force_refresh:
                self._remove_entry(key)
                self.misses += 1
                return None
            
            # Check staleness
            if entry.is_stale(request.cache_timeout):
                self._remove_entry(key)
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            self.hits += 1
            data = entry.access()
            
            self.logger.debug(f"📊 Cache HIT: {key} (age: {entry.get_age_seconds():.1f}s)")
            return data
    
    def put(self, request: DataRequest, data: MarketData, ttl: Optional[int] = None):
        """
        Store market data in cache
        
        Args:
            request: Data request that generated this data
            data: MarketData to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if not request.use_cache:
            return
        
        key = self._generate_key(request)
        ttl = ttl or self.default_ttl
        
        with self._lock:
            # Create cache entry
            entry = CacheEntry(data, ttl)
            
            # Ensure capacity
            self._ensure_capacity(entry.size_bytes)
            
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Add new entry
            self._cache[key] = entry
            self.current_size_bytes += entry.size_bytes
            
            self.logger.debug(f"💾 Cache PUT: {key} (size: {entry.size_bytes} bytes, TTL: {ttl}s)")
    
    def invalidate(self, symbol: str, timeframe: Optional[str] = None):
        """
        Invalidate cache entries for a symbol
        
        Args:
            symbol: Symbol to invalidate
            timeframe: Specific timeframe to invalidate (all if None)
        """
        with self._lock:
            keys_to_remove = []
            
            for key in self._cache.keys():
                if symbol in key:
                    if timeframe is None or timeframe in key:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            if keys_to_remove:
                self.logger.info(f"🗑️ Invalidated {len(keys_to_remove)} cache entries for {symbol}")
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self.current_size_bytes = 0
            self.logger.info("🧹 Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'entries': len(self._cache),
                'size_mb': self.current_size_bytes / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'utilization_pct': (self.current_size_bytes / self.max_size_bytes * 100),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate_pct': hit_rate,
                'evictions': self.evictions,
                'total_requests': total_requests
            }
    
    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Get information about cached entries"""
        with self._lock:
            entries_info = []
            
            for key, entry in self._cache.items():
                entries_info.append({
                    'key': key,
                    'size_bytes': entry.size_bytes,
                    'age_seconds': entry.get_age_seconds(),
                    'access_count': entry.access_count,
                    'expires_in_seconds': (entry.expires_at - datetime.now()).total_seconds(),
                    'is_expired': entry.is_expired()
                })
            
            return entries_info
    
    def optimize(self):
        """Optimize cache by removing expired entries and defragmenting"""
        with self._lock:
            # Remove expired entries
            self._cleanup_expired()
            
            # If still over capacity, evict LRU entries
            if self.current_size_bytes > self.max_size_bytes * 0.9:
                self._evict_lru()
            
            self.logger.info(f"🔧 Cache optimized: {len(self._cache)} entries, {self.current_size_bytes / (1024*1024):.1f}MB")
    
    def shutdown(self):
        """Shutdown cache and cleanup thread"""
        self._stop_cleanup = True
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        self.clear()
        self.logger.info("🏛️ Spartan Data Cache shutdown complete")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.shutdown()
        except Exception:
            pass