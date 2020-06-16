# -*- coding: utf-8 -*-

# Lib
from asyncio import sleep
from os import popen
from copy import deepcopy

# Site
from dbl import DBLException
from discord.embeds import Embed
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command, group, is_owner
from discord.ext.commands.errors import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError
)

# Local
from utils.classes import Bot


class Admin(Cog):
    """Administrative Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.say_dest = None

    @staticmethod
    def color(ctx: Context):
        """Color for embeds"""

        if ctx.guild:
            return ctx.guild.me.color
        else:
            return None

    """ ######################
         Managing Bot Modules
        ###################### """

    @is_owner()
    @group(name="module", aliases=["cog", "mod"], invoke_without_command=True)
    async def module(self, ctx: Context):
        """Base command for managing bot modules

        Use without subcommand to list currently loaded modules"""

        modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
        space = len(max(modules.keys(), key=len))

        fmt = "\n".join([f"{module}{' ' * (space - len(module))} : {cog}" for module, cog in modules.items()])

        em = Embed(
            title="Administration: Currently Loaded Modules",
            description=f"```py\n{fmt}\n```",
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="load", usage="(module name)")
    async def load(self, ctx: Context, module: str):
        """load a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.load_extension(module)

        except ExtensionNotFound:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )

        except ExtensionAlreadyLoaded:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionAlreadyLoaded__**\n"
                            f"Module `{module}` is already loaded",
                color=0xFF0000
            )

        except NoEntryPointError:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xFF0000
                )
            else:
                em = Embed(
                    title="Administration: Load Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xFF0000
                )

        except Exception as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )

        else:
            em = Embed(
                title="Administration: Load Module",
                description=f"Module `{module}` loaded successfully",
                color=0x00FF00
            )

        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="unload", usage="(module name)")
    async def unload(self, ctx: Context, module: str):
        """Unload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.unload_extension(module)

        except ExtensionNotLoaded:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module `{module}` is not loaded",
                color=0xFF0000
            )

        except Exception as error:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )

        else:
            em = Embed(
                title="Administration: Unload Module",
                description=f"Module `{module}` unloaded successfully",
                color=0x00FF00
            )
        
        await ctx.send(embed=em)

    @is_owner()
    @module.command(name="reload", usage="(module name)")
    async def reload(self, ctx: Context, module: str):
        """Reload a module

        If `verbose=True` is included at the end, error tracebacks will
        be sent to the errorlog channel"""

        module = f"cogs.{module}"

        try:
            self.bot.reload_extension(module)

        except ExtensionNotLoaded:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotLoaded__**\n"
                            f"Module `{module}` is not loaded",
                color=0xFF0000
            )

        except ExtensionNotFound:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )

        except NoEntryPointError:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )

        except ExtensionFailed as error:
            if isinstance(error.original, TypeError):
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"The cog loaded by `{module}` must be a subclass of discord.ext.commands.Cog",
                    color=0xFF0000
                )
            else:
                em = Embed(
                    title="Administration: Reload Module Failed",
                    description=f"**__ExtensionFailed__**\n"
                                f"An execution error occurred during module `{module}`'s setup function",
                    color=0xFF0000
                )

        except Exception as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )

        else:
            em = Embed(
                title="Administration: Reload Module",
                description=f"Module `{module}` reloaded successfully",
                color=0x00FF00
            )
    
        await ctx.send(embed=em)

    """ ######################
         General Use Commands
        ###################### """

    # @is_owner()  # TODO: My invite command if you wanted to re-use it
    # @command(name='invite')
    # async def invite(self, ctx: Context):
    #     """Sends an OAuth bot invite URL"""
    #
    #     app_info: AppInfo = await self.bot.application_info()
    #     permissions = Permissions(536881152)
    #
    #     em = Embed(
    #         title=f'OAuth URL for {self.bot.user.name}',
    #         description=f'[Click Here]'
    #                     f'({oauth_url(app_info.id, permissions)}) '
    #                     f'to invite {self.bot.user.name} to your guild.',
    #         color=self.color(ctx)
    #     )
    #     await ctx.send(embed=em)

    # @is_owner()
    # @group(name="say", invoke_without_command=True)
    # async def say(self, ctx: Context, *, msg: str = ""):
    #     """Makes the bot send a message
    #
    #     If self.say_dest is set, it will send the message there
    #     If it is not, it will send to ctx.channel"""
    #
    #     dest: Messageable = self.say_dest if self.say_dest else ctx.channel
    #     await dest.send(msg)
    #
    # @is_owner()
    # @say.command(name="in")
    # async def say_in(self, ctx: Context, dest: str = None):
    #     """Sets the destination for messages from `[p]say`"""
    #
    #     if dest:
    #         try:
    #             self.say_dest: TextChannel = await GlobalTextChannelConverter().convert(ctx, dest)
    #         except BadArgument as error:
    #             em = Embed(
    #                 title="Invalid Channel Identifier",
    #                 description=f"**__{type(error).__name__}__**: {str(error)}",
    #                 color=0xFF0000
    #             )
    #             await ctx.send(embed=em)
    #         else:
    #             em = Embed(
    #                 title="Administration: Set `say` Destination",
    #                 description=f"__Say destination set__\n"
    #                             f"Guild: {self.say_dest.guild.name}\n"
    #                             f"Channel: {self.say_dest.mention}\n"
    #                             f"ID: {self.say_dest.id}",
    #                 color=0x00FF00
    #             )
    #             await ctx.send(embed=em)
    #     else:
    #         self.say_dest = None
    #         em = Embed(
    #             title="Administration: Set `say` Destination",
    #             description=f"Say destination has been unset",
    #             color=0x00FF00
    #         )
    #         await ctx.send(embed=em)

    """ #########################
         Updating and Restarting
        ######################### """

    @staticmethod
    def gitpull() -> str:
        """Uses os.popen to `git pull`"""
        resp = popen("git pull").read()
        resp = f"```diff\n{resp}\n```"
        return resp

    @is_owner()
    @command(name="pull")
    async def pull(self, ctx: Context):
        """Updates bot repo from master"""

        em = Embed(
            title="Administration: Git Pull",
            description=self.gitpull(),
            color=0x00FF00
        )
        await ctx.send(embed=em)

    @is_owner()
    @group(name='restart', aliases=["kill", "f", "logout"], invoke_without_command=True)
    async def _restart(self, ctx: Context):
        """Restarts the bot"""

        # if not exists(join(self.bot.cwd, "Serialized", "data.pkl")):
        #     await ctx.send("[Unable to save] data.pkl not found. Replace file before shutting down.")
        #     print("[Unable to save] data.pkl not found. Replace file before shutting down.")
        #     return

        # print("Saving files and awaiting logout...")
        # with open(join(self.bot.cwd, "Serialized", "data.pkl"), "wb") as f:
        #     try:
        #         data = {
        #             "VanityAvatars": self.bot.VanityAvatars,
        #             "Blacklists": self.bot.Blacklists,
        #             "Closets": self.bot.Closets,
        #             "ServerBlacklists": self.bot.ServerBlacklists
        #         }
        #
        #         dump(data, f)
        #     except Exception as e:
        #         await ctx.send(f"[Unable to save; Data Reset] Pickle dumping Error: {e}")

        em = Embed(
            title="Administration: Restart",
            description=f"{ctx.author.mention} initiated bot restart.",
            color=0x00FF00
        )

        await ctx.send(embed=em)
        await self.bot.logout()

    """ ######################
         User Data Management
        ###################### """
    
    @command(aliases=["rs_av"])
    @is_owner()
    async def resetallavatars(self, ctx: Context):
        if ctx.guild:
            return await ctx.message.delete()

        self.bot.user_data["VanityAvatars"] = {
            "guildID": {
                "userID": [
                    "avatar_url",
                    "previous",
                    "is_blocked"
                ]
            }
        }
        await ctx.author.send("Reset all avatars.")
        print("[] Deleted all avatars on owner's request.")

    @command(aliases=["rs_bl"])
    @is_owner()
    async def resetallblacklists(self, ctx: Context):
        if ctx.guild:
            return await ctx.message.delete()

        self.bot.user_data["Blacklists"] = {
            "authorID": (
                ["channelID"],
                ["prefix"]
            )
        }
        await ctx.author.send("Reset all blacklists.")
        print("[] Deleted all blacklists on owner's request.")
    
    @command(aliases=["rs_sbl"])
    @is_owner()
    async def resetallserverblacklists(self, ctx: Context):
        if ctx.guild:
            return await ctx.message.delete()
        
        self.bot.user_data["ServerBlacklists"] = {
            "guildID": (
                ["channelID"],
                ["prefix"])
        }
        await ctx.author.send("Reset all server blacklists.")
        print("[] Deleted all server-blacklists on owner's request.")
        
    @command(aliases=["rs_cl"])
    @is_owner()
    async def resetallclosets(self, ctx: Context):
        if ctx.guild:
            return await ctx.message.delete()
        
        self.bot.user_data["Closets"] = {
            "auhthorID":
                {"closet_name": "closet_url"}
        }
        await ctx.author.send("Reset all closets.")
        print("[] Deleted all closets on owner's request.")

    """ ####################
         Bot Configurations
        #################### """

    @is_owner()
    @group(name="config", aliases=["bot", "settings"], invoke_without_command=True)
    async def config(self, ctx: Context):
        """View Bot settings"""
        em = Embed(
            title="Administration: Config",
            description=f"The options and values are listed below:\n"
                        f"```debug_mode: {self.bot.debug_mode}\n"
                        f"auto_pull: {self.bot.auto_pull}\n"
                        f"tz: {self.bot.tz}\n"
                        f"prefix: {self.bot.command_prefix}```",
            color=0x0000FF
        )
        return await ctx.send(embed=em)

    @is_owner()
    @config.command(name="prefix", aliases=["command_prefix"])
    async def prefix(self, ctx: Context, *, val: str = None):
        """View or set bot prefix"""

        if val:
            orig = deepcopy(self.bot.command_prefix)
            self.bot.command_prefix = val

            em = Embed(
                title="Administration: Bot Prefix Config",
                description=f"New prefix: `{val}`\n"
                            f"Original prefix: `{orig}`",
                color=0x00FF00
            )

        else:
            em = Embed(
                title="Administration: Bot Prefix Config",
                description=f"Bot prefix: `{self.bot.command_prefix}`",
                color=0x0000FF
            )

        return await ctx.send(embed=em)

    @is_owner()
    @config.command(name="tz", aliases=["timezone"])
    async def tz(self, ctx: Context, *, val: str = None):
        """View or set bot time zone"""

        if val:
            if val in ["EST", "CST", "UTC"]:
                orig = deepcopy(self.bot.tz)
                self.bot.tz = val

                em = Embed(
                    title="Administration: Bot Timezone Config",
                    description=f"New timezone: `{val}`\n"
                                f"Original timezone: `{orig}`",
                    color=0x00FF00
                )

            else:
                em = Embed(
                    title="Administration: Bot Timezone Config",
                    description=f"Invalid timezone given: `{val}`\n"
                                f"Valid values: `EST` `CST` `UTC`",
                    color=0xFF0000
                )

        else:
            em = Embed(
                title="Administration: Bot Timezone Config",
                description=f"Bot timezone: `{self.bot.tz}`",
                color=0x00FF00
            )

        return await ctx.send(embed=em)

    @is_owner()
    @config.command(name="debug", aliases=["debug_mode"])
    async def debug(self, ctx: Context, *, val: str = None):
        """View or set bot prefix"""

        if val:
            if val.lower() in ["true", "false"]:
                val = True if val == "true" else False
                orig = deepcopy(self.bot.debug_mode)
                self.bot.debug_mode = val

                em = Embed(
                    title="Administration: Bot Debug Mode Config",
                    description=f"New value: `{val}`\n"
                                f"Original value: `{orig}`",
                    color=0x00FF00
                )

            else:
                em = Embed(
                    title="Administration: Bot Debug Mode Config",
                    description=f"Invalid value given: `{val}`\n"
                                f"Valid values: `True` `False`",
                    color=0xFF0000
                )

        else:
            em = Embed(
                title="Administration: Bot Debug Mode Config",
                description=f"Debug Mode: `{self.bot.debug_mode}`",
                color=0x0000FF
            )

        return await ctx.send(embed=em)

    @is_owner()
    @config.command(name="autopull", aliases=["auto_pull"])
    async def autopull(self, ctx: Context, *, val: str = None):
        """View or set bot prefix"""

        if val:
            if val.lower() in ["true", "false"]:
                val = True if val == "true" else False
                orig = deepcopy(self.bot.auto_pull)
                self.bot.auto_pull = val

                em = Embed(
                    title="Administration: Bot Auto-Pull Config",
                    description=f"New value: `{val}`\n"
                                f"Original value: `{orig}`",
                    color=0x00FF00
                )

            else:
                em = Embed(
                    title="Administration: Bot Auto-Pull Config",
                    description=f"Invalid value given: `{val}`\n"
                                f"Valid values: `True` `False`",
                    color=0xFF0000
                )

        else:
            em = Embed(
                title="Administration: Auto-Pull Config",
                description=f"Auto-Git Pull Mode: `{self.bot.debug_mode}`",
                color=0x0000FF
            )

        return await ctx.send(embed=em)

    """ ##################
         Discord Bot List
        ################## """

    @is_owner()
    @group(name="dbl", invoke_without_command=True)
    async def dbl(self, ctx: Context):
        """See current DBL connection status"""

        if self.bot.dbl:
            dbl_guilds = await self.bot.dbl.get_guild_count(self.bot.user.id)
            dbl_guilds_count = dbl_guilds["server_count"]
            bot_url = self.bot.dbl_page
            em = Embed(
                title="Administration: DBL Status",
                description=f"DiscordBotList Client is currently connected.\n"
                            f"Guilds: `{dbl_guilds_count}`\n"
                            f"Bot Page: {bot_url}\n"
                            f"Bot Vote Page: {bot_url}/vote",
                color=0x0000FF
            )

        else:
            em = Embed(
                title="Administration: DBL Status",
                description="DiscordBotList Client is not connected.",
                color=0xFF0000
            )

        return await ctx.send(embed=em)

    @is_owner()
    @dbl.command(name="connect", aliases=["reconnect"])
    async def connect(self, ctx: Context):
        """Connects (or reconnects) DBL"""

        if self.bot.dbl:
            try:
                await self.bot.dbl.close()
                self.bot.dbl = None
                await sleep(3)

            except DBLException as error:
                em = Embed(
                    title="Administration: Connect DBL",
                    description=f"An error prevented disconnecting from DBL\n"
                                f"**__{error.__class__.__name__}:__** "
                                f"{error[:1000]}",
                    color=0xFF0000
                )
                return await ctx.send(embed=em)

        await self.bot.connect_dbl(autopost=True)

        if self.bot.dbl:
            em = Embed(
                title="Administration: Connect DBL",
                description="DiscordBotList reconnection successful",
                color=0x00FF00
            )

        else:
            em = Embed(
                title="Administration: Connect DBL",
                description="DiscordBotList reconnection failed",
                color=0xFF0000
            )

        return await ctx.send(embed=em)


def setup(bot: Bot):
    """Admin"""
    bot.add_cog(Admin(bot))
