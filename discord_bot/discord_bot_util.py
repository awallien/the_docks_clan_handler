from discord import Embed, Color, app_commands

ICON_URI_PATH = "https://oldschool.runescape.wiki/images/Clan_icon_-_"
rank_to_icon = {
    '1':"Gnome_Child.png?b0561",    '2':"Kitten.png?9dc78",
    '3':"Adventurer.png?3630c",     '4':"Crew.png?6c963",
    '5':"Adventurer.png?3630c",     '6':"Fire.png?f7cb3",
    '7':"Inquisitor.png?0f3a8",     '8':"Barbarian.png?f92d8",
    '9':"Diamond.png?f7cb3",        '10':"Crusader.png?87d1d",
    '11':"Beast.png?53696",         '12':"Epic.png?f3acc",
    '13':"Raider.png?fff9d",        '14':"Gamer.png?3630c",
    'A':"Administrator.png?9dc78", 
    'D':"Deputy_owner.png?b0561",
    'O':"Owner.png?53696"
}

def get_rank_icon_url(rank):
    if rank not in rank_to_icon:
        raise Exception(f"Rank not found: {rank}")
    return ICON_URI_PATH + rank_to_icon[rank]

def err_embed(msg, title="Error"):
    return Embed(
        title=title,
        description=msg,
        color=Color.dark_red()
    )

def info_embed(msg, title="Info"):
    return Embed(
        title=title,
        description=msg,
        color=Color.blue()
    )

async def set_true_autocompletion(_, current):
    return [
        app_commands.Choice(name=choice, value=choice)
        for choice in ["True"] if current.lower() in choice.lower()
    ]
