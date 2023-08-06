import aioredis
import motor.motor_asyncio
import asyncio

class CacheStorage:

    def __init__(self, config, loop):
        self.config = config
        self.loop = loop
        self.redis_con = None

    async def init_connection(self):
        if self.config["redis"]:
            await self.init_redis()
        if self.config["mongo"]:
            self.init_mongo()

    def get_db_settings(self, name):
        db_config = self.config[name]["debug"] if self.config["debug"] else self.config[name]["production"]
        return db_config["host"], db_config["port"], db_config["password"], db_config.get("db_name")

    async def init_redis(self):
        host, port, password, _ = self.get_db_settings("redis")
        self.redis_con = await aioredis.create_redis(address=(host, port), password=password)

    def init_mongo(self):
        host, port, password, db_name = self.get_db_settings("mongo")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            host, port,
            password=password
        )
        self.db = self.client[db_name]

    def get_mongo_collection(self, collection_name):
        return self.db[collection_name]

    async def set(self, key, value):
        await self.redis_con.set(key, value)

    async def scan(self, cur, match):
        return await self.redis_con.scan(cur, match=match, count=100)

    async def delete(self, keys):
        await self.redis_con.delete(*keys)

    async def set_ex(self, key, value, time_in_sec):
        await self.redis_con.setex(key, time_in_sec, value)

    async def mget(self, keys):
        return await self.redis_con.mget(*keys)

    async def mset(self, *pairs):
        """pairs key, value"""
        await self.redis_con.mset(*pairs)

    async def get(self, key):
        return await self.redis_con.get(key)

    async def increment(self, key, amount=1):
        await self.redis_con.incrby(key, amount)


# IT'S ONLY FOR METHODS TESTING
if __name__ == "__main__":
    import asyncio
    config = {
        "debug": True,
        "redis": {
            "debug": {
                "port": 6379,
                "host": "localhost",
                "password": None
            }
        }
    }
    loop = asyncio.get_event_loop()

    def main():
        r = CacheStorage(config, loop)
        loop.create_task(_main(r))
        # print(r.redis_con)
        # await r.set("sec", "11101234123")
        # print(r.get("sec"))
    # loop.create_task(main)

    async def _main(conn):
        a = ['project:907f66d736b76cd3fe02ac7c20aa20d4', 'project:907f66d736b76cd3fe02ac7c20aa20d4', 'project:227dbe5431183b973472d30cae4a1f64', 'project:907f66d736b76cd3fe02ac7c20aa20d4', 'project:227dbe5431183b973472d30cae4a1f64', 'project:907f66d736b76cd3fe02ac7c20aa20d4', 'project:227dbe5431183b973472d30cae4a1f64']
        await conn.init_connection()
        await asyncio.sleep(2)
        # print(conn.redis_con)
        print(await conn.mget(a))
        # print(await conn.get("sec"))


    main()
    loop.run_forever()
    # loop.run_until_complete(main())
