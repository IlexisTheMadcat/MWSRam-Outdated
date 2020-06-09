
# Lib
from datetime import datetime
from os import getcwd, utime
from os.path import exists, join, split, splitext
from pathlib import Path
from pickle import dump, Unpickler, load
from re import match

# Site
from dbl.client import DBLClient
from dbl.errors import DBLException
from discord.channel import TextChannel
from discord.ext.commands.bot import Bot as DiscordBot
from discord.ext.commands.context import Context
from discord.ext.commands.converter import IDConverter
from discord.ext.commands.errors import BadArgument
from discord.user import User
from discord.utils import find, get
from typing import Any, Dict, List, Union

# Local


class Paginator:

    def __init__(
            self,
            page_limit: int = 1000,
            trunc_limit: int = 2000,
            headers: List[str] = None,
            header_extender: str = u'\u200b'
    ):
        self.page_limit = page_limit
        self.trunc_limit = trunc_limit
        self._pages = None
        self._headers = None
        self._header_extender = header_extender
        self.set_headers(headers)

    @property
    def pages(self):
        if self._headers:
            self._extend_headers(len(self._pages))
            headers, self._headers = self._headers, None
            return [
                (headers[i], self._pages[i]) for i in range(len(self._pages))
            ]
        else:
            return self._pages

    def set_headers(self, headers: List[str] = None):
        self._headers = headers

    def set_header_extender(self, header_extender: str = u'\u200b'):
        self._header_extender = header_extender

    def _extend_headers(self, length: int):
        while len(self._headers) < length:
            self._headers.append(self._header_extender)

    def set_trunc_limit(self, limit: int = 2000):
        self.trunc_limit = limit

    def set_page_limit(self, limit: int = 1000):
        self.page_limit = limit

    def paginate(self, value):
        """
        To paginate a string into a list of strings under
        `self.page_limit` characters. Total len of strings
        will not exceed `self.trunc_limit`.
        :param value: string to paginate
        :return list: list of strings under 'page_limit' chars
        """
        spl = str(value).split('\n')
        ret = []
        page = ''
        total = 0
        for i in spl:
            if total + len(page) < self.trunc_limit:
                if (len(page) + len(i)) < self.page_limit:
                    page += '\n{}'.format(i)
                else:
                    if page:
                        total += len(page)
                        ret.append(page)
                    if len(i) > (self.page_limit - 1):
                        tmp = i
                        while len(tmp) > (self.page_limit - 1):
                            if total + len(tmp) < self.trunc_limit:
                                total += len(tmp[:self.page_limit])
                                ret.append(tmp[:self.page_limit])
                                tmp = tmp[self.page_limit:]
                            else:
                                ret.append(tmp[:self.trunc_limit - total])
                                break
                        else:
                            page = tmp
                    else:
                        page = i
            else:
                ret.append(page[:self.trunc_limit - total])
                break
        else:
            ret.append(page)
        self._pages = ret
        return self.pages


class GlobalTextChannelConverter(IDConverter):
    """Converts to a :class:`~discord.TextChannel`.

    Copy of discord.ext.commands.converters.TextChannelConverter,
    Modified to always search global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """

    @staticmethod
    def _get_from_guilds(bot, getter, argument):
        """Copied from discord.ext.commands.converter to prevent
        access to protected attributes inspection error"""
        result = None
        for guild in bot.guilds:
            result = getattr(guild, getter)(argument)
            if result:
                return result
        return result

    async def convert(self, ctx: Context, argument: str) -> TextChannel:
        bot = ctx.bot

        search = self._get_id_match(argument) or match(r'<#([0-9]+)>$', argument)

        if match is None:
            # not a mention
            if ctx.guild:
                result = get(ctx.guild.text_channels, name=argument)
            else:
                def check(c):
                    return isinstance(c, TextChannel) and c.name == argument
                result = find(check, bot.get_all_channels())
        else:
            channel_id = int(search.group(1))
            if ctx.guild:
                result = ctx.guild.get_channel(channel_id)
            else:
                result = self._get_from_guilds(bot, 'get_channel', channel_id)

        if not isinstance(result, TextChannel):
            raise BadArgument('Channel "{}" not found.'.format(argument))

        return result


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
        self.auto_pull = kwargs.pop("auto_pull", True)
        self.debug_mode = kwargs.pop("debug_mode", False)
        self.tz = kwargs.pop("tz", "UTC")

        # Attribute for accessing tokens from file
        self.auth = PickleInterface(f"{self.cwd}\\Serialized\\tokens.pkl")

        # Attribute will be filled in `on_ready`
        self.owner: User = kwargs.pop("owner", None)

        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        super().run(self.auth["MWS_BOT_TOKEN"], *args, **kwargs)

    def connect_dbl(self, autopost: bool = None):

        print("Connecting DBL with token.")
        try:
            if not self.auth["MWS_DBL_TOKEN"]:
                raise DBLException
            dbl = DBLClient(self, self.auth["MWS_DBL_TOKEN"], autopost=autopost)

        except DBLException:
            self.auth["MWS_DBL_TOKEN"] = None
            print("\nDBL Login Failed: No token was provided or token provided was invalid.")
            dbl = None

        if dbl:
            self.auth["MWS_DBL_SUCCESS"] = True
        else:
            self.auth["MWS_DBL_SUCCESS"] = False

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

        for x_loop in self.univ.Loops:
            x_loop.close()

        await super().logout()


class PickleInterface:

    def __init__(self, fp: str = "file.pkl"):  # TODO: Add loop and lock
        self._fp = fp

        try:
            self._fp = self._path
        except Exception as error:
            raise error

    def __getitem__(self, item: Union[str, int]):
        return self._payload.get(item, None)

    def __setitem__(self, key: Union[str, int], val: Union[str, int, bool, None]):
        self._set(key, val)

    @property
    def _path(self):
        dir_path, file_name = split(self._fp)

        file, ext = splitext(file_name)
        if ext != ".pkl":
            raise NameError(f"File name provided is not a valid pickle file (*.pkl): {file_name}")

        if not dir_path:
            dir_path = getcwd()
            self._fp = join(dir_path, file_name)

        try:
            if not exists(self._fp):
                if not exists(dir_path):
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                with open(self._fp, "a"):
                    utime(self._fp, None)

        except PermissionError:
            raise PermissionError(f"Access is denied to file path `{self._fp}`")

        return self._fp

    @property
    def _payload(self):
        with open(self._path, "rb") as fp:
            try:
                payload = dict(load(fp))
            except EOFError:
                payload = dict()
        return payload

    def _set(self, key: str, val: str):
        payload = self._payload
        payload[key] = val
        with open(self._path, "wb") as fp:
            dump(payload, fp)

    def update(self, mapping: Dict):
        for key, val in mapping.items():
            self._set(key, val)

    def get(self, key: Union[str, int], default: Any = None):
        val = self[key]
        return val if val is not None else default

    def keys(self):
        return self._payload.keys()

    def values(self):
        return self._payload.values()

    def items(self):
        return self._payload.items()
