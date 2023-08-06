import asyncio

class BaseStateManager:
    def __init__(self, config):
        self.config = config
        self.loop = asyncio.get_event_loop()

    def __getattr__(self, item):
        return self.config.get(item)

    def __getitem__(self, item):
        return self.config.get(item)

    def __setitem__(self, key, value):
        self.config[key] = value