from jsonschema import validate
from typhoon.api.base import BaseApi

class BaseComponent(BaseApi):

    def __init__(self, request, state, sub_components=None):
        super().__init__()
        self.sub_components = sub_components
        self.state = state
        self.component = None
        self.request = request
        self.method = self.request.method
        self.headers = self.request.headers
        self.cookies = self.request.cookies
        self.events = {}
        self.schemas = {}
        self.attributes = {}
        self.components = {}
        self.editable_attributes = []
        self.base_errors = {
            0: "Event not found",
            100: "Schema isn't valid",
            200: "Sub component isn't defined"
        }

        self.errors = {
            0: "Attribute not found",
            100: "Attribute isn't editable",
            200: "Value not found",
            300: "Value isn't valid"
        }



    def isValidSubComponent(self, sub_component):
        if not self.components.get(sub_component):
            raise Exception(self.base_errors[200])

    def get_sub_component(self):
        sub_component = None

        if len(self.sub_components) > 1:
            sub_component = self.sub_components[0]
            self.sub_components = self.sub_components[1:]
            self.isValidSubComponent(sub_component)

        return sub_component

    async def isValidEvent(self):
        body = await self.request.json()
        self.event = self.get_event(body, self.request)


        if not self.events.get(self.event):
            raise Exception(self.base_errors[0])

        if self.schemas.get(self.event):
            validate(body, self.schemas[self.event])





    async def init(self):

        body = await self.request.json()
        sub_component = self.get_sub_component()

        if not sub_component:
            await self.isValidEvent()
            return await self.events[self.event]()

        controller = self.components[sub_component](self.request, self.state, self.sub_components)
        response = await controller.init()
        return response

    def success_event(self):
        return {
            "status" : True,
            "event": self.event
        }

    def error_event(self, reason):
        return {
            "status": False,
            "event": self.event,
            "reason": reason
        }

    def validate_change(self, data):
        attribute = data.get("attribute")

        value = data.get("value")

        if not attribute:
            raise Exception(self.errors[0])

        if attribute not in self.editable_attributes:
            raise Exception(self.errors[100])

        if not value:
            raise Exception(self.errors[200])

    async def change(self):
        data = await self.request.json()

        try:
            self.validate_change(data)
            setattr(self.component, data["attribute"], int(data["value"]))
        except Exception as e:
            raise Exception(e)

        return {
            "change": True
        }
