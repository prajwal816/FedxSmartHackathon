"""
Cache Manager for storing and retrieving optimization results
"""

import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import pickle
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of route optimization results and external API data"""
    
    def __init__(self):
        self.cache_dir = "cache"
        self.route_cache = {}
        self.api_cache = {}
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def store_route(self, route_id: str, route_data: Any) -> bool:
        """
        Store route optimization result
        
        Args:
            route_id: Unique route identifier
            route_data: Route optimization result
            
        Returns:
            Success status
        """
        try:
            # Store in memory cache
            self.route_cache[route_id] = {
                'data': route_data,
                'timestamp': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
            
            # Store to disk for persistence
            cache_file = os.path.join(self.cache_dir, f"route_{route_id}.pkl")
            with open(cache_file, 'wb') as f:
                pickle.dump(self.route_cache[route_id], f)
            
            logger.info(f"Route {route_id} cached successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache route {route_id}: {str(e)}")
            return False
    
    def get_route(self, route_id: str) -> Optional[Any]:
        """
        Retrieve cached route data
        
        Args:
            route_id: Route identifier
            
        Returns:
            Cached route data or None
        """
        try:
            # Check memory cache first
            if route_id in self.route_cache:
                cached_item = self.route_cache[route_id]
                
                # Check if expired
                if datetime.utcnow() < cached_item['expires_at']:
                    logger.info(f"Route {route_id} retrieved from memory cache")
                    return cached_item['data']
                else:
                    # Remove expired item
                    del self.route_cache[route_id]
            
            # Check disk cache
            cache_file = os.path.join(self.cache_dir, f"route_{route_id}.pkl")
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cached_item = pickle.load(f)
                
                # Check if expired
                if datetime.utcnow() < cached_item['expires_at']:
                    # Load back to memory cache
                    self.route_cache[route_id] = cached_item
                    logger.info(f"Route {route_id} retrieved from disk cache")
                    return cached_item['data']
                else:
                    # Remove expired file
                    os.remove(cache_file)
            
            logger.info(f"Route {route_id} not found in cache")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve route {route_id} from cache: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """
        Store general cache data
        
        Args:
            key: Cache key
            value: Data to cache
            timeout: Expiration timeout in seconds
            
        Returns:
            Success status
        """
        try:
            self.api_cache[key] = {
                'data': value,
                'timestamp': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=timeout)
            }
            
            logger.debug(f"Cached data with key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache data with key {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve general cache data
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None
        """
        try:
            if key in self.api_cache:
                cached_item = self.api_cache[key]
                
                # Check if expired
                if datetime.utcnow() < cached_item['expires_at']:
                    logger.debug(f"Retrieved cached data for key: {key}")
                    return cached_item['data']
                else:
                    # Remove expired item
                    del self.api_cache[key]
            
            logger.debug(f"No cached data found for key: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached data for key {key}: {str(e)}")
            return None
    
    def delete_route(self, route_id: str) -> bool:
        """
        Delete cached route data
        
        Args:
            route_id: Route identifier
            
        Returns:
            Success status
        """
        try:
            # Remove from memory cache
            if route_id in self.route_cache:
                del self.route_cache[route_id]
            
            # Remove from disk cache
            cache_file = os.path.join(self.cache_dir, f"route_{route_id}.pkl")
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            logger.info(f"Route {route_id} deleted from cache")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete route {route_id} from cache: {str(e)}")
            return False
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        current_time = datetime.utcnow()
        
        try:
            # Clear expired API cache entries
            expired_keys = []
            for key, cached_item in self.api_cache.items():
                if current_time >= cached_item['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.api_cache[key]
                cleared_count += 1
            
            # Clear expired route cache entries
            expired_routes = []
            for route_id, cached_item in self.route_cache.items():
                if current_time >= cached_item['expires_at']:
                    expired_routes.append(route_id)
            
            for route_id in expired_routes:
                self.delete_route(route_id)
                cleared_count += 1
            
            # Clear expired disk cache files
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.startswith('route_') and filename.endswith('.pkl'):
                        filepath = os.path.join(self.cache_dir, filename)
                        try:
                            with open(filepath, 'rb') as f:
                                cached_item = pickle.load(f)
                            
                            if current_time >= cached_item['expires_at']:
                                os.remove(filepath)
                                cleared_count += 1
                        except:
                            # Remove corrupted cache files
                            os.remove(filepath)
                            cleared_count += 1
            
            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} expired cache entries")
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache entries: {str(e)}")
            return cleared_count
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Cache statistics
        """
        try:
            current_time = datetime.utcnow()
            
            # Memory cache stats
            memory_routes = len(self.route_cache)
            memory_api = len(self.api_cache)
            
            # Disk cache stats
            disk_routes = 0
            if os.path.exists(self.cache_dir):
                disk_routes = len([f for f in os.listdir(self.cache_dir) 
                                 if f.startswith('route_') and f.endswith('.pkl')])
            
            # Expired entries
            expired_memory_routes = sum(1 for item in self.route_cache.values() 
                                      if current_time >= item['expires_at'])
            expired_memory_api = sum(1 for item in self.api_cache.values() 
                                   if current_time >= item['expires_at'])
            
            return {
                'memory_cache': {
                    'routes': memory_routes,
                    'api_data': memory_api,
                    'expired_routes': expired_memory_routes,
                    'expired_api': expired_memory_api
                },
                'disk_cache': {
                    'routes': disk_routes
                },
                'cache_directory': self.cache_dir,
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {'error': 'Failed to retrieve cache statistics'}
    
    def clear_all(self) -> bool:
        """
        Clear all cache data
        
        Returns:
            Success status
        """
        try:
            # Clear memory caches
            self.route_cache.clear()
            self.api_cache.clear()
            
            # Clear disk cache
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    filepath = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
            
            logger.info("All cache data cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear all cache data: {str(e)}")
            return False