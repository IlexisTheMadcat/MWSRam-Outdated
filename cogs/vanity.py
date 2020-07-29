
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
        mode = None

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
                mode = "Used URL"

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
                    {author.id: [None, None, False, True]}
                )

            if self.bot.user_data["VanityAvatars"][guild.id][author.id][0] is None:
                self.bot.user_data["VanityAvatars"][guild.id][author.id] = [url, url,
                                                                            self.bot.user_data["VanityAvatars"][guild.id][author.id][2],
                                                                            self.bot.user_data["VanityAvatars"][guild.id][author.id][3]]

            else:
                self.bot.user_data["VanityAvatars"][guild.id][author.id] = [
                    url,
                    self.bot.user_data["VanityAvatars"][guild.id][author.id][0],
                    self.bot.user_data["VanityAvatars"][guild.id][author.id][2],
                    self.bot.user_data["VanityAvatars"][guild.id][author.id][3]
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
                self.bot.user_data["VanityAvatars"][guild.id][author.id][2],
                self.bot.user_data["VanityAvatars"][guild.id][author.id][3]
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
    @bot_has_permissions(send_messages=True, embed_links=True, attach_files=True)
    async def current(self, ctx: Context, user: User, standard: str = None):

        guild = ctx.guild
        author = ctx.author

        if standard not in ["standard", "standard_url"]:
            standard = None

        if not guild:
            return await ctx.send(embed=Embed(
                title="Error",
                description="This command cannot be used in a DM channel. Consider "
                            "using it in a private channel in one of your servers.",
                color=0xff0000
            ))
        
        if user.id == self.bot.user.id:
            print(f'[] Sent bot\'s avatar url to user \"{author}\".')
            return await ctx.send(embed=Embed(
                title="Ram's Avatar",
                description=f'My avatar is located here:\n',
            ).set_image(url=self.bot.user.avatar_url))
        
        else:
            async def show_standard():
                if (str(user.avatar_url).endswith(".webp") or str(user.avatar_url).endswith(".webp?size=1024")) and standard != "standard_url":
                    r = get(user.avatar_url, allow_redirects=True)                  # Compatibility for mobile devices unable
                    with open(f"{self.bot.cwd}/avatar{user.id}.webp", "wb") as f:   # to render .webp files, especially iOS
                        f.write(r.content)

                    im = Image.open(f"{self.bot.cwd}/avatar{user.id}.webp")
                    im.save(f"{self.bot.cwd}/avatar{user.id}.png", format="PNG")
                    file = File(f"{self.bot.cwd}/avatar{user.id}.png")
                    im.close()

                    print(
                        f'[] Sent standard avatar url for \"{user}\"'
                        f' to user \"{author}\".'
                    )

                    await ctx.send(embed=Embed(
                        title=f"{user}'s Standard Avatar",
                        description=f"Their current standard avatar is here:",
                        color=0xff87a3
                    ))
                    await ctx.send(file=file)

                    remove(f"{self.bot.cwd}/avatar{user.id}.webp")
                    remove(f"{self.bot.cwd}/avatar{user.id}.png")

                    return

                else:
                    print(
                        f'[] Sent standard avatar url for \"{user}\"'
                        f' to user \"{author}\".'
                    )

                    await ctx.send(embed=Embed(
                        title=f"{user}'s Standard Avatar",
                        description=f"Their current standard avatar url is located here:",
                        color=0xff87a3
                    ).set_image(url=user.avatar_url))

                    return

            if not standard:
                if guild.id in self.bot.user_data["VanityAvatars"] and user.id in self.bot.user_data["VanityAvatars"][guild.id] and self.bot.user_data["VanityAvatars"][guild.id][user.id][0]:

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

            elif standard in ["standard", "standard_url"]:
                await show_standard()

    @command(aliases=["pv"])
    async def preview(self, ctx, url=None):
        pass

    @command(aliases=["toggle_x", "quick_del"])
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def toggle_quick_delete(self, ctx):
        guild = ctx.guild
        author = ctx.author
        if guild.id in self.bot.user_data["VanityAvatars"] and author.id in self.bot.user_data["VanityAvatars"][guild.id]:
            self.bot.user_data["VanityAvatars"][guild.id][author.id][3] = not self.bot.user_data["VanityAvatars"][guild.id][author.id][3]
            symbol = self.bot.user_data["VanityAvatars"][guild.id][author.id][3]
            if symbol:
                symbol = "✅"
            elif not symbol:
                symbol = "❎"

            await ctx.send(embed=Embed(
                title="Quick delete",
                description=f"{symbol} Quick delete toggled.\n",
                color=0xff87a3
            ))
        else:
            await ctx.send(embed=Embed(
                title="Error",
                description="You can't use this feature until you have created your vanity for the first time here.",
                color=0xff0000
            ))


def setup(bot: Bot):
    bot.add_cog(VanityCommands(bot))
