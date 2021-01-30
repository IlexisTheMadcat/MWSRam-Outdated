
# Lib

# Site
from discord import Embed
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
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def add_to_closet(self, ctx: Context, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)
    
        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "https://discordbots.org/bot/687427956364279873/vote "
                            "and click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000
            ))

        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000
            ))

        if not ctx.message.attachments and \
                not self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity equipped.\n"
                            "You can attach a file to add without a vanity.",
                color=0xff0000
            ))

        else:
            try:
                if ctx.author.id not in self.bot.user_data["Closets"].keys():
                    self.bot.user_data["Closets"][ctx.author.id] = {}

                if name in self.bot.user_data["Closets"][ctx.author.id].keys():
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"A closet entry with that name already exists.\n"
                                    f"See your closet entries with this command: "
                                    f"`{self.bot.command_prefix}see_closet`.",
                        color=0xff0000
                    ))

                if len(self.bot.user_data["Closets"][ctx.author.id].keys()) >= 10:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description="You've reached (or somehow exceeded) the max "
                                    "number of vanities allowed in your closet.\n"
                                    "Consider removing one of them.",
                        color=0xff0000
                    ))

                if len(name) > 20:
                    return await ctx.send(embed=Embed(
                        title="Name Error",
                        description="Your name can't be longer than 20 characters.",
                        color=0xff0000
                    ))

                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                    self.bot.user_data["Closets"][ctx.author.id].update({name: url})
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added attached file to your closet with name `{name}`.",
                        color=0xff87a3
                    ))

                elif self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0] is not None:
                    url = self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0]
                    self.bot.user_data["Closets"][ctx.author.id].update({name: url})
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added current vanity avatar to closet with name `{name}`.",
                        color=0xff87a3
                    ))

            except KeyError or IndexError:
                self.bot.user_data["Closets"][ctx.author.id] = {}
                try:
                    self.bot.user_data["Closets"][ctx.author.id].update(
                        {name: self.bot.user_data["VanityAvatars"][ctx.guild.id][ctx.author.id][0]}
                    )
                except IndexError or KeyError:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"You don't have a vanity equipped. This particular error was caused because you haven't created your closet yet.\n"
                                    f"First, set your vanity using the `{self.bot.command_prefix}set_vanity <url>` command and try again.",
                        color=0xff0000
                    ))
                else:
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f"Added with closet entry \"{name}\".",
                        color=0xff87a3
                    ))

    @command(aliases=["cl_remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_from_closet(self, ctx: Context, name: str):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "https://discordbots.org/bot/687427956364279873/vote "
                            "and click on 'Vote'.\n"
                            "Then come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000
            ))
        
        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = {}

        try:
            if name not in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"See your closet entries with this command: "
                                f"`{self.bot.command_prefix}see_closet`.",
                    color=0xff0000
                ))

            else:
                self.bot.user_data["Closets"][ctx.author.id].pop(name)

        except KeyError:
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with the name `{name}` doesn't exist.\n"
                            f"See your closet entries with this command: "
                            f"`{self.bot.command_prefix}see_closet`.",
                color=0xff0000
            ))
        else:
            await ctx.send(embed=Embed(
                title="Success",
                description=f"Removed closet entry \"{name}\".",
                color=0xff87a3
            ))

    @command(aliases=["cl_rename"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def rename_closet_entry(self, ctx: Context, name: str, rename: str):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "https://discordbots.org/bot/687427956364279873/vote and "
                            "click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000
            ))
        
        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            
        try:
            if len(rename) > 20:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Your name can't be longer than 20 characters.",
                    color=0xff0000
                ))

            if name == rename:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Both names are the same.",
                    color=0xff0000
                ))

            elif name not in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{name}` doesn't exist.\n"
                                f"See your closet entries with this command: "
                                f"`{self.bot.command_prefix}see_closet`.",
                    color=0xff0000
                ))

            elif rename in self.bot.user_data["Closets"][ctx.author.id].keys():
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with the name `{rename}` already exists.\n"
                                f"See your closet entries with this command: "
                                f"`{self.bot.command_prefix}see_closet`.",
                    color=0xff0000
                ))

            else:
                orig_url = self.bot.user_data["Closets"][ctx.author.id].pop(name)
                self.bot.user_data["Closets"][ctx.author.id].update({rename: orig_url})

        except KeyError:
            self.bot.user_data["Closets"][ctx.author.id] = dict()
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with with the name `{name}` doesn't exist.\n"
                            f"See your closet entries with this command: "
                            f"`{self.bot.command_prefix}see_closet`.",
                color=0xff0000
            ))

        else:
            await ctx.send(embed=Embed(
                title="Success",
                description=f"Renamed closet entry \"{name}\" to \"{rename}\".",
                color=0xff87a3
            ))

    @command(aliases=["cl", "closet"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_closet(self, ctx: Context, name: User = None):
        if not name:
            name = ctx.author
            if name.id not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][name.id] = {}

            check = await self.bot.get_user_vote(name.id)
                
            if not check:
                return await ctx.send(embed=Embed(
                    title="Vote-Locked!",
                    description="Closets are vote-locked. Please go to "
                                "https://discordbots.org/bot/687427956364279873/vote and "
                                "click on 'Vote'.\nThen come back and try again.\n"
                                "If you just now voted, wait a few moments.",
                    color=0xff87a3
                ))

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
                            f"▛▚ Name: {i}\n"
                            f"▙▞ URL: ({self.bot.user_data['Closets'][name.id][i]})\n"
                            f"\n"
                        )
                else:
                    raise KeyError
                
            except KeyError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing in your closet.",
                    color=0xff0000
                ))

        else:
            if name.id not in self.bot.user_data["Closets"].keys():
                self.bot.user_data["Closets"][name.id] = dict()
    
            check = await self.bot.get_user_vote(name.id)

            if not check:
                return await ctx.send(embed=Embed(
                    title="Vote-Locked!",
                    description=f"Closets are vote-locked. Tell {name.name} to go to "
                                f"https://discordbots.org/bot/687427956364279873/vote "
                                f"and click on 'Vote'.\nThen come back and try again.\n"
                                f"If you just now voted, wait a few moments.",
                    color=0xff0000
                ))
        
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
                await ctx.send(embed=Embed(
                    title="Error",
                    description="They have nothing in their closet.",
                    color=0xff0000
                ))
                return

        message_part.append("```")
        message = ''.join(message_part)

        await ctx.send(embed=Embed(
            title=f"{name}'s Closet",
            description=message,
            color=0xff87a3,
        ))

    @command(aliases=["cl_preview", "cl_pv"])
    @bot_has_permissions(send_messages=True, embed_links=True, manage_webhooks=True)
    async def preview_closet_entry(self, ctx, name):
        check = await self.bot.get_user_vote(ctx.author.id)

        if not check:
            return await ctx.send(embed=Embed(
                title="Vote-Locked!",
                description="Closets are vote-locked. Please go to "
                            "https://discordbots.org/bot/687427956364279873/vote and "
                            "click on 'Vote'.\nThen come back and try again.\n"
                            "If you just now voted, wait a few moments.",
                color=0xff0000
            ))

        if ctx.author.id not in self.bot.user_data["Closets"].keys():
            self.bot.user_data["Closets"][ctx.author.id] = dict()

        try:
            if name in self.bot.user_data["Closets"][ctx.author.id].keys():
                dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
                await dummy.send(embed=Embed(
                    title="Preview",
                    description=f"{self.bot.user.name}: Preview message.\n",
                    color=0xff87a3
                ).set_image(url=self.bot.user_data['Closets'][ctx.author.id][name]),
                    avatar_url=self.bot.user_data["Closets"][ctx.author.id][name])
                return await dummy.delete()

            else:
                await ctx.send(embed=Embed(
                    title="Name Error",
                    description=f"A closet entry with that name doesn't exist. "
                                f"See your closet entries with this command: "
                                f"`{self.bot.command_prefix}see_closet`.",
                    color=0xff0000
                ))

        except KeyError or IndexError:
            return await ctx.send(embed=Embed(
                title="Name Error",
                description=f"A closet entry with that name doesn't exist. "
                            f"See your closet entries with this command: "
                            f"`{self.bot.command_prefix}see_closet`.",
                color=0xff0000
            ))


def setup(bot: Bot):
    bot.add_cog(ClosetCommands(bot))
