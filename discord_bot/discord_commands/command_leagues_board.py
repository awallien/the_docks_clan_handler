from clan_db import ClanDatabase
from discord_bot import err_embed, info_embed
from discord import Embed, Color, ButtonStyle, ui as dui
from pprint import pprint

class LeaguesBoardPagination(dui.View):
    current_page = 1
    sep = 10
    
    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data[:self.sep])
    
    def create_embed(self, data):
        embed = Embed(
            color = Color.blurple(),
            title = "The Docks Clan League V Board",
            description="I gathered all the current clan members' League V points. If you don't see your name in this list, please reach out to Goose.\n"
                        "NOTE: This is experimental, and currently there's a bug where going to a page would not work due to 401 Error. Goose will try to periodically update this board."
        )
        embed.set_thumbnail(url="https://oldschool.runescape.wiki/images/Raging_Echoes_League_combat_masteries_icon.png?4e2c2")
        embed.set_footer(text=f"Page {self.current_page}/{(len(self.data) // self.sep)+ 1}")
        for item in data:
            embed.add_field(name=item[0], value=item[1], inline=False)
        
        return embed

    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = ButtonStyle.gray
            self.prev_button.style = ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = ButtonStyle.green
            self.prev_button.style = ButtonStyle.primary
        
        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = ButtonStyle.gray
            self.next_button.style = ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = ButtonStyle.green
            self.next_button.style = ButtonStyle.primary

    def get_current_page_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(self.data) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        
        return self.data[from_item:until_item]

    @dui.button(label="|<",
                style=ButtonStyle.green)
    async def first_page_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page = 1

        await self.update_message(self.get_current_page_data())
    
    @dui.button(label="<",
                style=ButtonStyle.primary)
    async def prev_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message(self.get_current_page_data())
    
    @dui.button(label=">",
                style=ButtonStyle.primary)
    async def next_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message(self.get_current_page_data())
    
    @dui.button(label=">|",
                style= ButtonStyle.green)
    async def last_page_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1
        await self.update_message(self.get_current_page_data())

async def leagues_board_cb(BOT, ctx):
    BOT.db.internal_update()
    members = BOT.db.get_members()
    # members = ["metaGoose", "E1 KUL", "Sol_TheGuy"]
    print(members)
    mem_lps = []
    for member in members:
        member_df = BOT.db.get_player_data(member)
        if not member_df:
            print(f"No data found for {member}? skip for now")
        league_pts = int(member_df[ClanDatabase.LEAGUE_POINTS])
        if league_pts > 0:
            print(f"{member} {league_pts}")
            mem_lps.append((member, league_pts))
    
    mem_lps.sort(key=lambda x: x[1], reverse=True)

    page = 1
    int_rank = 0
    embeds = []
    for page_idx in range(0, len(mem_lps), 10):
        lps_pag_data = mem_lps[page_idx:page_idx+10]
        if page == 1:
            embed = Embed(
                color = Color.blurple(),
                title = "The Docks Clan League V Board",
                description="I gathered all the current clan members' League V points. If you don't see your name in this list, please reach out to Goose.\n"
            )
        else:
            embed = Embed(color = Color.blurple())
        embed.set_thumbnail(url="https://oldschool.runescape.wiki/images/Raging_Echoes_League_combat_masteries_icon.png?4e2c2")
        embed.set_footer(text=f"Page {page}/{len(mem_lps) // 10 + 1}")
        for rank, lps_data in enumerate(lps_pag_data):
            embed.add_field(name=f"{int_rank + rank + 1}. {lps_data[0]}", value=lps_data[1], inline=False)
        
        embeds.append(embed)
        int_rank += 10
        page += 1
    
    
    await ctx.send(embeds=embeds)


    # league_pag = LeaguesBoardPagination(timeout=None)
    # league_pag.data = mem_lps
    # await league_pag.send(ctx)
    