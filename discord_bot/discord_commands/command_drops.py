from util import debug_print
from datetime import datetime, timedelta, timezone
import re
from discord import Color, Embed, app_commands
from discord_bot import info_embed

VALID_DAYS = [30, 60, 90, 180]

def get_drop_embed_info(embed: Embed):
    """processes one embed to get info of player, item, and the item's value"""
    info = type("info", (), {"player":"N/A", "item":"N/A", "quantity":1, "value":0})()
    info.player = embed.author.name
    
    # get GE value
    ge_value_field = next((field for field in embed.fields if field.name == "GE Value"), None)
    if ge_value_field:
        value_str = ge_value_field.value
        match = re.search(r'[\d,]+', value_str)
        info.value = int(match.group(0).replace(",", "")) if match else 0
    else:
        return None
    
    # get item name
    matches = re.search(r'(\d+x)?\s*\[([^\]]+)\]', embed.description)
    
    quantity = matches.group(1)
    if quantity:
        info.quantity = int(matches.group(1)[:-1])
    
    info.item = matches.group(2)

    return info

async def cb_drops(BOT, ctx, days=30, player=None):
    if days not in VALID_DAYS:
        await ctx.send(f"Error: invalid input for days ({days})", ephemeral=True)
        return
    
    if player and player not in BOT.db.get_members():
        await ctx.send(f"Error: member '{player}' not found in clan database")
        return
    
    if not player and not ctx.author == BOT.mod:
        await ctx.send(f"Sorry, only Goose is allowed to not specify a player, please use the 'member' parameter")
        return

    reply_embed = await ctx.send(embed=info_embed("Please wait for this message to be updated.", "Collecting $$$"))

    dtime_days = (datetime.now() - timedelta(days=days)).replace(tzinfo=timezone.utc)
    
    players_drops = dict() # {K:name, V:{"Total GP":<int> "items":{"item <str>": {"value":<int>,"count":<int>}}, "MVD_item": <str|None>}
    message_cnt = 1
    async for message in BOT.drop_channel.history(after=dtime_days, oldest_first=False, limit=None):
        if message.author.name == BOT.drop_webhook:
            if message.embeds:
                debug_print(f"message {message_cnt}")
                message_cnt += 1
                for embed in message.embeds:
                    info = get_drop_embed_info(embed)
                    if info is None or (player and player != info.player):
                        break
                    
                    debug_print(f"{info.player}, {info.quantity}, {info.item}, {info.value}")
                    
                    player_drops_info = players_drops.get(info.player, None)
                    if player_drops_info is None:
                        players_drops[info.player] = {"Total GP": 0, "items": {}, "MVD_item": None}
                        player_drops_info = players_drops[info.player]

                    player_drops_info["Total GP"] += info.value
                    
                    drops_item = player_drops_info["items"].get(info.item, None)
                    if drops_item is None:
                        drops_item = {"value": info.value, "count": 1}
                        player_drops_info["items"][info.item] = drops_item
                    else:
                        drops_item["value"] += info.value
                        drops_item["count"] += info.quantity

                    mvd_item = player_drops_info["MVD_item"]
                    if (mvd_item is None) or (drops_item["value"] > player_drops_info["items"][mvd_item]["value"]):
                        player_drops_info["MVD_item"] = info.item
    
    drops_embed = make_drops_embed(BOT.drop_webhook, days, players_drops, player)
    await reply_embed.edit(embeds=[drops_embed])

async def days_drops_autocompletion(_, current):
    valid_days_str_list = list(map(str, VALID_DAYS))
    return [
        app_commands.Choice(name=day, value=day)
        for day in valid_days_str_list if current.lower() in day.lower()
    ]

def mvd_percentage(total_gp, mvd_value):
    """MVD value / Total GP"""
    perc = 0
    if total_gp != 0:
        perc = mvd_value / total_gp
    return f"{perc * 100:.2f}%"

def make_drops_embed(drop_wh_name, days, players_drops, player_only=None):
    player_desc = ""
    if player_only:
        player_desc = f"for _{player_only}_"
    
    embed = Embed(
        title=f" {days}-Day \"{drop_wh_name}\" Drop Archive",
        color=Color.blue(),
        description=f"I gathered the drops of The Docks Clan for the past {days} days{player_desc}. Here is what I collected:",
    )

    embed.set_thumbnail(url="https://oldschool.runescape.wiki/images/Coins_10000.png?7fa38")
    embed.set_footer(text="¹MVD Percentage = (MVD Value/Accumulated GP)*100\n"
                            "If you don't see your drops in the table above, then your plugin is all screwed up, and I can't properly parse your drops. "
                            "Please fix your plugin setup ASAP, if you want, or reach out to a fellow clan member to help you out.")
    
    if len(players_drops) == 0:
        embed.add_field(name="", value="**No data found :(**")
    else:
        for player in players_drops:
            drops_info = players_drops[player]
            total_gp = drops_info["Total GP"]
            mvd_item = drops_info["MVD_item"]
            mvd_info = drops_info["items"][mvd_item]
            mvd_value = mvd_info["value"]
            mvd_count = mvd_info["count"]

            embed.add_field(name=player, 
                            value=f"> **Accumulated GP**:                   {format(total_gp, ',')}\n"
                                f"> **Number of Unique Drops**:             {len(drops_info['items'])}\n"
                                f"> **Most Valuable Drop (MVD)**:           {mvd_count}x {mvd_item}\n"
                                f"> **MVD Value**:                          {format(mvd_value, ',')}\n"
                                f"> **MVD Percentage¹**:                    {mvd_percentage(total_gp, mvd_value)}",
                            inline=False)

    return embed
