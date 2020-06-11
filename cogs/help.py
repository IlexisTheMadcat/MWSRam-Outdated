
# Lib
from datetime import datetime
from os import stat

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command

# Local
from utils.classes import Bot


class MiscCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command()
    @bot_has_permissions(send_messages=True)
    async def invite(self, ctx: Context):
        """"""

        await ctx.send(
            f"**If you are not going to use the bot, I encourage to cancel the invite. "
            f"I can only join so many servers.**\n"
            f"Here: https://discordapp.com/api/oauth2/authorize?client_id=687427956364279873&"
            f"permissions=536881152&scope=bot"
        )
        print(f'[] Sent invite link to user "{ctx.author}"')

    @command(name="help")
    @bot_has_permissions(send_messages=True)
    async def bhelp(self, ctx: Context, section: str = "directory", subsection: str = None):
        em = Embed(title="Ram: Help", color=0xff547c)
        if section == "directory":
            em.description = f"""
Simple commands:
```
{self.bot.command_prefix}set_vanity <url or file_attachment>   - Set your server-specific avatar. More info: {self.bot.command_prefix}help commands _set
{self.bot.command_prefix}remove_vanity                         - Remove your server-specific avatar.
```
Required Permissions:
```
"Manage Messages"     - Step 1: To delete a message
"Manage Webhooks"     - Step 2: To send a transformed version of that message.
"Send Messages"       - To send notifications/messages for warnings, confirmations, etc.
```
**To see important announcements and command changes, Type and enter `{self.bot.command_prefix}help updates`**
**Use this if you think a command isn't working the same way it did last time you used it.**

--------------------------------------------------

Type `{self.bot.command_prefix}help <directory>`, where `directory` is one of the following:
**Details**
**Privacy**
**Commands**
**Actions**
**Limitations**
**Updates**
"""

        elif section.lower() == "details":
            total = 0
            
            for i in self.bot.univ.VanityAvatars.keys():
                for x in self.bot.univ.VanityAvatars[i].keys():
                    if self.bot.univ.VanityAvatars[i][x][0]:
                        total = total + 1

            owner = self.bot.owner
            em.description = f"""
**Details:**
Command prefix: `{self.bot.command_prefix}`
Have a custom profile picture for different servers.

This bot was created by: {owner}
Support Server invite: https://discord.gg/j2y7jxQ
Warning: Support server may contain swearing in open channels.
*Consider __Direct Messaging__ the developer instead for questions/information *after* joining the server.

Number of servers this bot is in now: {len(self.bot.guilds)}
:asterisk: Number of users having vanities equiped now: {total}
"""
            
        elif section.lower() == "privacy":
            em.description = f"""
__Bot Owner's **Privacy** notification:__
I wish not to record your messages sent using this bot.
I only track the server names, channel names, and user names that use this bot. None of these are written down to a file.
4 files *are* used to keep track of your __custom avatars__, __blacklisted channels/prefixes for users and servers__, and __closets__.
-- This is so they aren't removed when the bot needs to reload.

There should be no reason I have to read your messages for any debugging. If you think the bot is not working correctly:
First read the information __on file__ using this command: `{self.bot.command_prefix}help updates`
Make sure it has the permissions listed in `{self.bot.command_prefix}help permissions`, and that it can use these permissions in the channel you are in.
Make sure the channel you are in is not in yours or your server's blacklist. To see it, enter `{self.bot.command_prefix}see_blacklists` or `{self.bot.command_prefix}see_server_blacklists`.
Prefixes can also be added to the blacklist. Make sure your messages don't start with any of those.
-- Type and enter `{self.bot.command_prefix}help commands blacklist` to see how blacklisting works.
"""

        elif section.lower() == "commands":
            if not subsection:
                em.description = f"""
**Commands**
Type `{self.bot.command_prefix}help commands <command>`, where `command` is one of the following:
```
Vanity -- Change your avatar for different servers:
    set_vanity
    remove_vanity
    current
    
Blasklisting -- Disable your avatar for different places:
    blacklist
    see_blacklists

Closets -- Save your avatars in your personal cloest:
    add_to_closet
    remove_from_closet
    rename_closet_entry
    see_closet
    preview_closet_entry

Moderation -- Enforce some actions:
    list                  - No limits
    manage_user           - You require "Manage Messages" permission
    see_server_blacklists - No limits
    server_blacklist      - You require "Manage Channels" permission

Genral -- General commands:
    help
    invite
```

"""
                
            elif subsection.lower() == "set_vanity":
                em.description = f"""
**SET VANITY**; Aliases: "_set"
`{self.bot.command_prefix}set_vanity <url>`
--------------------------------------------------
Sets your server specific profile picture.
Uses the url provided if available, or a file attachment provided.
**--** If multiple file attachments are added, the first one is used.
**--** Discord recommends 256x256 pictures for best preformance.

__Priorities__:
`url` can be an entry from your closet. (used first)
`url` can be a web address linking to an image. (used if `url` is not a closet entry)
`url` can be **replaced** with a file attachment, leaving `url` empty. (used if `url` is not provided)
`url` can be nothing altogether if you have used a vanity before and it will use the avatar you last had on.

Any messages sent that are not in blacklisted channels and don't start with blacklisted prefixes will be transformed.
"""
                
            elif subsection.lower() == "remove_vanity":
                em.description = f"""
**REMOVE VANITY**; Aliases: "remove"
`{self.bot.command_prefix}remove_vanity`
--------------------------------------------------
Turns server specific profile picture off.
Use this command if you frequently use bot commands because of how this bot works.
**--** A bot could detect your original message, operate, and then detect the transformed version, and operate again. Also consider blacklisting the bot's prefix.
**----** This depends entirely on how the bot works. It may or may not filter out bot messages.
"""
                
            elif subsection.lower() == "current":
                em.description = f"""
**CURRENT**
`{self.bot.command_prefix}current <user> ["standard"]`
--------------------------------------------------
Returns you a link to 'user's avatar.
**--** If they have a vanity equiped, this will return their vanity avatar's url.
**----** To get their standard avatar at any time, add "standard" to your command.

**--** If they don't have a vanity avatar equiped, their standard avatar will be returned, even if "standard" is not provided.
"""
                
            elif subsection.lower() == "blacklist":
                em.description = f"""
**BLACKLIST**; Aliases: "bl"
`{self.bot.command_prefix}blacklist <mode> [item]`
--------------------------------------------------
You have the option to blacklist channels from transforming your messages.
**--** "mode" can be one of the following:
**----** `channal-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.
**----** `channal-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.

**--** `item` can be a channel ID `[channal-add, channal-remove]`, or a prefix string `[prefix-add, prefix-remove]`.
**----** `item` is required when using the modes `prefix-add` or `prefix-remove`.
**----** To get a channel ID, turn Developer Mode on in Discord, then right-click on the target channel and click "Copy ID".
**----** Or instead, you can mention the channel.

*Sending a message in a channel that is in your blacklist will not transform it.*
*Sending a message starting with a prefix in your blacklist will not transform it.*
"""
                
            elif subsection.lower() == "see_blacklists":
                em.description = f"""
**SEE_BLACKLISTS**; Aliases: "see_bl"
`{self.bot.command_prefix}see_blacklists`
--------------------------------------------------
See all items that you blacklisted. These can be managed cross-server because they are tied to your user id.
"""

            elif subsection.lower() == "add_to_closet":
                em.description = f"""
**ADD_TO_CLOSET**; Aliases: "cl_add"
`{self.bot.command_prefix}add_to_closet <name>`
--------------------------------------------------
Adds your current vanity avatar with a name to a closet that can hold up to 10 vanity avatars.
**--** `name` is required to distinguish between closet entries.
**--** You cannot add closet entries with the same name as one already in your closet.
**--** You may also attach an image to your message to disregard your current vanity avatar if you have one on or not.
**----** A URL cannot be provided to substitute this.
"""

            elif subsection.lower() == "remove_from_closet":
                em.description = f"""
**REMOVE_FROM_CLOSET**; Aliases: "cl_remove"
`{self.bot.command_prefix}remove_from_closet <name>`
--------------------------------------------------
Remove `name` from your closet.
**--** This won't work if `name` doesn't exist in your closet.
"""

            elif subsection.lower() == "rename_closet_entry":
                em.description = f"""
**RENAME_CLOSET_ENTRY**; Aliases: "cl_rn"
`{self.bot.command_prefix}rename_closet_entry <name> <rename>`
--------------------------------------------------
Renames closet entry `name` to `rename`.
**--** This won't work if `name` doesn't exist in your closet.
**--** This won't work if `rename` is already in your closet.
"""
                
            elif subsection.lower() == "see_closet":
                em.description = f"""
**SEE_CLOSET**; Aliases: "cl"
`{self.bot.command_prefix}see_closet [user]`
--------------------------------------------------
See all the items in your closet along with a `name` and its associated `url`.
**--** Closets can only hold up to 10 avatars.
**--** If `user` is provided, it will return that user's closet.
**----** Note that this will not work if `user` hasn't voted yet.
"""

            elif subsection.lower() == "see_closet":
                em.description = f"""
**PREVIEW_CLOSET_ENTRY**; Aliases: "cl_preview"
`{self.bot.command_prefix}preview_closet_entry <name>`
--------------------------------------------------
Sends a message with the vanity avatar of closet entry `name`.
**--** Fails if `name` is not in your closet.
"""

            elif subsection.lower() == "server_blacklist":
                f"""
This command functions very similar to the `{self.bot.command_prefix}blacklist` command.
The only few differences:
1) You require the `Manage Server` permission to use it.
2) Items blacklisted are added for everyone, so it is a great tool for enforcing it.

**SERVER_BLACKLIST**; Aliases: "s_bl"
`{self.bot.command_prefix}server_blacklist <mode> [item]`
--------------------------------------------------
Members with the `Manage Server` permission can blacklist channels from transforming your messages for that server.
**--** "mode" can be one of the following:
**----** `channal-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.
**----** `channal-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.

**--** `item` can be a channel ID `[channal-add, channal-remove]`, or a prefix string `[prefix-add, prefix-remove]`.
**----** `item` is required when using the modes `prefix-add` or `prefix-remove`.
**----** To get a channel ID, turn Developer Mode on in Discord, then right-click on the target channel and click "Copy ID".

Sending a message in a channel that is in the server blacklist will not transform it.
Sending a message starting with a prefix in the server blacklist will not transform it.
"""
                
            elif subsection.lower() == "see_server_blacklists":
                em.description = f"""
This command functions very similar to the `{self.bot.command_prefix}see_blacklists` command.
It shows the blacklisted items for the *server,* which apply to everyone.

**SEE_BLACKLISTS**; Aliases: "see_s_bl"
`{self.bot.command_prefix}see_server_blacklists`
--------------------------------------------------
See all items that are blacklisted for the server the command is invoked in. These can be managed by members with the `Manage Server` permission.
"""
                
            elif subsection.lower() == "list":
                em.description = f"""
**LIST**
`{self.bot.command_prefix}list`
--------------------------------------------------
Returns a list of all users in the server with vanities equiped.
**--** This list may contain members that have left. To remove them, use the `{self.bot.command_prefix}manage_user` below.
"""

            elif subsection.lower() == "manage_user":
                em.description = f"""
**MANAGE_USER**; Aliases: "manage", "user"
`{self.bot.command_prefix}manage_user <mode> <user>`
--------------------------------------------------
Manage a user's ability to use the bot. This applies only in this server.
**--** `mode` must be one of 3 things:
**----** `block` - The mentioned user will be unable to send vanity messages.
**----** `unblock` - The mentioned user will be allowed to send vanity messages.
**----** `get_info` - Returns the vanity status of `user`.
**------** Whether or not a user is blocked is an attribute of a user's vanity status.

**--** `user` is also required. Mention the user, or quote the full ID.
**----** Example: `@SUPER MECH M500` or "SUPER MECH M500#2352"
**------** This is the bot developer's YouTube alias. The username could be different.
"""
                
            elif subsection.lower() == "help":
                em.description = f"""
**HELP**; Aliases: "h"
`{self.bot.command_prefix}help [section] [command if <section> is "commands"]`
--------------------------------------------------
Shows a directory including the different sections of the help message.
"""
            elif subsection.lower() == "invite":
                em.description = f"""
**INVITE**
`{self.bot.command_prefix}invite`
--------------------------------------------------
Gives you an invite link to invite this bot to any server.
**--** You require the "Manage Server" permission in the target server to do this. This is a discord limitation.
"""
                
            else:
                em.description = f"Invalid subsection name. Type and enter `{self.bot.command_prefix}help commands` " \
                                 f"for subsection names."

        elif section.lower() == "actions":
            em.description = f"""
**Actions you can do:**
**(-)** __React to a vanity message with "❌" to delete it.__
**--** The message must be your own for this to work.

**(-)** __React to a vanity message with "❓" if you're unsure who might've sent it.__
**--** There can be times where a user could use the same vanity as someone else along with the same nickname.
**----** If they might also have the same username, look at their discriminator/4-digit tag.
"""
                
        elif section.lower() == "limitations":
            em.description = f"""
**Limitations:**
**(-)** __You cannot edit messages you send.__
**--** If you have to, consider deleting the target message and type again.

**(-)** __Your messages will not be stacked efficiently__ (There is a plan to fix this).
**--** Every message you send will have your name over it...
Unlike\nthe\ndefault\nstacking\nmechanic.
"""

        elif section.lower() == "updates":
            lastmodified = stat(f"{self.bot.cwd}\\changelog.txt").st_mtime
            lastmodified = datetime.fromtimestamp(lastmodified).strftime("%H:%M %m/%d/%Y")
            with open(f"{self.bot.cwd}\\changelog.txt", "r") as f:
                text = f.read()

            em.description = f"""
**Updates**
__Here you will find important updates regarding command changes and announcements.__
```
Last updated: {lastmodified}
{text}
```
"""
            
        else:
            em.description = f"Not a valid section name. This bot shows all commands with the `commands` section.\n" \
                             f"Type `{self.bot.command_prefix}help` for all sections."
            em.color = 0x000000

        try:
            print(f'[] Sent "{section}" help message to server "{ctx.guild.name}".')
        except AttributeError:
            pass

        await ctx.send(embed=em)


def setup(bot: Bot):
    bot.add_cog(MiscCommands(bot))
