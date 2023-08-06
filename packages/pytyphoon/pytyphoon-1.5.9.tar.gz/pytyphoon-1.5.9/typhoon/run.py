from tornado.platform.asyncio import AsyncIOMainLoop

import asyncio
import argparse
import uvloop
import signal
import json
import os

class ConfigurationComponent:
    def __init__(self, name, Component, ApiComponent, StateManager):
        self.name = name
        self.Component = Component
        self.StateManager = StateManager
        self.ApiComponent = ApiComponent
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        self.init_signals()
        self.parser = argparse.ArgumentParser()
        self.set_base_arguments()
        self.custom_args = {}

    def init_signals(self):
        try:
            self.loop.add_signal_handler(signal.SIGTERM, self.signal_handler, self.loop)
        except:
            pass

    def signal_handler(self):
        self.loop.remove_signal_handler(signal.SIGTERM)
        self.loop.stop()

    def set_base_arguments(self):
        self.parser.add_argument("--config", "-c", help="config filename")
        self.parser.add_argument("--register_host", "-r", help="register host")
        self.parser.add_argument("--debug", "-d", help="debug flag")
        self.parser.add_argument("--project_name", "-pr", help="project name")

    def add_run_argument(self, **kwargs):
        argument = kwargs["argument"]
        self.parser.add_argument("--"+argument, kwargs["short"], help=kwargs["help"])
        self.update_config_by_argument(argument, kwargs["name"])



    def init_config(self):
        self.args = self.parser.parse_args().__dict__
        config_filename = self.args["config"] or "config.json"
        self.config = self.StateManager(json.load(open(os.path.join(os.getcwd(), config_filename))))
        self.update_config_by_arguments()



    def update_config_by_argument(self, argument, config_name):
        self.custom_args[argument] = config_name

    def update_config_by_arguments(self):
        if self.args["register_host"]:
            self.config["register_service"]["host"] = self.args["register_host"]

        for argument in self.custom_args:
            if not argument in self.args: continue
            self.config[self.custom_args[argument]] = self.args[argument]

        self.config["project_name"] = self.args["project_name"]
        self.config["debug"] = bool(int(self.args["debug"]))


    def run(self):
        AsyncIOMainLoop().install()  # set bridge between asyncio and tornado
        self.init_config()
        self.Component(self.config)
        self.ApiComponent(self.config)
