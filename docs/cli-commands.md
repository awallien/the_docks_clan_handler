# CLI commands

Start the application with the `--cli` flag to open the `docks>` prompt. Names
and paths containing spaces must be quoted. Member name matching is
case-sensitive. Type `/help` at the prompt for a command summary.

## Create a member: `/cm`

```text
/cm member="Player One" [joined_date=YYYY-MM-DD] [rank=1]
```

`member` is required. If `joined_date` is omitted, it defaults to the local
date. If `rank` is omitted, the member starts at rank 1. Valid manual ranks are `1`
through `24`, `A`, `D`, and `O`.

## Read members: `/rm`

```text
/rm [members ...] [skill=name,...|all] [boss=name,...|all] [activities=name,...|all] [save=path]
```

Without member names, `/rm` lists all members. Otherwise, give names separated
by spaces. The table always includes member details and adds columns for each
selected metric. A skill adds level and XP columns; a boss adds a kill count;
an activity adds its count. Metric names are case-insensitive and come from
[`resources/hiscore_constants.py`](../resources/hiscore_constants.py).

```text
/rm "Player One" PlayerTwo skill=attack,magic boss="Abyssal Sire" activities="Clue Scrolls (all)"
/rm "Player One" skill=all boss=all activities=all save="reports/player one.csv"
```

Use `all` on any metric option to include every metric in that category. Missing
stored values appear as `—` in the table and as empty cells in CSV. Large
selections can make a wide table. `save` writes a new UTF-8 CSV file; paths are
relative to the working directory unless absolute, the parent directory must
exist, and existing files are not overwritten. If some requested names do not
exist, only matching members are shown; if none match, the command reports an
error.

The displayed metrics are stored values refreshed by the scheduler. Unranked
values show as unavailable. `last_rank_update` is the date a rank change was
acknowledged through the bot.

## View pending rank changes: `/rank_updates`

```text
/rank_updates
/rank_updates all
/rank_updates report
/rank_updates report <id>
```

The first command shows unacknowledged changes; `all` also includes acknowledged
and superseded history. Staff with the configured Discord admin role can run `/docks rank_updates`
to calculate and report proposed changes; its optional
`ack` argument defaults to `false`. When set to `true`, it acknowledges
previously pending entries after the response is delivered; newly calculated
changes remain pending. Acknowledge changes after applying them in-game.
The member's current rank and acknowledgement date change only when a pending
proposal is acknowledged.
Viewing this CLI report does not change ranks or acknowledge entries.

`/rank_updates report` displays the latest full bot report, including skipped members;
use `/rank_updates report <id>` to retrieve an earlier report. Reports remain available
even if Discord delivery failed or the rank changes were later acknowledged.

## Update a member: `/um`

```text
/um member="Player One" [new_name="New Name"] [joined_date=YYYY-MM-DD] [rank=2]
```

`member` identifies the existing member. Supply at least one field to update.
`new_name` changes the name while keeping the member's ID and linked stats.
An exact duplicate name is rejected; capitalization differences are distinct.
The same rank values listed for `/cm` apply. A manually supplied rank is stored
directly; it is not recalculated by the rank service.

## Delete members: `/dm`

```text
/dm "Player One" PlayerTwo
```

Supply one or more member names. Deleting a member also removes their linked
skill, boss, and activity records. The shared metric reference lists remain.

## Run a command file: `/rf`

```text
/rf "path/to/commands.txt"
```

The file must be a readable UTF-8 text file without null bytes; its extension
does not matter. Docksy executes one command per line and skips blank lines.
Errors are displayed and later commands continue. Nested `/rf` calls are not
allowed. `/help` and `/clear` work in a file; `/exit` or `/quit` stops the file
and exits the CLI. If shutdown starts while a command is running, Docksy waits
for that command to finish and does not start the next line.

## Prompt controls

- `/help` displays the command summary.
- `/clear` clears the terminal.
- `/exit` and `/quit` exit the CLI. The corresponding names without `/` also
  work interactively.
