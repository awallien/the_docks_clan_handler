from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass(frozen=True)
class CommandSpec:
    name: str
    usage: str
    description: str
    handler: Optional[str] = None
    required_args: frozenset[str] = frozenset()
    required_positionals: tuple[str, ...] = ()

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
        usage="/rm [members ...]",
        description="List all members or selected members' entries (space-separated) from clan DB",
        handler="cmd_rm",
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
    CommandSpec(name="/rf", usage="/rf </path/to/cmd-file>", description="File of commands to pass to execute in CLI"),
    CommandSpec(name="/help", usage="/help", description="Show help"),
    CommandSpec(name="/clear", usage="/clear", description="Clear the terminal"),
    CommandSpec(name="/exit", usage="/exit", description="Exit CLI"),
    CommandSpec(name="/quit", usage="/quit", description="Exit CLI"),
)

COMMAND_HELP: Dict[str, str] = {spec.name: spec.description for spec in COMMAND_SPECS}
HELP_ROWS: List[Tuple[str, str]] = [(spec.usage, spec.description) for spec in COMMAND_SPECS]
COMMAND_HANDLERS: Dict[str, str] = {spec.name: spec.handler for spec in COMMAND_SPECS if spec.handler is not None}
COMMAND_REQUIRED_ARGS = {spec.handler: spec.required_args for spec in COMMAND_SPECS if spec.handler is not None}
COMMAND_REQUIRED_POSITIONALS = {spec.handler: spec.required_positionals for spec in COMMAND_SPECS if spec.handler is not None}
