import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Dict

class _DocksClanLogger(logging.Logger):
    def __init__(self, log_file):
        super().__init__(log_file)
        self.setLevel(logging.INFO)
        log_dir = os.path.join(Path(__file__).parent.parent, "logs")
        if log_dir and not os.path.exists(log_dir):
            os.mkdir(log_dir, mode=744)
        handler = RotatingFileHandler(
            os.path.join(log_dir, log_file), maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(filename)s, %(funcName)s] %(message)s"
        )
        handler.setFormatter(formatter)
        if not self.hasHandlers():
            self.addHandler(handler)

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name == value
        if isinstance(value, _DocksClanLogger):
            return self.name == value.name
        return False
    
    def __hash__(self):
        return hash(self.name)
    


loggers : Dict[str, _DocksClanLogger] = {
    _DocksClanLogger("docks_clan.log")
}

def get_logger(log_file=''):
    log_file = (log_file or "docks_clan") + ".log"
    loggers[log_file] = loggers.get(log_file, _DocksClanLogger(log_file))

def set_logger_level(lvl: int, log_file: str = "") -> bool:
    """
    Set logging level for a specific logger or all loggers.
    """
    if lvl not in logging._nameToLevel.values():
        return False

    if log_file:
        logger = loggers.get(log_file)
        if not logger:
            return False
        logger.setLevel(lvl)
        return True

    for logger in loggers.values():
        logger.setLevel(lvl)

    return True
