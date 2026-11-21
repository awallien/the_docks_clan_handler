import asyncio
import logging
import sqlite3
from contextlib import contextmanager

from container import Container
from resources.hiscore_constants import ACTIVITIES, BOSSES, SKILLS
from util.osrs_api import Hiscore

logger = logging.getLogger(__name__)


class SchedulerAlreadyRunning(RuntimeError):
    pass


@contextmanager
def scheduler_lock(db_path):
    """Hold a separate SQLite write lock for this database's scheduler."""
    resolved_path = db_path.resolve()
    lock_path = resolved_path.with_name(resolved_path.name + ".scheduler.lock")
    conn = sqlite3.connect(lock_path, timeout=0)
    try:
        try:
            conn.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if getattr(exc, "sqlite_errorcode", 0) & 0xff in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                raise SchedulerAlreadyRunning(f"A scheduler is already running for {db_path}") from exc
            raise
        yield
    finally:
        conn.close()


def refresh_member(container: Container, member):
    """Fetch and atomically store one member's hiscore snapshot."""
    name = member["member"]
    repo = container.hiscore_repo()
    token = repo.begin_refresh(member["id"], name)
    if token is None:
        return False
    try:
        hiscore = Hiscore(name)
        skills = {}
        for metric in SKILLS:
            value = hiscore.skills.get(metric)
            if value.level < -1 or value.xp < -1:
                raise ValueError(f"Invalid hiscore values for skill '{metric}'")
            skills[metric] = None if value.level == -1 or value.xp == -1 else (value.level, value.xp)

        def scores(names, collection):
            result = {}
            for metric in names:
                score = collection.get(metric).score
                if score < -1:
                    raise ValueError(f"Invalid hiscore score for '{metric}'")
                result[metric] = None if score == -1 else score
            return result

        saved = repo.save_snapshot(member["id"], name, token, skills,
                                   scores(ACTIVITIES, hiscore.activities), scores(BOSSES, hiscore.bosses))
    except Exception:
        try:
            repo.fail_refresh(member["id"], name, token)
        except Exception:
            logger.exception("Could not record failed hiscore refresh for %s", name)
        raise
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
    """Refresh hiscores periodically; rank changes are handled separately."""
    with scheduler_lock(container.db.path):
        while True:
            await refresh_members(container)
            await asyncio.sleep(delay)
