import asyncio

from star_builder import Type as _Type
from star_builder.types.validators import FORMATS


class Type(_Type):
    """
    获取属性时为空时，自动load数据
    """
    def __getattr__(self, item):
        """
        实现__getattr__是为了点获取属性时变成异步操作。
        :param item:
        :return:
        """
        loop = asyncio.get_event_loop()
        val_future = loop.create_future()
        properties = super().__getattribute__("validator").properties.keys()

        if item in properties:
            # 对于item存在于properties中的属性，则通过父类去获取
            # 若能获取到，则将future置为done。否则进行异步加载
            try:
                val = super().__getattr__(item)
                val_future.set_result(val)
            except AttributeError:
                self._load(val_future, item)
        else:
            # 不item不存在于properties中，则证明找不到item且item
            # 不是字段。直接将future设置异常。
            val_future.set_exception(AttributeError(item))
        return val_future

    @staticmethod
    async def add_success_callback(fut, callback):
        """
        这个方法的作用相当于future.set_done_callback。
        :param fut:
        :param callback:
        :return:
        """
        try:
            result = await fut
        except Exception as e:
            result = e
        callback(result)
        return result

    def _load(self, val_future, item):
        def set_val(doc_or_exc):
            try:
                self._dict.update(doc_or_exc)
                val_future.set_result(doc_or_exc[item])
            except TypeError:
                val_future.set_exception(doc_or_exc)
            except Exception as e:
                val_future.set_exception(e)

        task = self.add_success_callback(self.load(), set_val)
        asyncio.get_event_loop().create_task(task)

    async def load(self):
        return NotImplemented
