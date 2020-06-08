
# Lib
from asyncio import sleep
from traceback import print_tb

# Site
from discord.errors import Forbidden
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


# EngravedID characters
I = {
    0:  " ",
    1:  " ",
    2:  " ",
    3:  " ",
    4:  " ",
    5:  " ",
    6:  " ",
    7:  " ",
    8:  " ",
    9:  " ",
    10: "​"
}
C = {
    " ": 0,
    " ": 1,
    " ": 2,
    " ": 3,
    " ": 4,
    " ": 5,
    " ": 6,
    " ": 7,
    " ": 8,
    " ": 9
}


class Events(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Transform message
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.id == self.bot.user.id:
            return

        # Check if the message is a command. Terminates the event if so, so the command can run.
        verify_command = await self.bot.get_context(msg)
        if verify_command.valid:
            self.bot.univ.Inactive = 0
            return

        # React with passion
        if self.bot.user.mentioned_in(msg):
            try:
                if msg.author.id == self.bot.owner.id:
                    await msg.add_reaction("💕")
                else:
                    await msg.add_reaction("👋")
            except Forbidden:
                pass

        if msg.guild is None:
            return

        # Self-Blacklisted
        try:
            for i in self.bot.univ.Blacklists[msg.author.id][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.univ.Blacklists[msg.author.id][0]:
                if msg.channel.id == i:
                    return

        except KeyError:
            pass

        # Server-Blacklisted
        try:
            for i in self.bot.univ.ServerBlacklists[msg.guild.id][1]:
                if msg.content.startswith(i):
                    return

            for i in self.bot.univ.ServerBlacklists[msg.guild.id][0]:
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
            if msg.author.id in self.bot.univ.VanityAvatars[msg.guild.id].keys() and \
                    not msg.author.bot and \
                    self.bot.univ.VanityAvatars[msg.guild.id][msg.author.id][0]:

                EngravedID_encode = list()
                for i in str(msg.author.id):
                    EngravedID_encode.append(I[int(i)])
                EngravedID_encode.append(I[10])
                EngravedID = ''.join(EngravedID_encode)

                if msg.content != "":
                    new_content = f"{msg.content}  {EngravedID}"
                else:
                    new_content = I[10] + EngravedID

                try:
                    await msg.delete()
                except Forbidden:
                    await msg.author.send(
                        f"Your message couldn't be transformed because it is missing 1 or more permissions listed in "
                        f"`{self.bot.command_prefix}help permissions`.\nIf you keep getting this error, remove your "
                        f"vanity avatar or blacklist the channel you are trying to use it in.\nThis error my also be "
                        f"a false alarm. Just try again."
                    )

                    del start
                    return

                try:
                    dummy = await msg.channel.create_webhook(name=msg.author.display_name)
                    await dummy.send(
                        new_content,
                        files=AttachmentFiles,
                        avatar_url=self.bot.univ.VanityAvatars[msg.guild.id][msg.author.id][0]
                    )

                    stop = default_timer()
                    await dummy.delete()

                except Forbidden:
                    await msg.author.send(
                        f"Your message couldn't be transformed because it is missing 1 or more permissions listed in "
                        f"`{self.bot.command_prefix}help permissions`.\nIf you keep getting this error, remove your "
                        f"vanity avatar or blacklist the channel you are using it in.\nThis error my also be a false "
                        f"alarm. Just try again."
                    )

                    del start
                    return

                comptime = round(stop - start, 3)
                print(
                    f"Last message response time: {comptime} seconds from user \"{msg.author}\"."
                )

                self.bot.univ.LatestRS = comptime
                self.bot.univ.Inactive = 0

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

    # Deleting/Enquring a message
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
        except Exception as e:
            print("[Error in event \"on_reaction_add\"]", e)
            return

        if reaction.guild is None:
            return

        if str(reaction.emoji) == "❌" and \
                reaction.message.author.bot and \
                reaction.message.author.discriminator == "0000":
            try:
                EngravedID_decode = list(reaction.message.content[-19:])
                EngravedID_decode.pop()

                EngravedID_decode_part = []
                for i in EngravedID_decode:
                    EngravedID_decode_part.append(str(C[i]))

                EngravedID = ''.join(EngravedID_decode_part)
                EngravedID = int(EngravedID)
                identification = await self.bot.fetch_user(EngravedID)
            except Exception as e:
                print("[Error in event \"on_raw_reaction_add\"]", e)
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
                await user.send("That's not your message.\nThe reaction was left unchanged.")

        if str(reaction.emoji) == "❓" and \
                reaction.message.author.bot and \
                reaction.message.author.discriminator == "0000":
            try:
                EngravedID_decode = list(reaction.message.content[-19:])
                EngravedID_decode.pop()

                EngravedID_decode_part = []
                for i in EngravedID_decode:
                    EngravedID_decode_part.append(str(C[i]))

                EngravedID = ''.join(EngravedID_decode_part)
                EngravedID = int(EngravedID)
                identification = await self.bot.fetch_user(EngravedID)
            except Exception as e:
                print("[Error in event \"on_raw_reaction_add\"]", e)
                return

            await user.send(
                f'Unsure who that was?\nTheir username is \"'
                f'{identification.name}#{identification.discriminator}\"'
                f'.\nThe reaction was left unchanged.'
            )
        else:
            return

    # Guild Count change notifications
    # --------------------------------------------------------------------------------------------------------------------------
    @Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.owner.send(f"Joined server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        print(f"Joined server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")

    @Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.owner.send(f"Left server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")
        print(f"Left server \"{guild.name}\". Now in {len(self.bot.guilds)} servers.")

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
                await msg.author.send \
                    (f"Command \"{supposed_command}\" doesn't exist. Your message was still transformed if allowed.")

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
            print_tb(error)



def setup(bot: Bot):
    bot.add_cog(Events(bot))
