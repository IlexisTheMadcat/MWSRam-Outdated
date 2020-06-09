# Lib
from contextlib import suppress
from pickle import Unpickler
from os import getcwd
from os.path import join
from random import choice

# Site
from discord import __version__
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.errors import LoginFailure
from discord.permissions import Permissions
from discord.utils import oauth_url

# Local
from utils.classes import Bot

print("\nAttempting to open bot_config.pkl...", end="\n")
try:
    open(join(getcwd(), "Serialized", "bot_config.pkl"), "r").close()
except FileNotFoundError:
    open(join(getcwd(), "Serialized", "bot_config.pkl"), "x").close()

with open(join(getcwd(), "Serialized", "bot_config.pkl"), "rb") as f:
    try:
        config_data = Unpickler(f).load()
    except Exception as e:
        print(f"[Using defaults] Unpickling error: {e}{" "*30}")
        debug_mode = False
        auto_pull = True
        tz = "UTC"
    else:
        try:
            debug_mode = config_data["debug_mode"]
            auto_pull = config_data["auto_pull"]
            tz = config_data["tz"]
            print("Loaded bot_default.pkl")
        except KeyError:
            print(f'[Using defaults] bot_config.pkl file improperly formatted.{" " * 35}')  # print excess spaces to fully overwrite the '\r' above
            debug_mode = False  # Print exceptions to stdout. Some errors will not be printed for some reason, such as NameError outside of commands.
            auto_pull = True  # Auto pulls github updates every minute and reloads all loaded cogs.
            tz = "UTC"  # Triggers python to get real UTC time for Rams's status.

loading_choices = [  # because why not
    "Loading Random Access Memory...",
    "\"Wanna play?\"",
    "\"I wish you could wake me up later~\"",
    "\"I hope this isn't for debugging...\"",
    "Booting up the creative mind...",
    "Waking up the older sister...",
    "Charging RAM...",
    "\"Mmmmm~ h-huh..? Where's Rem? Where is she?? Tell me!\""
]
print(random.choice(loading_choices))

BOT_PREFIX = ":>"
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
# Extension "repl" must be loaded manually
# as it is not automatically available
# because it is not often needed.

bot = Bot(
    command_prefix=BOT_PREFIX,
    description="Change your profile picture for a specific server.",
    owner_ids=[331551368789622784, 125435062127820800],
    activity=Activity(type=ActivityType.watching, name=f"Just woke up."),
    status=Status.idle,
    # vv Configurable via :>bot
    debug_mode=debug_mode,
    auto_pull=auto_pull,
    tz=tz
)

bot.remove_command("help")

print(f"Running in: {bot.cwd}")
print(f"Discord API version: {__version__}")

print(
    f"Owner commands:\n"
    f"{BOT_PREFIX}resetallavatars          - Delete all avatars\n"
    f"{BOT_PREFIX}resetallblacklists       - Delete all blacklists\n"
    f"{BOT_PREFIX}resetallclosets          - Delete all closets\n"
    f"{BOT_PREFIX}resetallserverblacklists - Delete all server blacklists\n"
)


@bot.event
async def on_ready():
    app_info = await bot.application_info()
    bot.owner = bot.get_user(app_info.owner.id)

    permissions = Permissions()
    permissions.update(
        send_messages=True,
        manage_messages=True,
        manage_webhooks=True
    )

    print(f"\n"
          f"#-------------------------------#"
          f"| Loading initial cogs... "
          f"#-------------------------------#")

    for cog in INIT_EXTENSIONS:
        print(f"| Loading initial cog {cog}")
        try:
            bot.load_extension(f"cogs.{cog}")
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

    if not bot.auth["MWS_DBL_SUCCESS"]:
        if bot.auth["MWS_DBL_TOKEN"]:
            confirm_new_dbl_token = input("Last DBL login failed or unknown. Enter new token? (Y/n): ")
            confirm_new_dbl_token = confirm_new_dbl_token.lower().startswith("y")
        else:
            print("No DBL token stored.", end="")
            confirm_new_dbl_token = True

        if confirm_new_dbl_token:
            new_bdl_token = input("Enter new DBL token:\n")
            bot.auth["MWS_DBL_SUCCESS"] = new_bdl_token

    print("Logging in with token.")

    while True:

        try:

            if not bot.auth["MWS_BOT_TOKEN"]:
                raise LoginFailure

            with suppress(RuntimeError):
                bot.run()

        except LoginFailure:
            try:
                bot.auth["MWS_BOT_TOKEN"] = None

                print("\nLogin Failed: No token was provided or token provided was invalid.")
                new_token = input("Provide new bot token: ")

                bot.auth["MWS_BOT_TOKEN"] = new_token

            except KeyboardInterrupt:
                print("\nLogin with new bot token cancelled. Aborting.")
                break

        except KeyboardInterrupt:
            break
