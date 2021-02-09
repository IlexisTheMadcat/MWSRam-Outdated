[![Discord Bots](https://top.gg/api/widget/687427956364279873.svg)](https://top.gg/bot/687427956364279873)

# Vanity Profile Pics || Ram
## Want a new look just for the occasion? Let me suit you up.

### Introduction
With this bot, roleplay doesn't have to be played with a profile picture intended for work or other communities.\
You can change your avatar with one line of a command and your future messages will transform into your new avatar.

**Starter Commands**
```
var:set_vanity <image_url (or file attachment)>
Sets the image for your new server specific avatar.
Can support link argument and file attachment.
-- URL argument is used if both are given for some reason.
-- If multiple attachments are provided for some reason, the first one is used.
-- If you remove your vanity, you can set your previous vanity without any parameters.

var:remove_vanity
Removes your vanity avatar
```
**Actions:**\
React to a message with "❌" to delete a vanity message.\
React to a message with "❓" to recieve a DM telling you the real user who sent it.

With a vanity equipped, send a message anywhere in a specific server to transform your message into your new avatar.

**Required Permissions:**
```
"Read Messages"       - To read commands. This is a default permission.
"Manage Messages"     - Step 1: To delete a message.
"Manage Webhooks"     - Step 2: To send a transformed version of that message.
"Send Messages"       - To send notifications/messages for warnings, confirmations, etc.
"Embed Links"         - To stylize messages using beautiful embeds with my hair color!
"Attach Files"        - To attach files for iOS viewability in the "var:current <user>" command
```

A vanity is your avatar specific to a server.\
[![Vanity Message Difference](https://media.discordapp.net/attachments/655456170391109663/720039939743416420/unknown.png)](about:blank)

Your ownership of a vanity message is acquired using a special method Ram uses to engrave your messages with your ID.\
You may notice this here:\
[![Engraved ID Example](https://media.discordapp.net/attachments/655456170391109663/720040327335116930/unknown.png)](about:blank)

# Commands
```
Vanity -- Change your avatar for different servers:
    set_vanity
    remove_vanity
    current
    toggle_quick_delete
    
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

## **Vanity Commands**
### SET_VANITY; Aliases: "set"
`var:set_vanity <url>`\
**--------------------------------------------------**\
Sets your server specific profile picture.\
Uses the url provided if available, or a file attachment provided.\
**--** If multiple file attachments are added, the first one is used.\
**--** Discord recommends 256x256 pictures for best preformance.

### REMOVE_VANITY; Aliases: "remove"
`var:remove_vanity`\
**--------------------------------------------------**\
Turns server specific profile picture off.\
Use this command if you frequently use bot commands because of how this bot works.\
**--** A bot could detect your original message, operate, and then detect the transformed version, and operate again. Also consider blacklisting the bot's prefix.\
**----** This depends entirely on how the bot works. It may or may not filter out bot messages.

### CURRENT
`var:current <user> ["standard"]`\
**--------------------------------------------------**\
Returns you a link to `user`s avatar.\
**--** If they have a vanity equipped, this will return their vanity avatar's url.\
**----** To get their standard avatar at any time, add "standard" to your command.\
**--** If they don't have a vanity avatar equipped, their standard avatar will be returned, even if "standard" is not provided.\

### TOGGLE_QUICK_DELETE; Aliases: "toggle_x", "quick_del"
`var:toggle_quick_delete`\
**--------------------------------------------------**\
Toggle the quick delete reaction that appears under message by default.\
-- This "quick_delete" feature allows user who find it difficult to react to delete their message provides them a shortcut for 5 seconds.\
-- Use this command to turn said feature off. It does bother some users.

### PREVIEW; Aliases: "vp"
`var:preview <url>`
**--------------------------------------------------**\
Preview how your image will appear as the vanity icon.\
-- File attachments are not (yet) supported, please enter the URL.

## **Blacklisting**
This feature-set allows you to block Ram from transforming your message if it is in a certain channel or starts with a certain prefix.

### BLACKLIST; Aliases: "bl"
`vara:blacklist <mode> [item]`\
**--------------------------------------------------**\
You have the option to blacklist channels from transforming your messages.\
**--** "mode" can be one of the following:\
**----** `channal-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.\
**----** `channal-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.\
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.\
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.\
**--** `item` can be a channel ID (`[channal-add, channal-remove]`), or a prefix string (`[prefix-add, prefix-remove]`).\
**----** `item` is required when using the modes `prefix-add` or `prefix-remove`.\
**----** To get a channel ID, turn Developer Mode on in Discord, then right-click on the target channel and click "Copy ID".\
**----** Or instead, you can mention the channel.

*Sending a message in a channel that is in your blacklist will not transform it.*\
*Sending a message starting with a prefix in your blacklist will not transform it.*

### SEE_BLACKLISTS; Aliases: "see_bl"
`var:see_blacklists`\
**--------------------------------------------------**\
See all items that you blacklisted. These can be managed cross-server because they are tied to your user id.

## Closets - These commands require you to vote the bot at [Top.gg](https://top.gg/bot/687427956364279873).
This feature-set allows you to store your favorite vanities into a Key:Value dictionary.\
To set a closet entry as your vanity, enter the `var:set` command followed by the closet entry's name.\
Remember, `var:set` takes `url` as an argument, and will almost always treat it as a URL. \
However, if `url` is a closet entry name, it will use that. If not, you may get an error response.

### ADD_TO_CLOSET; Aliases: "cl_add"
`var:add_to_closet <name>`\
**--------------------------------------------------**\
Adds your current vanity avatar with a name to a closet that can hold up to 10 vanity avatars.\
**--** `name` is required to distinguish between closet entries.\
**--** You cannot add closet entries with the same name as one already in your closet.\
**--** You may also attach an image to your message to disregard your current vanity avatar if you have one on or not.\
**----** A URL cannot be provided to substitute this.

### REMOVE_FROM_CLOSET; Aliases: "cl_remove"
`var:remove_from_closet <name>`\
**--------------------------------------------------**\
Remove `name` from your closet.\
**--** This won't work if `name` doesn't exist in your closet.

### RENAME_CLOSET_ENTRY; Aliases: "cl_rn"
**--------------------------------------------------**\
`var:rename_closet_entry <name> <rename>`\
Renames closet entry `name` to `rename`.\
**--** This won't work if `name` doesn't exist in your closet.\
**--** This won't work if `rename` is already in your closet.

### SEE_CLOSET; Aliases: "cl"
`var:see_closet [user]`\
**--------------------------------------------------**\
See all the items in your closet along with a `name` and its associated `url`.
**--** Closets can only hold up to 10 avatars.
**--** If `user` is provided, it will return that user's closet.
**----** Note that this will not work if `user` hasn't voted yet.

### PREVIEW_CLOSET_ENTRY; Aliases: "cl_preview"
`var:preview_closet_entry <name>`\
**--------------------------------------------------**\
Sends a message with the vanity avatar of closet entry `name`.\
**--** This won't work if `name` doesn't exist in your closet.

## Moderation - Some of these require a moderation permission.
Check the full list above to see what permission you need for a command.

### SERVER_BLACKLIST; Aliases: "s_bl"
Note: This command functions very similar to the `var:blacklist` command.\
The only few differences:\
1) You require the `Manage Server` permission to use it.\
2) Items blacklisted are added for everyone, so it is a great tool for enforcing it. \
These are tied to your server's id.
`var:server_blacklist <mode> [item]`\
**--------------------------------------------------**\
Members with the `Manage Server` permission can blacklist channels from transforming your messages for that server.\
**--** "mode" can be one of the following:\
**----** `channal-add` or `ch-a` - add a channel to turn vanity avatars off for that channel.\
**----** `channal-remove` or `ch-r` - remove a channel to turn vanity avatars back on for that channel.\
**----** `prefix-add` or `pf-a` - add a prefix to prevent vanity messaages from appearing for messages starting with said prefix.\
**----** `prefix-remove` or `pf-a` - remove a prefix to allow vanity messages to appear for messages starting with said prefix.\
**--** `item` can be a channel ID `[channal-add, channal-remove]`, or a prefix string `[prefix-add, prefix-remove]`.\
**----** `item` is required when using the modes `prefix-add` or `prefix-remove`.\
**----** To get a channel ID, turn Developer Mode on in Discord, then right-click on the target channel and click "Copy ID".

### SEE_BLACKLISTS; Aliases: "see_s_bl"
This command functions very similar to the `var:see_blacklists` command.\
It shows the blacklisted items for the *server,* which apply to everyone.
`var:see_server_blacklists`\
**--------------------------------------------------**\
See all items that are blacklisted for the server the command is invoked in. These can be managed by members with the `Manage Server` permission.

### **LIST**
`var:list`\
**--------------------------------------------------**\
Returns a list of all users in the server with vanities equipped.

### MANAGE_USER; Aliases: "manage", "user"
`var:manage_user <mode> <user>`\
**--------------------------------------------------**\
Manage a user's ability to use the bot. This applies only in this server.\
**--** `mode` must be one of 3 things:\
**----** `block` - The mentioned user will be unable to send vanity messages.\
**----** `unblock` - The mentioned user will be allowed to send vanity messages.\
**----** `get_info` - Returns the vanity status of `user`.\
**------** Whether or not a user is blocked is an attribute of a user's vanity status.

**--** `user` is also required. Mention the user, or quote the full ID.\
**----** Example: `@SUPER MECH M500` or "SUPER MECH M500#2352"\
**------** This is the bot developer's YouTube alias. The username could be different.

### **HELP**; Aliases: "h"
`var:help [section] [command if <section> is "commands"]`\
**--------------------------------------------------**\
Shows a directory including the different sections of the help message.

### **INVITE**
`var:invite`\
**--------------------------------------------------**\
Gives you an invite link to invite this bot to any server.\
**--** You require the "Manage Server" permission in the target server to do this. This is a discord limitation.

# *This project was inspired by TupperBox.*
