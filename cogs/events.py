
# Lib
from re import findall
from asyncio.exceptions import TimeoutError
from contextlib import suppress

# Site
from discord import Embed, Status
from discord.message import Message
from discord.utils import get
from discord.errors import Forbidden, HTTPException, NotFound
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import (
    BotMissingPermissions,
    CommandNotFound,
    MissingPermissions,
    MissingRequiredArgument,
    NotOwner, BadArgument
)
from NHentai import NHentai
#https://pypi.org/project/NHentai-API/

# Local
from utils.utils import (
    get_engraved_id_from_msg as get_eid, 
    create_engraved_id_from_user as create_eid
)

class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Transform message
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_message(self, msg: Message):
        if msg.channel.id == self.bot.listening_channel:
            print(f"[Recieve] ----- Message ----- |\n[] {msg.author.display_name} ({msg.author})\n{msg.content if msg.content != '' else '[No Content]'}")
            if msg.attachments:
                for x, e in enumerate(msg.attachments, 1):
                    print(f"Attachment {x}: {e.url}")
                    
            print("\n")
            
        if msg.author.bot:
            return

        if msg.author.id == 726313554717835284:
            ids = msg.content.split(";")
            voter = int(ids[0])
            voted_for = int(ids[1])

            if voted_for == self.bot.user.id:
                user = await self.bot.fetch_user(voter)
                try:
                    await user.send(
                        "Thanks for voting!"
                    )
                
                except HTTPException or Forbidden:
                    print(f"[❌] User \"{user}\" voted for \"{self.bot.user}\". DM Failed.")
                else:
                    print(f"[] User \"{user}\" voted for \"{self.bot.user}\".")

                return

        # Check if the message is a command. Terminates the event if so, so the command can run.
        verify_command = await self.bot.get_context(msg)
        if verify_command.valid:
            self.bot.inactive = 0
            return

        # Support can be run through DMs
        if msg.guild is None and msg.author.id != self.bot.owner_ids[0]:
            if msg.content.startswith("> "):
                if msg.author.id not in self.bot.config['muted_dms']:
                    if msg.author.id in self.bot.waiting:
                        await msg.channel.send(":clock9: Please wait, you already have a question open.\n"
                                                "You'll get a response from me soon.")

                        return

                    dev_guild = self.bot.get_guild(699399549218717707)  # Developer's Guild
                    user = dev_guild.get_member(self.bot.owner_ids[0])
                    if user.status == Status.dnd:
                        await msg.channel.send(":red_circle: The developer currently has "
                                                "Do Not Disturb on. Please try again later.")
                        return
                    elif user.status == Status.idle:
                        conf = await msg.channel.send(":orange_circle: The developer is currently idle, "
                                                        "are you sure you want to send?\n"
                                                        "Sending `Yes` will send the message, but you *may* not get a response.\n"
                                                        "(`Yes`, `No`)")

                        def check(m):
                            return m.content.lower() in ["yes", "no"]
                        try:
                            message = await self.bot.wait_for("message", timeout=20, check=check)
                        except TimeoutError:
                            await conf.edit(":orange_circle: The developer is currently idle, "
                                            "are you sure you want to send?\n"
                                            "Sending `Yes` will send the message, but you *may* not get a response.\n"
                                            "(`Yes`, `No`)")
                        else:
                            if message.content == "no":
                                return await conf.edit(":orange_circle: The developer is currently idle.\n"
                                                        "Please try again later.")

                            elif message.content == "yes":
                                await conf.delete()

                    status_msg = await msg.channel.send(":clock9: "
                                                        "I sent your message to the developer.\n"
                                                        "Please stand by for a response or "
                                                        "until **this message is edited**...\n")

                    self.bot.waiting.append(msg.author.id)

                    embed = Embed(color=0x32d17f)
                    embed.title = f"Message from user {msg.author} (ID: {msg.author.id}):"
                    embed.description = f"{msg.content}\n\n" \
                                        f"Replying to this DM **within 120 seconds** " \
                                        f"after accepting **within 10 minutes** " \
                                        f"will relay the message back to the user."

                    dm = await user.send(content="**PENDING**", embed=embed)
                    await dm.add_reaction("✅")
                    await dm.add_reaction("❎")

                    def check(sreaction, suser):
                        if self.bot.thread_active:
                            self.bot.loop.create_task(
                                reaction.channel.send("There is already an active thread running...\n "
                                                        "Please finish the **`ACTIVE`** one first."))
                            return False
                        else:
                            return sreaction.message.id == dm.id and \
                                str(sreaction.emoji) in ["✅", "❎"] and \
                                suser == user
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=600, check=check)
                    except TimeoutError:
                        await dm.edit(content="**TIMED OUT**")
                        await status_msg.edit(content=":x: "
                                                        "The developer is unavailable right now. Try again later.")
                        return
                    else:
                        if str(reaction.emoji) == "❎":
                            await dm.edit(content="**DENIED**")
                            await status_msg.edit(content=":information_source: The developer denied your message. "
                                                            "Please make sure you are as detailed as possible.")
                            return
                        elif str(reaction.emoji) == "✅":
                            await dm.edit(content="**ACTIVE**")
                            await status_msg.edit(content=":information_source: "
                                                            "The developer is typing a message back...")
                            self.bot.thread_active = True
                            pass

                    def check(message):
                        return message.author == user and message.channel == dm.channel
                    while True:

                        try:
                            response = await self.bot.wait_for("message", timeout=120, check=check)
                        except TimeoutError:
                            conf = await user.send(":warning: Press the button below to continue typing.")
                            await conf.add_reaction("🔘")

                            def conf_button(b_reaction, b_user):
                                return str(b_reaction.emoji) == "🔘" and b_user == user \
                                        and b_reaction.message.channel == dm.channel

                            try:
                                await self.bot.wait_for("reaction_add", timeout=10, check=conf_button)
                            except TimeoutError:
                                await conf.delete()
                                await dm.edit(content="**TIMED OUT**")
                                await dm.channel.send("You timed out. "
                                                        "The user was notified that you are not available right now.")

                                self.bot.waiting.remove(msg.author.id)
                                self.bot.thread_active = False
                                await status_msg.edit(content=":information_source: "
                                                                "The developer timed out on typing a response. "
                                                                "Please ask at a later time.\n"
                                                                "You may also join the support server here: "
                                                                "https://discord.gg/j2y7jxQ")
                                
                            else:
                                await conf.delete()
                                continue
                        else:
                            self.bot.waiting.remove(msg.author.id)
                            self.bot.thread_active = False
                            await dm.edit(content="**Answered**")
                            await dm.channel.send(":white_check_mark: Okay, message sent.")
                            await status_msg.edit(content=":white_check_mark: The developer has responded.")
                            await msg.channel.send(f":newspaper: Response from the developer:\n{response.content}")
                            
                else:
                    await msg.channel.send("You've been muted by the developer, "
                                            "so you cannot send anything.\n"
                                            "If you believe you were muted by mistake, "
                                            "please join the support server:\n"
                                            "https://discord.gg/j2y7jxQ\n\n"
                                            "**Note that spamming will get you banned without hesitation.**")

            else:
                await msg.channel.send("Please start your message with "
                                        "\"`> `\" "
                                        "to ask a question or send compliments.\n"
                                        "This is the markdown feature to create quotes.",
                                        delete_after=5)
            
            return

                    
        if msg.content.lower() in ["pspsp", "pspsps", "pspspsp", "pspspsps"]:
            emoji_ = get(msg.guild.emojis, name="ch_40hara_hide")
            await msg.channel.send(str(emoji_))
            
            return

        if msg.channel.category.id in \
            [740663474568560671, 740663386500628570]:
            if 741431440490627234 in [r.id for r in msg.author.roles]:
                await msg.delete()
                await msg.channel.send(
                    content=msg.author.mention,
                    embed=Embed(
                        title="Muted!", 
                        description="You are currently muted. You cannot upload here at this time.\n",
                        color=0x32d17f),
                    delete_after=10
                )
                return
            if msg.attachments == []:
                await msg.delete()
                await msg.channel.send(
                    content=msg.author.mention,
                    embed=Embed(
                        title="Media", 
                        description="If you want to send a message, please do so in one of the Discussion channels.\n"
                                    "The best place to do that is in <#742571100009136148>.",
                        color=0x32d17f),
                    delete_after=10
                )
            elif msg.attachments != []:
                await msg.add_reaction("⬆")
            
            return
        
        # Search for links and reformat
        new_content = msg.content
        link_findings1 = findall("https://discordapp.com/channels/740662779106689055/[0-9]{18}/[0-9]{18}", new_content)
        for i in link_findings1:
            new_content = new_content.replace(i, "")
        
        link_findings2 = findall("https://discord.com/channels/740662779106689055/[0-9]{18}/[0-9]{18}", new_content)
        for i in link_findings2:
            new_content = new_content.replace(i, "")
        
        nhentai_codes1 = findall("n[0-9]{6}", new_content)
        for i in nhentai_codes1:
            new_content = new_content.replace(i, "")
        
        nhentai_codes2 = findall("n[0-9]{5}", new_content)
        for i in nhentai_codes2:
            new_content = new_content.replace(i, "")
        
        
        link_findings = link_findings1+link_findings2
        nhentai_codes = nhentai_codes1+nhentai_codes2

        jumps = []
        mentions = []

        if link_findings:

            for link in link_findings:
                link_parts = link.split("/")
                channel = self.bot.get_channel(int(link_parts[5]))
                if not channel:
                    continue
                
                try:
                    message = await channel.fetch_message(int(link_parts[6]))
                except NotFound:
                    continue
                
                new_content = new_content.replace(link, "")

                jumps.append(f"By: {message.author.mention} | {':warning:' if channel.is_nsfw() else ':white_check_mark:'} [\[Jump to message\]]({link})")
                mentions.append(message.author.mention)

        if nhentai_codes and msg.channel.is_nsfw():
            jumps.append("\nNhentai codes attached:")
            for x, i in enumerate(nhentai_codes):
                code = nhentai_codes[x].strip("n")

                nhentai = NHentai()
                doujin: dict = nhentai._get_doujin(id=code)
                if doujin:
                    jumps.append(f"[{code} | {doujin['title']}](https://nhentai.net/g/{code}/)")
                    new_content = new_content.replace(f"n{code}", "")

        UID_findings = findall("<@![0-9]{18}>", new_content)
        for i in UID_findings:
            mentions.append(i)

        if jumps:
            jumps = list(set(jumps))
            mentions = list(set(mentions))

            jumps.reverse()
            mentions.reverse()

            while msg.author.mention in mentions: 
                mentions.remove(msg.author.mention)
            
            jumps = "\n".join(jumps)
            mentions = ", ".join(mentions)

            new_content = new_content.strip("\n")

            eid_string = create_eid(msg.author.id)
            await msg.delete()
            conf = await msg.channel.send(
                content=f"{mentions}",
                embed=Embed(
                description=f"{jumps}\n"
                            f"{'ーーーーーー' if new_content != '' else ''}\n"
                            f"{new_content}",  # \n\n{self.bot.user.mention}: React with :x: to delete this message.",
                author={
                    "name":msg.author.display_name,
                    "icon_url":msg.author.avatar_url
                },
                color=0x32d17f
            ).set_author(
                name=msg.author.display_name,
                icon_url=msg.author.avatar_url
            ))
            if mentions:
                await conf.edit(
                    content=f"{mentions}{eid_string}"
                )
            # await conf.add_reaction("❌")
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        class Reaction:
            def __init__(self):
                pass

        try:
            reaction = Reaction()
            reaction.emoji = payload.emoji
            reaction.channel = self.bot.get_channel(payload.channel_id)
            reaction.message = await reaction.channel.fetch_message(payload.message_id)
            reaction.guild = self.bot.get_guild(payload.guild_id)
            user = self.bot.get_user(payload.user_id)
        except Exception as e:
            print(f"[Error in \"on_raw_reaction_add\"] {e}")
            return

        if reaction.guild is None:
            return
        
        if user.bot:
            return
        
        '''
        if reaction.message.author.id == self.bot.user.id and \
            str(reaction.emoji) == "❌":

            if self.bot.get_user(get_eid(reaction.message.content)) == user.id:
                await reaction.message.delete()
        '''

        if reaction.message.channel.category.id in \
            [740663386500628570, 740663474568560671]:
            if str(reaction.emoji) == "⬆" and \
                user.id == reaction.message.author.id:
                member = reaction.message.guild.get_member(user.id)
                await reaction.message.remove_reaction(reaction.emoji, member)
                await reaction.message.channel.send(
                    content=user.mention,
                    embed=Embed(
                        title="Upvote", 
                        description="You can't upvote your own post!",
                        color=0x32d17f),
                    delete_after=5
                )


    # Guild Count change notifications
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_guild_update(self, pre, post):
        if pre.id == 740662779106689055 and \
            pre.icon_url != post.icon_url:
            channel = self.bot.get_channel(742211981720813629)
            await channel.send(post.icon_url)


    # Errors
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        if not isinstance(error, CommandNotFound):
            with suppress(Forbidden):
                await ctx.message.add_reaction("❌")
            
        if not self.bot.config['debug_mode']:
            msg = ctx.message
            em = Embed(title="Error", color=0xff0000)
            if isinstance(error, BotMissingPermissions):
                em.description = f"This bot is missing one or more permissions listed in `{self.bot.command_prefix}help`" \
                                 f"under `Required Permissions`, " \
                                 f"or you are trying to use the command in a DM channel."

            elif isinstance(error, MissingPermissions):
                em.description = f"You are missing a required permission, or you are trying to use the command in a DM channel.\n" \
                                 f"Check `{self.bot.command_prefix}help commands` and look by the command you tried to use." \

            elif isinstance(error, NotOwner):
                em.description = "That command is not listed in the help menu and is to be used by the owner only."

            elif isinstance(error, MissingRequiredArgument):
                em.description = f"\"{error.param.name}\" is a required argument for command " \
                                 f"\"{ctx.command.name}\" that is missing."

            elif isinstance(error, BadArgument):
                em.description = f"You didn't type something correctly. Details below:\n" \
                                 f"{error}"

            elif isinstance(error, CommandNotFound):
                supposed_command = msg.content.split()[0]
                em.description = f"Command \"{supposed_command}\" doesn't exist. Your message was still transformed if allowed."

            else:
                if ctx.command.name:
                    em.description = f"`[Error in command \"{ctx.command.name}\"] {error}`\n" \
                                     f"If you keep getting this error, let the developer know by " \
                                     f"sending a DM here with a quoted message. " \
                                     f"Don't hesitate, he's open for DMs right now!\n\n" \
                                     f"For example:\n" \
                                     f"> An error occurred and I need help! <explain what happened please>\n" \
                                     f"Please detail your message with what you were trying to do, " \
                                     f"or the message will likely be declined or ignored."

                    if self.bot.config['error_log_channel'] is None:
                        print(f"[Error in command \"{ctx.command.name}\"] {error}")
                    else:
                        print(f"[Error in command \"{ctx.command.name}\"] {error}")
                        error_channel = self.bot.get_channel(self.bot.config['error_log_channel'])
                        if error_channel:
                            await error_channel.send(embed=Embed(title="Error", description=f"`[Error in command \"{ctx.command.name}\"] {error}`", color=0xff0000))
                else:
                    if self.bot.config['error_log_channel'] is None:
                        print(f"[Error outside of command] {error}")
                    else:
                        print(f"[Error outside of command] {error}")
                        error_channel = self.bot.get_channel(self.bot.config['error_log_channel'])
                        if error_channel:
                            await error_channel.send(embed=Embed(title="Error (likely critical)", description=f"`[Error outside of command] {error}`", color=0xff0000))

            await ctx.author.send(embed=em)

        else:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
