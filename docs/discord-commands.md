# Discord Bot Commands

Docksy exposes these Discord slash commands under the `/docks` command group.

General commands require any role listed in `ALLOWED_ROLES` or the configured
`ADMIN_ROLE`. The `ADMIN_ROLE` is required for staff-only commands.
Configure `ALLOWED_ROLES` as a comma-separated list of exact Discord role names
and `ADMIN_ROLE` as one exact role name. The staff role can use general
commands even if it is not listed in `ALLOWED_ROLES`.

In the table, **all** means any configured general or admin role, and **admin**
means the configured admin role only.

## Commands

| Command | Arguments | Allowed roles | Description |
| --- | --- | --- | --- |
| `/docks docs` | None | all | Shows guides, references, and useful docs for the server and clan. |
| `/docks drops` | `historical_days`, `member` | all | Fetches a summary of drops from the drops channel and clog thread. Requesting all members also requires being the configured bot owner. |
| `/docks spin` | `options`, `weights`, `randomize_weights` | all | Picks one option from a semicolon-separated list, optionally using weights. |
| `/docks new_member` | `member` | all | Sends a new-member request to the bot owner/moderator. |
| `/docks update_member` | `member`, `name_change` | all | Sends a member update request to the bot owner/moderator. |
| `/docks delete_member` | `member` | all | Sends a member removal request to the bot owner/moderator. |
| `/docks clan_stats` | `member`, `verbose` | all | Shows the acknowledged rank and date, with optional hiscore-derived rank details. |
| `/docks rank_updates` | `ack`, `report` | admin | Calculates and displays proposed rank changes using stored hiscores. |
| `/docks challenge` | None | all | Sends a challenge request to the bot owner/moderator. |
| `/docks donate` | `value` | all | Displays a donation acknowledgement for a value greater than 0 and at most 10. |

## Argument Details

### `/docks drops`

- `historical_days`: optional number of days to scan. Choices: `7`, `14`, `30`, `60`, `90`, `180`. Defaults to `30`.
- `member`: optional RSN filter. If omitted, only the configured bot owner can request all members, and they must still have an allowed role.

### `/docks spin`

- `options`: required semicolon-separated options. Example: `raid;skill;boss`.
- `weights`: optional semicolon-separated weights matching the number of options. Lower weights are more likely because the command converts weights into inverse probabilities.
- `randomize_weights`: optional boolean. If enabled, supplied weights are shuffled; if no weights are supplied, random weights are generated.

### Member Commands

- `member`: RSN of the clan member.
- `name_change`: optional new RSN for `/docks update_member`.
- `verbose`: optional boolean for `/docks clan_stats`; when enabled, Docksy attempts to include hiscore-derived rank details.

### `/docks rank_updates`

- `ack`: optional boolean, defaulting to `false`. When `true`, changes that
  were already pending before this run are acknowledged after all messages are
  delivered. Newly calculated changes remain pending. Acknowledge changes after
  applying them in-game.
- `report`: optional boolean, defaulting to `false`. When `true`, a text report
  is attached to the response as well as displaying the updates in messages.
- The stored current rank and acknowledgement date change only when the
  corresponding pending proposal is acknowledged. A newer proposal replaces an
  outdated pending proposal.
- The command uses stored snapshots; members whose latest refresh failed or has
  not completed are skipped. The full report can also be retrieved through the
  CLI, including if Discord delivery fails.
