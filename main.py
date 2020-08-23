# Lib
import os
from copy import deepcopy

# Site
from discord import __version__
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.permissions import Permissions
from discord.utils import oauth_url

# Local
from utils.classes import Bot
from utils.fileinterface import PickleInterface as PI


CONFIG_DEFAULTS = {
    "debug_mode": False,       # Print exceptions to stdout.
    "auto_pull": False,         # Auto pulls github updates every minute and reloads all loaded cogs.
    "muted_dms": list(),       # List of user IDs to block support DMs from. Y'know, in case of the abusers.
    "error_log_channel": None,  # The channel ID to print error exceptions to.
    "password": None  # WILL be required to use the control panel
}

INIT_EXTENSIONS = [
    "admin",
    "background",
    "commands",
    "events", 
    "help",
    "repl",
    #"web"  # A web-based eval controller for Kyaru.
]

config_data = PI("Serialized/bot_config.pkl", create_file=True)

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

print("[] Configurations loaded from Serialized/bot_config.pkl")


bot = Bot(
    description="I help keep my new home organized.",
    owner_ids=[331551368789622784],  # DocterBotnikM500
    activity=Activity(type=ActivityType.playing, name=f"the \"wake up\" game."),
    status=Status.idle,
    command_prefix="k!" if os.name == "posix" else "[kyaru]:",

    # Configurable via [p]bot
    config=config_data
)

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
        administrator=True
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
          f"#------------------------------#\n")


if __name__ == "__main__":
    
    bot.run()

# https://www.japan-guide.com/e/e2221.html#stay