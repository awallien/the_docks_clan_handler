CREATE TABLE IF NOT EXISTS clan (
    id INTEGER PRIMARY KEY,
    member TEXT NOT NULL UNIQUE,
    joined_date DATE,
    rank TEXT,
    last_rank_date DATE
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