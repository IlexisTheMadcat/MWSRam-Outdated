# Lib
import os
from json import dumps, loads
from replit import db
from copy import deepcopy
from random import choice

# Site
from discord import __version__
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.permissions import Permissions
from discord.utils import oauth_url

# Local
from utils.classes import Bot
from utils.fileinterface import PickleInterface as PI

db.update({"Tokens":{"BOT_TOKEN":"Njg3NDI3OTU2MzY0Mjc5ODcz.XmlnLA.Z5dF3Xcb-SIYJXnb6xzjDXVQ11M", "DBL_TOKEN":""}})

CONFIG_DEFAULTS = {
    "debug_mode": False, 
    # Print exceptions to stdout.  # TODO: Examine `on_error` to print all
    
    "auto_pull": True,    
    # Auto pulls github updates every minute and reloads all loaded cogs.
    
    "muted_dms": list(),   
    # List of user IDs to block support DMs from. Y'know, in case of the abusers.
    
    "error_log_channel": None
    # The channel that errors are sent to. 
    # If debug_mode is set to True, these errors are sent to stdout instead with more detail.
}

DATA_DEFAULTS = {
    "VanityAvatars": {
        "guildID": {
            "userID": [
                "avatar_url",
                "previous",
                "is_blocked"
            ]
        }
    },
    "Blacklists": {
        "authorID": (["channelID"], ["prefix"])
    },
    "ServerBlacklists": {
        "guildID": (["channelID"], ["prefix"])
    },
    "Closets": {
        "authorID": {
            "closet_name": "closet_url"
        }
    },
    "Webhooks": {
        "channelID": "webhookID"
    }
}

INIT_EXTENSIONS = [
    "admin",
    "background",
    "blacklist",
    "closet",
    "events",
    "help",
    "moderation",
    "vanity",
    "repl"
]

LOADING_CHOICES = [  # because why not
    "Loading Random Access Memory...",
    '"It appears nothing here will fit except women\'s clothes."',
    "Booting up the creative but stubborn mind...",
    "Waking up the older sister...",
    "Charging RAM...",
    '"I was only waiting to help Roswaal-sama put on fresh clothes."',
    '"By the way, do you have plans after this?"',
    '"I see you really are studying, sir."',
    '"No, thank you, sir."',
    '"What can you do by learning anything now?!"',
    '"I\'m not interested."',
    "Requesting the one they call Ram..."
]


config_data = PI("Serialized/bot_config.pkl", create_file=True)

string = dumps(dict(db))
user_data = dict(loads(string))

# Check the bot config file
for key in CONFIG_DEFAULTS:
    if key not in config_data:
        config_data[key] = CONFIG_DEFAULTS[key]
        print(f"[MISSING VALUE] Config '{key}' missing. "
              f"Inserted default '{CONFIG_DEFAULTS[key]}'")
found_data = deepcopy(config_data)  # Duplicate to avoid RuntimeError exception
for key in found_data:
    if key not in CONFIG_DEFAULTS:
        config_data.pop(key)  # Remove redundant data
        print(f"[REDUNDANCY] Invalid config \'{key}\' found. "
              f"Removed key from file.")
del found_data  # Remove variable from namespace

# Check the database
for key in DATA_DEFAULTS:
    if key not in user_data:
        user_data[key] = DATA_DEFAULTS[key]
        print(f"[MISSING VALUE] Data key '{key}' missing. "
              f"Inserted default '{DATA_DEFAULTS[key]}'")
found_data = deepcopy(config_data)  # Duplicate to avoid RuntimeError exception
for key in found_data:
    if key not in CONFIG_DEFAULTS:
        config_data.pop(key)  # Remove redundant data
        print(f"[REDUNDANCY] Invalid data \'{key}\' found. "
              f"Removed key from file.")
del found_data  # Remove variable from namespace

db.update(user_data)

print("[] Configurations loaded from Serialized/bot_config.pkl")


bot = Bot(
    description="Change your profile picture for a specific server.",
    owner_ids=[331551368789622784, 125435062127820800],  # DocterBotnikM500, SirThane
    activity=Activity(type=ActivityType.playing, name=f"the \"wake up\" game."),
    status=Status.idle,
    command_prefix="var:" if os.name == "posix" else "[ram]:",

    # Configurable via [p]bot
    config=config_data
)

# To be replaced by custom help command
# TODO: Move to `help.py` when done
bot.remove_command("help")

print(f"[BOT INIT] Running in: {bot.cwd}\n"
      f"[BOT INIT] Discord API version: {__version__}")


@bot.event
async def on_ready():
    await bot.connect_dbl(autopost=True)

    app_info = await bot.application_info()
    bot.owner = bot.get_user(app_info.owner.id)

    permissions = Permissions()
    permissions.update(
        send_messages=True,
        embed_links=True,
        manage_messages=True,
        manage_webhooks=True,
        add_reactions=True,
        attach_files=True
    )

    print(f"\n"
          f"#-------------------------------#\n"
          f"| Loading initial cogs...\n"
          f"#-------------------------------#")

    for cog in INIT_EXTENSIONS:
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"| Loaded initial cog {cog}")
        except Exception as e:
            print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")

    print(f"#-------------------------------#\n"
          f"| Successfully logged in.\n"
          f"#-------------------------------#\n"
          f"| User:      {bot.user}\n"
          f"| User ID:   {bot.user.id}\n"
          f"| Owner:     {bot.owner}\n"
          f"| Guilds:    {len(bot.guilds)}\n"
          f"| Users:     {len(list(bot.get_all_members()))}\n"
          f"| OAuth URL: {oauth_url(app_info.id, permissions)}\n"
          f"#------------------------------#\n"
          f"| {choice(LOADING_CHOICES)}\n"
          f"#-------------------------------#\n")


if __name__ == "__main__":
    bot.run()
