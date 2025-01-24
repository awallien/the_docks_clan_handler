import shlex
from mgmt import YamlCommandParser


class DocksClanScriptRunner:

    def __init__(self, banner="Docks Clan Script Runner v2", prompt_chr=">"):
        self._banner = banner
        self._prompt_quit = False
        self._prompt_chr = prompt_chr
        self._parser = YamlCommandParser().init_yaml_commands("docks_clan_commands")

    def run(self):
        print(self.banner)
        while not self._prompt_quit:
            resp = input(f"{self._prompt_chr}").strip()

            if not resp:
                continue

            fields = shlex.split(resp)
            match fields[0]:
                case "quit"|"exit":
                    self._prompt_quit = True
                case _:
                    status = self._parser.process(fields)
                    if not status:
                        print("Something went wrong")

if __name__ == "__main__":
    pass