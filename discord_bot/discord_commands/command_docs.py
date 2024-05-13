from discord import utils as dutils
from discord_bot.discord_bot_util import err_embed, info_embed
from util import err_print

DOCS = [
    "\"The Docks\" Ranking System and Permission Settings",
    "How to Set Up Drop Notifications",
    "The Docks Clan Bot Help Desk"
]

async def cb_docs(BOT, ctx):
    docs_msg = ""
    
    for doc in DOCS:
        try:
            thr = dutils.get(BOT.forum_channel.threads, name=doc)
            docs_msg += f"**{doc}**: {thr.mention}\n"
        except:
            err_print(f"{doc} does not exist")
    
    if not docs_msg:
        docs_msg = "Hmmm... there seems to be no docs here..."
        embed = err_embed(docs_msg, "Interesting...")
    else:
        docs_msg = "Here is a list of relevant documents/threads: \n" + docs_msg
        embed = info_embed(docs_msg, "Dock's Docs")
    
    await ctx.send(embed=embed, ephemeral=True)