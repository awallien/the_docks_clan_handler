
import asyncio
import shlex
import time
from pathlib import Path
from typing import Dict

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from container import Container
from mgmt import (COMMANDS_BY_NAME, COMMAND_HELP, HELP_ROWS, CLI_WELCOME,
                  COMMAND_PREFIX_WARNING, CommandSpecsHandler)

class DocksClanCLICompleter(Completer):
    """Command completer that includes short descriptions in dropdown metadata."""

    def __init__(self, command_help: Dict[str, str]):
        self._command_help = command_help

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if " " in text:
            return
        
        for command, description in self._command_help.items():
            if command.startswith(text):
                yield Completion(
                    command,
                    start_position=-len(text),
                    display=command,
                    display_meta=description,
                )


class DocksClanCLI:
    """Interactive runtime CLI"""

    def __init__(self, container: Container):
        self._cli_prompt = "docks> "
        self._console = Console()
        self._session = self._build_prompt_session()
        self._completer = DocksClanCLICompleter(COMMAND_HELP)
        self._interrupt_armed = False
        self._last_interrupt_at = 0.0
        self._handler = CommandSpecsHandler(container)

    def _build_prompt_session(self) -> PromptSession:
        history_file = Path(__file__).parent.resolve() / ".cli_history"
        style = Style.from_dict(
            {
                "prompt": "ansicyan bold",
            }
        )

        return PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=style,
        )
    
    def _ok(self, message: str) -> None:
        self._console.print(f"[green]✓[/green] {message}")

    def _warn(self, message: str) -> None:
        self._console.print(f"[yellow]![/yellow] {message}")
    
    def _error(self, message: str) -> None:
        self._console.print(f"[red]✗[/red] {message}")

    def _info(self, message: str) -> None:
        self._console.print(f"[cyan]•[/cyan] {message}")

    def _print_help(self) -> None:
        table = Table(title="The Docks Clan CLI Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for usage, description in HELP_ROWS:
            table.add_row(usage, description)
        
        self._console.print(table)

    async def run(self) -> int:
        """The main CLI run loop"""

        self._console.print(
            Panel.fit(
                CLI_WELCOME,
                border_style="cyan",
            )
        )

        while True:
            try:
                raw = (await self._session.prompt_async(
                    self._cli_prompt,
                    completer=self._completer,
                    complete_while_typing=True,
                )).strip()
            except EOFError:
                self._console.print("")
                break
            except KeyboardInterrupt:
                now = time.monotonic()
                if self._interrupt_armed and (now - self._last_interrupt_at) <= 2.0:
                    self._warn("Exiting on second Ctrl+C.")
                    break
                self._interrupt_armed = True
                self._last_interrupt_at = now
                self._warn("Press Ctrl+C again within 2 seconds to exit.")
                continue
                
            if not raw:
                continue

            self._interrupt_armed = False

            if await self._dispatch(raw):
                break
        
        return 0
    
    def _print_response(self, resp, *, table=False) -> None:
        if resp is None:
            self._warn("Command completed with no output.")
        
        elif isinstance(resp, list):
            if table and resp:
                display = Table(show_header=True, header_style="bold magenta")
                for name in resp[0]:
                    display.add_column(str(name))
                for row in resp:
                    display.add_row(*(str(value) if value is not None else "—" for value in row.values()))
                self._console.print(display)
            else:
                for item in resp:
                    self._console.print(dict(item) if hasattr(item, "keys") else item)
        
        else:
            self._ok(str(resp))

    async def _dispatch(self, raw: str, in_cmd_file: bool = False) -> bool | None:
        """Handles raw input from the user"""

        try:
            parts = shlex.split(raw)
        except ValueError as exc:
            self._error(f"Parse error: {exc}")
            return
        
        if not parts:
            return
        
        command = parts[0]
        args = parts[1:]
        spec = COMMANDS_BY_NAME.get(command)
        if not in_cmd_file and not raw.startswith("/") and (spec is None or args):
            self._warn(COMMAND_PREFIX_WARNING)
            return

        if spec is not None and spec.control and (not spec.no_arguments or not args):
            if in_cmd_file and not spec.allow_in_file:
                self._error("Invalid command: Recursive file reads not allowed")
                return
            return await getattr(self, spec.control)(args)

        task = asyncio.create_task(asyncio.to_thread(self._handle_command, command, args))
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            if not task.done():
                self._warn("Waiting for the current command to finish before shutting down.")
            await task
            raise

    async def _control_help(self, args):
        self._print_help()

    async def _control_clear(self, args):
        self._console.clear()

    async def _control_exit(self, args):
        return True

    async def _read_cmd_file(self, args: list[str]):
        """Read file of commands and dispatch them"""
        if not len(args) == 1:
            self._error("Command failed: expects one arg - </path/to/cmd-file>")
            return

        filepath = Path(args[0])
        if not filepath.exists():
            self._error(f"Command failed: '{args[0]}' file not found")
            return

        if not filepath.is_file():
            self._error(f"Command failed: '{args[0]}' is not a regular file")
            return

        try:
            contents = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self._error(f"Command failed: unable to read '{args[0]}' as UTF-8 text: {exc}")
            return

        if "\x00" in contents:
            self._error(f"Command failed: '{args[0]}' is not a text file")
            return

        for line in contents.splitlines():
            await asyncio.sleep(0)
            if not (line := line.strip()):
                continue
            if await self._dispatch(line, True) is True:
                return True

    def _handle_command(self, command: str, args: list[str]):
        spec = COMMANDS_BY_NAME.get(command)
        if spec is None or spec.handler is None:
            self._error(f"Unknown command: {command}")
            return
        
        handler = getattr(self._handler, spec.handler)

        try:
            resp = handler(args)
            self._print_response(resp, table=spec.table_output)
        except Exception as exc:
            self._error(f"Command failed: {exc}")
