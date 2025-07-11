# app/services/cache_service.py

import hashlib
import json
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheService:
    """Service for caching summaries and video data to improve performance."""
    
    def __init__(self, cache_dir: str = "cache", cache_duration_hours: int = 24):
        """
        Initialize cache service.
        
        Args:
            cache_dir (str): Directory to store cache files
            cache_duration_hours (int): How long to keep cache entries (in hours)
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, url: str) -> str:
        """
        Generate a cache key for a YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Cache key (hash of URL)
        """
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            str: File path for cache entry
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """
        Check if cache entry is still valid.
        
        Args:
            cache_data (Dict[str, Any]): Cache entry data
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        try:
            cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
            return datetime.now() - cached_time < self.cache_duration
        except (ValueError, TypeError):
            return False
    
    def get_cached_summary(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached summary for a YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[Dict[str, Any]]: Cached data if available and valid, None otherwise
        """
        try:
            cache_key = self._get_cache_key(url)
            cache_file = self._get_cache_file_path(cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if self._is_cache_valid(cache_data):
                return {
                    'summary': cache_data.get('summary'),
                    'keywords': cache_data.get('keywords'),
                    'video_info': cache_data.get('video_info'),
                    'cached_at': cache_data.get('timestamp')
                }
            else:
                # Remove expired cache
                os.remove(cache_file)
                return None
                
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def cache_summary(self, url: str, summary: str, keywords: str, video_info: Dict[str, str]) -> bool:
        """
        Cache a summary for a YouTube URL.
        
        Args:
            url (str): YouTube URL
            summary (str): Generated summary
            keywords (str): Extracted keywords
            video_info (Dict[str, str]): Video metadata
            
        Returns:
            bool: True if caching was successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(url)
            cache_file = self._get_cache_file_path(cache_key)
            
            cache_data = {
                'url': url,
                'summary': summary,
                'keywords': keywords,
                'video_info': video_info,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error caching summary: {e}")
            return False
    
    def clear_expired_cache(self) -> int:
        """
        Clear all expired cache entries.
        
        Returns:
            int: Number of cache entries removed
        """
        removed_count = 0
        
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if not self._is_cache_valid(cache_data):
                            os.remove(file_path)
                            removed_count += 1
                            
                    except Exception:
                        # Remove corrupted cache files
                        os.remove(file_path)
                        removed_count += 1
                        
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
        
        return removed_count
    
    def clear_all_cache(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            int: Number of cache entries removed
        """
        removed_count = 0
        
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    removed_count += 1
                    
        except Exception as e:
            print(f"Error clearing cache: {e}")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        try:
            if not os.path.exists(self.cache_dir):
                return {
                    'total_entries': 0,
                    'valid_entries': 0,
                    'expired_entries': 0,
                    'total_size_mb': 0
                }
            
            total_entries = 0
            valid_entries = 0
            expired_entries = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_entries += 1
                    total_size += os.path.getsize(file_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if self._is_cache_valid(cache_data):
                            valid_entries += 1
                        else:
                            expired_entries += 1
                            
                    except Exception:
                        expired_entries += 1
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {
                'total_entries': 0,
                'valid_entries': 0,
                'expired_entries': 0,
                'total_size_mb': 0
            }
