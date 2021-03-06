import asyncio
import collections.abc
import json
import os

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal


db_models = {
      "guilds": {
        "ver": 1.0,
        "player_controller": {
            "channel": None,
            "message_id": None
        },
        "djroles": []
    }
}


class LocalDatabase:

    def __init__(self, bot):

        self.bot = bot

        self.data = {
            'guilds': {},
            'users': {}
        }

        self.file_update = 0
        self.data_update = 0

        if not os.path.isfile('database.json'):
            with open('database.json', 'w') as f:
                json.dump(self.data, f)

        else:
            with open('database.json') as f:
                self.data = json.load(f)

        self.bot.loop.create_task(self.write_json_task())

    async def write_json_task(self):

        while True:

            if self.file_update != self.data_update:

                with open('database.json', 'w') as f:
                    json.dump(self.data, f)

                self.file_update += 1

            await asyncio.sleep(30)

    async def get_data(self, id_: int, *, db_name: Literal['users', 'guilds']):

        id_ = str(id_)

        data = self.data[db_name].get(id_)

        if not data:

            data = dict(db_models[db_name])

        return data


    async def update_data(self, id_: int, data: dict, *, db_name: Literal['users', 'guilds']):

        id_ = str(id_)

        self.data[db_name][id_] = data

        self.data_update += 1


class Database:

    def __init__(self, token, name):
        self._connect = AsyncIOMotorClient(token, connectTimeoutMS=30000)
        self._database = self._connect[name]
        self.name = name
        self.cache = {
            'guilds': {},
            'users': {}
        }

    async def push_data(self, data, db_name: Literal['users', 'guilds']):

        db = self._database[db_name]
        await db.insert_one(data)

    async def get_data(self, id_: int, *, db_name: Literal['users', 'guilds']):

        db = self._database[db_name]

        id_ = str(id_)

        data = self.cache[db_name].get(id_)

        if not data:
            data = await db.find_one({"_id": id_})

            if not data:
                data = dict(db_models[db_name])
                data['_id'] = id_
                await self.push_data(data, db_name)

            self.cache[db_name][id_] = data

        return data


    async def update_data(self, id_, data: dict, *, db_name: Literal['users', 'guilds']):

        db = self._database[db_name]

        id_ = str(id_)

        d = await db.update_one({'_id': id_}, {'$set': data}, upsert=False)
        self.cache[db_name][id_] = data
        return d


def update_values(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_values(d.get(k, {}), v)
        elif not isinstance(v, list):
            d[k] = v
    return d
