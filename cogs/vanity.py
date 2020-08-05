
# Lib
from os import remove

# Site
from discord import File, Embed
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command
from discord.user import User
from requests import get
from PIL import Image

# Local
from utils.classes import Bot


class VanityCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=["set"])
    @bot_has_permissions(manage_webhooks=True)
    async def set_vanity(self, ctx: Context, url: str = None):

        guild = ctx.guild
        author = ctx.author
        chan = ctx.channel
        msg = ctx.message

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. "
                            "Consider using it in a private channel in one of your servers.",
                color=0xff0000
            ))

        user_perms = ctx.channel.permissions_for(ctx.author)
        mode = "Used URL"

        if (guild.id in self.bot.user_data["VanityAvatars"] and
                author.id in self.bot.user_data["VanityAvatars"][guild.id] and
                self.bot.user_data["VanityAvatars"][guild.id][author.id][2]) and \
                not user_perms.manage_nicknames:
            return await ctx.send(embed=Embed(
                title="Permission Denied",
                description="You are currently blocked from using vanity avatars in this "
                            "server. Contact a moderator with the `Manage Messages` "
                            "permission to unblock you.",
                color=0xff0000
            ))
        
        try:
            if url in self.bot.user_data["Closets"][author.id]:
                check = await self.bot.get_user_vote(author.id)

                if not check:
                    return await ctx.send(embed=Embed(
                        title="Vote-Locked!",
                        description=f"Closets are vote-locked. Please go to "
                                    f"{self.bot.dbl_vote} and click on 'Vote'.\nThen come "
                                    f"back and try again. If you just now voted, wait a "
                                    f"few moments.",
                        color=0xff0000
                    ))

                elif check:
                    url = self.bot.user_data["Closets"][author.id][url]
                    mode = "Used closet entry"
            else:
                pass

        except KeyError or IndexError:
            pass
        
        if url is None:
            try:
                url = msg.attachments[0].url
                mode = "Used attachment"

            except IndexError:
                try:
                    url = self.bot.user_data["VanityAvatars"][guild.id][author.id][1]

                    if url is None:
                        raise KeyError

                    else:
                        mode = "Used previous avatar"

                except KeyError:
                    await ctx.send(embed=Embed(
                        title="Error",
                        description="Not enough parameters!",
                        color=0xff0000
                    ))
                    return

        try:
            dummy = await chan.create_webhook(name=author.display_name)
            await dummy.send(embed=Embed(
                title=f"{mode}; Success",
                description=f"{self.bot.user.display_name}: Vanity successfully created.\n"
                            f"Send a message in an unblocked channel to test it out!‎‎\n",
                color=0xff87a3),
                avatar_url=url
            )
            await dummy.delete()

        except Exception as e:
            return await ctx.send(embed=Embed(
                title="URL Error",
                description=f"An error has occurred;\n"
                            f"Try making sure your url is valid and/or the image is a valid resolution.\n"
                            f"Your channel may also have to many webhooks. Read the error below.\n"
                            f"`Error: {e}`",
                color=0xff0000
            ))

        else:
            if guild.id not in self.bot.user_data["VanityAvatars"]:
                self.bot.user_data["VanityAvatars"].update({guild.id: dict()})

            if author.id not in self.bot.user_data["VanityAvatars"][guild.id]:
                self.bot.user_data["VanityAvatars"][guild.id].update(
                    {author.id: [None, None, False]}
                )

            if self.bot.user_data["VanityAvatars"][guild.id][author.id][0] is None:
                self.bot.user_data["VanityAvatars"][guild.id][author.id] = \
                [url, url, self.bot.user_data["VanityAvatars"][guild.id][author.id][2]]

            else:
                self.bot.user_data["VanityAvatars"][guild.id][author.id] = [
                    url,
                    self.bot.user_data["VanityAvatars"][guild.id][author.id][0],
                    self.bot.user_data["VanityAvatars"][guild.id][author.id][2]
                ]
                
            print(
                f'+ SET/CHANGED vanity avatar for user '
                f'\"{ctx.author}\" in server "{ctx.guild.name}".'
            )

    @command(aliases=["remove"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def remove_vanity(self, ctx: Context):

        guild = ctx.guild
        author = ctx.author

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers.",
                color=0xff87a3
            ))
        
        if guild.id in self.bot.user_data["VanityAvatars"] and \
                author.id in self.bot.user_data["VanityAvatars"][guild.id] and \
                self.bot.user_data["VanityAvatars"][guild.id][author.id][0]:
            self.bot.user_data["VanityAvatars"][guild.id][author.id] = [
                None,
                self.bot.user_data["VanityAvatars"][guild.id][author.id][0],
                self.bot.user_data["VanityAvatars"][guild.id][author.id][2]
            ]

            await ctx.send(embed=Embed(
                title="Success",
                description="Removed vanity.",
                color=0xff87a3
            ))
            print(
                f'- REMOVED vanity avatar for user \"{ctx.author}\" '
                f'in server "{ctx.guild.name}".'
            )

        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You don't have a vanity avatar on right now.",
                color=0xff0000
            ))

    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def current(self, ctx: Context, user: User, standard: str = None):

        guild = ctx.guild
        author = ctx.author

        if standard != "standard":
            standard = None
        
        if user.id == self.bot.user.id:
            print(f'[] Sent bot\'s avatar url to user \"{author}\".')
            return await ctx.send(embed=Embed(
                title="Ram's Avatar",
                description=f'My avatar is located here:\n',
            ).set_image(url=self.bot.user.avatar_url))
        
        else:
            async def show_standard():
                print(
                    f'[] Sent standard avatar url for \"{user}\"'
                    f' to user \"{author}\".'
                )

                await ctx.send(embed=Embed(
                    title=f"{user}'s Standard Avatar",
                    description=f"Their current standard avatar is located here:",
                    color=0xff87a3
                ).set_image(url=user.avatar_url))

                return

            if not standard or standard != "standard":
                if not guild:
                    return await ctx.send(embed=Embed(
                        title="Error",
                        description="This command cannot be used in a DM channel (if looking for vanity avatar). "
                                    "Consider using it in a private channel in one of your servers.",
                        color=0xff0000
                    ))
                
                if guild.id in self.bot.user_data["VanityAvatars"] and \
                    user.id in self.bot.user_data["VanityAvatars"][guild.id] and \
                    self.bot.user_data["VanityAvatars"][guild.id][user.id][0]:

                    print(
                        f'[] Sent vanity avatar url for \"{user}\"'
                        f' to user \"{author}\".'
                    )

                    return await ctx.channel.send(embed=Embed(
                        title=f"Vanity Avatar: {user}",
                        description=f"Their current vanity avatar is located here:\n",
                        color=0xff87a3
                    ).set_image(url=self.bot.user_data['VanityAvatars'][guild.id][user.id][0]))

                else:
                    await show_standard()

            elif standard == "standard":
                await show_standard()

    @command(aliases=["pv"])
    async def preview(self, ctx, url=None):
        pass

    @command(aliases=["toggle_x", "quick_del"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def toggle_quick_delete(self, ctx: Context):
        guild = ctx.guild
        author = ctx.author
        if author.id not in self.bot.user_data["UserSettings"]:
            self.bot.user_data["UserSettings"][author.id] = {
                "use_engraved_id": True,
                "use_quick_delete": True
            }
        
        self.bot.user_data["UserSettings"][author.id]["use_quick_delete"] = not \
            self.bot.user_data["UserSettings"][author.id]["use_quick_delete"]
        
        symbol = self.bot.user_data["UserSettings"][author.id]["use_quick_delete"]
        if symbol:
            symbol = "✅"
        elif not symbol:
            symbol = "❎"

        await ctx.send(embed=Embed(
            title="Quick delete",
            description=f"{symbol} Quick delete toggled.\n",
            color=0xff87a3
        ))

    
    @command(aliases=["toggle_eid", "engraved_id"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def toggle_engraved_id(self, ctx: Context):
        """
        Users have the option of turning off Engraved_ID.
        A risk to take when calling this command is that
        messages sent before the bot is reloaded will no longer
        be able to be deleted due to bot cache limitations.
        However, users with `Manage Messages` permission 
        do not have to worry.
        """

        if ctx.author.id not in self.bot.user_data["UserSettings"]:
            self.bot.user_data["UserSettings"][ctx.author.id] = \
                {
                    "use_quick_delete": True,
                    "use_engraved_id": True
                }

        self.bot.user_data["UserSettings"][ctx.author.id]["use_engraved_id"] = \
            not self.bot.user_data["UserSettings"][ctx.author.id]["use_engraved_id"]
        
        symbol = self.bot.user_data["UserSettings"][ctx.author.id]["use_engraved_id"]
        if symbol:
            symbol = "✅"
        elif not symbol:
            symbol = "❎"
        
        await ctx.send(embed=Embed(
                title="EngravedID",
                description=f"{symbol} EngravedID toggled.\n",
                color=0xff87a3
        ))
        
def setup(bot: Bot):
    bot.add_cog(VanityCommands(bot))
