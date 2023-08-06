from .base import BaseQueue


class PriorityQueue(BaseQueue):
    def __init__(self, config, name, postfix):
        super().__init__(config, name, postfix)

    def message_handler(self, message):
        message.enable_async()
        self.callback(message)
