import asyncio
import argparse

from app import DocksClanCLI, clan_db_schdeduler
from container import Container
from db import Database, init_schema

BOT = None
stop_event = asyncio.Event()

async def run_cli(container):
    try:
        return await asyncio.to_thread(
            lambda: DocksClanCLI(container).run()
        )
    finally:
        stop_event.set()

async def main():
    parser = argparse.ArgumentParser(description="Docks Clan App")
    parser.add_argument('--cli', action='store_true', help='Enable CLI mode')
    parser.add_argument('--bot', action='store_true', help='Enable Bot mode')

    args = parser.parse_args()
    tasks = []

    if not (args.cli or args.bot):
        parser.error("At least one of --cli or --bot must be specified.")

    db = Database("clan.db")
    init_schema(db)
    container = Container(db)

    tasks.append(asyncio.create_task(clan_db_schdeduler(container, init_delay=900, delay=3600)))

    if args.cli:
        tasks.append(asyncio.create_task(run_cli(container)))
        
    if args.bot:
        global BOT
        from app.bot import BOT
        tasks.append(asyncio.create_task(BOT.run(container)))
    
    try:
        # Wait until stop_event is triggered (via CLI exit or KeyboardInterrupt)
        await stop_event.wait()
    finally:
        print("Shutting down...")
        if BOT is not None:
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
