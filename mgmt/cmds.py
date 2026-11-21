from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

CLI_WELCOME = (
    "[bold cyan]The Docks Clan CLI[/bold cyan]\n"
    "Type [bold]/help[/bold] for commands. Type [bold]/exit[/bold] to quit."
)
COMMAND_PREFIX_WARNING = "Commands must start with '/'. Type /help for usage."

@dataclass(frozen=True)
class CommandSpec:
    name: str
    usage: str
    description: str
    handler: Optional[str] = None
    required_args: frozenset[str] = frozenset()
    required_positionals: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    control: Optional[str] = None
    no_arguments: bool = False
    allow_in_file: bool = True
    table_output: bool = False

@dataclass
class CommandSpecResponse:
    success: bool
    msg: str

COMMAND_SPECS: Tuple[CommandSpec, ...] = (
    # Clan member's entry commands
    CommandSpec(
        name="/cm",
        usage="/cm member=... [joined_date=YYYY-MM-DD] [rank=...]",
        description="Create a new clan member's entry in clan DB",
        handler="cmd_cm",
        required_args=frozenset({"member"}),
    ),
    CommandSpec(
        name="/rm",
        usage="/rm [members ...] [skill=name,...|all] [boss=name,...|all] [activities=name,...|all] [save=path]",
        description="Show member details and selected metrics; optionally save CSV",
        handler="cmd_rm",
        table_output=True,
    ),
    CommandSpec(
        name="/um",
        usage="/um member=... [new_name=...] [key=value ...]",
        description="Update a clan member's info in clan DB",
        handler="cmd_um",
        required_args=frozenset({"member"}),
    ),
    CommandSpec(
        name="/dm",
        usage="/dm member [members ...]",
        description="Delete clan member's entry(s) from clan DB",
        handler="cmd_dm",
        required_positionals=("member",),
    ),

    # Internal help, exit, quit
    CommandSpec(name="/rank_updates", usage="/rank_updates [all|report [id]]", description="Show rank changes or a saved report", handler="cmd_rank_updates", table_output=True),
    CommandSpec(name="/rf", usage="/rf </path/to/cmd-file>", description="File of commands to pass to execute in CLI", control="_read_cmd_file", allow_in_file=False),
    CommandSpec(name="/help", usage="/help", description="Show help", aliases=("help",), control="_control_help", no_arguments=True),
    CommandSpec(name="/clear", usage="/clear", description="Clear the terminal", aliases=("clear",), control="_control_clear", no_arguments=True),
    CommandSpec(name="/exit", usage="/exit", description="Exit CLI", aliases=("exit",), control="_control_exit", no_arguments=True),
    CommandSpec(name="/quit", usage="/quit", description="Exit CLI", aliases=("quit",), control="_control_exit", no_arguments=True),
)

COMMAND_HELP: Dict[str, str] = {spec.name: spec.description for spec in COMMAND_SPECS}
COMMANDS_BY_NAME = {name: spec for spec in COMMAND_SPECS for name in (spec.name, *spec.aliases)}
HELP_ROWS: List[Tuple[str, str]] = [(spec.usage, spec.description) for spec in COMMAND_SPECS]
COMMAND_HANDLERS: Dict[str, str] = {spec.name: spec.handler for spec in COMMAND_SPECS if spec.handler is not None}
COMMAND_REQUIRED_ARGS = {spec.handler: spec.required_args for spec in COMMAND_SPECS if spec.handler is not None}
COMMAND_REQUIRED_POSITIONALS = {spec.handler: spec.required_positionals for spec in COMMAND_SPECS if spec.handler is not None}
