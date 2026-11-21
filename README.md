# Docksy

**Docksy** is a companion bot and CLI toolkit for managing The Docks clan, an OSRS clan community in game and on Discord.

---
## Requirements
- Python 3.11+
- SQLite 3.35+ when migrating an existing database
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- Other dependencies listed in `requirements.txt`

Install dependencies with:
```bash
pip install -r requirements.txt
```
---

## Usage
### (Windows 10+ Based)
#### Running Docksy
```
PS > .\run.ps1
```

### (Linux Based)
#### Running Docksy
```
$ ./run.sh
```

By default, the CLI, bot, and scheduler run together. Use `./run.sh --bot` and
`./run.sh --scheduler` to run the bot and scheduler independently, and
`./run.sh --cli` for a separate administrative session. Flags can be combined.
The same flags work with `run.ps1`.

Running either script also generates the required OSRS metadata files:

- `util/osrs_api/bosses.py`
- `util/osrs_api/skills.py`
- `util/osrs_api/activities.py`

**Note**: For any database migration, stop all Docksy processes before applying changes, and then restart them afterward.
Generally, these migrations should be perfomed during a planned maintenance window.
See the [database migration guide](docs/database-migrations.md) for details.
The [database schema reference](docs/database-schema.md) describes the tables and columns.

## Bot

The Discord bot provides clan members with server guides, drop summaries, and
other community tools. It also lets the bot owner review member requests and
manage rank updates using stored hiscore data.

See the [Discord command reference](docs/discord-commands.md) for details.

## CLI

The CLI provides an interactive terminal for administering clan members,
viewing stored hiscores, exporting reports, and reviewing rank changes.

See the [CLI command reference](docs/cli-commands.md) for details.

## Scheduler

The scheduler refreshes hiscores on startup and then waits one hour between
cycles. Unranked values are shown as unavailable, and failed refreshes leave
the last snapshot intact. It records refresh outcomes but does not update ranks.

Only one scheduler can run for a database at a time. A second instance exits
with an error; a separate SQLite lock file coordinates the processes without
blocking the CLI or bot from using the database.

---

## Configuration
See `env.example` for the required environment variables.

---

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
