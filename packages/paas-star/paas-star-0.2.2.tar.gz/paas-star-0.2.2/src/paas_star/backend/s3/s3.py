import asyncio
from boto import connect_s3


class S3(object):

    def __init__(self, *args, **kwargs):
        self.conn = connect_s3(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self.conn, item)

    async def get_bucket(self, bucket):
        loop = asyncio.get_event_loop()
        return Bucket(
            await loop.run_in_executor(None, self.conn.get_bucket, bucket))

    async def lookup(self, bucket):
        loop = asyncio.get_event_loop()
        return Bucket(
            await loop.run_in_executor(None, self.conn.lookup, bucket))


class Bucket(object):
    """
    dummy s3 bucket
    """
    def __init__(self, bucket):
        self.bucket = bucket

    async def delete_key(self, name):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.bucket.delete_key, name)

    async def new_key(self, name):
        return Key(self.bucket.new_key(name))

    async def get_key(self, name):
        loop = asyncio.get_event_loop()
        return Key(await loop.run_in_executor(None, self.bucket.get_key, name))


class Key(object):
    """
    dummy s3 key
    """
    def __init__(self, key):
        self.key = key

    async def set_contents_from_string(self, content):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.key.set_contents_from_string, content)

    async def set_canned_acl(self, arg):
        pass

    async def get_contents_as_string(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.key.get_contents_as_string)
