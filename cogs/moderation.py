
# Lib

# Site
from discord.errors import NotFound
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
from discord.user import User

# Local
from utils.classes import Bot


class ModerationCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["s_bl"])
    @bot_has_permissions(send_messages=True)
    @has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx: Context, mode: str, item: str = None):
        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )
            return

        channeladd = ["channel-add", "ch-a"]
        channelremove = ["channel-remove", "ch-r"]
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if (not item) and (mode in channeladd or mode in channelremove):
            item = str(ctx.channel.id)
        
        if mode in channeladd:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)
            except ValueError:
                await ctx.send(
                    f"`channel` needs to be a number and proper channel ID. You can also #mention the channel.\n"
                    f"See `{self.bot.command_prefix}help Commands` under `{self.bot.command_prefix}blacklist` "
                    f"to see how to get channel ID."
                )
                return
            else:
                try:
                    channel = await self.bot.fetch_channel(item)
                except NotFound:
                    await ctx.send(
                        f"No channel with that ID exists.\nSee `{self.bot.command_prefix}help commands` under "
                        f"`{self.bot.command_prefix}blacklist` to see how to get channel IDs.\n"
                        f"You can also #mention the channel."
                    )
                else:
                    if channel not in ctx.guild.channels:
                        await ctx.send(
                            "The channel has to be in this server. I wouldn't just let you cheese your friends "
                            "like that in another server."
                        )
                        return
                    
                    if ctx.guild.id not in self.bot.univ.ServerBlacklists.keys():
                        self.bot.univ.ServerBlacklists[ctx.guild.id] = ([], [])

                    if item not in self.bot.univ.ServerBlacklists[ctx.guild.id][0]:
                        self.bot.univ.ServerBlacklists[ctx.guild.id][0].append(item)
                        await ctx.send(
                            f'Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was blacklisted for this server.\nYou can still use bot commands there.'
                        )
                        print(f'+ Channel "{channel.name}" in server "{channel.guild.name}" was server-blacklisted.')
                    else:
                        await ctx.send("You already blacklisted that channel for this server.")
                    return

        elif mode in channelremove:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")
                
            try:
                item = int(item)
            except ValueError:
                await ctx.send(
                    f"`channel` needs to be a number and proper channel ID.\nType and enter "
                    f"`{self.bot.command_prefix}see_blacklists` and find the __ID__ of the channel "
                    f"you want to remove from that list.\nYou can also \\#mention the channel."
                )
                return
            
            else:
                if ctx.guild.id in self.bot.univ.ServerBlacklists.keys():
                    if item in self.bot.univ.ServerBlacklists[ctx.guild.id][0]:
                        self.bot.univ.ServerBlacklists[ctx.guild.id][0].remove(item)
                        channel = await self.bot.fetch_channel(item)
                        await ctx.send(
                            f'Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was removed from your server\'s blacklist.'
                        )
                        print(
                            f'- Channel "{channel.name}" in server "{channel.guild.name}" '
                            f'was removed from server-blacklisted items.'
                        )
                    else:
                        await ctx.send(
                            f"That channel isn't in your server's blacklist.\n"
                            f"Type `{self.bot.command_prefix}see_server_blacklists` to see "
                            f"your blacklisted channels and prefies."
                        )
                        return
                else:
                    await ctx.send("You have nothing to remove from your server's blacklist yet.")
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                await ctx.send("Your prefix can only be up to 5 characters long.")
                return

            if item.startswith(self.bot.command_prefix):
                await ctx.send("For protection, you cannot blacklist this bot's prefix.")
                return
        
            if ctx.guild.id not in self.bot.univ.ServerBlacklists.keys():
                self.bot.univ.ServerBlacklists[ctx.guild.id] = ([], [])

            if item not in self.bot.univ.ServerBlacklists[ctx.guild.id][1]:
                self.bot.univ.ServerBlacklists[ctx.guild.id][1].append(item)
                await ctx.send(f"Added \"{item}\" to blacklisted prefixes for this server.")
                print(f"+ Added \"{item}\" to blacklisted prefixes for user \"{ctx.author}\"")
            else:
                await ctx.send("That prefix is already blacklisted for this server.")

        elif mode in prefixremove:
            if ctx.guild.id in self.bot.univ.ServerBlacklists.keys():
                if item in self.bot.univ.ServerBlacklists[ctx.guild.id][1]:
                    self.bot.univ.ServerBlacklists[ctx.guild.id][1].remove(item)
                    await ctx.send(f'Removed "{item}" from blacklisted prefixes for this server.')
                    print(f'- Removed "{item}" from blacklisted prefixes for user \"{ctx.author}\".')
                else:
                    await ctx.send(
                        f"`{item}` isn't in your blacklist.\nType `{self.bot.command_prefix}see_server_blacklists` "
                        f"to see your blacklisted channels and prefixes."
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
    @command(aliases=["see_s_bl"])
    @bot_has_permissions(send_messages=True)
    async def see_server_blacklists(self, ctx: Context):
        if ctx.guild.id in self.bot.univ.ServerBlacklists.keys():
            message_part = list()

            async def render():
                if self.bot.univ.ServerBlacklists[ctx.guild.id] == ([], []):
                    message_part.append("You haven't blacklisted anything for this server yet.")
                    return True
                
                message_part.append("Here are this server's blacklisted items:\n")
                if not len(self.bot.univ.ServerBlacklists[ctx.guild.id][0]) == 0:
                    message_part.append("**Channels:**\n")
                    for i in self.bot.univ.ServerBlacklists[ctx.guild.id][0]:
                        try:
                            channel = await self.bot.fetch_channel(i)
                        except NotFound:
                            self.bot.univ.ServerBlacklists[ctx.guild.id][0].remove(i)
                            return False
                        else:
                            message_part.append(f"-- Name: {channel.mention}; ID: {channel.id}\n")
                            
                    return True
    
            while True:
                result = await render()
                if result is False:
                    message_part = list()
                    message_part.append("Here are your blacklisted items:\n```")
                    continue
                else:
                    break

            if not len(self.bot.univ.ServerBlacklists[ctx.guild.id][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in self.bot.univ.ServerBlacklists[ctx.guild.id][1]:
                    message_part.append(f'-- `"{i}"`\n')

            message_full = ''.join(message_part)
            await ctx.send(message_full)
        else:
            await ctx.send("You haven't blacklisted anything for this server yet.")

        print(f'[] Sent server-blacklisted items for user \"{ctx.author}\" in server \"{ctx.guild.name}\".')

    @command()
    @bot_has_permissions(send_messages=True)
    async def list(self, ctx: Context):
        message = list()
        if ctx.guild.id in self.bot.univ.VanityAvatars.keys() and self.bot.univ.VanityAvatars[ctx.guild.id] != dict():
            async with ctx.typing():
                message.append(
                    "Here are users using vanities in this server; The list may contain members who have left:\n```"
                )
                for i in self.bot.univ.VanityAvatars[ctx.guild.id].keys():
                    user = await self.bot.fetch_user(i)
                    message.append(f"{user} - URL: {self.bot.univ.VanityAvatars[ctx.guild.id][i][1]}\n")

                message.append("```")
                await ctx.send(f"{''.join(message)}")
        else:
            await ctx.send("This server has no users with equipped vanities.")
            return
    
    @command(aliases=["manage", "user"])
    @bot_has_permissions(send_messages=True)
    @has_permissions(manage_messages=True)
    async def manage_user(self, ctx: Context, mode: str, user: User):
        invoker_member = await ctx.guild.fetch_member(ctx.author.id)
        user_member = await ctx.guild.fetch_member(user.id)
        invoker_role = invoker_member.top_role
        user_role = user_member.top_role
        
        if ctx.guild.id in self.bot.univ.VanityAvatars.keys() and \
                user.id in self.bot.univ.VanityAvatars[ctx.guild.id].keys():
            if user.id == ctx.author.id and not ctx.author == ctx.guild.owner:
                await ctx.send("You cannot use this command on yourself.")
                return

            if not invoker_member == ctx.guild.owner:
                if ctx.guild.id in self.bot.univ.VanityAvatars and \
                        ctx.author.id in self.bot.univ.VanityAvatars[ctx.guild.id] and \
                        self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][2]:
                    await ctx.send(
                        "You cannot use this command because you were blocked from "
                        "using vanity avatars by another user."
                    )
                    return

            if user_member is None:
                await ctx.send("That user is not a part of this server.")
                return

            if not invoker_member == ctx.guild.owner:
                if invoker_role < user_role:
                    await ctx.send("You cannot block this user because they have a higher role than you.")
                    return
            
            if mode == "block":
                if self.bot.univ.VanityAvatars[ctx.guild.id][user.id][2]:
                    await ctx.send("That user is already blocked.")
                    return
                else:
                    self.bot.univ.VanityAvatars[ctx.guild.id][user.id][0] = None
                    self.bot.univ.VanityAvatars[ctx.guild.id][user.id][2] = True
                    await ctx.send("User avatar removed and blocked for this server.")
                    return
                    
            elif mode == "unblock":
                if not self.bot.univ.VanityAvatars[ctx.guild.id][user.id][2]:
                    await ctx.send("That user is already unblocked.")
                    return
                else:
                    self.bot.univ.VanityAvatars[ctx.guild.id][user.id][2] = False
                    await ctx.send("User unblocked for this server.")
                    return
        else:
            await ctx.send("That user has no information linked with this server.")
            return


def setup(bot: Bot):
    bot.add_cog(ModerationCommands(bot))
