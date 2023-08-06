# -*- coding:utf-8 -*-
"""
使用gridfs 模拟s3服务部分model和接口
"""
import motor


class DummyS3(object):
    """
        dummy s3 conn
    """
    def __getattr__(self, item):
        raise AttributeError("DummyS3 doesn't support %s" % item)

    def __init__(self, mongo):
        self.mongo = mongo

    async def get_bucket(self, bucket):
        return Bucket(bucket, mongo=self.mongo)

    async def lookup(self, bucket):
        return Bucket(bucket, mongo=self.mongo)


class Bucket(object):
    """
    dummy s3 bucket
    """
    def __init__(self, name, mongo):
        self.mongo = mongo
        self.name = name

    async def delete_key(self, name):
        db = motor.MotorGridFS(self.mongo["s3"], collection=self.name)
        f = await db.find_one({"filename": name})
        return await db.delete(f.name)

    async def new_key(self, name):
        return Key(self.name, name, self.mongo)

    async def get_key(self, name):
        return Key(self.name, name, self.mongo)


class Key(object):
    """
    dummy s3 key
    """
    def __init__(self, bucket_name, name, mongo):
        self.bucket_name = bucket_name
        self.name = name
        self.mongo = mongo

    async def set_contents_from_string(self, content):
        db = motor.MotorGridFS(self.mongo["s3"], collection=self.bucket_name)
        await db.put(content, filename=self.name)

    async def set_canned_acl(self, arg):
        pass

    async def get_contents_as_string(self):
        db = motor.MotorGridFS(self.mongo["s3"], collection=self.bucket_name)
        doc = await db.find_one({"filename": self.name})
        return await doc.read()