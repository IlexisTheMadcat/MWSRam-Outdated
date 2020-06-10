
# Lib

# Site
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
    @bot_has_permissions(send_messages=True)
    async def blacklist(self, ctx: Context, mode: str, item: str = None):
        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )
            return
        
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
                await ctx.send(
                    f"`item` needs to be a number and proper channel ID. You can also #mention the channel.\n"
                    f"See `{self.bot.command_prefix}help Commands` under `{self.bot.command_prefix}blacklist` "
                    f"to see how to get channel ID."
                )
                return

            else:
                try:
                    channel = self.bot.get_channel(item)
                except NotFound:
                    await ctx.send(
                        f"No channel with that ID exists.\n"
                        f"See `{self.bot.command_prefix}help commands` under `{self.bot.command_prefix}blacklist` "
                        f"to see how to get channel IDs.\nYou can also #mention the channel."
                    )
                else:
                    if ctx.author.id not in self.bot.univ.Blacklists.keys():
                        self.bot.univ.Blacklists[ctx.author.id] = ([], [])

                    if item not in self.bot.univ.Blacklists[ctx.author.id][0]:
                        self.bot.univ.Blacklists[ctx.author.id][0].append(item)
                        
                        if here:
                            await ctx.send(
                                f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                f'(here) was blacklisted for you.\nYou can still use bot commands here.'
                            )
                        elif not here:
                            await ctx.send(
                                f'Channel "{channel.name}" in server "{channel.guild.name}" '
                                f'was blacklisted for you.\nYou can still use bot commands there.'
                            )
                            
                        print(
                            f'+ Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was blacklisted for \"{ctx.author}\".'
                        )
                    else:
                        if not here:
                            await ctx.send("That channel is already blacklisted for you.")

                        elif here:
                            await ctx.send("This channel is already blacklisted for you.")

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
                await ctx.send(
                    f"`channel` needs to be a number and proper channel ID.\n"
                    f"Type and enter `{self.bot.command_prefix}see_blacklists` "
                    f"and find the __ID__ of the channel you want to remove from that list.\n"
                    f"You can also \\#mention the channel."
                )
                return
            else:
                if ctx.author.id in self.bot.univ.Blacklists.keys():
                    if item in self.bot.univ.Blacklists[ctx.author.id][0]:
                        self.bot.univ.Blacklists[ctx.author.id][0].remove(item)
                        channel = await self.bot.get_channel(item)
                        await ctx.send(
                            f'Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was removed from your blacklist.'
                        )
                        print(
                            f'- Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was removed from blacklisted items for user \"{ctx.author}\".'
                        )
                    else:
                        if not here:
                            await ctx.send(
                                f"That channel isn't in your blacklist.\n"
                                f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                                f"blacklisted channels and prefixes."
                            )
                        elif here:
                            await ctx.send(
                                f"This channel isn't in your blacklist.\n"
                                f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                                f"blacklisted channels and prefixes.")
                        return
                else:
                    await ctx.send("You have nothing to remove from your blacklist.")
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                await ctx.send("Your prefix can only be up to 5 characters long.")
                return

            if item.startswith(self.bot.command_prefix):
                await ctx.send("For protection, you cannot blacklist this bot's prefix.")
                return
        
            if ctx.author.id not in self.bot.univ.Blacklists.keys():
                self.bot.univ.Blacklists[ctx.author.id] = ([], [])

            if item not in self.bot.univ.Blacklists[ctx.author.id][1]:
                self.bot.univ.Blacklists[ctx.author.id][1].append(item)
                await ctx.send(f'Added "{item}" to blacklisted prefixes for you.')
                print(f'+ Added "{item}" to blacklisted prefixes for user \"{ctx.author}\"')
            else:
                await ctx.send("That prefix is already blacklisted for you.")

        elif mode in prefixremove:
            if ctx.author.id in self.bot.univ.Blacklists.keys():
                if item in self.bot.univ.Blacklists[ctx.author.id][1]:
                    self.bot.univ.Blacklists[ctx.author.id][1].remove(item)
                    await ctx.send(f'Removed "{item}" from blacklisted prefixes for you.')
                    print(f'- Removed "{item}" from blacklisted prefixes for user \"{ctx.author}\".')
                else:
                    await ctx.send(
                        f"`{item}` isn't in your blacklist.\n"
                        f"Type `{self.bot.command_prefix}see_blacklists` to see your "
                        f"blacklisted channels and prefixes."
                    )
                    return
            else:
                await ctx.send("You have nothing to remove from your blacklist.")
                return

        else:
            await ctx.send(
                f'Invalid mode passed: `{mode}`; Refer to `{self.bot.command_prefix}help commands blacklist`.'
            )

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["see_bl"])
    @bot_has_permissions(send_messages=True)
    async def see_blacklists(self, ctx: Context):

        if ctx.author.id in self.bot.univ.Blacklists.keys():
            message_part = []

            async def render():
                if self.bot.univ.Blacklists[ctx.author.id] == ([], []):
                    await ctx.send("You haven't blacklisted anything yet.")
                message_part.append("Here are your blacklisted items:\n")
                if not len(self.bot.univ.Blacklists[ctx.author.id][0]) == 0:
                    message_part.append("**Channels:**\n")
                    for n in self.bot.univ.Blacklists[ctx.author.id][0]:
                        try:
                            channel = self.bot.get_channel(n)
                        except NotFound:
                            self.bot.univ.Blacklists[ctx.author.id][0].remove(n)
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

            if not len(self.bot.univ.Blacklists[ctx.author.id][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in self.bot.univ.Blacklists[ctx.author.id][1]:
                    message_part.append(f'-- `"{i}"`\n')

            message_full = ''.join(message_part)
            await ctx.send(message_full)
        else:
            await ctx.send("You haven't blacklisted anything yet.")
        print(f'[] Sent blacklisted items for user \"{ctx.author}\".')


def setup(bot: Bot):
    bot.add_cog(BlacklistCommands(bot))

def teardown(bot: Bot):
    bot.remove_cog(BlacklistCommands(bot))
