
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

from mgmt import COMMAND_HANDLERS, COMMAND_HELP, HELP_ROWS, CommandSpecsHandler

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

    def __init__(self, ):
        self._cli_prompt = "docks> "
        self._console = Console()
        self._session = self._build_prompt_session()
        self._completer = DocksClanCLICompleter(COMMAND_HELP)
        self._interrupt_armed = False
        self._last_interrupt_at = 0.0

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

    def run(self) -> int:
        """The main CLI run loop"""

        self._console.print(
            Panel.fit(
                "[bold cyan]The Docks Clan CLI[/bold cyan]\nType [bold]/help[/bold] for commands. Type [bold]/exit[/bold] to quit.",
                border_style="cyan",
            )
        )

        while True:
            try:
                raw = self._session.prompt(
                    self._cli_prompt,
                    completer=self._completer,
                    complete_while_typing=True,
                ).strip()
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

            if raw in {"/exit", "/quit", "exit", "quit"}:
                break

            if raw in {"/help", "help"}:
                self._print_help()
                continue

            if raw in {"/clear", "clear"}:
                self._console.clear()

            if not raw.startswith("/"):
                self._warn("Commands must start with '/'. Type /help for usage.")
                continue

            self._dispatch(raw)
        
        return 0

    def _dispatch(self, raw: str) -> None:
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

        handler_name = COMMAND_HANDLERS.get(command)
        if handler_name is None:
            self._error(f"Unknown command: {command}")
            return
        
        handler = getattr(CommandSpecsHandler, handler_name)

        try:
            resp = handler(args)
            if resp.success:
                self._ok(resp.msg)
            else:
                self._error(resp.msg)
        except Exception as exc:
            self._error(f"Command failed: {exc}")
