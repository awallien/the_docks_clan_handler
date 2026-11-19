import argparse
import asyncio
import signal

from app import DocksClanCLI, clan_db_schdeduler
from container import Container
from db import Database, init_schema


async def run_cli(container):
    return await DocksClanCLI(container).run()


async def run_bot(container):
    from app.bot import BOT

    try:
        await BOT.run(container)
    finally:
        await BOT.close()


async def main():
    parser = argparse.ArgumentParser(description="Docks Clan App")
    parser.add_argument('--cli', action='store_true', help='Run the CLI')
    parser.add_argument('--bot', action='store_true', help='Run the Discord bot')
    parser.add_argument('--scheduler', action='store_true', help='Run the scheduler')
    args = parser.parse_args()
    run_all = not (args.cli or args.bot or args.scheduler)

    db = Database("clan.db")
    init_schema(db)
    container = Container(db)

    loop = asyncio.get_running_loop()
    stop = asyncio.Event()
    installed_signals = []
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
            installed_signals.append(sig)
        except (NotImplementedError, RuntimeError):
            # Windows event loops do not support add_signal_handler.
            pass

    tasks = {}
    if args.cli or run_all:
        tasks[asyncio.create_task(run_cli(container), name="cli")] = "cli"
    if args.bot or run_all:
        tasks[asyncio.create_task(run_bot(container), name="bot")] = "bot"
    if args.scheduler or run_all:
        tasks[asyncio.create_task(clan_db_schdeduler(container, delay=3600), name="scheduler")] = "scheduler"
    stop_task = asyncio.create_task(stop.wait(), name="shutdown signal")

    try:
        done, _ = await asyncio.wait([*tasks, stop_task], return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task is stop_task:
                continue
            task.result()  # Propagate failures to the service manager.
            if tasks[task] != "cli":
                raise RuntimeError(f"{tasks[task]} stopped unexpectedly")
    finally:
        print("Shutting down...")
        for task in [*tasks, stop_task]:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, stop_task, return_exceptions=True)
        for sig in installed_signals:
            loop.remove_signal_handler(sig)
        print("All tasks stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
