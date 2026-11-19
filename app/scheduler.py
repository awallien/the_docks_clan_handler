import asyncio
import logging

from container import Container
from resources.hiscore_constants import ACTIVITIES, BOSSES, SKILLS
from util.osrs_api import Hiscore

logger = logging.getLogger(__name__)


def refresh_member(container: Container, member):
    """Fetch and atomically store one member's ranked hiscore values."""
    name = member["member"]
    hiscore = Hiscore(name)
    skills = {}
    for metric in SKILLS:
        value = hiscore.skills.get(metric)
        if value.level < -1 or value.xp < -1:
            raise ValueError(f"Invalid hiscore values for skill '{metric}'")
        if value.level != -1 and value.xp != -1:
            skills[metric] = (value.level, value.xp)

    def scores(names, collection):
        result = {}
        for metric in names:
            score = collection.get(metric).score
            if score < -1:
                raise ValueError(f"Invalid hiscore score for '{metric}'")
            if score != -1:
                result[metric] = score
        return result

    def calculate_rank(current_rank, joined_date):
        try:
            return container.rank_service().get_next_rank(hiscore, current_rank, joined_date)
        except (TypeError, ValueError, OverflowError):
            logger.exception("Cannot calculate rank for %s; keeping current rank", name)
            return None

    saved = container.hiscore_repo().save_snapshot(
        member["id"], name, skills,
        scores(ACTIVITIES, hiscore.activities), scores(BOSSES, hiscore.bosses),
        calculate_rank,
    )
    if not saved:
        logger.info("Skipped %s: member was renamed or removed during refresh", name)
    return saved


async def refresh_members(container: Container):
    members = await asyncio.to_thread(container.clan_service().list_members)
    for member in members:
        task = asyncio.create_task(asyncio.to_thread(refresh_member, container, member))
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            # Do not abandon an in-flight fetch/write on shutdown.
            try:
                await task
            except Exception:
                logger.exception("Hiscore refresh failed for %s during shutdown", member["member"])
            raise
        except Exception:
            logger.exception("Hiscore refresh failed for %s", member["member"])


async def clan_db_schdeduler(container: Container, delay: int = 3600):
    """Refresh hiscores and eligible ranks periodically."""
    while True:
        await refresh_members(container)
        await asyncio.sleep(delay)
