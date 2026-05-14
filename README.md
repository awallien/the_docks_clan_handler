# The Docks Clan Handler

A Python project that provides:
- A **CLI tool** for command management and execution.
- A **Discord bot** powered by `discord.py` for server automation.

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
#### Running the CLI, Bot, or Both
```
PS > .\run.ps1 --cli [--bot]
```

### (Linux Based)
#### Running the CLI, Bot or Both
```
Not Supported. (Coming soon.)
```

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
