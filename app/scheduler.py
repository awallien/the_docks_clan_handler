import asyncio

from container import Container


async def clan_db_schdeduler(container: Container, delay: int=3600, init_delay: int=900):
    """Schedules a task to update clan members' info in DB.
    For each member:
        1. fetch hiscore
        2. update rank, boss, skill, activity tables in DB
    """

    # Iniially wait until DB is ready
    # TODO: convert to check and wait
    await asyncio.sleep(init_delay)

    while True:
        try:
            # print("Running scheduled boss update...")
            # clan_service = container.clan_service()
            
            # skill_service = container.skill_service()
            # boss_service = container.boss_service()
            # activity_service = container.activity_service()
            # rank_service = container.rank_service()

            # # Example: fetch members from DB
            # members = clan_service.get_all_members()  # sync? wrap if needed

            # # If this is sync DB call, do:
            # members = await asyncio.to_thread(clan_service.get_all_members)

            # names = [m["member"] for m in members]

            # # Fetch hiscores in parallel (your earlier logic)
            # results = await fetch_many(names)

            # # Update DB
            # for name, data in results.items():
            #     if data is None:
            #         continue

            #     # if boss_service is sync → wrap it
            #     await asyncio.to_thread(
            #         boss_service.update_from_hiscore,
            #         name,
            #         data
            #     )
            pass
        except Exception as e:
            print(f"[Scheduler Error] {e}")
            return

        # wait 1 hour
        await asyncio.sleep(delay)