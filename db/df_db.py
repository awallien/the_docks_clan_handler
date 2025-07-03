from typing import Callable, Optional, List, Dict, Self, Tuple, Any, Union
from datetime import datetime
from pyarrow import parquet as pq
import pandas as pd
from dao import IDatabaseColumns


class DatabaseColumn:
    """Database Column containing the name of the column and default value"""

    def __init__(self, name, default, dtype, categories=None):
        self._name : str        = name
        self._default : Any     = default

        # https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes
        self._dtype: str        = dtype

        # only used if dtype is 'category'
        self._categories: List[Union[str, int]] = categories

        # Check if dtype is valid
        if self._dtype == "category":
            assert isinstance(self._categories, list), \
                "`categories` must be a list if dtype is `category`"
            assert all(isinstance(cat, (str, int)) for cat in self._categories), \
                "`categories` must be a list of str or int if dtype is `category`"
    
    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default
        
    @property
    def dtype(self):
        return self._dtype
    
    @property
    def categories(self):
        return self._categories
    
    def query_expr(self, cmp_val, op) -> str:
        val = ''
        if self.dtype == "string":
            val = f"'{cmp_val}'"
        elif self.dtype == "datatime64[ns]":
            val = f""
        return f"({self.name} {op} {val})"
    
    def __eq__(self, value) -> bool:
        if not isinstance(value, DatabaseColumn):
            return False
        return (
            self.name == value.name and
            self.default == value.default and
            self.dtype == value.dtype and
            self.categories == self.categories
        )
    
    def __repr__(self):
        return f"DatabaseColumn(name={self.name}, default={self.default}, dtype={self.dtype}, categories={self.categories})"

class DatabaseRow:
    """Database row containing a set of values, (i.e. ContentValues in java)"""

    def __init__(self):
        self._contents : Dict[DatabaseColumn, Any]  = dict()

    def get(self, col: DatabaseColumn):
        return self._contents.get(col.name, col.default)
    
    def put(self, col: DatabaseColumn, value: Any):
        assert isinstance(value, col.dtype), f"`{value}` does not match type {col.dtype}"
        self._contents[col.name] = value

    def columns(self, as_str=False):
        if as_str:
            return [col.name for col in self._contents.keys()]
        return list(self._contents.keys())


