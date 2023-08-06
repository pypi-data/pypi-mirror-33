import nsq
import json
import asyncio
import requests

class BaseQueue:
    def __init__(self, config, name, postfix):
        self.name = name
        self.status = False
        self.installed_reader = False
        self.addresses = []
        self.config = config
        self.loop = asyncio.get_event_loop()
        self.config_queue = self.config.queues[self.name]
        self.channel = self.config_queue["channel"]
        self.postfix = postfix
        self.topic = self.get_topic()
        self.init()

    def get_topic(self):
        topic = "{}_{}".format(self.config["project_name"], self.config_queue["topic"] + self.postfix)

        if not self.config_queue.get("share"):
            topic = "{}_{}".format(self.config["component_name"],topic)

        if self.config["debug"]:
            topic = "{}_debug".format(topic)

        return topic

    def init(self):
        self.nsqlookupd_ip = "nsqlookupd:4161"
        self.get_nsqd_ips()
        self.init_writer()

    def init_writer(self):
        tcp_addresses = ["{}:4150".format(ip) for ip in self.addresses]
        if self.config_queue.get("writable"):
            self.writer = nsq.Writer(tcp_addresses)


    def install_topic(self):
        if self.topic in self.config["topics"]: return
        http_addresses = ["{}:4151".format(ip) for ip in self.addresses]
        for nsqd_ip in http_addresses:
            requests.post("http://{}/topic/create?topic={}".format(nsqd_ip, self.topic))
            requests.post("http://{}/channel/create?topic={}&channel=tasks".format(nsqd_ip, self.topic))

        self.config["topics"].append(self.topic)


    def init_reader(self):
        if self.installed_reader: return
        self.install_topic()
        self.reader = nsq.Reader(
            topic=self.topic, channel=self.channel, message_handler=self.message_handler,
            lookupd_connect_timeout=10, requeue_delay=10, msg_timeout=self.msg_timeout,
            lookupd_http_addresses=[self.nsqlookupd_ip], max_in_flight=self.concurrent, max_backoff_duration=256
        )
        self.installed_reader = True
        if not self.status:
            self.reader.set_max_in_flight(0)

    @property
    def msg_timeout(self):
        return self.config_queue["msg_timeout"]

    @msg_timeout.setter
    def msg_timeout(self, value):
        self.config_queue["msg_timeout"] = value
        self.init_reader()

    def is_busy(self):
        return self.reader.is_starved()

    def pause(self):
        self.status = False
        self.reader.set_max_in_flight(0)

    def set_callback(self, callback):
        self.callback = callback

    @property
    def concurrent(self):
        return self.config_queue["concurrent"]

    @concurrent.setter
    def concurrent(self, value):
        self.config_queue["concurrent"] = value
        if self.status:
            print("change concurrent on " + self.topic, self.concurrent)
            self.reader.set_max_in_flight(0)
            self.init_reader()
            self.reader.set_max_in_flight(self.concurrent)

    def start(self):
        print("CALL start from q: ", self.status, self.topic, self.concurrent, self.is_busy())
        if not self.status:
            self.status = True
            print("Start Queue", self.topic, self.concurrent)

            self.reader.set_max_in_flight(self.concurrent)

    def get_nsqd_ips(self):
        data = requests.get("http://{}/nodes".format(self.nsqlookupd_ip)).content
        nodes = json.loads(data.decode())
        for producer in nodes.get("producers"):
            ip = producer["remote_address"].split(':')[0]
            self.addresses.append(ip)

    def delay_push(self, message, delay):

        self.writer.dpub(self.topic, delay*1000, message.encode())

    def push(self, message):
        self.writer.pub(self.topic, message.encode())

    def get_stats(self):
        stats = []
        for ip in self.addresses:
            data = json.loads(requests.get('http://{}:4151/stats?format=json&topic={}'.format(ip,self.topic)).content.decode())
            for topic in data["topics"]:
                if topic["topic_name"] != self.topic:
                    continue

                for channel in topic["channels"]:
                    if channel["channel_name"] != self.channel:
                        continue
                    stats.append(channel)
        return stats

    async def queue_checker(self, message):
        raise NotImplementedError

    def message_handler(self, message):
        raise NotImplementedError
