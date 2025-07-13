from typing import Callable, Optional, List, Dict, Self, Tuple, Any, Union
from pyarrow import parquet as pq
import pandas as pd 
from .icolumns import IDatabaseColumns, DatabaseColumn


class DatabaseRow:
    """Database row containing a set of values, (i.e. ContentValues in java)"""

    def __init__(self):
        self._contents : Dict[DatabaseColumn, Any]  = dict()

    def get(self, col: DatabaseColumn):
        return self._contents.get(col, col.default)
    
    def put(self, col: DatabaseColumn, value: Any):
        self._contents[col] = value

    def columns(self, as_str=False):
        if as_str:
            return [col.name for col in self._contents.keys()]
        return list(self._contents.keys())
    
    def __str__(self):
        return "DatabaseRow(" + " ".join([f"{k.name}={v}" for k,v in self._contents.items()]) + ")"

    def __repr__(self):
        return str(self)


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
        
        self._db = self._create_table()

    def add_row(self, obj: DatabaseRow) -> bool:
        """Add a row to the DataFrame"""
        assert self._db is not None, "Database should NOT be None"
        
        if not self._validate_row(obj):
            return False

        # Ensure row is not already present in db
        query_expr = '&'.join(
            [f"{db_col.query_expr(obj.get(db_col), '==')}" for db_col in self._prim_cols]
        )
        queried_df = self._db.query(query_expr)
        if not queried_df.empty:
            return False

        # Prepare the new row and insert it into the database. 
        # The final state of the database ensures that all rows 
        #  are sorted according to the sort function provided to this class, 
        #  which is applied when the database is saved.`
        # For now, the new row is stored at the end of the database.
        new_row_df = (
            pd.DataFrame([{column.name: obj.get(column) for column in self._cols}])
            .astype(self._db.dtypes.to_dict(), errors="raise")
        )
        self._db = pd.concat([self._db, new_row_df], ignore_index=True)
        self._sort_pending = True

        return True

    def update_row(self, obj: DatabaseRow) -> bool:
        """
        Update the values of a row in the database using the primary values from the given object.
        Note: Primary values cannot be modified through this function. 
        To update primary values, you must delete the existing row and reinsert it with the new values.
        """
        assert self._db is not None, "Database is None"

        if not self._validate_row(obj):
            return False

        # Ensure row is present in the db and get its row index
        mask = pd.Series(True, index=self._db.index)
        for col in self._prim_cols:
            val = obj.get(col)
            mask &= (self._db[col.name] == val)

        match_ixs = self._db.index[mask]
        match_ixs_len = len(match_ixs)
        assert match_ixs_len <= 1, f"Unexpected number of indices: {match_ixs_len}"
        
        if match_ixs_len == 0:
            return False
             
        # Update row
        row_idx = match_ixs[0]
        columns = set(obj.columns()) - set(self._prim_cols)
        for col in columns:
            new_val = obj.get(col)
            if new_val == col.default:
                continue
            self._db.loc[row_idx, col.name] = new_val

        return True

    def get_row(self, obj: DatabaseRow) -> Optional[DatabaseRow]:
        """Get a row in a DataFrame and write it into a DatabaseRow"""
        assert self._db is not None, "Database is None"

        if not self._validate_row(obj):
            return None

        # Check if exists in the database
        query_expr = '&'.join(
            [f"{db_col.query_expr(obj.get(db_col), '==')}" for db_col in self._prim_cols]
        )
        queried_df = self._db.query(query_expr)
        queried_df_len = len(queried_df)
        assert queried_df_len <= 1, f"Unexpected number of indices: {queried_df_len}"
        
        if queried_df.empty:
            return None
        
        # Convert the queried df into a DatabaseRow
        record = queried_df.to_dict(orient="records")[0]
        
        row = DatabaseRow()
        for col in self._cols:
            row.put(col, record[col.name])
        
        return row

    def delete_row(self, obj: DatabaseColumn) -> bool:
        """Delete row in DataFrame based on primary key values in obj"""
        assert self._db is not None, "Database is None"
    
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
        assert self._db is not None, "Database is None"

        if self._sort_pending:
            self.sort()

        filtered_df = self._db
        if filter_expr:
            filtered_df = self._db.query(filter_expr)
        
        # Convert filtered rows into list of DatabaseRow
        records = filtered_df.to_dict(orient="records")
        rows = []
        for record in records:
            db_row = DatabaseRow()
            for col in self._cols:
                db_row.put(col, record[col.name])
            rows.append(db_row)

        return rows
    
    def sort(self) -> None:
        """Sort the database"""
        assert self._db is not None, "Database is None"

        if self._sort_pending:
            self._db = self._db.sort_values(
                by=[col.name for col in self._prim_cols],
                key=self._prim_cols_sort_fn
            ).reset_index(drop=True)
        
            self._sort_pending = False
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, cols: IDatabaseColumns) -> Self:
        """Create a DataFrameDatabase instance from an existing DataFrame"""
        new_dfdb = cls(
            prim_cols=cols.primary(),
            cols=cols.values(),
            prim_cols_sort_fn=cols.primary_sort
        )

        new_dfdb._db = df.astype(new_dfdb._get_db_col_types())
        return new_dfdb

    def _create_table(self) -> pd.DataFrame:
        """Create DataFrame table""" 
        db_col_types = self._get_db_col_types()
        return ( 
            pd.DataFrame(columns=list(db_col_types.keys()))
            .astype(db_col_types, errors='raise')
        )


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
