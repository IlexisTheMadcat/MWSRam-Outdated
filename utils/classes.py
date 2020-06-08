
# Lib
from datetime import datetime
from os import getcwd
from os.path import exists
from pickle import dump, Unpickler

# Site
from dbl.client import DBLClient
from dbl.errors import DBLException
from discord.ext.commands.bot import Bot as DiscordBot
from discord.user import User

# Local
from utils.tokens import Tokens


class Globals:
    def __init__(self):
        self.Inactive = 0
        self.cwd = getcwd()

        if not exists(f"{self.cwd}\\Serialized\\data.pkl"):
            print("[Unable to load] data.pkl not found. Replace file before shutting down. Saving disabled.")
            self.DisableSaving = True
            self.VanityAvatars = {"guildID": {"userID":["avatar_url", "previous", "is_blocked"]}}
            self.Blacklists = {"authorID": (["channelID"], ["prefix"])}
            self.ServerBlacklists = {"guildID": (["channelID"], ["prefix"])}
            self.Closets = {"auhthorID": {"closet_name":"closet_url"}}
            self.ChangelogCache = None

        else:
            self.DisableSaving = False
            with open(f"{self.cwd}\\Serialized\\data.pkl", "rb") as f:
                try:
                    data = Unpickler(f).load()
                    self.VanityAvatars = data["VanityAvatars"]
                    self.Blacklists = data["Blacklists"]
                    self.Closets = data["Closets"]
                    self.ServerBlacklists = data["ServerBlacklists"]
                    self.ChangelogCache = data["ChangelogCache"]
                    print("[] Loaded data.pkl.")
                except Exception as e:
                    self.VanityAvatars = {"guildID": {"userID":["avatar_url", "previous", "is_blocked"]}}
                    self.Blacklists = {"authorID": (["channelID"], ["prefix"])}
                    self.ServerBlacklists = {"guildID": (["channelID"], ["prefix"])}
                    self.Closets = {"auhthorID": {"closet_name": "closet_url"}}
                    self.ChangelogCache = None
                    print("[Data Reset] Unpickling Error:", e)


class Bot(DiscordBot):

    def __init__(self, *args, **kwargs):

        # Backwards patch Globals class for availability to cogs
        self.univ = Globals()
        self.cwd = self.univ.cwd

        # Capture extra meta from init for cogs, former `global`s
        self.debug_mode = kwargs.pop("debug_mode", False)
        self.tz = kwargs.pop("tz", "CST")

        # Attribute for accessing tokens from file
        self.auth = Tokens()

        # Attribute will be filled in `on_ready`
        self.owner: User = None

        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        super().run(self.auth.MWS_BOT_TOKEN, *args, **kwargs)

    def connect_dbl(self, autopost: bool = None):

        print("Connecting DBL with token.")
        try:
            if not self.auth.MWS_DBL_TOKEN:
                raise DBLException
            dbl = DBLClient(self, self.auth.MWS_DBL_TOKEN, autopost=autopost)

        except DBLException:
            self.auth.MWS_DBL_TOKEN = None
            print("\nDBL Login Failed: No token was provided or token provided was invalid.")
            dbl = None

        if dbl:
            self.auth.MWS_DBL_SUCCESS = True
        else:
            self.auth.MWS_DBL_SUCCESS = False

        return dbl

    async def logout(self):
        hour = str(datetime.now().hour)
        minute = str(datetime.now().minute)
        date = str(str(datetime.now().date().month) + "/" + str(datetime.now().date().day) + "/" + str(
            datetime.now().date().year))
        if len(hour) == 1:
            hour = "0" + hour
        if len(minute) == 1:
            minute = "0" + minute
        time = f"{hour}:{minute}, {date}"

        if not exists(f"{self.cwd}\\Serialized\\data.pkl") and not self.univ.DisableSaving:
            self.univ.DisableSaving = True
            print(f"[Unable to save] data.pkl not found. Replace file before shutting down. Saving disabled.")
            return
    
        if not self.univ.DisableSaving:
            print("Saving...", end="\r")
            with open(f"{self.cwd}\\Serialized\\data.pkl", "wb") as f:
                try:
                    data = {
                        "VanityAvatars": self.univ.VanityAvatars,
                        "Blacklists": self.univ.Blacklists,
                        "Closets": self.univ.Closets,
                        "ServerBlacklists": self.univ.ServerBlacklists,
                        "ChangelogCache": self.univ.ChangelogCache
                    }

                    dump(data, f)
                except Exception as e:
                    print(f"[{time} || Unable to save] Pickle dumping Error:", e)

            self.univ.Inactive = self.univ.Inactive + 1
            print(f"[VPP: {time}] Saved data.")

        await super().logout()
