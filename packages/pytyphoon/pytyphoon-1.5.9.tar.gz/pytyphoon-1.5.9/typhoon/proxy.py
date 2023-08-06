import json
import aiohttp
import asyncio


class Proxy:

    @staticmethod
    async def next_proxy(config, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config["proxy-manager-api"] + "/url=" + url) as response:
                    data = await response.text()
        except Exception as e:
            raise Exception("Network error: {}".format(e))

        current_proxy = json.loads(data)

        return current_proxy


if __name__ == "__main__":
    import os
    config = json.load(open(os.path.join(os.getcwd(), "config.json")))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Proxy.next_proxy(config, "www.newegg.com"))
