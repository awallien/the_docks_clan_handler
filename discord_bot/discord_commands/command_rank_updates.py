import asyncio
import io

import discord


def _message_chunks(content, limit=1900):
    """Split text without exceeding Discord's UTF-16 message limit."""
    chunks = []
    chunk = ""
    size = 0

    for line in content.splitlines(keepends=True):
        line_size = len(line.encode("utf-16-le")) // 2
        if chunk and size + line_size > limit:
            chunks.append(chunk)
            chunk, size = "", 0

        for char in line:
            char_size = 2 if ord(char) > 0xFFFF else 1
            if size + char_size > limit:
                chunks.append(chunk)
                chunk, size = "", 0
            chunk += char
            size += char_size

    if chunk:
        chunks.append(chunk)

    return chunks


def _rank_lines(rows):
    return "\n".join(
        f"{row['member']}: {row['previous_rank'] or 'unknown'} -> {row['new_rank']}"
        for row in rows
    )


def _format_updates(result):
    sections = []
    if result["to_acknowledge"]:
        sections.append(
            "Checking these previously proposed rank changes for acknowledgement:\n"
            + _rank_lines(result["to_acknowledge"])
        )
    if result["proposed"]:
        sections.append(
            "Here are the proposed rank updates. Please update the ranks in-game, then "
            "run this command with ack=true to acknowledge the changes:\n" + _rank_lines(result["proposed"])
        )
    if not result["to_acknowledge"] and not result["proposed"]:
        sections.append("There are no pending rank updates.")
    if result["skipped"]:
        sections.append(
            "Could not check these members:\n"
            + "\n".join(f"{name}: {reason}" for name, reason in result["skipped"])
        )
    return "\n\n".join(sections)


async def _send_updates(interaction, result, attach_report):
    chunks = _message_chunks(_format_updates(result))
    options = {"content": chunks[0], "allowed_mentions": discord.AllowedMentions.none()}
    if attach_report:
        options["attachments"] = [
            discord.File(io.BytesIO(result["report"].encode("utf-8")), filename="rank-updates.txt")
        ]

    await interaction.edit_original_response(**options)
    await _send_followups(interaction, chunks[1:])


async def _send_followups(interaction, chunks):
    for chunk in chunks:
        await interaction.followup.send(
            content=chunk,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def discord_bot_command_rank_updates(bot, interaction, ack=False, report=False):
    """Calculate and report rank changes; acknowledge only after delivery."""
    await interaction.response.defer(ephemeral=True)

    service = bot.container.rank_update_service()
    result = await asyncio.to_thread(service.prepare_updates, ack)
    await _send_updates(interaction, result, report)

    if ack:
        acknowledged = await asyncio.to_thread(
            service.acknowledge_details,
            [row["id"] for row in result["to_acknowledge"]],
        )
        if acknowledged:
            confirmation = "The database has been updated with the acknowledged ranks:\n" + _rank_lines(acknowledged)
        else:
            confirmation = "No rank changes were acknowledged in the database."
        await _send_followups(interaction, _message_chunks(confirmation))
