
# Lib
from datetime import datetime
from os import getcwd
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
from typing import List

# Local
from utils.fileinterface import PickleInterface as PI


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


VANITY_AVATARS_TEMPLATE = {
    "guildID": {
        "userID": [
            "avatar_url",
            "previous",
            "is_blocked"
        ]
    }
}
BLACKLISTS_TEMPLATE = {
    "authorID": (["channelID"], ["prefix"])
}
SERVER_BLACKLISTS_TEMPLATE = {
    "guildID": (["channelID"], ["prefix"])
}
CLOSETS_TEMPLATE = {
    "auhthorID": {
        "closet_name": "closet_url"
    }
}


class Bot(DiscordBot):

    def __init__(self, *args, **kwargs):

        # Timer to track minutes since responded to a command
        self.Inactive = 0

        self.cwd = getcwd()

        # List to store scheduled task loops  # TODO: Investigate
        self.Loops = list()

        # Load data from pkl
        try:
            self.user_data_pkl = PI(f"{self.cwd}/Serialized/data.pkl")
            self.DisableSaving = False

            self.VanityAvatars = self.user_data_pkl.get("VanityAvatars", VANITY_AVATARS_TEMPLATE)
            self.Blacklists = self.user_data_pkl.get("Blacklists", BLACKLISTS_TEMPLATE)
            self.ServerBlacklists = self.user_data_pkl.get("ServerBlacklists", SERVER_BLACKLISTS_TEMPLATE)
            self.Closets = self.user_data_pkl.get("Closets", CLOSETS_TEMPLATE)

            print("#-------------------------------#\n"
                  "[DATA LOADED] Loaded data.pkl.\n"
                  "#-------------------------------#\n")

        except FileNotFoundError:
            print("[CANNOT LOAD DATA] data.pkl not found. Replace file before shutting down. Saving disabled.")
            self.DisableSaving = True

            self.VanityAvatars = VANITY_AVATARS_TEMPLATE
            self.Blacklists = BLACKLISTS_TEMPLATE
            self.ServerBlacklists = SERVER_BLACKLISTS_TEMPLATE
            self.Closets = CLOSETS_TEMPLATE

        # Capture extra meta from init for cogs, former `global`s
        self.auto_pull = kwargs.pop("auto_pull", True)
        self.debug_mode = kwargs.pop("debug_mode", False)
        self.tz = kwargs.pop("tz", "UTC")

        # Attribute for accessing tokens from file
        self.auth = PI(f"{self.cwd}/Serialized/tokens.pkl", True)

        # Attribute will be filled in `on_ready`
        self.owner: User = kwargs.pop("owner", None)

        # To be filled by self.connect_dbl() in on_ready
        self.dbl: DBLClient = kwargs.pop("dbl", None)

        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        super().run(self.auth["MWS_BOT_TOKEN"], *args, **kwargs)

    def connect_dbl(self, autopost: bool = None):
        try:
            token = self.auth.get("MWS_DBL_TOKEN")
            self.dbl = DBLClient(self, token, autopost=autopost)

            print("[DBL LOGIN] Logged in to DBL with token.")

        except DBLException:
            self.auth["MWS_DBL_TOKEN"] = None
            self.dbl = None

            print("[DBL ERROR] Login Failed: No token was provided or token provided was invalid.")

    async def get_user_vote(self, user_id: int):
        if user_id == self.owner.id:
            return True

        elif not self.dbl:
            return False

        return await self.dbl.get_user_vote(user_id)

    async def logout(self):  # TODO: Clean this up. A lot was copied from 60s sch task

        time = datetime.now().strftime("%H:%M, %m/%d/%Y")

        if not self.user_data_pkl and not self.DisableSaving:
            self.DisableSaving = True
            print(f"[Unable to save] data.pkl not found. Replace file before shutting down. Saving disabled.")
            # return
    
        if not self.DisableSaving:

            print("Saving...", end="\r")
            data = {
                "VanityAvatars": self.VanityAvatars,
                "Blacklists": self.Blacklists,
                "Closets": self.Closets,
                "ServerBlacklists": self.ServerBlacklists,
                # "ChangelogCache": self.ChangelogCache
            }
            self.user_data_pkl.update(data)
            print(f"[VPP: {time}] Saved data.")

        if self.dbl:
            await self.dbl.close()

        for x_loop in self.Loops:
            x_loop.cancel()

        await super().logout()
