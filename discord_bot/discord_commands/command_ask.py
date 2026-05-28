import asyncio
import discord
import subprocess

from dataclasses import dataclass
from pathlib import Path

from app import settings
from discord_bot_util import EmbedUtil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot import TheDocksDiscordBot

MAX_AGENT_RETRY = 1

@dataclass
class AgentResponse:
    return_code: int
    msg: int

async def _execute_agent(exec: str,
                         api_key: str,
                         model: str,
                         query: str) -> AgentResponse:
    retry = 0
    db_cache_path = Path(__file__).resolve().parent.parent / "db" / "db_cache"
    command = [
        exec,
        "--api-key", api_key,
        "--model", model,
        "-p",
        "--approve-mcps",
        "--workspace", db_cache_path, "--trust",
        "--mode", "ask",
        query.strip()
    ]
    agent_response = None

    while retry < MAX_AGENT_RETRY:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300
            )

            stdout = stdout.decode().strip()
            stderr = stderr.decode().strip()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    command,
                    output=stdout,
                    stderr=stderr,
                )

            return AgentResponse(
                return_code=process.returncode,
                msg=stdout,
            )

        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError("Command timed out after 300 seconds")
    
    return agent_response


async def discord_bot_command_ask(bot: "TheDocksDiscordBot",
                                  interaction: discord.Interaction,
                                  query: str):
    if not all([
        exec := settings.AGENT_CMD, 
        api_key := settings.AGENT_API_KEY,
        model := settings.AGENT_MODEL,
    ]):
        await interaction.response.send_message(
            embed=EmbedUtil.error_embed(
                title="Zzz...",
                msg="Looks like I'm not online. Check back with me later, or message Goose for any concerns."
            )
        )
        return
    
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(
        content="Processing your query..."
    )

    try:
        result = await _execute_agent(exec, api_key, model, query)
        if result.return_code != 0:
            raise
        msg = result.msg
    except Exception as e:
        msg = "My brain exploded. Get Goose to fix me!"

    await interaction.edit_original_response(
        content=msg
    )
