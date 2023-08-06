import time
import json


class BaseTask:
    def __init__(self, config, task, queue_name=None):
        self.config = config
        self.task = task
        self.queue_name = queue_name
        self.set_component_task()
        self.added_at = time.time()
        self.created_at = time.time()

    def set_component_task(self):
        if self.task:
            self.component_task = self.task.get(self.config["component_name"], {})
            self.set_save_keys()

    def serialize(self):
        return json.dumps(self.task)

    def set_timestamp(self):
        self.added_at = time.time()

    def set_save_keys(self):
        if "save" not in self.component_task:
            self.component_task["save"] = {}
        if "system" not in self.component_task["save"]:
            self.component_task["save"]["system"] = {}
        if "project" not in self.component_task["save"]:
            self.component_task["save"]["project"] = {}

    def set_exception_definition(self, exception, error_def):
        type_, message = exception
        self.component_task["save"]["system"]["exception"] = {
            "type": str(type_) if type_ is not None else None,
            "message": str(message) if message is not None else None,
            "error_definition": error_def
        }