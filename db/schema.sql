CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clan (
    id INTEGER PRIMARY KEY,
    member TEXT NOT NULL UNIQUE,
    joined_date DATE,
    rank TEXT,
    last_rank_update DATE
);

CREATE TABLE IF NOT EXISTS hiscore_refresh (
    clan_id INTEGER PRIMARY KEY REFERENCES clan(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK(status IN ('pending', 'complete', 'incomplete', 'failed')),
    attempted_at TEXT NOT NULL,
    succeeded_at TEXT,
    attempt_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rank_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan_id INTEGER NOT NULL REFERENCES clan(id) ON DELETE CASCADE,
    previous_rank TEXT,
    new_rank TEXT NOT NULL,
    created_at TEXT NOT NULL,
    acknowledged_at TEXT,
    superseded_at TEXT
);

CREATE TABLE IF NOT EXISTS rank_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS bosses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS clan_skills (
    clan_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    level INTEGER DEFAULT 0 CHECK(level >= 0),
    total_xp INTEGER DEFAULT 0 CHECK(total_xp >= 0),

    PRIMARY KEY (clan_id, skill_id),

    FOREIGN KEY(clan_id) REFERENCES clan(id) ON DELETE CASCADE,
    FOREIGN KEY(skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS clan_activities (
    clan_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    count INTEGER DEFAULT 0 CHECK(count >= 0),

    PRIMARY KEY (clan_id, activity_id),

    FOREIGN KEY(clan_id) REFERENCES clan(id) ON DELETE CASCADE,
    FOREIGN KEY(activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS clan_bosses (
    clan_id INTEGER NOT NULL,
    boss_id INTEGER NOT NULL,
    count INTEGER DEFAULT 0 CHECK(count >= 0),

    PRIMARY KEY (clan_id, boss_id),

    FOREIGN KEY(clan_id) REFERENCES clan(id) ON DELETE CASCADE,
    FOREIGN KEY(boss_id) REFERENCES bosses(id) ON DELETE CASCADE
);
