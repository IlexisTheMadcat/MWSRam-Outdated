

class Moderation_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #--------------------------------------------------------------------------------------------------------------------------
    @commands.command(aliases=["s_bl"])
    @commands.bot_has_permissions(send_messages=True)
    @commands.has_permissions(manage_channels=True)
    async def server_blacklist(self, ctx, mode, item=None):
        msg = ctx.message
        if msg.guild is None:
            await msg.channel.send("This command cannot be used in a DM channel. Consider using it in a private channel in one of your servers.")
            return

        channeladd = ["channel-add", "ch-a"]
        channelremove = ["channel-remove", "ch-r"]
        prefixadd = ["prefix-add", "pf-a"]
        prefixremove = ["prefix-remove", "pf-r"]

        if (item is None) and (mode in channeladd or mode in channelremove):
            item = str(msg.channel.id)
        
        if mode in channeladd:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")

            try:
                item = int(item)
            except ValueError:
                await msg.channel.send(f"`channel` needs to be a number and proper channel ID. You can also #mention the channel.\nSee `{BOT_PREFIX}help Commands` under `{BOT_PREFIX}blacklist` to see how to get channel ID.")
                return
            else:
                try:
                    channel = await bot.fetch_channel(item)
                except discord.errors.NotFound:
                    await msg.channel.send(f"No channel with that ID exists.\nSee `{BOT_PREFIX}help commands` under `{BOT_PREFIX}blacklist` to see how to get channel IDs.\nYou can also #mention the channel.")
                else:
                    if channel not in msg.guild.channels:
                        await ctx.send("The channel has to be in this server. I wouldn't just let you cheese your friends like that in another server.")
                        return
                    
                    if msg.guild.id not in univ.ServerBlacklists.keys():
                        univ.ServerBlacklists[msg.guild.id] = ([],[])

                    if item not in univ.ServerBlacklists[msg.guild.id][0]:
                        univ.ServerBlacklists[msg.guild.id][0].append(item)
                        await msg.channel.send(f'Channel "{channel.name}" in server "{channel.guild.name}" was blacklisted for this server.\nYou can still use bot commands there.')
                        print(f'+ Channel "{channel.name}" in server "{channel.guild.name}" was server-blacklisted.')
                    else:
                        await msg.channel.send("You already blacklisted that channel for this server.")
                    return

        elif mode in channelremove:
            if item.startswith("<#") and item.endswith(">"):
                item = item.replace("<#", "")
                item = item.replace(">", "")
                
            try:
                item = int(item)
            except ValueError:
                await msg.channel.send(f"`channel` needs to be a number and proper channel ID.\nType and enter `{BOT_PREFIX}see_blacklists` and find the __ID__ of the channel you want to remove from that list.\nYou can also \\#mention the channel.")
                return
            
            else:
                if msg.guild.id in univ.ServerBlacklists.keys():
                    if item in univ.ServerBlacklists[msg.guild.id][0]:
                        univ.ServerBlacklists[msg.guild.id][0].remove(item)
                        channel = await bot.fetch_channel(item)
                        await msg.channel.send(f'Channel "{channel.name}" in server "{channel.guild.name}" was removed from your server\'s blacklist.')
                        print(f'- Channel "{channel.name}" in server "{channel.guild.name}" was removed from server-blacklisted items.')
                    else:
                        await msg.channel.send(f"That channel isn't in your server's blacklist.\nType `{BOT_PREFIX}see_server_blacklists` to see your blacklisted channels and prefies.")
                        return
                else:
                    await msg.channel.send("You have nothing to remove from your server's blacklist yet.")
                    return

        elif mode in prefixadd:
            if len(item) > 5:
                await msg.channel.send("Your prefix can only be up to 5 characters long.")
                return

            if item.startswith(BOT_PREFIX):
                await msg.channel.send("For protection, you cannot blacklist this bot's prefix.")
                return
        
            if msg.guild.id not in univ.ServerBlacklists.keys():
                univ.ServerBlacklists[msg.guild.id] = ([],[])

            if item not in univ.ServerBlacklists[msg.guild.id][1]:
                univ.ServerBlacklists[msg.guild.id][1].append(item)
                await msg.channel.send(f'Added "{item}" to blacklisted prefixes for this server.')
                print(f'+ Added "{item}" to blacklisted prefixes for user \"{msg.author.name+"#"+msg.author.discriminator}\"')
            else:
                await msg.channel.send("That prefix is already blacklisted for this server.")

        elif mode in prefixremove:
            if msg.guild.id in univ.ServerBlacklists.keys():
                if item in univ.ServerBlacklists[msg.guild.id][1]:
                    univ.ServerBlacklists[msg.guild.id][1].remove(item)
                    await msg.channel.send(f'Removed "{item}" from blacklisted prefixes for this server.')
                    print(f'- Removed "{item}" from blacklisted prefixes for user \"{msg.author.name+"#"+msg.author.discriminator}\".')
                else:
                    await msg.channel.send(f"`{item}` isn't in your blacklist.\nType `{BOT_PREFIX}see_server_blacklists` to see your blacklisted channels and prefixes.")
                    return
            else:
                await msg.channel.send("You have nothing to remove from your blacklist.")
                return

        else:
            await msg.channel.send(f'Invalid mode passed: `{mode}`; Refer to `{BOT_PREFIX}help commands blacklist`.')

    #--------------------------------------------------------------------------------------------------------------------------
    @commands.command(aliases=["see_s_bl"])
    @commands.bot_has_permissions(send_messages=True)
    async def see_server_blacklists(self, ctx):
        msg = ctx.message
        if msg.guild.id in univ.ServerBlacklists.keys():
            message_part = []

            async def render():
                if univ.ServerBlacklists[msg.guild.id] == ([], []):
                    message_part.append("You haven't blacklisted anything for this server yet.")
                    return True
                
                message_part.append("Here are this server's blacklisted items:\n")
                if not len(univ.ServerBlacklists[msg.guild.id][0]) == 0:
                    message_part.append("**Channels:**\n")
                    for i in univ.ServerBlacklists[msg.guild.id][0]:
                        try:
                            channel = await bot.fetch_channel(i)
                        except discord.errors.NotFound:
                            univ.ServerBlacklists[msg.guild.id][0].remove(i)
                            return False
                        else:
                            message_part.append(f"-- Name: {channel.mention}; ID: {channel.id}\n")
                            
                    return True
    
            while True:
                result = await render()
                if result is False:
                    message_part = []
                    message_part.append("Here are your blacklisted items:\n```")
                    continue
                else:
                    break

            if not len(univ.ServerBlacklists[msg.guild.id][1]) == 0:
                message_part.append("**Prefixes:**\n")
                for i in univ.ServerBlacklists[msg.guild.id][1]:
                    message_part.append(f'-- `"{i}"`\n')

            message_full = ''.join(message_part)
            await msg.channel.send(message_full)
        else:
            await msg.channel.send("You haven't blacklisted anything for this server yet.")

        print(f'[] Sent server-blacklisted items for user \"{msg.author.name+"#"+msg.author.discriminator}\" in server \"{msg.guild.name}\".')

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def list(self, ctx):
        message = []
        if ctx.guild.id in univ.VanityAvatars.keys() and univ.VanityAvatars[ctx.guild.id] != {}:
            async with ctx.typing():
                message.append("Here are users using vanities in this server; The list may contain members who have left:\n```")
                for i in univ.VanityAvatars[ctx.guild.id].keys():
                    user = await bot.fetch_user(i)
                    message.append(f"{user.name}#{user.discriminator} - URL: {univ.VanityAvatars[ctx.guild.id][i][1]}\n")

                message.append("```")
                await ctx.send(f"{''.join(message)}")
        else:
            await ctx.send("This server has no users with equiped vanities.")
            return
    
    @commands.command(aliases=["manage", "user"])
    @commands.bot_has_permissions(send_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def manage_user(self, ctx, mode, user: discord.User):
        msg = ctx.message
        invoker_member = await ctx.guild.fetch_member(ctx.author.id)
        user_member = await ctx.guild.fetch_member(user.id)
        invoker_role = invoker_member.top_role
        user_role = user_member.top_role
        
        if msg.guild.id in univ.VanityAvatars.keys() and user.id in univ.VanityAvatars[msg.guild.id].keys():
            if user.id == ctx.author.id and not ctx.author == ctx.guild.owner:
                await ctx.send("You cannot use this command on yourself.")
                return

            if not invoker_member == ctx.guild.owner:
                if msg.guild.id in univ.VanityAvatars and msg.author.id in univ.VanityAvatars[msg.guild.id] and univ.VanityAvatars[msg.guild.id][msg.author.id][2] == True:
                    await ctx.send("You cannot use this command because you were blocked from using vanity avatars by another user.")
                    return

            if user_member is None:
                await ctx.send("That user is not a part of this server.")
                return

            if not invoker_member == ctx.guild.owner:
                if invoker_role < user_role:
                    await ctx.send("You cannot block this user because they have a higher role than you.")
                    return
            
            if mode == "block":
                if univ.VanityAvatars[msg.guild.id][user.id][2] == True:
                    await ctx.send("That user is already blocked.")
                    return
                else:
                    univ.VanityAvatars[msg.guild.id][user.id][0] = None
                    univ.VanityAvatars[msg.guild.id][user.id][2] = True
                    await ctx.send("User avatar removed and blocked for this server.")
                    return
                    
            elif mode == "unblock":
                if univ.VanityAvatars[msg.guild.id][user.id][2] == False:
                    await ctx.send("That user is already unblocked.")
                    return
                else:
                    univ.VanityAvatars[msg.guild.id][user.id][2] = False
                    await ctx.send("User unblocked for this server.")
                    return
        else:
            await ctx.send("That user has no information linked with this server.")
            return
                    
    