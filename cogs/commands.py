
# Lib

# Site
from discord import Embed, User
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command

# Local


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=["avatar"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def current(self, ctx: Context, user: User):

        author = ctx.author

        print(
            f'[] Sent standard avatar url for \"{user}\"'
            f' to user \"{author}\".'
        )

        return await ctx.send(embed=Embed(
            title=f"{user}'s Avatar",
            color=0x32d17f
        ).set_image(url=user.avatar_url))


def setup(bot):
    bot.add_cog(Commands(bot))
