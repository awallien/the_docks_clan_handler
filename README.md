# Docksy

**Docksy** is a companion bot and CLI toolkit for managing The Docks clan, an OSRS clan community in game and on Discord.
It has multiple features, including tracking clan members, surface OSRS hiscore data, sumamrize drops, manage server-facing commands, and automate routine clan workflows from both Discord slash commands and an interactive terminal.


---

## Requirements
- Python 3.11+
- SQLite 3.35+ when migrating an existing database that has `last_rank_date`
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- Other dependencies listed in `requirements.txt`

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## Usage
### (Windows 10+ Based)
#### Running the CLI and Bot
```
PS > .\run.ps1
```

### (Linux Based)
#### Running the CLI and Bot
```
$ ./run.sh
```

By default, the CLI, bot, and scheduler run together. Use `./run.sh --bot` and
`./run.sh --scheduler` to run the bot and scheduler independently, and
`./run.sh --cli` for a separate administrative session. Flags can be combined;
the same flags work with `run.ps1`. Run only one scheduler instance at a time.
The scheduler refreshes stored hiscores for clan members on startup and
then every hour. Unranked values are skipped, leaving any previously stored
value unchanged. After a successful refresh it recalculates eligible clan ranks
and marks changes as pending. Special, honorary, and administrative ranks are
left unchanged. The `rank_update` flag remains set until a future reporting
workflow clears it; the bot command to report and clear flags is not yet built.

See the [CLI command reference](docs/cli-commands.md) for all commands and
examples.

In the CLI, `/rm` displays member details in a table. Select stored metrics and
optionally save the same rows to a new CSV file, for example:

```text
/rm "Player One" PlayerTwo skill=attack,magic boss="Abyssal Sire" activities="Clue Scrolls (all)" save=report.csv
/rm "Player One" skill=all boss=all activities=all
```

Omit player names to show all members. Metric names come from
`resources/hiscore_constants.py`; quote arguments containing spaces. Missing
stored values display as `—` and are blank in CSV. Existing files are not
overwritten. The `all` options can produce a very wide table; CSV may be easier
to inspect.

Note that running these scripts will also generate the needed OSRS metadata files:
- `util/osrs_api/bosses.py`
- `util/osrs_api/skills.py`
- `util/osrs_api/activities.py`

---

## Configuration
See `env.example` for the required environment variables.

---

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
