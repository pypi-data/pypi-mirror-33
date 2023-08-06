import asyncio
import json
import time
from typhoon.tasks.base import BaseTask


class BaseAsync(BaseTask):
    def __init__(self, config, message=None, queue_name=None, task=None):
        super().__init__(config, task, queue_name)
        self.message = message
        self._init_attributes()
        self.set_component_task()

    def _init_attributes(self):
        if self.message and self.queue_name:
            self.task = json.loads(self.message.body)
            self.config_queue = self.config.queues[self.queue_name]
            self.loop = asyncio.get_event_loop()
            self.touching_task = self.loop.create_task(self.touching())

    def done(self):
        finished_at = time.time()
        self.component_task["save"]["system"].update([
            ("added_at", self.added_at),
            ("finished_at", finished_at),
            ("duration", finished_at - self.added_at)
        ])
        self.touching_task.cancel()
        self.message.finish()

    async def touching(self):
        while True:
            self.message.touch()
            await asyncio.sleep(self.get_latency())

    def get_latency(self):
        return self.config_queue["msg_timeout"] - 1
