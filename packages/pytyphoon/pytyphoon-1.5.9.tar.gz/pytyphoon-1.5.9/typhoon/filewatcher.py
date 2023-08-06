import time
import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileWatcher:
    def __init__(self, loop=None, directory=os.getcwd() + "/tmp", callback=None):
        self.loop = loop
        self.directory = directory
        self.callback = callback
        self.observer = Observer()
        self.run()

    def close(self):
        self.observer.stop()
        self.observer.join()

    def on_watch(self, event):
        self.callback(event)

    def run(self):
        event_handler = Handler(self.on_watch)
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()


class Handler(FileSystemEventHandler):

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        is_event = event.event_type in ['created', 'modified']
        is_cache = '_tmp___' in event.src_path or '__pycache__' in event.src_path

        if event.is_directory or not is_event or is_cache:
            return None

        self.callback(event)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    def callback(event):
        print("callback", event)

    w = FileWatcher(loop=loop, callback=callback)
    w.run()
    loop.run_forever()

