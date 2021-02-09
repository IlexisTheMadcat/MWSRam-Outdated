# Lib
from replit import db
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
        time = datetime.utcnow().strftime("%H:%M")

        if self.bot.inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.config['debug_mode']:
            activity = Activity(
                type=ActivityType.playing,
                name="in DEBUG MODE"
            )

        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.text_status} | UTC: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def save_data(self):
        time = datetime.now().strftime("%H:%M, %m/%d/%Y")

        db.clear()
        db.update(self.bot.user_data)

        self.bot.inactive = self.bot.inactive + 1
        print(f"[VAR: {time}] Running.")

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
