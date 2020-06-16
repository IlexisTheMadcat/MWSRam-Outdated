
# Lib

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

    @command(aliases=["cl_add"])
    @bot_has_permissions(send_messages=True)
    async def add_to_closet(self, ctx: Context, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)
    
        if not check:
            return await ctx.send(
                "Closets are vote-locked. Please go to "
                "https://discordbots.org/bot/687427956364279873/vote "
                "and click on 'Vote'.\nThen come back and try again.\n"
                "If you just now voted, wait a few moments."
            )

        if not ctx.guild:
            return await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel "
                "in one of your servers."
            )

        if ctx.message.attachments == list():
            return await ctx.send("You don't have a vanity equiped.")

        else:
            try:
                if ctx.author.id not in self.bot.user_data["Closets"].keys():
                    self.bot.user_data["Closets"][ctx.author.id] = {}

                if name in self.bot.user_data["Closets"][ctx.author.id].keys():
                    return await ctx.send(
                        f"A closet entry with that name already exists. "
                        f"Refer to `{self.bot.command_prefix}see_closet`."
                    )

                if len(self.bot.user_data["Closets"][ctx.author.id].keys()) >= 10:
                    return await ctx.send(
                        "You've reached your max number of avatars in your "
                        "closet. Consider removing one of them."
                    )

                if len(name) > 20:
                    await ctx.send("Your name can't be longer than 20 characters.")
                    return

                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                    await ctx.send(
                        f"Added attached file to your closet with name `{name}`."
                    )

                elif self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0] is not None:
                    url = self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0]
                    await ctx.send(f"Added current vanity avatar to closet with name `{name}`.")

                else:
                    return await ctx.send("You don't have an avatar equipped.")

                self.bot.user_data["Closets"][ctx.author.id].update({name: url})
            except KeyError or IndexError:
                self.bot.user_data["Closets"][ctx.author.id] = {}
                try:
                    self.bot.user_data["Closets"][ctx.author.id].update(
                        {name: self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0]}
                    )
                except IndexError or KeyError:
                    await ctx.send("You don't have a vanity equipped.")
                await ctx.send(f"Added with closet entry \"{name}\".")

    @command(aliases=["cl_remove"])
    @bot_has_permissions(send_messages=True)
    async def remove_from_closet(self, ctx: Context, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(
                "Closets are vote-locked. Please go to "
                "https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\n"
                "If you just now voted, wait a few moments."
            )
        
        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = {}

        try:
            if name not in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(
                    f"A closet entry with that name doesn't exist. See your "
                    f"closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )

            else:
                self.bot.user_data["Closets"][ctx.author.id].pop(name)

        except KeyError or IndexError:
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            await ctx.send(
                f"A closet entry with that name doesn't exist. See your "
                f"closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )
        else:
            await ctx.send(f"Removed closet entry \"{name}\".")

    @command(aliases=["cl_rename"])
    @bot_has_permissions(send_messages=True)
    async def rename_closet_entry(self, ctx: Context, name: str, rename: str):
        check = await self.bot.get_user_vote(ctx.author.id)
    
        if not check:
            return await ctx.send(
                "Closets are vote-locked. Please go to "
                "https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\n"
                "If you just now voted, wait a few moments."
            )
        
        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            
        try:
            if len(rename) > 20:
                return await ctx.send("Your name can't be longer than 20 characters.")

            elif name not in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(
                    f"A closet entry with that name doesn't exist. "
                    f"See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )

            elif rename in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(
                    f"A closet entry with that name already exists. "
                    f"See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )

            else:
                orig_url = self.bot.user_data["Closets"][ctx.author.id].pop(name)
                self.bot.user_data["Closets"][ctx.author.id].update({rename: orig_url})

        except KeyError:
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            await ctx.send(
                f"A closet entry with that name doesn't exist. "
                f"See your closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )
        else:
            await ctx.send(f"Renamed closet entry \"{name}\" to \"{rename}\".")

    @command(aliases=["cl"])
    @bot_has_permissions(send_messages=True)
    async def see_closet(self, ctx: Context, name: User = None):
        """"""

        if not name:
            name = ctx.author
            if name.id not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][name.id] = {}

            check = await self.bot.get_user_vote(ctx.author.id)
                
            if not check:
                return await ctx.send(
                    "Closets are vote-locked. Please go to "
                    "https://discordbots.org/bot/687427956364279873/vote and "
                    "click on 'Vote'.\nThen come back and try again.\n"
                    "If you just now voted, wait a few moments."
                )

            message_part = list()
            try:
                message_part.append(
                    f"Here is your closet. You can use these anywhere. Used "
                    f"{len(self.bot.user_data['Closets'][name.id].keys())}"
                    f"/10 slots.```\n"
                )
                if self.bot.user_data["Closets"][name.id] != dict():
                    for i in self.bot.user_data["Closets"][name.id].keys():
                        message_part.append(
                            f"▛▚ Name: {i}\n▙▞ URL: ("
                            f"{self.bot.user_data['Closets'][name.id][i]})\n\n"
                        )
                else:
                    raise KeyError
                
            except KeyError:
                return await ctx.send("You have nothing in your closet.")

        else:
            if name.id not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][name.id] = dict()
    
            check = await self.bot.get_user_vote(name.id)

            if not check:
                return await ctx.send(
                    f"Closets are vote-locked. Tell {name.name} to go to "
                    f"https://discordbots.org/bot/687427956364279873/vote "
                    f"and click on 'Vote'.\nThen come back and try again.\n"
                    f"If you just now voted, wait a few moments."
                )
        
            message_part = list()
            try:
                message_part.append(
                    f"Here is their closet. Used "
                    f"{len(self.bot.user_data['Closets'][name.id].keys())}"
                    f"/10 slots.```\n"
                )
                if self.bot.user_data["Closets"][name.id] != dict():
                    for i in self.bot.user_data["Closets"][name.id].keys():
                        message_part.append(
                            f"▛▚ Name: {i}\n▙▞ URL: ("
                            f"{self.bot.user_data['Closets'][name.id][i]})\n\n"
                        )

                else:
                    raise KeyError

            except KeyError:
                await ctx.send("They have nothing in their closet.")
                return

        message_part.append("```")
        message = ''.join(message_part)

        await ctx.send(message)

    @command(aliases=["cl_preview"])
    @bot_has_permissions(send_messages=True, manage_webhooks=True)
    async def preview_closet_entry(self, ctx, name):
        """"""

        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(
                "Closets are vote-locked. Please go to "
                "https://discordbots.org/bot/687427956364279873/vote and "
                "click on 'Vote'.\nThen come back and try again.\n"
                "If you just now voted, wait a few moments."
            )
        
        msg = ctx.message
        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = dict()

        try:
            if name in self.bot.user_data["Closets"][ctx.author.id].keys():
                dummy = await msg.channel.create_webhook(name=msg.author.display_name)
                await dummy.send(
                    f"{self.bot.user.name}: Preview message.\n"
                    f"{self.bot.user_data['Closets'][ctx.author.id][name]}",
                    avatar_url=self.bot.user_data["Closets"][ctx.author.id][name]
                )
                return await dummy.delete()

            else:
                await ctx.send(
                    f"A closet entry with that name doesn't exist. "
                    f"See your closet entries with this command: "
                    f"`{self.bot.command_prefix}see_closet`."
                )

        except KeyError or IndexError:
            return await ctx.send(
                f"A closet entry with that name doesn't exist. "
                f"See your closet entries with this command: "
                f"`{self.bot.command_prefix}see_closet`."
            )


def setup(bot: Bot):
    bot.add_cog(ClosetCommands(bot))
