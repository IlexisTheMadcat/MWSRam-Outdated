
# Lib
from asyncio.exceptions import TimeoutError
from asyncio import sleep
from contextlib import suppress
from typing import List

# Site
from discord import Webhook, Embed, Status
from discord.errors import Forbidden, NotFound, HTTPException
from discord.utils import get
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import (
    BotMissingPermissions,
    CommandNotFound,
    MissingPermissions,
    MissingRequiredArgument,
    NotOwner
)
from discord.message import Message
from timeit import default_timer

# Local
from utils.classes import Bot
from utils.utils import (
    EID_FROM_INT,
    create_engraved_id_from_user,
    get_engraved_id_from_msg,
)


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Transform message
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_message(self, msg: Message):
        # Pre-event Checks
        # if msg.guild is None:
        #     return

        if msg.author.id == self.bot.user.id:
            return

        if msg.author.id == 726313554717835284:
            ids = msg.content.split(";")
            voter = int(ids[0])
            voted_for = int(ids[1])

            if voted_for == self.bot.user.id:  # append `or 687427956364279873` for testing instance
                user = await self.bot.fetch_user(voter)
                try:
                    await user.send(
                        "Thanks for voting! You will now have access to the following commands shortly for 12 hours:\n"
                        "```\n"
                        f"{self.bot.command_prefix}add_to_closet\n"
                        f"{self.bot.command_prefix}remove_from_closet\n"
                        f"{self.bot.command_prefix}rename_closet_entry\n"
                        f"{self.bot.command_prefix}see_closet\n"
                        f"{self.bot.command_prefix}preview_closet_entry\n"
                        f"```\n"
                        f"These commands allow you to store favorite vanity avatars "
                        f"and use them anywhere. You can only hold up to 10.\n"
                        f"For help on the usage of each command, "
                        f"enter `{self.bot.command_prefix}help commands <command name>`.")

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

        if msg.guild is None:
            if msg.author.id != self.bot.owner_ids[0]:
                if msg.content.startswith("> "):
                    if msg.author.id not in self.bot.muted_dms:
                        if msg.author.id in self.bot.waiting:
                            await msg.channel.send(":clock9: Please wait, my master may be typing...\n"
                                                   "You'll get a response from me soon.")

                            return

                        dev_guild = self.bot.get_guild(699399549218717707)  # Developer's Guild
                        user = dev_guild.get_member(self.bot.owner_ids[0])
                        if user.status == Status.dnd:
                            await msg.channel.send(":red_circle: The developer currently has "
                                                   "Do Not Disturb on. Please try again later.")
                            return

                        self.bot.waiting.append(msg.author.id)

                        embed = Embed(color=0xff87a3)
                        embed.title = f"Message from user {msg.author} (ID: {msg.author.id}):"
                        embed.description = f"{msg.content}\n\n" \
                                            f"Replying to this DM within 120 seconds will " \
                                            f"relay the message back to the user."

                        dm = await user.send(embed=embed)

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
                                    await dm.channel.send("You timed out. "
                                                          "The user was notified that you are not available right now.")

                                    self.bot.waiting.remove(msg.author.id)
                                    await msg.channel.send("The developer failed to respond. "
                                                           "Please ask at a later time.\n"
                                                           "You may also join the support server here: "
                                                           "https://discord.gg/j2y7jxQ")
                                    return
                                else:
                                    await conf.delete()
                                    continue
                            else:
                                self.bot.waiting.remove(msg.author.id)
                                await dm.channel.send(":white_check_mark: Okay, message sent.")
                                await msg.channel.send(f":newspaper: Response from the developer:\n{response.content}")
                                return
                    else:
                        await msg.channel.send("You've been muted by the developer, "
                                               "so you cannot send anything.\n"
                                               "If you believe you were muted by mistake, "
                                               "please join the support server:\n"
                                               "https://discord.gg/j2y7jxQ\n\n"
                                               "**Note that spamming will get you banned without hesitation.**")
                        return
                else:
                    await msg.channel.send("Please start your message with "
                                           "\"`> `\" "
                                           "to ask a question or send compliments.\n"
                                           "This is the markdown feature to create quotes.",
                                           delete_after=5)
                    return
            return

        # React with passion
        if self.bot.user.mentioned_in(msg):
            try:
                if msg.author.id in self.bot.owner_ids:
                    await msg.add_reaction("💕")
                else:
                    await msg.add_reaction("👋")
            except Forbidden:
                pass

        # Self-Blacklisted
        try:
            for i in self.bot.user_data["Blacklists"][msg.author.id][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.user_data["Blacklists"][msg.author.id][0]:
                if msg.channel.id == i:
                    return

        except KeyError:
            pass

        # Server-Blacklisted
        try:
            for i in self.bot.user_data["ServerBlacklists"][msg.guild.id][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.user_data["ServerBlacklists"][msg.guild.id][0]:
                if msg.channel.id == i:
                    return

        except KeyError:
            pass

        # Get attachments
        start = default_timer()
        AttachmentFiles = []
        for i in msg.attachments:
            try:
                dcfileobj = await i.to_file()
                AttachmentFiles.append(dcfileobj)
            except Exception as e:
                print("[Error while getting attachment]", e)
                continue

        try:
            if msg.author.bot and msg.author.discriminator == "0000":
                EngravedID = get_engraved_id_from_msg(msg.content)
                if self.bot.get_user(EngravedID):
                    with suppress(Forbidden):
                        await msg.add_reaction("❌")
                        await sleep(5)
                        with suppress(NotFound):
                            await msg.remove_reaction("❌", msg.guild.me)

            if msg.author.id in self.bot.user_data["VanityAvatars"][msg.guild.id].keys() and \
                    not msg.author.bot and \
                    self.bot.user_data["VanityAvatars"][msg.guild.id][msg.author.id][0]:

                EngravedID = create_engraved_id_from_user(msg.author.id)

                if msg.content != "":
                    new_content = f"{msg.content}  {EngravedID}"
                else:
                    new_content = EID_FROM_INT[10] + EngravedID

                bot_perms = msg.channel.permissions_for(msg.guild.me)
                if not all((
                    bot_perms.manage_messages,
                    bot_perms.manage_webhooks
                )):
                    await msg.author.send(
                        f"Your message couldn't be transformed because it is "
                        f"missing 1 or more permissions listed in "
                        f"`{self.bot.command_prefix}help` under `Required Permissions`.\n"
                        f"If you keep getting this error, remove your "
                        f"vanity avatar or blacklist the channel you are "
                        f"trying to use it in."
                    )

                    del start
                    return
                else:
                    await msg.delete()

                    if "webhooks" not in self.bot.user_data.keys():
                        self.bot.user_data["webhooks"] = {"channelID": "webhookID"}

                    if msg.channel.id not in self.bot.user_data["webhooks"]:
                        self.bot.user_data["webhooks"][msg.channel.id] = 0

                    webhooks: List[Webhook] = await msg.channel.webhooks()
                    webhook: Webhook = get(webhooks, id=self.bot.user_data["webhooks"].get(msg.channel.id))
                    if webhook is None:
                        webhook: Webhook = await msg.channel.create_webhook(name="Vanity Profile Pics")
                        self.bot.user_data["webhooks"][msg.channel.id] = webhook.id

                    await webhook.send(
                        new_content,
                        files=AttachmentFiles,
                        avatar_url=self.bot.user_data["VanityAvatars"][msg.guild.id][msg.author.id][0],
                        username=msg.author.display_name
                    )
                    self.bot.inactive = 0
                    stop = default_timer()

                comptime = round(stop - start, 3)
                print(
                    f"Last message response time: {comptime} seconds from user \"{msg.author}\"."
                )

                self.bot.LatestRS = comptime
                self.bot.inactive = 0

                if comptime > 3:
                    if self.bot.owner.id == msg.author.id:
                        await msg.author.send(
                            f"Your message took over 2 seconds to be transformed ({comptime} seconds)."
                        )
                    else:
                        await self.bot.owner.send(
                            f"Last message response time was over 2 seconds from user \"{msg.author}\" "
                            f"({comptime} seconds)."
                        )
                        await msg.author.send(
                            f"Your message took over 2 seconds to be transformed ({comptime} seconds). The owner "
                            f"was just notified about this delay.\nFeel free to mute me if I complain too much. "
                            f"Please note that it's harder for me to carry out media than pure text."
                        )

            else:
                return

        except KeyError:
            return

    # Deleting/Inquiring a message
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        class Reaction:
            def __init__(self):
                pass

        try:
            reaction = Reaction()
            reaction.emoji = payload.emoji
            reaction.channel = await self.bot.fetch_channel(payload.channel_id)
            reaction.message = await reaction.channel.fetch_message(payload.message_id)
            reaction.guild = await self.bot.fetch_guild(payload.guild_id)
            reaction.member = await reaction.guild.fetch_member(payload.user_id)
            user = await self.bot.fetch_user(payload.user_id)
        except Exception:
            return

        if reaction.guild is None:
            return

        if str(reaction.emoji) == "❌" and \
                reaction.message.author.bot and \
                reaction.message.author.discriminator == "0000":
            try:
                EngravedID = get_engraved_id_from_msg(reaction.message.content)
                identification = await self.bot.fetch_user(EngravedID)
            except Exception:
                return

            if identification == user:
                try:
                    await self.bot.http.delete_message(
                        reaction.channel.id,
                        reaction.message.id,
                        reason="Deleted on user request."
                    )
                except Forbidden:
                    await self.bot.http.remove_reaction(
                        reaction.channel.id,
                        reaction.message.id,
                        reaction.emoji,
                        reaction.member.id
                    )
                    await user.send('`If you want to do that, this bot needs the "Manage Messages" permission.`')
            else:
                if user != self.bot.user:
                    with suppress(Forbidden):
                        await user.send(f"That's not your message to delete. Ask {str(user)} to delete it.\nThe reaction was left unchanged.")

        if str(reaction.emoji) == "❓" and \
                reaction.message.author.bot and \
                reaction.message.author.discriminator == "0000":
            try:
                EngravedID = get_engraved_id_from_msg(reaction.message.content)
                identification = await self.bot.fetch_user(EngravedID)
            except Exception as e:
                print("[Error in event \"on_raw_reaction_add\"]", e)
                return

            await user.send(
                f'Unsure who that was?\nTheir username is \"{str(identification)}\".\n'
                f'The reaction was left unchanged.'
            )
        else:
            return

    # Guild Count change notifications
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.owner.send(f"Joined server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        print(f"Joined server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        if guild.id not in self.bot.user_data["VanityAvatars"]:
            self.bot.user_data["VanityAvatars"][guild.id] = {}

    @Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.owner.send(f"Left server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        print(f"Left server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        if guild.id in self.bot.user_data["VanityAvatars"] and self.bot.user_data["VanityAvatars"][guild.id]:
            self.bot.user_data["VanityAvatars"].pop(guild.id)

    # Errors
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        if not self.bot.debug_mode:
            msg = ctx.message
            if isinstance(error, BotMissingPermissions):
                await msg.author.send(
                    f"This bot is missing one or more permissions listed in "
                    f"`{self.bot.command_prefix}help permissions`."
                )

            elif isinstance(error, MissingPermissions):
                await msg.author.send(f"You are missing a required permission!")

            elif isinstance(error, NotOwner):
                await msg.author.send(
                    "That command is not listed in the help menu and is to be used by the owner only."
                )

            elif isinstance(error, MissingRequiredArgument):
                await msg.author.send(f"\"{error.param.name}\" is a required argument that is missing.")

            elif isinstance(error, CommandNotFound):
                supposed_command = msg.content.split()[0]
                await sleep(1)
                await msg.author.send(
                    f"Command \"{supposed_command}\" doesn't exist. Your message was still transformed if allowed."
                )

            else:
                if ctx.command.name:
                    await ctx.author.send(
                        f"[Error in command \"{ctx.command.name}\"]  {error}\n"
                        f"If you keep getting this error, let the developer know!"
                    )
                    print(f"[Error in command \"{ctx.command.name}\"] ", error)
                else:
                    await ctx.author.send(
                        f"[Error outside of command] {error}\n"
                        f"If you keep getting this error, let the developer know!"
                    )
                    print("[Error outside of command]", error)
        else:
            raise error


def setup(bot: Bot):
    bot.add_cog(Events(bot))
