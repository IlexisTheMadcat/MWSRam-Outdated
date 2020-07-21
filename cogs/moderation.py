
# Lib

# Site
from discord import Embed
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
    @bot_has_permissions(send_messages=True, embed_links=True)
    @has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx: Context, mode: str, item: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider using "
                            "it in a private channel in one of your servers.",
                color=0xff0000
            ))

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
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID. "
                                f"You can also #mention the channel.",
                    color=0xff0000
                ))

            else:
                channel = await self.bot.get_channel(item)

                if channel is None:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description=f"No channel with that ID exists. Please #mention the channel instead.",
                        color=0xff0000
                    ))

                else:
                    if channel not in guild.channels:
                        return await ctx.send(embed=Embed(
                            title="Access Denied",
                            description="The channel has to be in this server. I wouldn't "
                                        "just let you cheese your friends like that in "
                                        "another server.",
                            color=0xff0000
                        ))
                    
                    if guild.id not in self.bot.user_data["ServerBlacklists"]:
                        self.bot.user_data["ServerBlacklists"][guild.id] = (list(), list())

                    if item not in self.bot.user_data["ServerBlacklists"][guild.id][0]:
                        self.bot.user_data["ServerBlacklists"][guild.id][0].append(item)
                        print(
                            f'+ Channel "{channel.name}" in server '
                            f'"{channel.guild.name}" was server-blacklisted.'
                        )
                        return await ctx.send(embed=Embed(
                            title="Success",
                            description=f'Channel "{channel.name}" in server '
                                        f'"{channel.guild.name}" was blacklisted for this '
                                        f'server.\nYou can still use bot commands there.',
                            color=0xff87a3
                        ))

                    else:
                        return await ctx.send(embed=Embed(
                            title="Error",
                            description="You already blacklisted that channel for this "
                                        "server.",
                            color=0xff87a3
                        ))

        elif mode in channelremove:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")
                
            try:
                item = int(item)

            except ValueError:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description=f"`channel` needs to be a number and proper channel ID. Please #mention the channel instead.",
                    color=0xff0000
                ))

            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][guild.id][0]:
                    self.bot.user_data["ServerBlacklists"][guild.id][0].remove(item)
                    channel = await self.bot.fetch_channel(item)
                    print(
                        f'- Channel "{channel.name}" in server '
                        f'"{channel.guild.name}" was removed from '
                        f'server-blacklisted items.'
                    )
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Channel "{channel.name}" in server '
                                    f'"{channel.guild.name}" was removed from your '
                                    f'server\'s blacklist.',
                        color=0xff87a3
                    ))

                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"That channel isn't in your server's blacklist.\n"
                                    f"Type `{self.bot.command_prefix}see_server_blacklists` "
                                    f"to see your blacklisted channels "
                                    f"and prefixes.",
                        color=0xff0000
                    ))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your server's "
                                "blacklist yet.",
                    color=0xff0000
                ))

        elif mode in prefixadd:
            if len(item) > 5:
                return await ctx.send(embed=Embed(
                    title="Name Error",
                    description="Your prefix can only be up to 5 characters long.",
                    color=0xff0000
                ))
        
            if guild.id not in self.bot.user_data["ServerBlacklists"]:
                self.bot.user_data["ServerBlacklists"][guild.id] = (list(), list())

            if item not in self.bot.user_data["ServerBlacklists"][guild.id][1]:
                self.bot.user_data["ServerBlacklists"][guild.id][1].append(item)
                print(
                    f'+ Added \"{item}\" to blacklisted prefixes for user '
                    f'"{author}"'
                )
                return await ctx.send(embed=Embed(
                    title="Success",
                    description=f"Added \"{item}\" to blacklisted prefixes for this server.",
                    color=0xff87a3
                ))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That prefix is already blacklisted for this server.",
                    color=0xff0000
                ))

        elif mode in prefixremove:
            if guild.id in self.bot.user_data["ServerBlacklists"]:
                if item in self.bot.user_data["ServerBlacklists"][guild.id][1]:
                    self.bot.user_data["ServerBlacklists"][guild.id][1].remove(item)
                    print(
                        f'- Removed "{item}" from blacklisted prefixes for '
                        f'user "{ctx.author}".'
                    )
                    return await ctx.send(embed=Embed(
                        title="Success",
                        description=f'Removed "{item}" from blacklisted prefixes for this server.',
                        color=0xff87a3
                    ))

                else:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description=f"`{item}` isn't in your blacklist.\nType "
                                    f"`{self.bot.command_prefix}see_server_blacklists` "
                                    f"to see your blacklisted channels and prefixes.",
                        color=0xff0000
                    ))

            else:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="You have nothing to remove from your blacklist.",
                    color=0xff0000
                ))

        else:
            return await ctx.send(embed=Embed(
                title="Argument Error",
                description=f'Invalid mode passed: `{mode}`; Refer to '
                            f'`{self.bot.command_prefix}help commands blacklist`.',
                color=0xff0000
            ))

    @command(aliases=["see_s_bl"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def see_server_blacklists(self, ctx: Context):

        guild = ctx.guild

        if guild.id not in self.bot.user_data["ServerBlacklists"]:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You haven't blacklisted anything for this server yet.",
                color=0xff0000
            ))

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
                            f"-- Name: {channel.mention}; ID: {channel.id}"
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
        await ctx.send(embed=Embed(
            title="Server Blacklist",
            description=message_full,
            color=0xff87a3
        ))

        print(
            f'[] Sent server-blacklisted items for user '
            f'"{ctx.author}" in server "{guild.name}".'
        )

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def list(self, ctx: Context):
        guild = ctx.guild
        message = list()
        if guild.id in self.bot.user_data["VanityAvatars"] and \
                self.bot.user_data["VanityAvatars"][guild.id] != dict():
            message.append(
                "Here are users using vanities in this server; "
                "The list may contain members who have left:\n```"
            )

            show_list = False
            for u_id in self.bot.user_data["VanityAvatars"][guild.id]:
                user = self.bot.get_user(u_id)
                if user and self.bot.user_data["VanityAvatars"][guild.id][u_id][0]:
                    message.append(
                        f"{user} - URL: \n"
                        f"{self.bot.user_data['VanityAvatars'][guild.id][u_id][0]}\n\n"
                    )
                    show_list = True

            if not show_list:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="This server has no users with equipped vanities.",
                    color=0xff0000
                ))

            message.append("```")
            await ctx.send(embed=Embed(
                title="Server Equipped Vanities",
                description=''.join(message),
                color=0xff87a3,
            ))

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="This server has no users with equipped vanities.",
                color=0xff0000
            ))

    @bot_has_permissions(send_messages=True, embed_links=True)
    @has_permissions(manage_nicknames=True)
    @command(aliases=["manage", "user"])
    async def manage_user(self, ctx: Context, mode: str, user: Member):

        guild = ctx.guild
        author = ctx.author
        author_role = author.top_role
        
        if not (guild.id in self.bot.user_data["VanityAvatars"] and
                user.id in self.bot.user_data["VanityAvatars"][guild.id]):
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user has no information linked with this server.",
                color=0xff0000
            ))

        if user.id == author.id and author.id != guild.owner.id:
            return await ctx.send(embed=Embed(
                title="Error",
                description="You cannot use this command on yourself.",
                color=0xff0000
            ))

        if author.id != guild.owner.id and guild.id in self.bot.user_data["VanityAvatars"] and author.id \
                in self.bot.user_data["VanityAvatars"][guild.id] and \
                self.bot.user_data["VanityAvatars"][guild.id][author.id][2]:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot use this command because you were blocked "
                            "from using vanity avatars by another user.",
                color=0xff0000
            ))

        if user is None:
            return await ctx.send(embed=Embed(
                title="Error",
                description="That user is not a part of this server or does not exist.",
                color=0xff0000
            ))

        if author != guild.owner and author_role <= user.top_role:
            return await ctx.send(embed=Embed(
                title="Permission Error",
                description="You cannot manage this user because they have an "
                            "equal or higher role than you.",
                color=0xff0000
            ))

        if mode == "block":
            if self.bot.user_data["VanityAvatars"][guild.id][user.id][2]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already blocked.",
                    color=0xff0000
                ))

            else:
                self.bot.user_data["VanityAvatars"][guild.id][user.id][0] = None
                self.bot.user_data["VanityAvatars"][guild.id][user.id][2] = True
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User vanity avatar removed and blocked for this server.",
                    color=0xff87a3
                ))

        elif mode == "unblock":
            if not self.bot.user_data["VanityAvatars"][guild.id][user.id][2]:
                return await ctx.send(embed=Embed(
                    title="Error",
                    description="That user is already unblocked.",
                    color=0xff0000
                ))

            else:
                self.bot.user_data["VanityAvatars"][guild.id][user.id][2] = False
                return await ctx.send(embed=Embed(
                    title="Success",
                    description="User unblocked for this server.",
                    color=0xff87a3
                ))

        elif mode == "get_info":
            return await ctx.send(embed=Embed(
                title="Info",
                description=f"**Vanity status for user {str(user)}:**\n"
                            f"Vanity url: {self.bot.user_data['VanityAvatars'][guild.id][user.id][0]}\n"
                            f"Previous url: {self.bot.user_data['VanityAvatars'][guild.id][user.id][1]}\n"
                            f"Is blocked:  {self.bot.user_data['VanityAvatars'][guild.id][user.id][2]}",
                color=0xff87a3
            ))


def setup(bot: Bot):
    bot.add_cog(ModerationCommands(bot))
