from datetime import date
from types import SimpleNamespace

from repositories.hiscore_repo import utc_now
from entity import ClanMemberRank
from resources.hiscore_constants import SKILLS
from util.osrs_api import Skills


class RankUpdateService:
    """Calculate rank changes from stored snapshots and retain reports."""

    def __init__(self, db, rank_service):
        self.db = db
        self.rank_service = rank_service

    @staticmethod
    def _load_skills(conn, member_id):
        skills = Skills()
        for name in SKILLS:
            skill = skills.get(name)
            skill.level, skill.xp = -1, -1
        rows = conn.execute(
            "SELECT s.name, cs.level, cs.total_xp FROM clan_skills cs "
            "JOIN skills s ON s.id = cs.skill_id WHERE cs.clan_id = ?", (member_id,)
        ).fetchall()
        for row in rows:
            skill = skills.get(row["name"])
            if skill is not None:
                skill.level, skill.xp = row["level"], row["total_xp"]
        return SimpleNamespace(skills=skills)

    def get_snapshot(self, member_id):
        with self.db.connection() as conn:
            conn.execute("BEGIN")
            row = conn.execute("SELECT status FROM hiscore_refresh WHERE clan_id = ?", (member_id,)).fetchone()
            if row is None or row["status"] not in ("complete", "incomplete"):
                return None
            return self._load_skills(conn, member_id)

    def calculate(self):
        skipped = []
        with self.db.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            members = conn.execute(
                "SELECT c.id, c.member, c.rank, c.joined_date, h.status "
                "FROM clan c LEFT JOIN hiscore_refresh h ON h.clan_id = c.id ORDER BY c.id"
            ).fetchall()
            for member in members:
                pending = conn.execute(
                    "SELECT id, previous_rank, new_rank FROM rank_changes "
                    "WHERE clan_id = ? AND acknowledged_at IS NULL AND superseded_at IS NULL ORDER BY id",
                    (member["id"],),
                ).fetchall()
                if (member["rank"] in ClanMemberRank.special_rank()
                        or member["rank"] in ClanMemberRank.honorable_ranks()
                        or member["rank"] in ClanMemberRank.administrative_ranks()):
                    if pending:
                        conn.execute("UPDATE rank_changes SET superseded_at = ? WHERE clan_id = ? AND acknowledged_at IS NULL AND superseded_at IS NULL", (utc_now(), member["id"]))
                    continue
                if member["status"] not in ("complete", "incomplete"):
                    skipped.append((member["member"], member["status"] or "not refreshed"))
                    continue
                hiscore = self._load_skills(conn, member["id"])
                try:
                    rank = self.rank_service.get_next_rank(hiscore, member["rank"], member["joined_date"])
                except (TypeError, ValueError, OverflowError) as exc:
                    skipped.append((member["member"], f"invalid member data: {exc}"))
                    continue
                # Keep one matching proposal; retire stale proposals when the
                # eligible or acknowledged rank has changed.
                matching = [row for row in pending if row["new_rank"] == rank
                            and (row["previous_rank"] == member["rank"] or row["new_rank"] == member["rank"])]
                keep = matching[-1]["id"] if matching else None
                for row in pending:
                    if row["id"] != keep:
                        conn.execute("UPDATE rank_changes SET superseded_at = ? WHERE id = ?", (utc_now(), row["id"]))
                if rank != member["rank"] and keep is None:
                    conn.execute("INSERT INTO rank_changes (clan_id, previous_rank, new_rank, created_at) VALUES (?, ?, ?, ?)",
                                 (member["id"], member["rank"], rank, utc_now()))
            conn.commit()
        return skipped

    def pending(self, include_acknowledged=False):
        condition = "" if include_acknowledged else "WHERE r.acknowledged_at IS NULL AND r.superseded_at IS NULL"
        return [dict(row) for row in self.db.fetch_all(
            "SELECT r.id, c.member, r.previous_rank, r.new_rank, r.created_at, r.acknowledged_at, r.superseded_at "
            "FROM rank_changes r JOIN clan c ON c.id = r.clan_id "
            f"{condition} ORDER BY r.id"
        )]

    def prepare_updates(self, ack=False):
        """Calculate proposals, save a report, and select changes for display."""
        previous = self.pending() if ack else []
        skipped = self.calculate()
        pending = self.pending()
        _, report = self.create_report(pending, skipped)

        previous_ids = {row["id"] for row in previous}
        to_acknowledge = [row for row in pending if row["id"] in previous_ids]
        proposed = [row for row in pending if row["id"] not in previous_ids]

        unrefreshed = [name for name, reason in skipped if reason == "not refreshed"]
        newly_joined = set()
        if unrefreshed:
            placeholders = ",".join("?" for _ in unrefreshed)
            members = self.db.fetch_all(
                f"SELECT member, rank, joined_date FROM clan WHERE member IN ({placeholders})",
                unrefreshed,
            )
            today = date.today().toordinal()
            newly_joined = {
                member["member"] for member in members
                if member["rank"] == "1"
                and isinstance(member["joined_date"], int)
                and 0 <= today - member["joined_date"] < 30
            }

        return {
            "to_acknowledge": to_acknowledge,
            "proposed": proposed,
            "skipped": [(name, reason) for name, reason in skipped
                        if reason != "not refreshed" or name not in newly_joined],
            "report": report,
        }

    def create_report(self, pending, skipped):
        lines = ["Pending rank changes:"]
        lines.extend(f"{row['member']}: {row['previous_rank'] or 'unknown'} -> {row['new_rank']} ({row['created_at']})" for row in pending)
        if not pending:
            lines.append("None.")
        if skipped:
            lines.append("\nSkipped members:")
            lines.extend(f"{name}: {reason}" for name, reason in skipped)
        content = "\n".join(lines)
        result = self.db.execute("INSERT INTO rank_reports (created_at, content) VALUES (?, ?)", (utc_now(), content))
        return result.lastrowid, content

    def get_report(self, report_id=None):
        if report_id is None:
            return self.db.fetch_one("SELECT * FROM rank_reports ORDER BY id DESC LIMIT 1")
        return self.db.fetch_one("SELECT * FROM rank_reports WHERE id = ?", (report_id,))

    def acknowledge(self, event_ids):
        return len(self.acknowledge_details(event_ids))

    def acknowledge_details(self, event_ids):
        """Apply eligible changes and return the changes actually acknowledged."""
        if not event_ids:
            return []
        with self.db.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            acknowledged = []
            now = utc_now()
            for event_id in event_ids:
                row = conn.execute(
                    "SELECT r.clan_id, r.previous_rank, r.new_rank, c.member, c.rank, h.status "
                    "FROM rank_changes r JOIN clan c ON c.id = r.clan_id "
                    "LEFT JOIN hiscore_refresh h ON h.clan_id = c.id "
                    "WHERE r.id = ? AND r.acknowledged_at IS NULL AND r.superseded_at IS NULL", (event_id,)
                ).fetchone()
                if row is None:
                    continue
                if row["status"] not in ("complete", "incomplete"):
                    continue
                if row["rank"] != row["previous_rank"] and row["rank"] != row["new_rank"]:
                    continue
                conn.execute("UPDATE rank_changes SET acknowledged_at = ? WHERE id = ?", (now, event_id))
                conn.execute("UPDATE clan SET rank = ?, last_rank_update = ? WHERE id = ?",
                             (row["new_rank"], date.today().toordinal(), row["clan_id"]))
                acknowledged.append(dict(row))
            conn.commit()
        return acknowledged
