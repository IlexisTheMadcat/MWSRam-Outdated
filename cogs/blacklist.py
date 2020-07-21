
# Lib

# Site
from discord import Embed
from discord.errors import NotFound
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command, bot_has_permissions

# Local
from utils.classes import Bot


class BlacklistCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def blacklist(self, ctx: Context, mode: str, item: str = None):
        if not ctx.guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers.",
                color=0xff0000
            ))
        
        channeladd = ["channel-add", "ch-a"]  # TODO: Maybe `blacklist` should be `group` with `mode`s as subcommands.
        channelremove = ["channel-remove", "ch-r"]  # TODO: Ask me about this.
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if mode in channeladd:
            if not item:
                item = str(ctx.channel.id)
                here = True
            else:
                here = False

            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)

            except ValueError:
                await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`item` needs to be a number and proper channel ID. You can also #mention the channel.\n"
                                f"See `{self.bot.command_prefix}help Commands` under `{self.bot.command_prefix}blacklist` "
                                f"to see how to get channel ID.",
                    color=0xff0000
                ))
                return

            else:
                try:
                    channel = self.bot.get_channel(item)
                except NotFound:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description=f"No channel with that ID exists.\n"
                                    f"See `{self.bot.command_prefix}help commands` under `{self.bot.command_prefix}blacklist` "
                                    f"to see how to get channel IDs.\nYou can also #mention the channel.",
                        color=0xff0000
                    ))

                else:
                    if ctx.author.id not in self.bot.user_data["Blacklists"].keys():
                        self.bot.user_data["Blacklists"][ctx.author.id] = ([], [])

                    if item not in self.bot.user_data["Blacklists"][ctx.author.id][0]:
                        self.bot.user_data["Blacklists"][ctx.author.id][0].append(item)
                        
                        if here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                            f'(here) was blacklisted for you.\nYou can still use bot commands here.',
                                color=0xff87a3
                            ))

                        elif not here:
                            await ctx.send(embed=Embed(
                                title="Success",
                                description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                            f'was blacklisted for you.\nYou can still use bot commands there.',
                                color=0xff87a3
                            ))
                            
                        print(
                            f'+ Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was blacklisted for \"{ctx.author}\".'
                        )
                    else:
                        if not here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description="That channel is already blacklisted for you.",
                                color=0xff0000
                            ))

                        elif here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description="This channel is already blacklisted for you.",
                                color=0xff0000
                            ))

                        return

        elif mode in channelremove:
            if not item:
                item = str(ctx.channel.id)
                here = True
            else:
                here = False

            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)
            except ValueError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID.\n"
                                f"Type and enter `{self.bot.command_prefix}see_blacklists` "
                                f"and find the __ID__ of the channel you want to remove from that list.\n"
                                f"You can also \\#mention the channel.",
                    color=0xff0000
                ))

            else:
                if ctx.author.id in self.bot.user_data["Blacklists"].keys():
                    if item in self.bot.user_data["Blacklists"][ctx.author.id][0]:
                        self.bot.user_data["Blacklists"][ctx.author.id][0].remove(item)
                        channel = self.bot.get_channel(item)
                        await ctx.send(embed=Embed(
                            title="Success",
                            description=f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                        f'was removed from your blacklist.',
                            color=0xff87a3
                        ))
                        print(
                            f'- Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was removed from blacklisted items for user \"{ctx.author}\".'
                        )
                    else:
                        if not here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description=f"That channel isn't in your blacklist.\n"
                                            f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                                            f"blacklisted channels and prefixes.",
                                color=0xff0000
                            ))

                        elif here:
                            await ctx.send(embed=Embed(
                                title="Error",
                                description=f"This channel isn't in your blacklist.\n"
                                            f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                                            f"blacklisted channels and prefixes.",
                                color=0xff0000
                            ))
                        return
                else:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="You have nothing to remove from your blacklist.",
                        color=0xff0000))
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000
                ))

            if ctx.author.id not in self.bot.user_data["Blacklists"].keys():
                self.bot.user_data["Blacklists"][ctx.author.id] = ([], [])

            if item not in self.bot.user_data["Blacklists"][ctx.author.id][1]:
                self.bot.user_data["Blacklists"][ctx.author.id][1].append(item)
                await ctx.send(embed=Embed(
                    title="Success",
                    description=f'Added "{item}" to blacklisted prefixes for you.',
                    color=0xff87a3
                ))

                print(f'+ Added "{item}" to blacklisted prefixes for user \"{ctx.author}\"')
            else:
                await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for you.",
                    color=0xff0000
                ))

        elif mode in prefixremove:
            if ctx.author.id in self.bot.user_data["Blacklists"].keys():
                if item in self.bot.user_data["Blacklists"][ctx.author.id][1]:
                    self.bot.user_data["Blacklists"][ctx.author.id][1].remove(item)
                    await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Removed "{item}" from blacklisted prefixes for you.',
                        color=0xff0000
                    ))

                    print(f'- Removed "{item}" from blacklisted prefixes for user \"{ctx.author}\".')
                    return
                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"`{item}` isn't in your blacklist.\n"
                                    f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                                    f"blacklisted channels and prefixes.",
                        color=0xff0000
                    ))
            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your blacklist.",
                    color=0xff0000
                ))

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description=f'Invalid mode passed: `{mode}`; Refer to `{self.bot.command_prefix}help commands blacklist`.',
                color=0xff0000
            ))

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["see_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_blacklists(self, ctx: Context):

        if ctx.author.id in self.bot.user_data["Blacklists"].keys():
            if self.bot.user_data["Blacklists"][ctx.author.id] == ([], []):
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You haven't blacklisted anything yet.",
                    color=0xff0000
                ))

            message_part = []

            async def render():
                message_part.append("Here are your blacklisted items:\n")
                if not len(self.bot.user_data["Blacklists"][ctx.author.id][0]) == 0:
                    message_part.append("**Channels:**\n")
                    for n in self.bot.user_data["Blacklists"][ctx.author.id][0]:
                        try:
                            channel = self.bot.get_channel(n)
                        except NotFound:
                            self.bot.user_data["Blacklists"][ctx.author.id][0].remove(n)
                            return False
                        else:
                            message_part.append(
                                f"-- Server: `{channel.guild.name}`; Name: {channel.mention}; ID: {channel.id}\n"
                            )
                            
                    return True

            while True:
                result = await render()
                if result is False:
                    message_part = list()
                    message_part.append("Here are your blacklisted items:\n```")
                    continue
                else:
                    break

            if not len(self.bot.user_data["Blacklists"][ctx.author.id][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in self.bot.user_data["Blacklists"][ctx.author.id][1]:
                    message_part.append(f'-- `"{i}"`\n')

            message_full = ''.join(message_part)
            await ctx.send(embed=Embed(
                tile="Blacklist",
                description=message_full,
                color=0xff87a3
            ))
        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You haven't blacklisted anything yet.",
                color=0xff0000
            ))

        print(f'[] Sent blacklisted items for user \"{ctx.author}\".')


def setup(bot: Bot):
    bot.add_cog(BlacklistCommands(bot))
