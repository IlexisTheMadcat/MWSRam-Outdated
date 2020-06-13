# Lib
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


CONFIG_DEFAULTS = {
    "debug_mode": False,  # Print exceptions to stdout.  # TODO: Examine `on_error` to print all
    "auto_pull": True,    # Auto pulls github updates every minute and reloads all loaded cogs.
    "tz": "UTC",          # Triggers python to get real UTC time for Rams's status.
    "command_prefix": ":>",
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
]


print("...\n\n#-------------------------------#")

config_data = PI("Serialized/bot_config.pkl", create_file=True)

bot_config = {
    "debug_mode": config_data.get("debug_mode"),
    "auto_pull": config_data.get("auto_pull"),
    "tz": config_data.get("tz"),
    "command_prefix": config_data.get("prefix"),
}

defaults_used = False
for key, val in bot_config.items():
    if val is None:
        config_data[key] = CONFIG_DEFAULTS[key]
        bot_config[key] = CONFIG_DEFAULTS[key]
        defaults_used = True
        print(f"[USING CONFIG DEFAULT] Config '{key}' missing. Inserted default '{CONFIG_DEFAULTS[key]}'")
if not defaults_used:
    print("[CONFIG LOADED] Configurations successfully loaded from Serialized/bot_config.pkl")

print("#-------------------------------#\n")
loading_choices = [  # because why not
    "Loading Random Access Memory...",
    '"It appears nothing here will fit except women\'s clothes."',
    "Booting up the creative but stubbern mind...",
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

print("#-------------------------------#")
print(f"{choice(loading_choices)}")
print(f"#-------------------------------#\n")

# Extension "repl" must be loaded manually
# as it is not automatically available
# because it is not often needed.

bot = Bot(
    description="Change your profile picture for a specific server.",
    owner_ids=[331551368789622784, 125435062127820800],
    activity=Activity(type=ActivityType.watching, name=f"Just woke up."),
    status=Status.idle,

    # Configurable via :>bot
    **bot_config
)

# To be replaced by custom help command  # TODO: Move to `help.py` when done
bot.remove_command("help")

print("#-------------------------------#")
print(f"[BOT INIT] Running in: {bot.cwd}")
print(f"[BOT INIT] Discord API version: {__version__}")
print("#-------------------------------#\n")


@bot.event
async def on_ready():
    bot.connect_dbl(autopost=True)

    app_info = await bot.application_info()
    bot.owner = bot.get_user(app_info.owner.id)

    permissions = Permissions()
    permissions.update(
        send_messages=True,
        manage_messages=True,
        manage_webhooks=True
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
          f"| Usern:     {bot.user}\n"
          f"| User ID:   {bot.user.id}\n"
          f"| Owner:     {bot.owner}\n"
          f"| Guilds:    {len(bot.guilds)}\n"
          f"| Users:     {len(list(bot.get_all_members()))}\n"
          f"| OAuth URL: {oauth_url(app_info.id, permissions)}\n"
          f"# ------------------------------#")


if __name__ == "__main__":

    print("[BOT INIT] Logging in with token.")
    bot.run()
