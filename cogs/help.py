
# Lib
from datetime import datetime
from os import stat

# Site
from discord import Embed, AppInfo, Permissions
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command
from discord.utils import oauth_url

# Local
from utils.classes import Bot


class MiscCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # ------------------------------------------------------------------------------------------------------------------
    @command()
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def invite(self, ctx: Context):
        """Sends an OAuth bot invite URL"""

        app_info: AppInfo = await self.bot.application_info()
        permissions = Permissions()
        permissions.update(
            send_messages=True,
            manage_messages=True,
            manage_webhooks=True,
            add_reactions=True,
            attach_files=True,
            embed_links=True
        )

        em = Embed(
            title=f'OAuth URL for {self.bot.user.name}',
            description=f'[Click Here]'
                        f'({oauth_url(app_info.id, permissions)}) '
                        f'to invite me to your server.',
            color=0xff87a3
        )
        await ctx.send(embed=em)

    @command(name="help")
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def bhelp(self, ctx: Context, section: str = "directory", subsection: str = None):
        em = Embed(title="Ram: Help", color=0xff87a3)
        if section == "directory":
            em.description = f"""
Simple commands:
```
{self.bot.command_prefix}set_vanity <url or file_attachment>
Set your server-specific avatar. More info: {self.bot.command_prefix}help commands set_vanity

{self.bot.command_prefix}remove_vanity
Remove your server-specific avatar.
```
Required Permissions:
```
"Manage Messages"
Step 1: To delete a message

"Manage Webhooks"
Step 2: To send a transformed version of that message.

"Send Messages"
To send notifications/messages for warnings, confirmations, etc.

"Add Reactions"
To provide a temporary button to delete your message quickly.
```
**To see important announcements and command changes, Type and enter `{self.bot.command_prefix}help updates`**
**Use this if you think a command isn't working the same way it did last time you used it.**

--------------------------------------------------

Type `{self.bot.command_prefix}help <directory>`, where `<directory>` is one of the following:
**Details**
**Privacy**
**Commands**
**Actions**
**Limitations**
**Updates**
"""

        elif section.lower() == "details":
            total = 0
            
            for i in self.bot.user_data["VanityAvatars"].keys():
                for x in self.bot.user_data["VanityAvatars"][i].keys():
                    if self.bot.user_data["VanityAvatars"][i][x][0]:
                        total = total + 1

            owners = [self.bot.get_user(uid).mention for uid in self.bot.owner_ids]
            owners = '\n'.join(owners)
            em.description = f"""
**Details:**
Command prefix: `{self.bot.command_prefix}`
Create a custom directory to better organize your channels.

This bot was created by:
{owners}

Support Server invite: https://discord.gg/j2y7jxQ
Warning: Support server may contain swearing in open channels.
*Consider DMing the developer instead for questions/information.

Number of servers this bot is in now: {len(self.bot.guilds)}
:asterisk: Number of users having vanities equipped now: {total}
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
Note: Do NOT include angle- or square- brackets in your command arguments.
Type `{self.bot.command_prefix}help commands <command>`, where `<command>` is one of the following:
```
Vanity -- Change your avatar for different servers:
    set_vanity
    remove_vanity
    current
    toggle_quick_delete
    
Blacklisting -- Disable your avatar for different places:
    blacklist
    see_blacklists

Closets -- Save your avatars in your personal closet:
    add_to_closet
    remove_from_closet
    rename_closet_entry
    see_closet
    preview_closet_entry

Moderation -- Enforce some actions:
    list - No limits
    manage_user - "M/Nicknames" required
    see_server_blacklists - No limits
    server_blacklist - "M/Channels" required

General -- General commands:
    help
    invite
```

"""
                
            elif subsection.lower() == "set_vanity":
                em.description = f"""
**SET VANITY**; Aliases: "set"
`{self.bot.command_prefix}set_vanity <url>`
--------------------------------------------------
Sets your server specific profile picture.
Uses the url provided if available, or a file attachment provided.
**--** If multiple file attachments are added, the first one is used.

__Priorities__:
`url` can be an entry from your closet. (used first)
`url` can be a web address linking to an image. (used if `url` is not a closet entry)
`url` can be **replaced** with a file attachment, leaving `url` empty. (used if `url` is not provided)
`url` can be nothing altogether if you have used a vanity before and it will use the avatar you last had on.

Any messages sent that are not in blacklisted channels and don't start with blacklisted prefixes will be transformed.
Messages you send as a vanity will have a temporary :x: button to conveniently allow you to delete your message.
You can react with :x: to delete it any time.
:warning: For mods: Using this bot will fill your audit log with message deletions. 
"""
                
            elif subsection.lower() == "remove_vanity":
                em.description = f"""
**REMOVE VANITY**; Aliases: "remove"
`{self.bot.command_prefix}remove_vanity`
--------------------------------------------------
Turns server specific profile picture off.
Use this command if you frequently use bot commands because of how this bot works.
**--** Also consider blacklisting the bot's prefix.
"""
                
            elif subsection.lower() == "current":
                em.description = f"""
**CURRENT**
`{self.bot.command_prefix}current <user> ["standard" | "standard_url"]`
--------------------------------------------------
Returns a link to `user`'s vanity avatar.
**--** Passing "standard" will return the standard avatar as a *file* if it's *not animated.* 
**----** The standard avatar is returned as a file anyway if `user` does not have a vanity equipped.

**--** Passing "standard_url" will return a link to the standard avatar.
**----** Due to compatibility, these do not render on iOS
**----** \\*Attempting to follow said link will be tedious for you on iOS.

**--** If the standard avatar is *animated,* the link will be returned instead as this is viewable on all platforms.
**-- Vanities always return links.**
"""

            elif subsection.lower() == "toggle_quick_delete":
                em.description = f"""
**TOGGLE_QUICK_DELETE**; Aliases: "toggle_x", "quick_del"
`vpr:toggle_quick_delete`
**--------------------------------------------------**
Toggle the quick delete reaction that appears under message by default.
-- This "quick_delete" feature allows user who find it difficult to react to delete their message provides them a shortcut for 5 seconds.
-- Use this command to turn said feature off. It does bother some users.
"""
                
            elif subsection.lower() == "blacklist":
                em.description = f"""
**BLACKLIST**; Aliases: "bl"
`{self.bot.command_prefix}blacklist <mode> [item]`
--------------------------------------------------
You have the option to blacklist channels from transforming your messages.
**--** "mode" must be one of the following:
**----** `channel-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.
**----** `channel-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.

**--** `item` can be a mentioned channel (or ID) `[channel-add, channel-remove]`, or must a prefix string `[prefix-add, prefix-remove]`.
**----** For `pf-a` or `pf-r`, `item` must be a string of up to five characters representing a prefix to block.
**----** For `ch-a` or `ch-r`, leaving `item` blank will block the current channel.
**------** You can mention a channel to block it remotely.

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
See all the items in your closet with a name and its associated url.
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
**----** `channel-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.
**----** `channel-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.

**--** `item` can be a mentioned channel (or ID) `[channel-add, channel-remove]`, or must a prefix string `[prefix-add, prefix-remove]`.
**----** For `pf-a` or `pf-r`, `item` must be a string of up to five characters representing a prefix to block.
**----** For `ch-a` or `ch-r`, leaving `item` blank will block the current channel.
**------** You can mention a channel to block it remotely.

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
See all items that are blacklisted for the server the command is invoked in. 
These can be managed by members with the `Manage Server` permission.
"""
                
            elif subsection.lower() == "list":
                em.description = f"""
**LIST**
`{self.bot.command_prefix}list`
--------------------------------------------------
Returns a list of all users in the server with vanities equipped.
**--** This list may contain members that have left. 
**----** To remove them, use the `{self.bot.command_prefix}manage_user` below.
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
"""

        elif section.lower() == "updates":
            lastmodified = stat(f"{self.bot.cwd}/changelog.txt").st_mtime
            lastmodified = datetime.fromtimestamp(lastmodified).strftime("%H:%M %m/%d/%Y")
            with open(f"{self.bot.cwd}/changelog.txt", "r") as f:
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
            return

        await ctx.send(embed=em)
        if not subsection:
            if ctx.guild:
                print(f'[] Sent "{section}" help message to server "{ctx.guild.name}".')
            else:
                print(f'[] Sent "{section}" help message to user "{str(ctx.author)}".')
        elif subsection:
            if ctx.guild:
                print(f'[] Sent "{section}.{subsection}" help message to server "{ctx.guild.name}".')
            else:
                print(f'[] Sent "{section}.{subsection}" help message to user "{str(ctx.author)}".')


def setup(bot: Bot):
    bot.add_cog(MiscCommands(bot))
