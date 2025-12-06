"""
Cache Manager for Travelopedia
Provides in-memory caching for API responses and session data
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from collections import OrderedDict
from pathlib import Path


class CacheManager:
    """In-memory cache manager with TTL support."""
    
    def __init__(self, max_size=1000, default_ttl=3600):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
        self.cache_file = Path("output/cache_data.json")
        self.cache_file.parent.mkdir(exist_ok=True)
    
    def _generate_key(self, *args, **kwargs):
        """Generate cache key from arguments."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if entry['expires_at'] > time.time():
                self.hits += 1
                # Move to end (LRU)
                self.cache.move_to_end(key)
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key, value, ttl=None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
    
    def delete(self, key):
        """Delete entry from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self):
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def cleanup_expired(self):
        """Remove all expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def save_to_disk(self):
        """Save cache to disk for persistence."""
        cache_data = {
            'cache': dict(self.cache),
            'stats': self.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_disk(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Restore cache entries that haven't expired
                current_time = time.time()
                for key, entry in cache_data.get('cache', {}).items():
                    if entry['expires_at'] > current_time:
                        self.cache[key] = entry
                
                return True
            except Exception as e:
                print(f"Error loading cache from disk: {e}")
                return False
        return False


class SessionCache:
    """Session-specific cache for user data."""
    
    def __init__(self):
        """Initialize session cache."""
        self.sessions = {}
        self.session_ttl = 3600  # 1 hour
    
    def create_session(self, session_id):
        """Create a new session."""
        self.sessions[session_id] = {
            'data': {},
            'created_at': time.time(),
            'last_accessed': time.time()
        }
    
    def get_session(self, session_id):
        """Get session data."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Check if expired
            if time.time() - session['last_accessed'] < self.session_ttl:
                session['last_accessed'] = time.time()
                return session['data']
            else:
                # Remove expired session
                del self.sessions[session_id]
        
        return None
    
    def set_session_data(self, session_id, key, value):
        """Set data in session."""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]['data'][key] = value
        self.sessions[session_id]['last_accessed'] = time.time()
    
    def get_session_data(self, session_id, key, default=None):
        """Get data from session."""
        session_data = self.get_session(session_id)
        if session_data:
            return session_data.get(key, default)
        return default
    
    def delete_session(self, session_id):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session['last_accessed'] >= self.session_ttl
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
        
        return len(expired_sessions)


# Global cache instances
_global_cache = None
_session_cache = None


def get_cache():
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
        _global_cache.load_from_disk()
    return _global_cache


def get_session_cache():
    """Get session cache instance."""
    global _session_cache
    if _session_cache is None:
        _session_cache = SessionCache()
    return _session_cache


def cache_api_response(func):
    """Decorator to cache API responses."""
    def wrapper(*args, **kwargs):
        cache = get_cache()
        
        # Generate cache key
        key = cache._generate_key(func.__name__, *args, **kwargs)
        
        # Try to get from cache
        cached_value = cache.get(key)
        if cached_value is not None:
            return cached_value
        
        # Call function and cache result
        result = func(*args, **kwargs)
        cache.set(key, result)
        
        return result
    
    return wrapper
