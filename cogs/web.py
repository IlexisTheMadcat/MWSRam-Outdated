# Lib
import os
import jinja2
import json
from aiohttp import web
from aiohttp_jinja2 import (
    setup as jinja_setup,
    render_template as html
)
from inspect import isawaitable

# Site
from discord.ext import tasks
from discord.ext.commands import Cog

# Local


app = web.Application()
routes = web.RouteTableDef()

jinja_setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
)


class Webserver(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()
        self.ret = None

        @routes.get('/')
        async def welcome(request):
            return html("home.html", request, context={})

        @routes.post('/send')
        async def send_message(request):
            data = await request.post()
            print("[IN] Sending Message:", dict(data)["text"])
            channel = self.bot.get_channel(self.bot.listening_channel)
            if not channel:
                print("[OUT] Listening channel not found!")
                return html("home.html", request, context={"ret":f"Channel not found!"})
            else:
                message = await channel.send(dict(data)["text"])
                return html("home.html", request, context={"ret":f"Sent message: {message.content}"})

        @routes.post('/evaluate')
        async def evaluate_code(request):
            data = await request.post()
            print("[IN] Running:", dict(data)["evaluation"])
            try:
                self.ret = eval(dict(data)["evaluation"])
            except Exception as e:
                print(f"[OUT] Raised {type(e).__name__}: {e}")
                return html("home.html", request, context={"ret":f"Raised {type(e).__name__}: {e}"})

            if isawaitable(self.ret):
                self.ret = await self.ret
            
            print("[OUT] Returned Result:", self.ret)
            return html("home.html", request, context={"ret":f"Returned Result: {self.ret}"})
        
        @routes.post("/channel")
        async def change_channel(request):
            data = await request.post()
            self.bot.listening_channel = int(dict(data)["channel_change"])
            channel = self.bot.get_channel(self.bot.listening_channel)

            messages = list()
            if channel is not None:
                async for i in channel.history(limit=50):
                    messages.append(i)
            else:
                print("[GET] Channel not found!")
            
            messages.reverse()
            for i in messages:
                print(f"[GET] ----- Message ----- |\n[] {i.author.display_name} ({i.author})\n{i.content if i.content != '' else '[No Content]'}")
                if i.attachments:
                    for x, e in enumerate(i.attachments, 1):
                        print(f"Attachment {x}: {e.url}")
                    
                    print("\n")
            
            raise web.HTTPFound("/")

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