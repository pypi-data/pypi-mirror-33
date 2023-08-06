import random
import sys
import json
import socket
import asyncio
import aiohttp

from aiohttp import web

from .base import BaseApi

class Api(BaseApi):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.app = web.Application()
        self.port = None

    def init_router(self):
        pass

    async def request_register(self, session, params):
        register_service = self.state["register_service"]
        data = {
            "component":"registration",
            "event":"register",
            "additional":{
                "component": self.state["component_name"],
                "port": self.port,
                "project": self.state["project_name"]
            }
        }
        data["additional"].update(params)
        async with session.post("http://{}:{}".format(register_service["host"], register_service["port"]), json=data) as response:
            return response, await response.read()

    async def register_component(self, params={}):

        async with aiohttp.ClientSession() as session:
            response, content = await self.request_register(session, params)

    def up(self):
        self.init_router()
        self.port = self.get_port()
        if self.state["register_service"]:
            self.loop.create_task(self.register_component())

        web.run_app(self.app, port=self.port)

    def get_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = None
        for p in range(8000, 65535):
            try:
                s.bind(("", int(p)))
                s.listen(1)
                port = s.getsockname()[1]
                s.close()
                break
            except Exception as e:
                continue
        return port

    def close(self):
        self.app.shutdown()

    async def handler(self, request):

        response = None

        try:
            await self.isValidRequest(request)
            body = await request.json()
            component = self.get_component(body,request)
            controller = self.components[component](request, self.state, self.get_subcomponents(request))
            response = await controller.init()

        except Exception as e:

            return self.sendError(e)

        return web.Response(text=json.dumps(response), headers={
            "Content-Type": "application/json"
        })