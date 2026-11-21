# Database schema

Docksy stores its data in a SQLite database under `db/db_cache/`. The schema
is defined in [`db/schema.sql`](../db/schema.sql); this guide describes its
tables and how the application uses them.

SQLite `DATE` columns do not enforce a date format. Docksy normally stores
`clan.joined_date` and `clan.last_rank_update` as Python date ordinals. Refresh
and rank timestamps are stored as UTC text. Columns are nullable unless marked
required below. Foreign keys are enabled on Docksy database connections.

## Clan members and ranks

### `clan`

One row per clan member. The member name is unique.

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | INTEGER | Primary key. |
| `member` | TEXT | Required, unique player name. |
| `joined_date` | DATE | Date the member joined the clan. |
| `rank` | TEXT | Current acknowledged rank. |
| `last_rank_update` | DATE | Date the current rank was acknowledged. |

### `rank_changes`

Records proposed, acknowledged, and superseded rank changes for members.
Deleting a member also deletes their rank changes.

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | INTEGER | Auto-incrementing primary key. |
| `clan_id` | INTEGER | Required foreign key to `clan.id`. |
| `previous_rank` | TEXT | Rank before the proposed change. |
| `new_rank` | TEXT | Required proposed rank. |
| `created_at` | TEXT | Required time the change was created. |
| `acknowledged_at` | TEXT | Time the change was acknowledged, if applicable. |
| `superseded_at` | TEXT | Time the proposal was replaced or invalidated, if applicable. |

A change is pending when both `acknowledged_at` and `superseded_at` are null.

### `rank_reports`

Stores rank update reports for later retrieval through the CLI.

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | INTEGER | Auto-incrementing primary key. |
| `created_at` | TEXT | Required time the report was created. |
| `content` | TEXT | Required report text. |

## Hiscores

### `hiscore_refresh`

Stores the latest refresh attempt for each member. Deleting a member also
deletes their refresh record.

| Column | Type | Purpose |
| --- | --- | --- |
| `clan_id` | INTEGER | Primary key and foreign key to `clan.id`. |
| `status` | TEXT | Required: `pending`, `complete`, `incomplete`, or `failed`. |
| `attempted_at` | TEXT | Required time of the latest attempt. |
| `succeeded_at` | TEXT | Time of the last successful response, if any. |
| `attempt_id` | TEXT | Required identifier for the latest attempt. |

`incomplete` means a response was saved with one or more unavailable skills.
A failed refresh leaves the last successful snapshot intact.

### Reference tables: `skills`, `activities`, and `bosses`

Each table lists the known names for that category. Initialization seeds these
tables from `resources/hiscore_constants.py`.

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | INTEGER | Primary key. |
| `name` | TEXT | Unique skill, activity, or boss name. |

### `clan_skills`

Stores a member's skill snapshot. The primary key is (`clan_id`, `skill_id`).

| Column | Type | Purpose |
| --- | --- | --- |
| `clan_id` | INTEGER | Required foreign key to `clan.id`. |
| `skill_id` | INTEGER | Required foreign key to `skills.id`. |
| `level` | INTEGER | Non-negative skill level; defaults to `0`. |
| `total_xp` | INTEGER | Non-negative skill XP; defaults to `0`. |

### `clan_activities`

Stores activity scores. The primary key is (`clan_id`, `activity_id`).

| Column | Type | Purpose |
| --- | --- | --- |
| `clan_id` | INTEGER | Required foreign key to `clan.id`. |
| `activity_id` | INTEGER | Required foreign key to `activities.id`. |
| `count` | INTEGER | Non-negative activity score; defaults to `0`. |

### `clan_bosses`

Stores boss kill counts. The primary key is (`clan_id`, `boss_id`).

| Column | Type | Purpose |
| --- | --- | --- |
| `clan_id` | INTEGER | Required foreign key to `clan.id`. |
| `boss_id` | INTEGER | Required foreign key to `bosses.id`. |
| `count` | INTEGER | Non-negative boss kill count; defaults to `0`. |

Deleting a member or a reference entry cascades to its corresponding snapshot
rows. A successful refresh removes rows for unavailable or unranked values;
those values are represented by missing rows rather than stored as `-1`.

## Migrations

### `schema_migrations`

Tracks migrations recorded for the database. See the [migration guide](database-migrations.md).

| Column | Type | Purpose |
| --- | --- | --- |
| `version` | INTEGER | Migration version and primary key. |
| `name` | TEXT | Required migration filename. |
| `applied_at` | TEXT | Required time the migration was recorded. |
