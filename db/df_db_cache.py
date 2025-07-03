from datetime import datetime
from typing import List, Tuple, Union
from db import DataFrameDatabase
from dao import IDatabaseColumns
import pandas as pd
import pathlib
import os


class DataFrameDatabaseDirCache:

    def __init__(self):
        self._cache_db_dir : str   = f"{str(pathlib.Path(__file__).parent.absolute())}/cache"
        
        if not os.path.isdir(self._cache_db_dir):
            os.mkdir(self._cache_db_dir)

        assert os.path.isdir(self._cache_db_dir), f"{self._cache_db_dir} dir does not exist"

    def cache_list(self) -> List[Tuple[int, str, str]]:
        """
        Get list of cache files in directory
        Each item in tuple contains an index, filename, and last modified datetime
        """
        files = []

        for idx, file in enumerate(os.listdir(self._cache_db_dir)):
            fpath = os.path.join(self._cache_db_dir, file)
            last_modified_datetime = datetime.fromtimestamp(os.path.getmtime(fpath))
            files.append((idx, file, str(last_modified_datetime)))

        files.sort(key= lambda f: f[2], reverse=True)
        return files

    def save(self, df_db: pd.DataFrame, fname: str):
        """Save to cache"""
        fpath = os.path.join(self._cache_db_dir, fname)
        df_db.to_parquet(fpath, index=False)
        print(f"DB saved successfully to {fpath}")
        return True

    def load(self, cols: IDatabaseColumns, fname='', f_idx=-1) -> Union[pd.DataFrame, None]:
        """Load file from cache - just returns the filename in cache, or the most recent one"""
        lst_file = self.cache_list()
        cache_file = None

        if not lst_file:
            return None
                
        if fname:
            for f_item in lst_file:
                if f_item[1] == fname:
                    cache_file = f_item

        if f_idx > 0 and f_idx in range(0, len(lst_file)):
            cache_file = lst_file[f_idx]

        # If no specific file is requested, return the most recent one
        if cache_file is None:
            cache_file = lst_file[0]

        df = pd.read_parquet(os.path.join(self._cache_db_dir, cache_file[1]))
        
        # Ensure the DataFrame has the correct columns
        if not all(col.name in df.columns for col in cols):
            print(f"Cache file {cache_file[1]} does not contain the required columns.")
            return None
         
        return DataFrameDatabase.from_dataframe(df, cols)


    def delete(self, fname='', f_idx=-1) -> bool:
        if not fname or f_idx < 0:
            return False
        
        cache_file = self.load(fname, f_idx)
        if not cache_file:
            return False
        
        os.remove(os.path.join(self._cache_db_dir, cache_file))
        return True