class DataFrameDatabase:
    """Database class, where underlying data structure is pandas DataFrame"""

    def __init__(self, prim_cols, cols, prim_cols_sort_fn=None):
        self._db      : pd.DataFrame                         = None
        self._prim_cols : Tuple[DatabaseColumn]              = prim_cols
        self._cols : List[DatabaseColumn]                    = cols
        self._sort_pending : bool                            = False
        self._prim_cols_sort_fn : Callable[[Any], Any]       = prim_cols_sort_fn or (lambda x: x)

        assert \
            all([prim_col in self._cols for prim_col in self._prim_cols]), \
            "Primary column is NOT found in list of columns"
        
        self._create_table()

    def add_row(self, obj: DatabaseRow) -> bool:
        """Add a row to the DataFrame"""
        assert self._db, "Database should NOT be None"
        
        if not self._validate_row(obj):
            return False
        
        # Ensure row is not already present in db
        query_expr = '&'.join(
            [f"{db_col.query_expr(obj.get(db_col), '==')}" for db_col in self._prim_cols]
        )
        queried_df = self._db.query(query_expr)
        if not queried_df.empty():
            return False
        
        # Prepare the new row and insert it into the database. 
        # The final state of the database ensures that all rows 
        #  are sorted according to the sort function provided to this class, 
        #  which is applied when the database is saved.`
        # For now, the new row is stored at the end of the database.
        new_row_df = pd.DataFrame([{column.name: obj.get(column.name, column.default) for column in self._cols}])
        pd.concat([self._db, new_row_df], ignore_index=True)
        self._sort_pending = True
        
        return True

    def update_row(self, obj: DatabaseRow) -> bool:
        """
        Update the values of a row in the database using the primary values from the given object.
        Note: Primary values cannot be modified through this function. 
        To update primary values, you must delete the existing row and reinsert it with the new values.
        """
        assert self._db, "Database is None"

        if not self._validate_row(obj):
            return False
        
        def row_filter(row):
            for col in self._prim_cols:
                val = obj.get(col)
                if not val == row[col.name]:
                    return False
            return True

        # Ensure row is present in the db and get its row index
        match_ixs = self._db.index[self._db.apply(row_filter, axis=1)]
        match_ixs_len = len(match_ixs)
        assert match_ixs_len <= 1, f"Unexpected number of indices: {match_ixs_len}"
        
        if not match_ixs_len:
            return False
             
        # Prepare the updated row and replace 
        prepared_row = {col.name: obj.get(col) for col in obj.columns()}
        self._db.loc[match_ixs[0], obj.columns(as_str=True)] = prepared_row
        
        return True

    def get_row(self, obj: DatabaseRow) -> Optional[DatabaseRow]:
        """Get a row in a DataFrame and write it into a DatabaseRow"""
        assert self._db, "Database is None"

        if not self._validate_row(obj):
            return None

        # Check if exists in the database
        query_expr = '&'.join(
            [f"{db_col.query_expr(obj.get(db_col), '==')}" for db_col in self._prim_cols]
        )
        queried_df = self._db.query(query_expr)
        queried_df_len = len(queried_df)
        assert queried_df_len <= 1, f"Unexpected number of indices: {queried_df_len}"
        
        if not queried_df.empty():
            return None
        
        # Convert the queried df into a DatabaseRow
        row = DatabaseRow()
        for col in self._cols:
            val = queried_df[col.name][0]
            if col.dtype == "datetime64[ns]":
                val = val.date()
            row.put(col, val)
        
        return row

    def delete_row(self, obj: DatabaseColumn) -> bool:
        """Delete row in DataFrame based on primary key values in obj"""
        assert self._db, "Database is None"
    
        if not self._validate_row(obj):
            return False
        
        def row_filter(row):
            for col in self._prim_cols:
                val = obj.get(col)
                if not val == row[col.name]:
                    return False
            return True

        # Ensure row exists in database and get its index
        match_ixs = self._db.index[self._db.apply(row_filter, axis=1)]
        match_ixs_len = len(match_ixs)
        assert match_ixs_len <= 1, f"Unexpected number of indices: {match_ixs_len}"
        
        if not match_ixs_len:
            return False

        # # Drop the row from the DataFrame
        self._db = self._db.drop(match_ixs[0]).reset_index(drop=True)

        return True
    
    def dump(self, filter_expr: Optional[str]=None) -> List[DatabaseRow]:
        """Dump rows from the DataFrame with optional filter expression"""
        assert self._db, "Database is None"

        if self._sort_pending:
            self.sort()

        if filter_expr:
            filtered_df = self._db.query(filter_expr)
        else:
            filtered_df = self._db

        # Convert filtered rows into list of DatabaseRow
        rows = []
        for row in filtered_df.itertuples(index=False, name=None):
            db_row = DatabaseRow()
            for column, value in zip(self._cols, row):
                if column.dtype == "datetime64[ns]":
                    value = value.date()
                db_row.put(column, value)
            rows.append(db_row)
        
        return rows
    
    def sort(self) -> None:
        """Sort the database"""
        assert self._db, "Database is None"

        if self._sort_pending:
            self._db = self._db.sort_values(
                by=[col.name for col in self._prim_cols],
                key=self._prim_cols_sort_fn
            ).reset_index(drop=True)
        
            self._sort_pending = False
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, cols: IDatabaseColumns) -> Self:
        """Create a DataFrameDatabase instance from an existing DataFrame"""
        return cls(
            prim_cols=cols.primary(),
            cols=cols.values(),
            prim_cols_sort_fn=cols.primary_sort
        )

    def _create_table(self) -> bool:
        """Create DataFrame table"""
        if self._db:
            return False
        
        db_col_types = self._get_db_col_types()
        self._db = ( 
            pd.DataFrame(columns=list(db_col_types.keys()))
                .astype(self._get_db_col_types())
        )

        return True
    
    def _get_db_col_types(self) -> Dict[str, Union[pd.CategoricalDtype, str]]:
        """Get dictionary of column data types"""
        db_col_types = dict()
        for db_col in self._cols:
            col_type = None
            if db_col.dtype == "category":
                col_type = pd.CategoricalDtype(db_col.categories)
            else:
                col_type = db_col.dtype
            
            db_col_types[db_col.name] = col_type
        
        return db_col_types

    def _validate_row(self, row: DatabaseRow) -> bool:
        """Ensure row is validated before doing actions with DataFrame"""
        return all(row.get(key) is not None for key in self._prim_cols)
