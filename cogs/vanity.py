
# Lib

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command
from discord.user import User

# Local
from utils.classes import Bot


class VanityCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vanities = bot.user_data["VanityAvatars"]
        self.closets = bot.user_data["Closets"]

    @command(aliases=["set"])
    @bot_has_permissions(manage_webhooks=True)
    async def set_vanity(self, ctx: Context, url: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel
        msg = ctx.message

        if not guild:
            return await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )

        if guild.id in self.vanities and author.id in self.vanities[guild.id] and self.vanities[guild.id][author.id][2]:
            return await ctx.send(
                "You are currently blocked from using vanity avatars in this "
                "server. Contact a moderator with the `Manage Messages` "
                "permission to unblock you."
            )
        
        try:
            if url in self.closets[author.id]:
                check = await self.bot.get_user_vote(author.id)

                if not check:
                    return await ctx.send(
                        f"Closets are vote-locked. Please go to "
                        f"{self.bot.dbl_vote} and click on 'Vote'.\nThen come "
                        f"back and try again. If you just now voted, wait a "
                        f"few moments."
                    )

                elif check:
                    url = self.closets[author.id][url]
                    await ctx.send("Used closet entry.")

        except KeyError or IndexError:
            pass
        
        if url is None:
            try:
                url = msg.attachments[0].url
                await ctx.send("Used attachment...")

            except IndexError:
                try:
                    url = self.vanities[guild.id][author.id][1]

                    if url is None:
                        raise KeyError

                    else:
                        await ctx.send("Used previous avatar...")

                except KeyError:
                    await ctx.send("Not enough parameters!")
                    return

        try:
            dummy = await chan.create_webhook(name=author.display_name)
            await dummy.send(
                f"{self.bot.user.display_name}: Vanity successfully created.\nSend a message in an unblocked channel to test it out!‎‎",
                avatar_url=url
            )
            await dummy.delete()

        except Exception as e:
            return await author.send(
                f"An error has occurred;\n"
                f"Try making sure your url is valid and/or the image is a valid resolution.\n"
                f"Your channel may also have to many webhooks. Read the error below. `Error: {e}`"
            )

        else:
            if guild.id not in self.vanities:
                self.vanities.update({guild.id: dict()})
                
            if author.id not in self.vanities[guild.id]:
                self.vanities[guild.id].update(
                    {author.id: [None, None, False]}
                )

            if self.vanities[guild.id][author.id][0] is None:
                self.vanities[guild.id][author.id] = [url, url, False]

            else:
                self.vanities[guild.id][author.id] = [
                    url,
                    self.vanities[guild.id][author.id][0],
                    False
                ]
                
            print(
                f'+ SET/CHANGED vanity avatar for user '
                f'\"{ctx.author}\" in server "{ctx.guild.name}".'
            )

    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True)
    async def remove_vanity(self, ctx: Context):

        guild = ctx.guild
        author = ctx.author

        if not guild:
            return await ctx.send(
                "This command cannot be used in a DM channel. Consider "
                "using it in a private channel in one of your servers."
            )
        
        if guild.id in self.vanities and author.id in self.vanities[guild.id] and self.vanities[guild.id][author.id][0]:
            self.vanities[guild.id][author.id] = [
                None,
                self.vanities[guild.id][author.id][0],
                self.vanities[guild.id][author.id][2]
            ]

            await ctx.send("Removed vanity.")
            print(
                f'- REMOVED vanity avatar for user \"{ctx.author}\" '
                f'in server "{ctx.guild.name}".'
            )

        else:
            await ctx.send("You don't have a vanity avatar on right now.")

    @command()
    @bot_has_permissions(send_messages=True)
    async def current(self, ctx: Context, user: User, standard: str = None):

        guild = ctx.guild
        author = ctx.author

        if standard != "standard":
            standard = None

        if not guild:
            return await ctx.send(
                "This command cannot be used in a DM channel. Consider "
                "using it in a private channel in one of your servers."
            )
        
        if user.id == self.bot.user.id:
            print(f'[] Sent bot\'s avatar url to user \"{author}\".')
            return await ctx.send(
                f'My avatar is located here:\n{self.bot.user.avatar_url}'
            )
        
        else:
            async def show_standard():
                print(
                    f'[] Sent standard avatar url for \"{user}\"'
                    f' to user \"{author}\".'
                )
                return await ctx.send(
                    f"Their current standard avatar is "
                    f"located here:\n{user.avatar_url}"
                )

            if not standard:  # Reverted to "and" because it must be a procedural if statement
                if guild.id in self.vanities and user.id in self.vanities[guild.id] and self.vanities[guild.id][user.id][0]:

                    print(
                        f'[] Sent vanity avatar url for \"{user}\" '
                        f'to user \"{author}\".'
                    )
                    return await ctx.channel.send(
                        f"Their current vanity avatar is located here:\n"
                        f"{self.vanities[guild.id][user.id][0]}"
                    )

                else:
                    await show_standard()

            elif standard == "standard":
                await show_standard()


def setup(bot: Bot):
    bot.add_cog(VanityCommands(bot))
