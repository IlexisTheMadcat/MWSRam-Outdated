
# Lib
from os import popen, getcwd
from os.path import join, exists
from asyncio import sleep
from datetime import datetime
from pickle import dump

# Site
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.ext.commands.cog import Cog
from discord.ext.tasks import loop

# Local
from utils.classes import Bot


class BackgroundTasks(Cog):
    """Background loops"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.dblpy = self.bot.connect_dbl()
        self.bot.univ.Loops = []
        self.bot.univ.Loops.append(self.save_data.start())
        self.bot.univ.Loops.append(self.status_change.start())
        self.bot.univ.Loops.append(self.auto_pull_github.start())

    @loop(seconds=60)
    async def status_change(self):
        if self.bot.tz != "UTC":
            hour = str(datetime.now().hour)
            minute = str(datetime.now().minute)
            if len(hour) == 1:
                hour = "0" + hour
            if len(minute) == 1:
                minute = "0" + minute
            time = f"{hour}:{minute}"

        else:
            utchour = str(datetime.utcnow().hour)
            utcminute = str(datetime.utcnow().minute)
            if len(utchour) == 1:
                utchour = "0" + utchour
            if len(utcminute) == 1:
                utcminute = "0" + utcminute
            time = f"{utchour}:{utcminute}"

        if self.bot.univ.Inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.debug_mode:
            activity = Activity(type=ActivityType.playing, name="IN DEBUG MODE")
        elif self.bot.univ.DisableSaving:
            activity = Activity(type=ActivityType.listening, name=f"SAVING DISABLED")
        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.command_prefix}help | {self.bot.tz}: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def save_data(self):
        hour = str(datetime.now().hour)
        minute = str(datetime.now().minute)
        date = str(str(datetime.now().date().month) + "/" + str(datetime.now().date().day) + "/" + str(
            datetime.now().date().year))
        if len(hour) == 1:
            hour = "0" + hour
        if len(minute) == 1:
            minute = "0" + minute
        time = f"{hour}:{minute}, {date}"

        if not (exists(join(getcwd(), "Serialized", "data.pkl")) and
                exists(join(getcwd(), "Serialized", "bot_config.pkl"))) and \
                not self.bot.univ.DisableSaving:

            self.bot.univ.DisableSaving = True
            print(
                f"[{time} || Unable to save] data.pkl and/or bot_config.pkl not found. Replace file before "
                f"shutting down. Saving disabled.")

            return

        elif (exists(join(getcwd(), "Serialized", "data.pkl")) and
              exists(join(getcwd(), "Serialized", "bot_config.pkl"))) and \
                self.bot.univ.DisableSaving:

            self.bot.univ.DisableSaving = False
            print(f"[{time}] Saving re-enabled.")
            return

        if not self.bot.univ.DisableSaving:
            print("Saving...", end="\r")
            with open(join(getcwd(), "Serialized", "data.pkl"), "wb") as f:
                data = {
                    "VanityAvatars": self.bot.univ.VanityAvatars,
                    "Blacklists": self.bot.univ.Blacklists,
                    "Closets": self.bot.univ.Closets,
                    "ServerBlacklists": self.bot.univ.ServerBlacklists,
                    "ChangelogCache": self.bot.univ.ChangelogCache
                }

                try:
                    dump(data, f)
                except Exception as e:
                    print(f"[{time} || Unable to save] Pickle dumping Error:", e)

            with open(join(getcwd(), "Serialized", "bot_config.pkl"), "wb") as f:
                config_data = {
                    "debug_mode": self.bot.debug_mode,
                    "auto_pull": self.bot.auto_pull,
                    "tz": self.bot.tz
                }

                try:
                    dump(config_data, f)
                except Exception as e:
                    print("[Unknown Error] Pickle dumping error:", e)

            self.bot.univ.Inactive = self.bot.univ.Inactive + 1
            print(f"[VPP: {time}] Saved data.")
    
    @loop(seconds=60)
    async def auto_pull_github(self):
        if self.bot.auto_pull:
            print("Checking git repository for changes...", end="\r")
            resp = popen("git pull").read()
            resp = f"```diff\n{resp}\n```"
            if str(resp) != f"```diff\nAlready up to date.\n\n```":
                await self.bot.owner.send(f"**__Auto-pulled from github repository__**\n{resp}")
                print("Changes sent to owner via Discord.")
                for x_loop in self.bot.univ.Loops:
                    x_loop.cancel()

                modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
                for module in modules.keys():
                    self.bot.reload_extension(module)
                # await self.bot.logout()
            else:
                print(f'No new changes.{" "*25}')

    @auto_pull_github.before_loop  # Start these 2 loops opposite of each other
    async def apg_wait(self):
        await self.bot.wait_until_ready()
        await sleep(45)

    @status_change.before_loop
    async def sc_wait(self):
        await self.bot.wait_until_ready()
        await sleep(30)

    @save_data.before_loop
    async def sd_wait(self):
        await self.bot.wait_until_ready()
        await sleep(15)


def setup(bot: Bot):
    bot.add_cog(BackgroundTasks(bot))
