from typing import Optional, List, Dict, Tuple, Callable, Any
from util import raise_err_if_null

import pandas as pd
import bisect
import numpy as np


class DatabaseRow:
    """Database row containing a set of values, (i.e. ContentValues in java)"""

    def __init__(self):
        self._contents : Dict[str, str]  = dict()

    def get(self, key, default=None):
        if key not in self._contents:
            return default
        return self._contents[key]
    
    def put(self, key, value):
        self._contents[key] = value


class DataFrameDatabase:
    """Database class, where underlying data structure is pandas DataFrame"""

    def __init__(self, key_idx, columns, key_idx_sort=None):
        self.db      : pd.DataFrame                 = None
        self.key_idx : Tuple[str]                   = key_idx
        self.columns : List[str]                    = columns
        self.key_idx_sort : Callable[[Any], Any]    = key_idx_sort or (lambda x: x)

        self.create_table()

    def create_table(self) -> bool:
        """Create DataFrame table"""
        if self.db:
            return False
        self.db = pd.DataFrame(columns=self.columns)
        return True

    def add_row(self, obj: DatabaseRow) -> bool:
        """Add a row to the DataFrame"""
        raise_err_if_null(self.db, "Database")
        
        if not self._validate_row(obj):
            return False
        
        # Ensure row is not already present in db
        key_idx_val = obj.get(self.key_idx)
        if key_idx_val in self.db[self.key_idx].values:
            return False
        
        # Prepare the new row into db
        prepare_row = {column: obj.get(column, np.nan) for column in self.columns}

        # Insert new row into db, while also maintaining sort order
        prim_key_val_lst = sorted(self.db[self.key_idx].to_list(), key=self.key_idx_sort)
        
        # Find the correct position to insert
        position = bisect.bisect_left(prim_key_val_lst, prepare_row[self.key_idx], key=self.key_idx_sort)

        # Insert the new row while maintaining the sort order
        new_row_df = pd.DataFrame([prepare_row])
        self.db = pd.concat(
            [self.db.iloc[:position], new_row_df, self.db.iloc[position:]],
            ignore_index=True
        )

        return True

    def update_row(self, key_val: Any, obj: DatabaseRow) -> bool:
        raise_err_if_null(self.db, "Database")
        
        if not self._validate_row(obj):
            return False
        
        # Ensure primary key value is in db
        if key_val not in self.db[self.key_idx].values:
            return False
        
        # Find the index of the row to update
        idx_loc = self.db.index[self.db[self.key_idx] == key_val].tolist()
        if not idx_loc:  # If no matching index is found
            return False
        
        # Prepare the updated row
        prepared_row = {column: obj.get(column, np.nan) for column in self.columns}

        # Update the row in the DataFrame
        self.db.loc[idx_loc[0], :] = prepared_row

        return True

    def get_row(self, key: Any) -> Optional[DatabaseRow]:
        """Get a row in a DataFrame and write it into a DatabaseRow"""
        raise_err_if_null(self.db, "Database")

        # Check if the key exists in the database
        matching_row = self.db[self.db[self.key_idx] == key]
        if matching_row.empty:
            return None  # Or raise an error if key not found is considered critical
        matching_row = matching_row.iloc[0]
    
        # Initialize and populate row
        row = DatabaseRow()
        for column in self.columns:
            row.put(column, matching_row[column])
        
        return row

    def delete_row(self, key_val: Any) -> bool:
        """Delete row in DataFrame based on primary key value"""
        raise_err_if_null(self.db, "Database")
        
        # Ensure the key exists in the database
        if key_val not in self.db[self.key_idx].values:
            return False  # Return False if the key is not found

        # Find the index of the row to delete
        idx_loc = self.db.index[self.db[self.key_idx] == key_val].tolist()
        if not idx_loc:
            return False

        # Drop the row from the DataFrame
        self.db = self.db.drop(idx_loc[0]).reset_index(drop=True)

        return True
    
    def dump(self, filter_expr: str=None) -> Dict[Any]:
        """Dump rows from the DataFrame with optional filter expression"""
        raise_err_if_null(self.db, "Database")

        if filter_expr:
            filtered_df = self.db.query(filter_expr)
            return filtered_df.to_dict(orient="records")
        
        return self.db.to_dict(orient="records") 

    def _validate_row(self, row: DatabaseRow) -> bool:
        """Ensure row is validated before doing actions with DataFrame"""
        return all(row.get(key) is not None for key in self.key_idx)
