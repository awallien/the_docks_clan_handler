CREATE TABLE IF NOT EXISTS clan(
    id INTEGER PRIMARY KEY,
    member TEXT NOT NULL UNIQUE,
    joined_date DATE,
    rank TEXT,
    last_rank_date DATE
);

CREATE TABLE IF NOT EXISTS skills(
    id INTEGER PRIMARY KEY,
    clan_id INTEGER UNIQUE,
    attack INTEGER,
    defence INTEGER,
    strength INTEGER,
    hitpoints INTEGER,
    ranged INTEGER,
    prayer INTEGER,
    magic INTEGER,
    cooking INTEGER,
    woodcutting INTEGER,
    fletching INTEGER,
    fishing INTEGER,
    firmaking INTEGER,
    crafting INTEGER,
    smithing INTEGER,
    mining INTEGER,
    herblore INTEGER,
    agility INTEGER,
    thieving INTEGER,
    slayer INTEGER,
    farming INTEGER,
    runecrafting INTEGER,
    hunter INTEGER,
    construction INTEGER,
    sailing INTEGER,
    FOREIGN KEY(clan_id)
        REFERENCES clan(id)
        ON DELETE CASCADE
);