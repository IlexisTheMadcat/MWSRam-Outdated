# Migration

# Lib
from dbl import DBLClient

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command, bot_has_permissions
from discord.user import User

# Local
from utils.classes import Bot


class ClosetCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dblpy = self.bot.connect_dbl(autopost=True)

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["cl_add"])
    @bot_has_permissions(send_messages=True)
    async def add_to_closet(self, ctx: Context, name: str):
        if ctx.author.id != self.bot.owner.id:
            check = await self.dblpy.get_user_vote(ctx.author.id)
        else:
            check = True
    
        if not check:
            await ctx.send(
                "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote "
                "and click on 'Vote'.\nThen come back and try again.\nIf you just now voted, wait a few moments."
            )
            return

        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. Consider using it in a private channel "
                "in one of your servers."
            )
            return

        if ctx.message.attachments == list():
            await ctx.send("You don't have a vanity equiped.")
            return

        else:
            try:
                if ctx.author.id not in self.bot.univ.Closets.keys():
                    self.bot.univ.Closets[ctx.author.id] = {}

                if name in self.bot.univ.Closets[ctx.author.id].keys():
                    await ctx.send(
                        f"A closet entry with that name already exists. Refer to `{self.bot.command_prefix}see_closet`."
                    )
                    return

                if len(self.bot.univ.Closets[ctx.author.id].keys()) >= 10:
                    await ctx.send(
                        "You've reached your max number of avatars in your closet. Consider removing one of them."
                    )
                    return

                if len(name) > 20:
                    await ctx.send("Your name can't be longer than 20 characters.")
                    return

                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                    await ctx.send(f"Added attached file to your closet with name `{name}`.")

                elif self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0] is not None:
                    url = self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0]
                    await ctx.send(f"Added current vanity avatar to closet with name `{name}`.")

                else:
                    await ctx.send("You don't have an avatar equipped.")
                    return

                self.bot.univ.Closets[ctx.author.id].update({name: url})
            except KeyError or IndexError:
                self.bot.univ.Closets[ctx.author.id] = {}
                try:
                    self.bot.univ.Closets[ctx.author.id].update(
                        {name: self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0]}
                    )
                except IndexError or KeyError:
                    await ctx.send("You don't have a vanity equipped.")
                await ctx.send(f"Added with closet entry \"{name}\".")
        
    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["cl_remove"])
    @bot_has_permissions(send_messages=True)
    async def remove_from_closet(self, ctx: Context, name: str):
        if ctx.author.id != self.bot.owner.id:
            check = await self.dblpy.get_user_vote(ctx.author.id)
        else:
            check = True

        if not check:
            await ctx.send(
                "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\nIf you just now voted, wait a few moments."
            )
            return
        
        if ctx.author.id not in self.bot.univ.Closets.keys():
            self.bot.univ.Closets[ctx.author.id] = {}

        try:
            if name not in self.bot.univ.Closets[ctx.author.id].keys():
                await ctx.send(
                    f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )
                return
            else:
                self.bot.univ.Closets[ctx.author.id].pop(name)
        except KeyError or IndexError:
            self.bot.univ.Closets[ctx.author.id] = dict()
            await ctx.send(
                f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )
        else:
            await ctx.send(f"Removed closet entry \"{name}\".")

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["cl_rename"])
    @bot_has_permissions(send_messages=True)
    async def rename_closet_entry(self, ctx: Context, name: str, rename: str):
        if ctx.author.id != self.bot.owner.id:
            check = await self.dblpy.get_user_vote(ctx.author.id)
        else:
            check = True
    
        if not check:
            await ctx.send(
                "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\nIf you just now voted, wait a few moments."
            )
            return
        
        if ctx.author.id not in self.bot.univ.Closets.keys():
            self.bot.univ.Closets[ctx.author.id] = dict()
            
        try:
            if len(rename) > 20:
                await ctx.send("Your name can't be longer than 20 characters.")
                return

            elif name not in self.bot.univ.Closets[ctx.author.id].keys():
                await ctx.send(
                    f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )
                return

            elif rename in self.bot.univ.Closets[ctx.author.id].keys():
                await ctx.send(
                    f"A closet entry with that name already exists. See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )
                return

            else:
                orig_url = self.bot.univ.Closets[ctx.author.id].pop(name)
                self.bot.univ.Closets[ctx.author.id].update({rename: orig_url})

        except KeyError:
            self.bot.univ.Closets[ctx.author.id] = dict()
            await ctx.send(
                f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )
        else:
            await ctx.send(f"Renamed closet entry \"{name}\" to \"{rename}\".")

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["cl"])
    @bot_has_permissions(send_messages=True)
    async def see_closet(self, ctx: Context, name: User = None):  # TODO: Use :class: discord.Member instead?
        """"""

        if not name:
            name = ctx.author
            if name.id not in self.bot.univ.Closets.keys():
                self.bot.univ.Closets[name.id] = {}
    
            if ctx.author.id != self.bot.owner.id:
                check = await self.dblpy.get_user_vote(ctx.author.id)
            else:
                check = True
                
            if not check:
                await ctx.send(
                    "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote and "
                    "click on 'Vote'.\nThen come back and try again.\nIf you just now voted, wait a few moments."
                )
                return

            message_part = list()
            try:
                message_part.append(
                    f"Here is your closet. You can use these anywhere. Used "
                    f"{len(self.bot.univ.Closets[name.id].keys())}/10 slots.```\n"
                )
                if self.bot.univ.Closets[name.id] != {}:
                    for i in self.bot.univ.Closets[name.id].keys():
                        message_part.append(f"▛▚ Name: {i}\n▙▞ URL: ({self.bot.univ.Closets[name.id][i]})\n\n")
                else:
                    raise KeyError
                
            except KeyError:
                await ctx.send("You have nothing in your closet.")
                return
        else:
            if name.id not in self.bot.univ.Closets.keys():
                self.bot.univ.Closets[name.id] = dict()
    
            check = await self.dblpy.get_user_vote(name.id)
            if not check:
                await ctx.send(
                    f"Closets are vote-locked. Tell {name.name} to go to "
                    f"https://discordbots.org/bot/687427956364279873/vote and click on 'Vote'.\n"
                    f"Then come back and try again.\nIf you just now voted, wait a few moments."
                )
                return
        
            message_part = list()
            try:
                message_part.append(
                    f"Here is their closet. Used {len(self.bot.univ.Closets[name.id].keys())}/10 slots.```\n"
                )
                if self.bot.univ.Closets[name.id] != dict():
                    for i in self.bot.univ.Closets[name.id].keys():
                        message_part.append(f"▛▚ Name: {i}\n▙▞ URL: ({self.bot.univ.Closets[name.id][i]})\n\n")
                else:
                    raise KeyError
            except KeyError:
                await ctx.send("They have nothing in their closet.")
                return

        message_part.append("```")
        message = ''.join(message_part)

        await ctx.send(message)

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["cl_preview"])
    @bot_has_permissions(send_messages=True, manage_webhooks=True)
    async def preview_closet_entry(self, ctx, name):
        """"""

        if ctx.author.id != self.bot.owner.id:
            check = await self.dblpy.get_user_vote(ctx.author.id)
        else:
            check = True

        if not check:
            await ctx.send(
                "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\nIf you just now voted, wait a few moments."
            )
            return
        
        msg = ctx.message
        if ctx.author.id not in self.bot.univ.Closets.keys():
            self.bot.univ.Closets[ctx.author.id] = dict()

        try:
            if name in self.bot.univ.Closets[ctx.author.id].keys():
                dummy = await msg.channel.create_webhook(name=msg.author.display_name)
                await dummy.send(
                    f"{self.bot.user.name}: Preview message.\n{self.bot.univ.Closets[ctx.author.id][name]}",
                    avatar_url=self.bot.univ.Closets[ctx.author.id][name]
                )
                await dummy.delete()
                return
            else:
                await ctx.send(
                    f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )
        except KeyError or IndexError:
            await ctx.send(
                f"A closet entry with that name doesn't exist. See your closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )
            return


def setup(bot: Bot):
    bot.add_cog(ClosetCommands(bot))

def teardown(bot: Bot):
    bot.remove_cog(ClosetCommands(bot))