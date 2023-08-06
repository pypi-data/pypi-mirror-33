import asyncio
from typhoon.queues.queues_manager import QueuesManager


class BaseComponent:

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()

        self.config = config
        self.queues_manager = QueuesManager(self.config, self.on_message)
        self.loop.create_task(self.on_start())

    def on_message(self, queue_name, message):
        raise NotImplementedError

    async def on_start(self):
        raise NotImplementedError

    def run(self):
        self.queues_manager.start()

    def stop(self):
        self.queues_manager.stop()
        for task in asyncio.Task.all_tasks():
            try:
                pass
                # task.cancel() #
            except:
                pass
