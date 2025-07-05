from colorama import init as colorama_init
from colorama import Fore
import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_file='app.log'):
        if hasattr(self.__class__, '_has_instance'):
            raise RuntimeError('Cannot create another instance')
        self.__class__._has_instance = True
        self.enable = False
        colorama_init(autoreset=True)
        self.__init_log_dir(log_file)

    def __init_log_dir(self, log_file):
            # Set up logging to a file with rotation
        log_dir = os.path.dirname(os.path.join(os.path.abspath(__file__), "logs"))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logger = logging.getLogger('the_docks_clan_handler')
        self.logger.setLevel(logging.DEBUG)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def set_enable(self, enable):
        self.enable = enable

    def is_enabled(self):
        return self.enable

    def debug_print(self, msg):
        if self.enable:
            self.logger.debug(Fore.GREEN + msg)

    def err_print(self, msg):
        self.logger.error(Fore.RED + msg)


_logger = Logger()
debug_set_enable = lambda x: _logger.set_enable(x)
debug_print = lambda msg: _logger.debug_print(msg)
err_print = lambda msg: _logger.err_print(msg)