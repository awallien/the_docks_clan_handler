from pathlib import Path
from typing import Dict

from .db import Database

class DatabaseManager:

    def __init__(self, db_path=None):
        if db_path and not Path(db_path).exists():
            raise Exception(f"DB path '{db_path}' does not exist.")
        
        self._db_path: Path = db_path or self._get_default_db_path()
    
    def _get_default_db_path(self):
        cur_path = Path(__file__).parent.resolve()
        cur_path.mkdir(exist_ok=True)
        return cur_path / "db_cache"

    def create_database(self, db_name: str) -> Path | None:
        path = self._db_path / db_name
        if path.exists():
            raise ValueError("Database '{db_name}' already exists.")
        
        path.touch()

        return path
    
    def list_databases(self) -> Dict[str, Path]:
        return {
            db_name: self._db_path / db_name for db_name in self._db_path.iterdir()
            if db_name.is_file()
        }
    
    def delete_database(self, db_name: str):
        path = self._db_path / db_name

        if not path.exists():
            raise ValueError(f"Database '{db_name}' does not exist.")
        
        path.unlink()

    def get_database(self, db_name: str) -> Database:
        db_file = self.list_databases().get(db_name, None)
        if not (db_file and db_file.exists()):
            raise ValueError(f"Database '{db_name}' does not exist.")
        return Database(db_file)
