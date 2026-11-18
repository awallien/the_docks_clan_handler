# Docksy

**Docksy** is a companion bot and CLI toolkit for managing The Docks clan, an OSRS clan community in game and on Discord.
It has multiple features, including tracking clan members, surface OSRS hiscore data, sumamrize drops, manage server-facing commands, and automate routine clan workflows from both Discord slash commands and an interactive terminal.


---

## Requirements
- Python 3.11+
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
The scheduler's hiscore refresh is not implemented yet.

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
