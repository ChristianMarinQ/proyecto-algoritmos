"""
Simple in-memory cache for API results.
Stores computed results so they don't need to be regenerated on every request.
"""


class CacheService:
    """
    Singleton cache that stores endpoint results in memory.
    Results persist until the server is restarted or cache is cleared.
    """
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get(cls, key: str):
        """Get a cached result by key, returns None if not found"""
        return cls._cache.get(key, None)

    @classmethod
    def set(cls, key: str, value):
        """Store a result in cache"""
        cls._cache[key] = value

    @classmethod
    def clear(cls):
        """Clear all cached results"""
        cls._cache = {}

    @classmethod
    def has(cls, key: str) -> bool:
        """Check if a key exists in cache"""
        return key in cls._cache
