import os
import asyncio
import importlib
from typhoon.filewatcher import FileWatcher


class BaseManager:
    def __init__(self, callback, config, last_level_path):
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.callback = callback
        self.directory = os.path.join(os.getcwd(), "project", last_level_path)
        self.init_watcher()
        self.strategies = {
            "http": {
                "strategy": None,
                "handler": None,
                "class": None,
                "module": None
            },
            "local": None,
            "ftp": None,
            "database": None
        }
    def init_watcher(self):
        if os.path.exists(self.directory):
            self.file_watcher = FileWatcher(callback=self.on_file_watch, directory=self.directory)
    def reload_handlers(self):
        for strategy in self.strategies:
            if not self.strategies[strategy]:
                continue
            importlib.reload(self.strategies[strategy]["module"])
            name = self.strategies[strategy]["class"]
            self.strategies[strategy]["handler"] = self.strategies[strategy]["module"].__dict__[name]

    def on_file_watch(self, event):
        print("Changed", event.src_path)
        self.reload_handlers()

    def close(self):
        self.file_watcher.close()
