
# This is my owner commands, add yours somewhere within this class

# Lib
from os.path import exists
from pickle import dump

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command, is_owner

# Local
from utils.classes import Bot


class OwnerCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["rs_av"])
    @is_owner()
    async def resetallavatars(self, ctx: Context):
        if ctx.guild:
            await ctx.message.delete()
            return

        self.bot.univ.VanityAvatars = {"guildID": {"userID": ["avatar_url", "previous", "is_blocked"]}}
        await ctx.author.send("Reset all avatars.")
        print("[] Deleted all avatars on owner's request.")

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["rs_bl"])
    @is_owner()
    async def resetallblacklists(self, ctx: Context):
        if ctx.guild:
            await ctx.message.delete()
            return

        self.bot.univ.Blacklists = {"authorID": (["channelID"], ["prefix"])}
        await ctx.author.send("Reset all blacklists.")
        print("[] Deleted all blacklists on owner's request.")

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["rs_sbl"])
    @is_owner()
    async def resetallserverblacklists(self, ctx: Context):
        if ctx.guild:
            await ctx.message.delete()
            return
        
        self.bot.univ.ServerBlacklists = {"guildID": (["channelID"], ["prefix"])}
        await ctx.author.send("Reset all server blacklists.")
        print("[] Deleted all server-blacklists on owner's request.")
        
    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["rs_cl"])
    @is_owner()
    async def resetallclosets(self, ctx: Context):
        if ctx.guild:
            await ctx.message.delete()
            return
        
        self.bot.univ.Closets = {"auhthorID": {"closet_name": "closet_url"}}
        await ctx.author.send("Reset all closets.")
        print("[] Deleted all closets on owner's request.")

    # ------------------------------------------------------------------------------------------------------------------
    @command(name="logout")
    @is_owner()
    async def blogout(self, ctx: Context):
        await ctx.send("Logging out...")
        if not exists(f"{self.bot.cwd}\\Serialized\\data.pkl"):
            await ctx.send("[Unable to save] data.pkl not found. Replace file before shutting down.")
            print("[Unable to save] data.pkl not found. Replace file before shutting down.")
            return

        print("Saving files and awaiting logout...")
        with open(f"{self.bot.cwd}\\Serialized\\data.pkl", "wb") as f:
            try:
                data = {
                    "VanityAvatars": self.bot.univ.VanityAvatars,
                    "Blacklists": self.bot.univ.Blacklists,
                    "Closets": self.bot.univ.Closets,
                    "ServerBlacklists": self.bot.univ.ServerBlacklists,
                    "ChangelogCache": self.bot.univ.ChangelogCache
                }

                dump(data, f)
            except Exception as e:
                await ctx.send(f"[Unable to save; Data Reset] Pickle dumping Error: {e}")

        await self.bot.logout()


def setup(bot: Bot):
    bot.add_cog(OwnerCommands(bot))
