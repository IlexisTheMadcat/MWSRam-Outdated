
# Lib
from os import popen
from asyncio import sleep
from datetime import datetime

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
        self.save_data.start()
        self.status_change.start()

    @loop(seconds=60)
    async def status_change(self):
        if self.bot.tz != "UTC":
            time = datetime.now().strftime("%H:%M")  # TODO: tz localize
        else:
            time = datetime.utcnow().strftime("%H:%M")

        if self.bot.inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.debug_mode:
            activity = Activity(
                type=ActivityType.playing,
                name="in DEBUG MODE"
            )

        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.command_prefix}help | {self.bot.tz}: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def save_data(self):
        time = datetime.now().strftime("%H:%M, %m/%d/%Y")

        await self.bot.user_data.save()

        self.bot.inactive = self.bot.inactive + 1
        print(f"[VPP: {time}] Saved data.", end="\n" if not self.bot.auto_pull else "\r")

        if self.bot.auto_pull:
            print(f"[VPP: {time}] Saved data. Checking git repository for changes...{' '*30}", end="\r")
            resp = popen("git pull").read()
            resp = f"```diff\n{resp}\n```"
            if str(resp) != f"```diff\nAlready up to date.\n\n```":
                for i in self.bot.owner_ids:
                    owner = self.bot.get_user(i)
                    await owner.send(f"**__Auto-pulled from github repository and restarted cogs.__**\n{resp}")
                    print(f"[VPP: {time}] Saved data. Changes sent to owner via Discord.")

                modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
                for module in modules.keys():
                    self.bot.reload_extension(module)
            else:
                print(f'[VPP: {time}] Saved data. No new changes.{" "*30}')

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
