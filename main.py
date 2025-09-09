import asyncio
import argparse

from app import DocksClanCLI, BOT

stop_event = asyncio.Event()

def blocking_cli(commands=[]):
    cli = DocksClanCLI()
    cli.run(commands)

async def run_cli(commands=[]):
    await asyncio.to_thread(blocking_cli, commands=commands)

async def main():
    parser = argparse.ArgumentParser(description="Docks Clan App")
    parser.add_argument('--cli', action='store_true', help='Enable CLI mode')
    parser.add_argument('--bot', action='store_true', help='Enable Bot mode')
    parser.add_argument('--cmds_file', type=argparse.FileType('r'), help="Path to a file containing commands, one per line")

    args = parser.parse_args()
    commands = []
    tasks = []

    if not (args.cli or args.bot):
        parser.error("At least one of --cli or --bot must be specified.")
        exit(1)
        
    if args.cli:
        if args.cmds_file:
            commands = [line.strip() for line in args.cmd_file if line.strip()]
        tasks.append(asyncio.create_task(run_cli(commands=commands)))
        
    if args.bot:
        tasks.append(asyncio.create_task(BOT.run()))
    
    try:
        # Wait until stop_event is triggered (via CLI exit or KeyboardInterrupt)
        await stop_event.wait()
    finally:
        print("Shutting down...")
        if args.bot:
            await BOT.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("All tasks stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("CTRL+C pressed. Exiting...")
        # Set stop_event to stop the bot if CLI isn't running
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(stop_event.set)
        except RuntimeError:
            # Event loop already closed
            pass
