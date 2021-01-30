# Lib
import os
import jinja2
from aiohttp import web
from aiohttp_jinja2 import (
    setup as jinja_setup,
    render_template as html
)

# Site
from discord.ext import tasks
from discord.ext.commands import Cog

# Local


app = web.Application()
routes = web.RouteTableDef()

jinja_setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "web_templates"))
)


class Webserver(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()
        self.ret = None

        @routes.get('/')
        async def index(request):
            raise web.HTTPFound("/ping")
        
        @routes.get('/ping')
        async def ping(request):
            return html("200.html", request, context={})
        
        self.webserver_port = os.environ.get('PORT', 8080)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Webserver(bot))

# 🐾chat-1 - 741381152543211550
