import shlex
import sys
from mgmt import YamlCommandParser


class DocksClanCLI:

    def __init__(self, banner="Docks Clan Script Runner v2", prompt_chr=">"):
        self._banner = banner
        self._prompt_quit = False
        self._prompt_chr = prompt_chr
        self._parser = None

    def _print_cli_cmds(self):
        print("Available commands:")
        print("  load <file>    - Load command list")
        print("  quit|exit      - Exit program")
        print("  ?              - Print available commands")
        print("---")
        if self._parser is not None:
            print(self._parser.get_cmds())

    def run(self):
        print(self._banner)
        try:
            while not self._prompt_quit:
                resp = input(f"{self._prompt_chr}  ").strip()

                if not resp:
                    continue

                fields = shlex.split(resp)
                match fields[0]:
                    case "":
                        continue
                    case "load":
                        if not len(fields) == 2:
                            self._print_cli_cmds()
                            continue
                        match fields[1]:
                            case "?":
                                print("Available command sets:")
                                print("\n".join(f"  - {f}" for f in YamlCommandParser.get_yaml_files()))
                                continue
                            case _ if not YamlCommandParser.yaml_file_exists(fields[1]):
                                print("Command set not found.", file=sys.stderr)
                                continue
                        self._parser = YamlCommandParser().parse(fields[1])
                    case "quit"|"exit":
                        self._prompt_quit = True
                    case "?":
                        self._print_cli_cmds()
                    case "config"|"show":
                        if not self._parser:
                            print("Command set is not loaded. Please \"load\" a proper command set.", file=sys.stderr)
                            continue
                        status = self._parser.process(resp)
                        if not status:
                            print("Something went wrong", file=sys.stderr)
                        else: 
                            print(status)
        except EOFError:
            print("Exiting CLI...")
        except FileNotFoundError as fnfe:
            print(f"Unable to load file: {fnfe}")


if __name__ == "__main__":
    pass
