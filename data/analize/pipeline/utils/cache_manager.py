"""
缓存管理模块 - 提高数据访问性能
"""
import pickle
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = 'data/analize/cache', ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            ttl: 缓存过期时间(秒)，默认1小时
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        
        # 元数据文件
        self.metadata_file = self.cache_dir / '_cache_metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
        return {}
    
    def _save_metadata(self):
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"保存缓存元数据失败: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的对象，如果不存在或过期返回None
        """
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if not cache_file.exists():
            return None
        
        # 检查是否过期
        if key in self.metadata:
            created_at = datetime.fromisoformat(self.metadata[key]['created_at'])
            if datetime.now() - created_at > timedelta(seconds=self.ttl):
                logger.debug(f"缓存已过期: {key}")
                self.delete(key)
                return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            logger.debug(f"缓存命中: {key}")
            return data
        except Exception as e:
            logger.warning(f"读取缓存失败: {key}, {e}")
            self.delete(key)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 要缓存的对象
            ttl: 自定义过期时间(秒)，None使用默认值
        """
        cache_file = self.cache_dir / f"{key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # 更新元数据
            self.metadata[key] = {
                'created_at': datetime.now().isoformat(),
                'ttl': ttl or self.ttl,
                'size_bytes': cache_file.stat().st_size,
            }
            self._save_metadata()
            
            logger.debug(f"缓存已设置: {key}")
        except Exception as e:
            logger.warning(f"设置缓存失败: {key}, {e}")
    
    def delete(self, key: str):
        """删除缓存"""
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            cache_file.unlink()
        
        if key in self.metadata:
            del self.metadata[key]
            self._save_metadata()
        
        logger.debug(f"缓存已删除: {key}")
    
    def clear(self):
        """清空所有缓存"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        
        self.metadata.clear()
        self._save_metadata()
        
        logger.info("所有缓存已清空")
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        total_size = sum(meta['size_bytes'] for meta in self.metadata.values())
        
        return {
            'total_items': len(self.metadata),
            'total_size_mb': total_size / 1024 / 1024,
            'cache_dir': str(self.cache_dir),
            'items': self.metadata,
        }
    
    def cleanup_expired(self):
        """清理过期缓存"""
        expired_keys = []
        
        for key, meta in self.metadata.items():
            created_at = datetime.fromisoformat(meta['created_at'])
            ttl = meta.get('ttl', self.ttl)
            
            if datetime.now() - created_at > timedelta(seconds=ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存")
        
        return len(expired_keys)


if __name__ == '__main__':
    # 测试缓存管理器
    logging.basicConfig(level=logging.DEBUG)
    
    cache = CacheManager()
    
    # 设置缓存
    cache.set('test_key', {'data': [1, 2, 3]})
    
    # 获取缓存
    data = cache.get('test_key')
    print(f"缓存数据: {data}")
    
    # 统计信息
    stats = cache.get_stats()
    print(f"缓存统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 清空缓存
    cache.clear()
