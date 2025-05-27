from colorama import init as colorama_init
from colorama import Fore

class Logger:
    def __init__(self):
        if getattr(self.__class__, '_has_instance', False):
            raise RuntimeError('Cannot create another instance')
        self.__class__._has_instance = True
        self.enable = False
        colorama_init(autoreset=True)
    
    def set_enable(self, enable):
        self.enable = enable

    def is_enabled(self):
        return self.enable

    def debug_print(self, msg):
        if self.enable:
            print(Fore.GREEN + msg)

    def err_print(self, msg):
        print(Fore.RED + msg)


_logger = Logger()
debug_set_enable = lambda x: _logger.set_enable(x)
debug_print = lambda msg: _logger.debug_print(msg)
err_print = lambda msg: _logger.err_print(msg)