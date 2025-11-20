# enhanced_cache.py
"""
استراتيجية caching محسّنة
✅ Multi-level cache (Memory + Disk)
✅ Smart invalidation
✅ Compression للبيانات الكبيرة
"""

import pickle
import zlib
from functools import wraps
from typing import Any, Optional
import time
from pathlib import Path


class EnhancedCache:
    """Cache متقدم بمستويات متعددة"""
    
    def __init__(
        self,
        memory_size: int = 100,
        disk_cache_dir: str = "cache",
        compress_threshold: int = 1024  # bytes
    ):
        self.memory_cache = {}  # L1 Cache
        self.memory_size = memory_size
        self.disk_cache_dir = Path(disk_cache_dir)
        self.disk_cache_dir.mkdir(exist_ok=True)
        self.compress_threshold = compress_threshold
        
        # إحصائيات
        self.stats = {
            'memory_hits': 0,
            'disk_hits': 0,
            'misses': 0,
            'compressions': 0
        }
    
    def _get_disk_path(self, key: str) -> Path:
        """مسار ملف الـ cache على القرص"""
        return self.disk_cache_dir / f"{hash(key) % 100000}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """الحصول من الـ cache"""
        # محاولة L1 (Memory)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() < entry['expires']:
                self.stats['memory_hits'] += 1
                return entry['value']
            else:
                del self.memory_cache[key]
        
        # محاولة L2 (Disk)
        disk_path = self._get_disk_path(key)
        if disk_path.exists():
            try:
                with open(disk_path, 'rb') as f:
                    data = f.read()
                
                # فك الضغط إذا لزم الأمر
                if data.startswith(b'COMPRESSED:'):
                    data = zlib.decompress(data[11:])
                
                entry = pickle.loads(data)
                
                if time.time() < entry['expires']:
                    # نقل إلى memory cache
                    self.memory_cache[key] = entry
                    self.stats['disk_hits'] += 1
                    return entry['value']
                else:
                    disk_path.unlink()
            except:
                pass
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """حفظ في الـ cache"""
        expires = time.time() + ttl
        entry = {'value': value, 'expires': expires}
        
        # حفظ في memory
        if len(self.memory_cache) >= self.memory_size:
            # حذف الأقدم
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['expires']
            )
            
            # نقل إلى disk قبل الحذف
            self._save_to_disk(oldest_key, self.memory_cache[oldest_key])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = entry
    
    def _save_to_disk(self, key: str, entry: dict):
        """حفظ على القرص"""
        try:
            data = pickle.dumps(entry)
            
            # ضغط إذا كان كبيراً
            if len(data) > self.compress_threshold:
                data = b'COMPRESSED:' + zlib.compress(data, level=6)
                self.stats['compressions'] += 1
            
            disk_path = self._get_disk_path(key)
            with open(disk_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"⚠️ فشل حفظ cache على القرص: {e}")
    
    def clear(self):
        """مسح الـ cache"""
        self.memory_cache.clear()
        for cache_file in self.disk_cache_dir.glob("*.cache"):
            cache_file.unlink()
    
    def get_stats(self) -> dict:
        """إحصائيات الأداء"""
        total_requests = sum([
            self.stats['memory_hits'],
            self.stats['disk_hits'],
            self.stats['misses']
        ])
        
        hit_rate = 0
        if total_requests > 0:
            hit_rate = (
                (self.stats['memory_hits'] + self.stats['disk_hits']) 
                / total_requests * 100
            )
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'memory_size': len(self.memory_cache)
        }


# Decorator محسّن
def smart_cache(ttl: int = 300, use_enhanced: bool = True):
    """Decorator مع caching محسّن"""
    if use_enhanced:
        cache = EnhancedCache()
    else:
        from cache_manager import CacheManager
        cache = CacheManager()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # توليد key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # محاولة الحصول من cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # تنفيذ الدالة
            result = func(*args, **kwargs)
            
            # حفظ في cache
            cache.set(key, result, ttl=ttl)
            
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator