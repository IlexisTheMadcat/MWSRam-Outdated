# -*- coding: utf-8 -*-

# Lib

# Site
from discord.abc import Messageable
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import group, is_owner
from discord.ext.commands.errors import (
    BadArgument,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError
)
# from discord.permissions import Permissions
# from discord.utils import oauth_url

# Local
from utils.classes import Bot


class Admin(Cog):
    """Administrative Commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

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
            await ctx.send(embed=em, delete_after=5)

        except ExtensionAlreadyLoaded:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__ExtensionAlreadyLoaded__**\n"
                            f"Module `{module}` is already loaded",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

        except NoEntryPointError:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

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
            await ctx.send(embed=em, delete_after=5)

        except Exception as error:
            em = Embed(
                title="Administration: Load Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            em = Embed(
                title="Administration: Load Module",
                description=f"Module `{module}` loaded successfully",
                color=0x00FF00
            )
            await ctx.send(embed=em, delete_after=5)

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
            await ctx.send(embed=em, delete_after=5)

        except Exception as error:
            em = Embed(
                title="Administration: Unload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            em = Embed(
                title="Administration: Unload Module",
                description=f"Module `{module}` unloaded successfully",
                color=0x00FF00
            )
            await ctx.send(embed=em, delete_after=5)

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
            await ctx.send(embed=em, delete_after=5)

        except ExtensionNotFound:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__ExtensionNotFound__**\n"
                            f"No module `{module}` found in cogs directory",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

        except NoEntryPointError:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__NoEntryPointError__**\n"
                            f"Module `{module}` does not define a `setup` function",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

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
            await ctx.send(embed=em, delete_after=5)

        except Exception as error:
            em = Embed(
                title="Administration: Reload Module Failed",
                description=f"**__{type(error).__name__}__**\n"
                            f"```py\n"
                            f"{error}\n"
                            f"```",
                color=0xFF0000
            )
            await ctx.send(embed=em, delete_after=5)

        else:
            em = Embed(
                title="Administration: Reload Module",
                description=f"Module `{module}` reloaded successfully",
                color=0x00FF00
            )
            await ctx.send(embed=em, delete_after=5)

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



    """ ######################
         General Use Commands
        ###################### """

    @is_owner()
    @group(name="say", invoke_without_command=True)
    async def say(self, ctx: Context, *, msg: str = ""):
        """Makes the bot send a message

        If self.say_dest is set, it will send the message there
        If it is not, it will send to ctx.channel"""

        dest: Messageable = self.say_dest if self.say_dest else ctx.channel
        await dest.send(msg)

    @is_owner()
    @say.command(name="in")
    async def say_in(self, ctx: Context, dest: str = None):
        """Sets the destination for messages from `[p]say`"""

        if dest:
            try:
                self.say_dest: TextChannel = await GlobalTextChannelConverter().convert(ctx, dest)
            except BadArgument as error:
                em = Embed(
                    title="Invalid Channel Identifier",
                    description=f"**__{type(error).__name__}__**: {str(error)}",
                    color=0xFF0000
                )
                await ctx.send(embed=em, delete_after=5)
            else:
                em = Embed(
                    title="Administration: Set `say` Destination",
                    description=f"__Say destination set__\n"
                                f"Guild: {self.say_dest.guild.name}\n"
                                f"Channel: {self.say_dest.mention}\n"
                                f"ID: {self.say_dest.id}",
                    color=0x00FF00
                )
                await ctx.send(embed=em, delete_after=5)
        else:
            self.say_dest = None
            em = Embed(
                title="Administration: Set `say` Destination",
                description=f"Say destination has been unset",
                color=0x00FF00
            )
            await ctx.send(embed=em, delete_after=5)

    @is_owner()
    @group(name='restart', aliases=["kill", "f"], invoke_without_command=True)
    async def _restart(self, ctx: Context):
        """Restarts the bot"""

        em = Embed(
            title="Administration: Restart",
            description=f"{ctx.author.mention} initiated bot restart.",
            color=0x00FF00
        )

        await ctx.send(embed=em, delete_after=5)
        await self.bot.logout()


def setup(bot: Bot):
    """Admin"""
    bot.add_cog(Admin(bot))
