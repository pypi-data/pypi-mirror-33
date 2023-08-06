import types
import inspect

from functools import wraps
from apistar import Route

from ..components.session import Session


def auth(func):
    args = inspect.getfullargspec(func).args
    args_def = ", ".join(args)
    func_def = """
@wraps(func)
async def wrapper(__route, __session, {}):
    from collections.abc import Awaitable
    assert __session.user, "Login required!"
    awaitable = func({})
    if isinstance(awaitable, Awaitable):
        return await awaitable
    return awaitable
    """.format(args_def, args_def)
    namespace = dict(__name__='entries_%s' % func.__name__)
    namespace["func"] = func
    namespace["wraps"] = wraps
    exec(func_def, namespace)

    wrapper = namespace["wrapper"]

    new_func = types.FunctionType(
        wrapper.__code__,
        wrapper.__globals__,
        wrapper.__name__,
        func.__defaults__)
    new_func.__annotations__.update(func.__annotations__)
    new_func.__annotations__["__route"] = Route
    new_func.__annotations__["__session"] = Session
    return new_func
