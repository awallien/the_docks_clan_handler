import shlex
from argparse import ArgumentParser
from . import debug_set_enable, debug_print

class PromptArgsResponse:
    def __init__(self, res, err_msg):
        self.res = res
        self.err = err_msg

    def __bool__(self):
        return self.res

RESPONSE_OK = PromptArgsResponse(True, "")
RESPONSE_ERR = lambda err_msg: PromptArgsResponse(False, err_msg)

def default_response_ok(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        return RESPONSE_OK
    return inner

class PromptArgs:
    def __init__(self, arg_name, cb, desc="", req_params = [], opt_params = [], opt_no_arg_params=[]):
        self.arg_name = arg_name
        self.cb = cb
        self.desc = desc
        self.arg_parser = ArgumentParser(prog=arg_name, description=desc, allow_abbrev=False)
        self.__init_arg_parser(req_params, opt_params, opt_no_arg_params)

    def __init_arg_parser(self, req_params, opt_params, opt_no_arg_params):
        for param in req_params:
            self.arg_parser.add_argument(param)
        for param in opt_params:
            self.arg_parser.add_argument("--"+param)
        for param in opt_no_arg_params:
            self.arg_parser.add_argument("--"+param, action="store_true", default=False)
        
    def print_help(self):
        print(self.arg_name, " "*(15-len(self.arg_name)), self.desc)
        
    def process(self, params):
        args_list = shlex.split(params)
        try:
            args = self.arg_parser.parse_args(args_list)
        except SystemExit:
            return RESPONSE_ERR("")
        return self.cb(args)
    
class PromptRunner:
    def __init__(self, cmds, quit_cmd="exit", banner="Script Prompt v1.0", prompt_chr=">", quit_handler=None):
        self.prompt_cmds = cmds
        self.prompt_quit = False
        self.banner = banner
        self.prompt_chr = prompt_chr

        # TODO: handle quit if db is not saved, for example
        self.quit_handler = quit_handler

        self.prompt_cmds["help"] = PromptArgs("help", self.prompt_help_call, "Prints list of commands and their description")
        self.prompt_cmds[quit_cmd] = PromptArgs(quit_cmd, self.prompt_quit_call, "Ends program")
        self.prompt_cmds["debug"] = PromptArgs("debug", self.prompt_debug_enable, "Enable/Disable debug", opt_no_arg_params=["on", "off"])

    @default_response_ok
    def prompt_quit_call(self, _):
        self.prompt_quit = True

    @default_response_ok
    def prompt_help_call(self, _):
        for cmd in self.prompt_cmds.values():
            cmd.print_help()

    @default_response_ok
    def prompt_debug_enable(self, args):
        on = args.on
        off = args.off
        debug_set_enable(True if on else False if off else False)
        debug_print(f"Debug is turned on")

    def run(self):
        print(self.banner)
        while not self.prompt_quit:
            resp = input(f"{self.prompt_chr} ")
            fields = resp.split(" ")
            cmd = fields[0]

            if not cmd:
                continue

            if cmd not in self.prompt_cmds:
                print("Invalid command:", cmd, "\nType 'help' to see list of commands")
                continue

            status = self.prompt_cmds[cmd].process(" ".join(fields[1:]))
            if not status.res:
                print(status.err)