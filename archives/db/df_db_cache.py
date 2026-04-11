from datetime import datetime
from typing import List, Optional
from collections import namedtuple
from .icolumns import IDatabaseColumns
from .df_db import DataFrameDatabase
import pandas as pd
import pathlib
import os

CacheItem = namedtuple("CacheItem", ["index", "filename", "datetime"])

class DataFrameDatabaseDirCache:

    def __init__(self):
        self._cache_db_dir : str   = f"{str(pathlib.Path(__file__).parent.absolute())}/cache"
        
        if not os.path.isdir(self._cache_db_dir):
            os.mkdir(self._cache_db_dir)

        assert os.path.isdir(self._cache_db_dir), f"{self._cache_db_dir} dir does not exist"

    def cache_list(self) -> List[CacheItem]:
        """
        Get list of cache files in directory
        Each item in tuple contains an index, filename, and last modified datetime
        """
        files = []

        for idx, file in enumerate(os.listdir(self._cache_db_dir)):
            fpath = os.path.join(self._cache_db_dir, file)
            last_modified_datetime = datetime.fromtimestamp(os.path.getmtime(fpath))
            files.append(CacheItem(idx, file, str(last_modified_datetime)))

        files.sort(key= lambda f: f.filename, reverse=True)
        return files

    def save(self, df_db: pd.DataFrame, fname: str):
        """Save to cache"""
        fpath = os.path.join(self._cache_db_dir, fname)
        df_db.to_parquet(fpath)
        print(f"DB saved successfully to {fpath}")
        return True

    def load(self, cols: IDatabaseColumns, fname='', f_idx=-1) -> Optional[pd.DataFrame]:
        """Load file from cache - just returns the filename in cache, or the most recent one"""
        cache_item = self._get_cache_item(fname, f_idx)

        if not cache_item:
            return None
        
        df = pd.read_parquet(os.path.join(self._cache_db_dir, cache_item.filename))
        
        # Ensure the DataFrame has the correct columns
        if not all(col.name in df.columns for col in cols.values()):
            print(f"Cache file {cache_item.filename} does not contain the required columns.")
            return None
         
        return DataFrameDatabase.from_dataframe(df, cols)


    def delete(self, fname='', f_idx=-1) -> bool:
        cache_item = self._get_cache_item(fname, f_idx)
        if not cache_item:
            return False        
        
        os.remove(os.path.join(self._cache_db_dir, cache_item.filename))
        return True
    
    def _get_cache_item(self, fname:str = '', f_idx:int = -1) -> Optional[CacheItem]:
        """Get cache item from cache list, given fname or f_idx"""
        if not fname and not f_idx >= 0:
            return None

        cache_item = None
        cache_list = self.cache_list()
        
        if f_idx >= 0 and f_idx < len(cache_list):
            cache_item = cache_list[f_idx]

        if fname:
            for item in cache_list:
                if item.filename == fname:
                    cache_item = item

        return cache_item
