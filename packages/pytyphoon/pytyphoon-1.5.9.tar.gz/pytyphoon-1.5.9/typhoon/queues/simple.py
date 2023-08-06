import asyncio
from .base import BaseQueue


class SimpleQueue(BaseQueue):
    def __init__(self, config, name, postfix=""):
        super().__init__(config, name, postfix)

    async def queue_checker(self, message):
        self.pause()
        await asyncio.sleep(self.config["pause_time"])
        self.start()

    def message_handler(self, message):
        message.enable_async()
        self.callback(self.name, message)
        if self.is_busy() and self.config["pause_time"]:
            self.loop.create_task(self.queue_checker(message))
