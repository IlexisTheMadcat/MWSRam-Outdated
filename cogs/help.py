
# Lib

# Site
from discord import Embed, AppInfo, Permissions
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command
from discord.utils import oauth_url

# Local


class MiscCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def invite(self, ctx: Context):
        """Sends an OAuth bot invite URL"""

        app_info: AppInfo = await self.bot.application_info()
        permissions = Permissions()
        permissions.update(
            administrator=True
        )

        em = Embed(
            title=f'OAuth URL for {self.bot.user.name}',
            description=f'[Click Here]'
                        f'({oauth_url(app_info.id, permissions)}) '
                        f'to invite me to your server.',
            color=0x32d17f
        )
        await ctx.send(embed=em)

    @command(name="help")
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def bhelp(self, ctx: Context, section: str = "directory", subsection: str = None):
        em = Embed(title="Hi, I'm Kyaru!", color=0x32d17f)
        if section == "directory":
            em.description = "I'm the mascot catgirl for [Catgirl Heaven](https://discord.gg/SFCCetG), " \
                             "where we hospitalize other catgirls and protect them from the rest of the internet's failed experiments.\n" \
                             "I make sure things stay tidy and keep the server maintained.\n" \
                             "\n" \
                             "I don't really do anything useful to the public, but you might be able to play with me somehow.\n" \
                             "*Not like that, pervert!*" 
        else:
            pass

        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(MiscCommands(bot))
