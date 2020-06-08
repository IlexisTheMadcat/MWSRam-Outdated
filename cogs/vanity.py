
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
        self.dblpy = self.bot.connect_dbl()

    @command(aliases=["_set"])
    @bot_has_permissions(manage_webhooks=True)
    async def set_vanity(self, ctx: Context, url: str = None):
        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )
            return

        if ctx.guild.id in self.bot.univ.VanityAvatars and \
                ctx.author.id in self.bot.univ.VanityAvatars[ctx.guild.id].keys():
            if self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][2]:
                await ctx.send(
                    "You are currently blocked from using vanity avatars in this server. "
                    "Contact a moderator with the `Manage Messages` permission to unblock you."
                )
                return
        
        try:
            if url in self.bot.univ.Closets[ctx.author.id]:
                if ctx.author.id != self.bot.owner.id:

                    check = await self.dblpy.get_user_vote(ctx.author.id)
                else:
                    check = True

                if not check:
                    await ctx.send(
                        "Closets are vote-locked. Please go to https://discordbots.org/bot/687427956364279873/vote and "
                        "click on 'Vote'.\nThen come back and try again. If you just now voted, wait a few moments."
                    )
                    return
                elif check:
                    url = self.bot.univ.Closets[ctx.author.id][url]
                    await ctx.send("Used closet entry.")
        except KeyError or IndexError:
            pass
        
        if url is None:
            try:
                url = ctx.message.attachments[0].url
                await ctx.send("Used attachment...")
            except IndexError:
                try:
                    url = self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][1]
                    if url is None:
                        raise KeyError
                    else:
                        await ctx.send("Used previous avatar...")
                except KeyError:
                    await ctx.send("Not enough parameters!")
                    return

        try:
            dummy = await ctx.channel.create_webhook(name=ctx.author.display_name)
            await dummy.send("Vanity Profile Pics: Vanity successfully created.‎‎", avatar_url=url)
            await dummy.delete()
        except Exception as e:
            await ctx.author.send(
                f"An error has occured; Try making sure your url is valid and is a valid resolution.\n"
                f"128x128 (no compression) or 400x400 is the way to go!\n`Error: {e}`"
            )
            return

        else:
            if ctx.guild.id not in self.bot.univ.VanityAvatars:
                self.bot.univ.VanityAvatars.update({ctx.guild.id: dict()})
                
            if ctx.author.id not in self.bot.univ.VanityAvatars[ctx.guild.id].keys():
                self.bot.univ.VanityAvatars[ctx.guild.id].update({ctx.author.id: [None, None, False]})

            if self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0] is None:
                self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id] = [url, url, False]
            else:
                self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id] = [
                    url,
                    self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0],
                    False
                ]
                
            print(f'+ SET/CHANGED vanity avatar for user \"{ctx.author}\" in server "{ctx.guild.name}".')
                
    # ------------------------------------------------------------------------------------------------------------------
    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True)
    async def remove_vanity(self, ctx: Context):
        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )
            return
        
        if ctx.guild.id in self.bot.univ.VanityAvatars and \
                ctx.author.id in self.bot.univ.VanityAvatars[ctx.guild.id] and \
                self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0]:
            self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id] = [
                None,
                self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][0],
                self.bot.univ.VanityAvatars[ctx.guild.id][ctx.author.id][2]
            ]

            await ctx.send("Removed vanity.")
            print(f'- REMOVED vanity avatar for user \"{ctx.author}\" in server "{ctx.guild.name}".')

        else:
            await ctx.send("You don't have a vanity avatar on right now.")

    # ------------------------------------------------------------------------------------------------------------------
    @command()
    @bot_has_permissions(send_messages=True)
    async def current(self, ctx: Context, user: User, standard: str = None):  # TODO: Maybe `Member`, not `User`?
        if standard != "standard":
            standard = None

        if not ctx.guild:
            await ctx.send(
                "This command cannot be used in a DM channel. "
                "Consider using it in a private channel in one of your servers."
            )
            return
        
        if user.id == self.bot.user.id:
            await ctx.send(f'My avatar is located here:\n{self.bot.user.avatar_url}')
            print(f'[] Sent bot\'s avatar url to user \"{ctx.author}\".')
            return
        
        else:
            async def show_standard():
                await ctx.send(f"Their current standard avatar is located here:\n{user.avatar_url}")
                print(f'[] Sent standard avatar url for \"{user}\" to user \"{ctx.author}\".')
                return
            
            if not standard and \
                    ctx.guild.id in self.bot.univ.VanityAvatars and \
                    user.id in self.bot.univ.VanityAvatars[ctx.guild.id]:

                if self.bot.univ.VanityAvatars[ctx.guild.id][user.id][0]:

                    await ctx.channel.send(
                        f"Their current vanity avatar is located here:\n"
                        f"{self.bot.univ.VanityAvatars[ctx.guild.id][user.id][0]}"
                    )
                    print(f'[] Sent vanity avatar url for \"{user}\" to user \"{ctx.author}\".')
                    return

                else:
                    await show_standard()

            elif standard == "standard":
                await show_standard()


def setup(bot: Bot):
    bot.add_cog(VanityCommands(bot))
