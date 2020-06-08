
# Lib
from pickle import dump
from time import sleep
# Site
from discord import __version__
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.errors import LoginFailure
from discord.permissions import Permissions
from discord.utils import oauth_url

# Local
from utils.classes import Bot

try:
    print("Press CTRL+C for user config settings. Ignore for defaults.", end="\r")
    for i in range(10):
        sleep(1)
except KeyboardInterrupt: # Enable a timeout that is interrupted by the user to configure. If no response, default options are used.
    debug_mode = input("\nEnter debug mode? (D=accept)\n---| ")
    if debug_mode == "D":
        debug_mode = True

    while True:
        tz = input("Time Zone:\n---| ")
        if tz in ["EST", "CST"]:
            break
else:
    print("Running with default settings.")
    debug_mode = False
    tz = "und"


print("Loading...")


BOT_PREFIX = ":>"
INIT_EXTENSIONS = [
    "admin",
    "background",
    "blacklist",
    "closet",
    "events",
    "help",
    "moderation",
    "repl",
    "vanity",
]


bot = Bot(
    command_prefix=BOT_PREFIX,
    description="Change your profile picture for a specific server.",
    owner_id=331551368789622784,
    debug_mode=debug_mode,
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

    activity = Activity(type=ActivityType.watching, name=f"Just woke up.")
    await bot.change_presence(status=Status.idle, activity=activity)

    # check changelog for differences since last save
    with open(f"{bot.cwd}\\changelog.txt", "r") as clfp:
        content = clfp.read()
        if content != bot.univ.ChangelogCache:
            for guild in bot.guilds:
                if guild.system_channel:
                    try:
                        await guild.system_channel.send(f"Changelog updated:\n```{content} ​```")
                    except Exception:
                        pass

            bot.univ.ChangelogCache = content
            with open(f"{bot.cwd}\\Serialized\\data.pkl", "wb") as pkfp:
                try:
                    data = {
                        "VanityAvatars": bot.univ.VanityAvatars,
                        "Blacklists": bot.univ.Blacklists,
                        "Closets": bot.univ.Closets,
                        "ServerBlacklists": bot.univ.ServerBlacklists,
                        "ChangelogCache": bot.univ.ChangelogCache
                    }

                    dump(data, pkfp)
                except Exception:
                    pass

            print("[] Sent changelog updates.")

    print(f"\n"
          f"#-------------------------------#"
          f"| Loading initial cogs..."
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

    if not bot.auth.MWS_DBL_SUCCESS:
        if bot.auth.MWS_DBL_TOKEN:
            confirm_new_dbl_token = input("Last DBL login failed or unknown. Enter new token? (Y/n): ")
            confirm_new_dbl_token = confirm_new_dbl_token.lower().startswith("y")
        else:
            print("No DBL token stored.", end="")
            confirm_new_dbl_token = True

        if confirm_new_dbl_token:
            new_bdl_token = input("Enter new DBL token:\n")
            bot.auth.MWS_DBL_SUCCESS = new_bdl_token

    print("Logging in with token.")

    while True:

        try:

            if not bot.auth.MWS_BOT_TOKEN:
                raise LoginFailure

            bot.run()

        except LoginFailure:
            try:
                bot.auth.MWS_BOT_TOKEN = None

                print("\nLogin Failed: No token was provided or token provided was invalid.")
                new_token = input("Provide new bot token: ")

                bot.auth.MWS_BOT_TOKEN = new_token

            except KeyboardInterrupt:
                print("\nLogin with new bot token cancelled. Aborting.")
                break

        except KeyboardInterrupt:
            break
