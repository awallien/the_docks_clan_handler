import asyncio
import argparse

from app import DocksClanCLI
from util import generate_hiscore_mdata_files


class DocksClanApp:
    """
    Main application class for the Docks Clan app.
    """
    def __init__(self):
        self._cli_runner = DocksClanCLI()
    
    async def _run_cli(self):
        """
        Init and run the CLI for the Docks Clan app.
        """
        self._cli_runner.run()

    async def _run_bot(self, **kwargs):
        pass

    async def run(self, flags=['cli'], **kwargs):
        """
        Run the Docks Clan app.
        TODO: Impl bot functionality, asyncio
        """
        tasks = []

        if "cli" in flags:
            tasks.append(asyncio.create_task(self._run_cli()))
        
        if "bot" in flags:
            tasks.append(asyncio.create_task(self._run_bot(**kwargs)))
        
        if tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for task in pending:
                task.cancel()
            for task in done:
                if task.exception():
                    raise task.exception()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Docks Clan App")
    parser.add_argument('--cli', action='store_true', help='Enable CLI mode')
    parser.add_argument('--bot', action='store_true', help='Enable Bot mode')
    parser.add_argument('--dev', action='store_true', help='Run bot in development mode')
    parser.add_argument('--prod', action='store_true', help='Run bot in production mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if not (args.cli or args.bot):
        parser.error("At least one of --cli or --bot must be specified.")
        
    flags = list()
    if args.cli:
        flags.append("cli")
    if args.bot:
        flags.append("bot")

    bot_mode = ""
    if args.bot:
        if args.dev and args.prod:
            parser.error("Cannot specify both --dev and --prod for bot mode.")
            exit(1)
        elif args.prod:
            bot_mode = "p"
        elif args.dev:
            bot_mode = "d"
        else:
            print("No bot mode specified, defaulting to 'development' mode.")
            bot_mode = "d"

    kwargs = dict()
    if bot_mode:
        kwargs["bot_mode"] = bot_mode
    kwargs["debug"] = args.debug

    generate_hiscore_mdata_files()  # Generate OSRS Hiscore metadata files

    try:
        asyncio.run(DocksClanApp().run(flags, **kwargs))
    except KeyboardInterrupt or asyncio.exceptions.CancelledError:
        print("\nExiting Docks Clan App...")