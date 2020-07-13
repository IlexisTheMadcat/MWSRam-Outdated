
# Lib

# Site
from discord.errors import NotFound
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import (
    bot_has_permissions,
    command,
    has_permissions
)
from discord.member import Member

# Local
from utils.classes import Bot


class ModerationCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=["s_bl"])
    @bot_has_permissions(send_messages=True)
    @has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx: Context, mode: str, item: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel

        if not guild:
            return await ctx.send(
                "This command cannot be used in a DM channel. Consider using "
                "it in a private channel in one of your servers."
            )

        channeladd = ["channel-add", "ch-a"]  # TODO: Make commands group
        channelremove = ["channel-remove", "ch-r"]
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if (not item) and (mode in channeladd or mode in channelremove):
            item = str(chan.id)
        
        if mode in channeladd:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)

            except ValueError:
                return await ctx.send(
                    f"`channel` needs to be a number and proper channel ID. "
                    f"You can also #mention the channel.\n"
                    f"See `{self.bot.command_prefix}help Commands` under "
                    f"`{self.bot.command_prefix}blacklist` "
                    f"to see how to get channel ID."
                )

            else:
                try:
                    channel = await self.bot.fetch_channel(item)

                except NotFound:
                    await ctx.send(
                        f"No channel with that ID exists.\nSee "
                        f"`{self.bot.command_prefix}help commands` under "
                        f"`{self.bot.command_prefix}blacklist` to see how to "
                        f"get channel IDs.\nYou can also #mention the channel."
                    )

                else:
                    if channel not in guild.channels:
                        return await ctx.send(
                            "The channel has to be in this server. I wouldn't "
                            "just let you cheese your friends like that in "
                            "another server."
                        )
                    
                    if guild.id not in self.bot.user_data["ServerBlacklists"]:
                        self.bot.user_data["ServerBlacklists"][guild.id] = (list(), list())

                    if item not in self.bot.user_data["ServerBlacklists"][guild.id][0]:
                        self.bot.user_data["ServerBlacklists"][guild.id][0].append(item)
                        print(
                            f'+ Channel "{channel.name}" in server '
                            f'"{channel.guild.name}" was server-blacklisted.'
                        )
                        return await ctx.send(
                            f'Channel "{channel.name}" in server '
                            f'"{channel.guild.name}" was blacklisted for this '
                            f'server.\nYou can still use bot commands there.'
                        )

                    else:
                        return await ctx.send(
                            "You already blacklisted that channel for this "
                            "server."
                        )

        elif mode in channelremove:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")
                
            try:
                item = int(item)

            except ValueError:
                return await ctx.send(
                    f"`channel` needs to be a number and proper channel ID.\n"
                    f"Type and enter `{self.bot.command_prefix}see_blacklists`"
                    f" and find the __ID__ of the channel you want to remove "
                    f"from that list.\nYou can also \\#mention the channel."
                )

            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][guild.id][0]:
                    self.bot.user_data["ServerBlacklists"][guild.id][0].remove(item)
                    channel = await self.bot.fetch_channel(item)
                    print(
                        f'- Channel "{channel.name}" in server '
                        f'"{channel.guild.name}" was removed from '
                        f'server-blacklisted items.'
                    )
                    return await ctx.send(
                        f'Channel "{channel.name}" in server '
                        f'"{channel.guild.name}" was removed from your '
                        f'server\'s blacklist.'
                    )

                else:
                    return await ctx.send(
                        f"That channel isn't in your server's blacklist.\n"
                        f"Type `{self.bot.command_prefix}see_server_blacklists` "
                        f"to see your blacklisted channels "
                        f"and prefixes."
                    )

            else:
                return await ctx.send(
                    "You have nothing to remove from your server's "
                    "blacklist yet."
                )

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(
                    "Your prefix can only be up to 5 characters long."
                )

            if item.startswith(self.bot.command_prefix):
                return await ctx.send(
                    "For protection, you cannot blacklist this bot's prefix."
                )
        
            if guild.id not in self.bot.user_data["ServerBlacklists"]:
                self.bot.user_data["ServerBlacklists"][guild.id] = (list(), list())

            if item not in self.bot.user_data["ServerBlacklists"][guild.id][1]:
                self.bot.user_data["ServerBlacklists"][guild.id][1].append(item)
                print(
                    f'+ Added \"{item}\" to blacklisted prefixes for user '
                    f'"{author}"'
                )
                return await ctx.send(
                    f"Added \"{item}\" to blacklisted prefixes for this "
                    f"server."
                )
            else:
                return await ctx.send(
                    "That prefix is already blacklisted for this server."
                )

        elif mode in prefixremove:
            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][guild.id][1]:
                    self.bot.user_data["ServerBlacklists"][guild.id][1].remove(item)
                    print(
                        f'- Removed "{item}" from blacklisted prefixes for '
                        f'user "{ctx.author}".'
                    )
                    return await ctx.send(
                        f'Removed "{item}" from blacklisted prefixes for '
                        f'this server.'
                    )

                else:
                    return await ctx.send(
                        f"`{item}` isn't in your blacklist.\nType "
                        f"`{self.bot.command_prefix}see_server_blacklists` "
                        f"to see your blacklisted channels and prefixes."
                    )

            else:
                return await ctx.send(
                    "You have nothing to remove from your blacklist."
                )

        else:
            return await ctx.send(
                f'Invalid mode passed: `{mode}`; Refer to '
                f'`{self.bot.command_prefix}help commands blacklist`.'
            )

    @command(aliases=["see_s_bl"])
    @bot_has_permissions(send_messages=True)
    async def see_server_blacklists(self, ctx: Context):

        guild = ctx.guild

        if guild.id not in self.bot.user_data["ServerBlacklists"]:
            return await ctx.send(
                "You haven't blacklisted anything for this server yet."
            )

        message_part = list()

        def render():
            if self.bot.user_data["ServerBlacklists"][guild.id] == (list(), list()):
                message_part.append(
                    "You haven't blacklisted anything for this server yet."
                )
                return True

            message_part.append(
                "Here are this server's blacklisted items:"
            )
            if len(self.bot.user_data["ServerBlacklists"][guild.id][0]) != 0:
                message_part.append("**Channels:**")
                for c_id in self.bot.user_data["ServerBlacklists"][guild.id][0]:
                    channel = guild.get_channel(c_id)
                    if channel:
                        message_part.append(
                            f"-- Name: {channel.mention};"
                            f" ID: {channel.id}"
                        )
                    else:
                        self.bot.user_data["ServerBlacklists"][guild.id][0].remove(i)
                        return False

                return True

        while True:
            result = render()
            if result is False:
                message_part = list()
                message_part.append("Here are your blacklisted items:```")
                continue
            else:
                break

        if len(self.bot.user_data["ServerBlacklists"][guild.id][1]) != 0:
            message_part.append("**Prefixes:**")
            for i in self.bot.user_data["ServerBlacklists"][guild.id][1]:
                message_part.append(f'-- `"{i}"`')

        message_full = "\n".join(message_part)
        await ctx.send(message_full)

        print(
            f'[] Sent server-blacklisted items for user '
            f'"{ctx.author}" in server "{guild.name}".'
        )

    @command()
    @bot_has_permissions(send_messages=True)
    async def list(self, ctx: Context):
        guild = ctx.guild
        message = list()
        if guild.id in self.bot.user_data["VanitiesAvatars"] and \
                self.bot.user_data["VanitiesAvatars"][guild.id] != dict():
            message.append(
                "Here are users using vanities in this server; "
                "The list may contain members who have left:\n```"
            )

            show_list = False
            for u_id in self.bot.user_data["VanitiesAvatars"][guild.id]:
                user = self.bot.get_user(u_id)
                if user and self.bot.user_data["VanitiesAvatars"][guild.id][u_id][0]:
                    message.append(
                        f"{user} - URL: \n"
                        f"{self.bot.user_data['VanitiesAvatars'][guild.id][u_id][0]}\n\n"
                    )
                    show_list = True

            if not show_list:
                return await ctx.send("This server has no users with equipped vanities.")

            message.append("```")
            await ctx.send(''.join(message))

        else:
            await ctx.send("This server has no users with equipped vanities.")

    @bot_has_permissions(send_messages=True)
    @has_permissions(manage_messages=True)
    @command(aliases=["manage", "user"])
    async def manage_user(self, ctx: Context, mode: str, user: Member):

        guild = ctx.guild
        author = ctx.author
        author_role = author.top_role
        
        if not (guild.id in self.bot.user_data["VanitiesAvatars"] and
                user.id in self.bot.user_data["VanitiesAvatars"][guild.id]):
            return await ctx.send(
                "That user has no information linked with this server."
            )

        if user.id == author.id and author.id != guild.owner.id:
            return await ctx.send(
                "You cannot use this command on yourself."
            )

        if author.id != guild.owner.id and guild.id in self.bot.user_data["VanitiesAvatars"] and author.id \
                in self.bot.user_data["VanitiesAvatars"][guild.id] and \
                self.bot.user_data["VanitiesAvatars"][guild.id][author.id][2]:
            return await ctx.send(
                "You cannot use this command because you were blocked "
                "from using vanity avatars by another user."
            )

        if user is None:
            return await ctx.send(
                "That user is not a part of this server or does not exist."
            )

        if author != guild.owner and author_role <= user.top_role:
            return await ctx.send(
                "You cannot manage this user because they have an "
                "equal or higher role than you."
            )

        if mode == "block":
            if self.bot.user_data["VanitiesAvatars"][guild.id][user.id][2]:
                return await ctx.send("That user is already blocked.")

            else:
                self.bot.user_data["VanitiesAvatars"][guild.id][user.id][0] = None
                self.bot.user_data["VanitiesAvatars"][guild.id][user.id][2] = True
                return await ctx.send(
                    "User avatar removed and blocked for this server."
                )

        elif mode == "unblock":
            if not self.bot.user_data["VanitiesAvatars"][guild.id][user.id][2]:
                return await ctx.send("That user is already unblocked.")

            else:
                self.bot.user_data["VanitiesAvatars"][guild.id][user.id][2] = False
                return await ctx.send("User unblocked for this server.")

        elif mode == "get_info":
            return await ctx.send(
                f"**Vanity status for user {str(user)}:**\n"
                f"Vanity url: {self.bot.user_data['VanitiesAvatars'][guild.id][user.id][0]}\n"
                f"Previous url: {self.bot.user_data['VanitiesAvatars'][guild.id][user.id][1]}\n"
                f"Is blocked:  {self.bot.user_data['VanitiesAvatars'][guild.id][user.id][2]}"
            )


def setup(bot: Bot):
    bot.add_cog(ModerationCommands(bot))
