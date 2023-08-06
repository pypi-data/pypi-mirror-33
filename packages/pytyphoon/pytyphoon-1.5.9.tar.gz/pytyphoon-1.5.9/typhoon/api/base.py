from traceback import format_exception
from aiohttp import web
import asyncio
import sys
import json

class BaseApi:
    def __init__(self):
        self.components = {}

        self.loop = asyncio.get_event_loop()
        self.errors = {
            0: "Format isn't json",
            100: "Component isn't valid",
            200: "Event not found",
            300: "Request schema error"
        }

    async def isValidRequest(self, request):

        body = None

        try:
            body = await request.json()
        except:
            raise Exception(self.errors[0])

        component = self.get_component(body, request)
        event = self.get_event(body, request)

        if not self.components.get(component):
            raise Exception(self.errors[100])

        if not event:
            raise Exception(self.errors[200])

    def get_subcomponents(self ,request):
        return request.path.split('/')[2:]

    def get_component(self, body, request):

        path  = request.path
        component = path.split('/')[1] if len(path.split('/')) >= 3 else path.strip('/')
        return component or body.get('component')

    def get_event(self, body, request):
        path = request.path
        path_len = len(path.split('/'))
        event = None

        if path_len == 3:
            event = path.split('/')[2]
        elif path_len > 3:
            event = path.split('/')[-1]

        return event or body.get("event")

    def sendError(self, e):
        error = self.getError(e)
        return web.Response(status=500, text=json.dumps(error), headers={
            "Content-Type": "application/json"
        })

    def getError(self, e):
        exc_info = sys.exc_info()
        exception_traceback = "".join(format_exception(*exc_info))
        return {
            "status": False,
            "exception": exception_traceback,
            "message": str(e)
        }