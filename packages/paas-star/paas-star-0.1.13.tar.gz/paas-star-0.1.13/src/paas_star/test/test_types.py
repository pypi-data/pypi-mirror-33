from paas_star import Type
import asyncio
from star_builder import validators
import uuid
import datetime

class Book(Type):
    id = validators.String(default=uuid.uuid1, format="UUID")
    created_at =validators.DateTime(default=datetime.datetime.now)
    name = validators.String()

    async def load(self):
        return {"name": "张三", }


async def test_model():
    b = Book(name="114")
    #b.format()
    print(b["id"])
    print(b["created_at"])
    print(await b.id)
    created_at = await b.created_at
    print(created_at)
    print(type(created_at))
    print(await b.name)

    b.format()
    b["id"] = "aaaa"
    print(b["id"])


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_model())


main()