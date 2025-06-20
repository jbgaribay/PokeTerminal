# cache_manager.py
"""
Comprehensive caching system for the Pokédex Terminal App
"""

import os
import json
import gzip
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import pickle

class CacheManager:
    """Advanced caching system with memory and file caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'file_hits': 0,
            'api_calls': 0,
            'size_mb': 0.0,
            'most_accessed': {},
            'generation_coverage': {},
            'session_start': datetime.now()
        }
        
        # Configuration
        self.config = {
            'enabled': True,
            'max_age_days': 30,
            'max_size_mb': 100,
            'compress': True,
            'preload_popular': True,
            'ascii_cache': True,
            'max_memory_items': 50,  # LRU eviction after this
            'background_preload': True
        }
        
        # Memory cache with LRU tracking
        self.memory_access_order = []
        self.cache_lock = threading.Lock()
        
        # Popular Pokemon for preloading (top 50 most searched)
        self.popular_pokemon = [
            'pikachu', 'charizard', 'blastoise', 'venusaur', 'mewtwo', 'mew',
            'lugia', 'ho-oh', 'celebi', 'rayquaza', 'kyogre', 'groudon',
            'dialga', 'palkia', 'giratina', 'arceus', 'reshiram', 'zekrom',
            'kyurem', 'xerneas', 'yveltal', 'zygarde', 'solgaleo', 'lunala',
            'necrozma', 'zacian', 'zamazenta', 'eternatus', 'koraidon', 'miraidon',
            'garchomp', 'lucario', 'dragonite', 'tyranitar', 'salamence',
            'metagross', 'latios', 'latias', 'darkrai', 'shaymin', 'victini',
            'zoroark', 'serperior', 'emboar', 'samurott', 'greninja', 'talonflame',
            'sylveon', 'goodra', 'noivern', 'decidueye', 'incineroar', 'primarina'
        ]
        
        self._initialize_cache_structure()
        self._load_cache_metadata()
        
        if self.config['background_preload']:
            self._start_background_preloader()
    
    def _initialize_cache_structure(self):
        """Create cache directory structure"""
        try:
            directories = [
                self.cache_dir,
                self.cache_dir / "pokemon",
                self.cache_dir / "moves", 
                self.cache_dir / "evolution_chains",
                self.cache_dir / "sprites" / "ascii",
                self.cache_dir / "locations",
                self.cache_dir / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                
            print(f"🗂️  Cache system initialized at: {self.cache_dir.absolute()}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize cache: {e}")
            self.config['enabled'] = False
    
    def _load_cache_metadata(self):
        """Load cache metadata and statistics"""
        metadata_file = self.cache_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.cache_stats.update(metadata.get('stats', {}))
                    # Reset session-specific stats
                    self.cache_stats['session_start'] = datetime.now()
                    print(f"📊 Cache loaded: {self.cache_stats['hits']} hits, {self.cache_stats['size_mb']:.1f}MB")
            except Exception as e:
                print(f"⚠️  Could not load cache metadata: {e}")
    
    def _save_cache_metadata(self):
        """Save cache metadata and statistics"""
        if not self.config['enabled']:
            return
            
        metadata_file = self.cache_dir / "metadata.json"
        try:
            metadata = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'stats': self.cache_stats,
                'config': self.config
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
                
        except Exception as e:
            print(f"⚠️  Could not save cache metadata: {e}")
    
    def _generate_cache_key(self, category: str, identifier: str, **kwargs) -> str:
        """Generate a cache key for different types of data"""
        if category == "pokemon":
            return f"pokemon_{identifier.lower()}"
        elif category == "move":
            return f"move_{identifier.lower()}"
        elif category == "evolution":
            return f"evolution_{identifier.lower()}"
        elif category == "sprite":
            width = kwargs.get('width', 50)
            sprite_type = kwargs.get('sprite_type', 'front')
            return f"sprite_{identifier.lower()}_{sprite_type}_{width}w"
        elif category == "location":
            generation = kwargs.get('generation', '')
            game = kwargs.get('game', '')
            return f"location_{identifier.lower()}_gen{generation}_{game}"
        elif category == "moves_by_gen":
            generation = kwargs.get('generation', '')
            game = kwargs.get('game', '')
            return f"moves_{identifier.lower()}_gen{generation}_{game}"
        else:
            return f"{category}_{identifier.lower()}"
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        # Determine subdirectory based on cache key prefix
        if cache_key.startswith('pokemon_'):
            subdir = "pokemon"
        elif cache_key.startswith('move_'):
            subdir = "moves"
        elif cache_key.startswith('evolution_'):
            subdir = "evolution_chains"
        elif cache_key.startswith('sprite_'):
            subdir = "sprites/ascii"
        elif cache_key.startswith('location_'):
            subdir = "locations"
        elif cache_key.startswith('moves_'):
            subdir = "locations"  # Store move data with locations
        else:
            subdir = "temp"
        
        file_path = self.cache_dir / subdir / f"{cache_key}.json"
        if self.config['compress']:
            file_path = file_path.with_suffix('.json.gz')
        
        return file_path
    
    def _is_cache_expired(self, file_path: Path) -> bool:
        """Check if a cache file is expired"""
        if not file_path.exists():
            return True
        
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        max_age = timedelta(days=self.config['max_age_days'])
        
        return file_age > max_age
    
    def _manage_memory_cache_size(self):
        """Implement LRU eviction for memory cache"""
        with self.cache_lock:
            while len(self.memory_cache) > self.config['max_memory_items']:
                # Remove least recently used item
                if self.memory_access_order:
                    oldest_key = self.memory_access_order.pop(0)
                    if oldest_key in self.memory_cache:
                        del self.memory_cache[oldest_key]
                else:
                    break
    
    def _update_access_stats(self, cache_key: str, hit_type: str):
        """Update access statistics"""
        with self.cache_lock:
            if hit_type == 'memory':
                self.cache_stats['memory_hits'] += 1
                self.cache_stats['hits'] += 1
            elif hit_type == 'file':
                self.cache_stats['file_hits'] += 1
                self.cache_stats['hits'] += 1
            elif hit_type == 'miss':
                self.cache_stats['misses'] += 1
                self.cache_stats['api_calls'] += 1
            
            # Track most accessed items
            base_key = cache_key.split('_')[1] if '_' in cache_key else cache_key
            self.cache_stats['most_accessed'][base_key] = self.cache_stats['most_accessed'].get(base_key, 0) + 1
    
    def get(self, category: str, identifier: str, **kwargs) -> Optional[Any]:
        """Get data from cache (memory -> file -> None)"""
        if not self.config['enabled']:
            return None
        
        cache_key = self._generate_cache_key(category, identifier, **kwargs)
        
        # 1. Check memory cache
        with self.cache_lock:
            if cache_key in self.memory_cache:
                # Move to end of access order (most recently used)
                if cache_key in self.memory_access_order:
                    self.memory_access_order.remove(cache_key)
                self.memory_access_order.append(cache_key)
                
                self._update_access_stats(cache_key, 'memory')
                return self.memory_cache[cache_key]
        
        # 2. Check file cache
        file_path = self._get_cache_file_path(cache_key)
        
        if file_path.exists() and not self._is_cache_expired(file_path):
            try:
                # Load from file
                if self.config['compress'] and file_path.suffix == '.gz':
                    with gzip.open(file_path, 'rt') as f:
                        data = json.load(f)
                else:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                
                # Store in memory cache
                with self.cache_lock:
                    self.memory_cache[cache_key] = data
                    self.memory_access_order.append(cache_key)
                    self._manage_memory_cache_size()
                
                self._update_access_stats(cache_key, 'file')
                return data
                
            except Exception as e:
                print(f"⚠️  Cache read error for {cache_key}: {e}")
                # Delete corrupted cache file
                try:
                    file_path.unlink()
                except:
                    pass
        
        # 3. Cache miss
        self._update_access_stats(cache_key, 'miss')
        return None
    
    def set(self, category: str, identifier: str, data: Any, **kwargs) -> bool:
        """Store data in cache (memory + file)"""
        if not self.config['enabled'] or data is None:
            return False
        
        cache_key = self._generate_cache_key(category, identifier, **kwargs)
        
        try:
            # Store in memory cache
            with self.cache_lock:
                self.memory_cache[cache_key] = data
                if cache_key in self.memory_access_order:
                    self.memory_access_order.remove(cache_key)
                self.memory_access_order.append(cache_key)
                self._manage_memory_cache_size()
            
            # Store in file cache
            file_path = self._get_cache_file_path(cache_key)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.config['compress']:
                with gzip.open(file_path, 'wt') as f:
                    json.dump(data, f, separators=(',', ':'), default=str)
            else:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Cache write error for {cache_key}: {e}")
            return False
    
    def clear(self, category: Optional[str] = None, identifier: Optional[str] = None):
        """Clear cache data"""
        if not self.config['enabled']:
            return
        
        if category is None and identifier is None:
            # Clear everything
            with self.cache_lock:
                self.memory_cache.clear()
                self.memory_access_order.clear()
            
            # Clear file cache
            import shutil
            try:
                shutil.rmtree(self.cache_dir)
                self._initialize_cache_structure()
                print("🗑️  All cache cleared")
            except Exception as e:
                print(f"⚠️  Error clearing cache: {e}")
        
        elif category and not identifier:
            # Clear category
            pattern = f"{category}_*"
            cleared_count = 0
            
            # Clear from memory
            with self.cache_lock:
                keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{category}_")]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                    if key in self.memory_access_order:
                        self.memory_access_order.remove(key)
                    cleared_count += 1
            
            # Clear from files
            subdir_map = {
                'pokemon': 'pokemon',
                'move': 'moves',
                'evolution': 'evolution_chains',
                'sprite': 'sprites/ascii',
                'location': 'locations'
            }
            
            if category in subdir_map:
                cache_subdir = self.cache_dir / subdir_map[category]
                if cache_subdir.exists():
                    try:
                        import shutil
                        shutil.rmtree(cache_subdir)
                        cache_subdir.mkdir(parents=True, exist_ok=True)
                        print(f"🗑️  Cleared {category} cache ({cleared_count} items from memory)")
                    except Exception as e:
                        print(f"⚠️  Error clearing {category} cache: {e}")
        
        else:
            # Clear specific item
            cache_key = self._generate_cache_key(category, identifier)
            
            # Clear from memory
            with self.cache_lock:
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                if cache_key in self.memory_access_order:
                    self.memory_access_order.remove(cache_key)
            
            # Clear from file
            file_path = self._get_cache_file_path(cache_key)
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"🗑️  Cleared cache for {identifier}")
                except Exception as e:
                    print(f"⚠️  Error clearing cache for {identifier}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self.config['enabled']:
            return {'enabled': False}
        
        # Calculate cache size
        total_size = 0
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
                    file_count += 1
        except:
            pass
        
        self.cache_stats['size_mb'] = total_size / (1024 * 1024)
        
        hit_rate = 0
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests > 0:
            hit_rate = (self.cache_stats['hits'] / total_requests) * 100
        
        session_duration = datetime.now() - self.cache_stats['session_start']
        
        return {
            'enabled': True,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_hits': self.cache_stats['hits'],
            'memory_hits': self.cache_stats['memory_hits'],
            'file_hits': self.cache_stats['file_hits'],
            'misses': self.cache_stats['misses'],
            'api_calls': self.cache_stats['api_calls'],
            'size_mb': f"{self.cache_stats['size_mb']:.1f}",
            'file_count': file_count,
            'memory_items': len(self.memory_cache),
            'session_duration': str(session_duration).split('.')[0],
            'most_accessed': dict(sorted(self.cache_stats['most_accessed'].items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
        }
    
    def preload_popular(self, api_client, limit: int = 20):
        """Preload popular Pokemon data"""
        if not self.config['enabled'] or not self.config['preload_popular']:
            return
        
        print(f"🔄 Preloading {limit} popular Pokemon...")
        loaded_count = 0
        
        for pokemon_name in self.popular_pokemon[:limit]:
            try:
                # Check if already cached
                if self.get('pokemon', pokemon_name) is None:
                    # Load from API
                    data = api_client.get_pokemon_data(pokemon_name)
                    if data:
                        self.set('pokemon', pokemon_name, data)
                        loaded_count += 1
                        print(f"   📦 Cached {pokemon_name.title()}")
                        
                        # Small delay to be nice to the API
                        time.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️  Failed to preload {pokemon_name}: {e}")
        
        print(f"✅ Preloaded {loaded_count} Pokemon")
    
    def _start_background_preloader(self):
        """Start background thread for preloading"""
        def background_preload():
            time.sleep(5)  # Wait 5 seconds after startup
            try:
                from api_client import PokeAPIClient
                api_client = PokeAPIClient()
                self.preload_popular(api_client, limit=10)
            except Exception as e:
                print(f"⚠️  Background preload failed: {e}")
        
        thread = threading.Thread(target=background_preload, daemon=True)
        thread.start()
    
    def cleanup_expired(self):
        """Remove expired cache files"""
        if not self.config['enabled']:
            return
        
        removed_count = 0
        total_size_saved = 0
        
        try:
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    if file.endswith(('.json', '.json.gz')):
                        file_path = Path(root) / file
                        if self._is_cache_expired(file_path):
                            size = file_path.stat().st_size
                            file_path.unlink()
                            removed_count += 1
                            total_size_saved += size
            
            if removed_count > 0:
                size_mb = total_size_saved / (1024 * 1024)
                print(f"🧹 Cleaned up {removed_count} expired files ({size_mb:.1f}MB saved)")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    def export_cache_info(self, filename: str = "cache_report.txt"):
        """Export detailed cache information to a file"""
        try:
            stats = self.get_stats()
            
            with open(filename, 'w') as f:
                f.write("POKÉDEX CACHE REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Cache Status: {'Enabled' if stats['enabled'] else 'Disabled'}\n")
                f.write(f"Hit Rate: {stats.get('hit_rate', 'N/A')}\n")
                f.write(f"Total Size: {stats.get('size_mb', 'N/A')} MB\n")
                f.write(f"File Count: {stats.get('file_count', 'N/A')}\n")
                f.write(f"Memory Items: {stats.get('memory_items', 'N/A')}\n")
                f.write(f"Session Duration: {stats.get('session_duration', 'N/A')}\n\n")
                
                f.write("MOST ACCESSED POKEMON:\n")
                f.write("-" * 30 + "\n")
                for pokemon, count in stats.get('most_accessed', {}).items():
                    f.write(f"{pokemon.title():<20} {count} times\n")
                
                f.write(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"📄 Cache report exported to {filename}")
            
        except Exception as e:
            print(f"⚠️  Error exporting cache info: {e}")
    
    def __del__(self):
        """Save metadata when the cache manager is destroyed"""
        try:
            self._save_cache_metadata()
        except:
            pass