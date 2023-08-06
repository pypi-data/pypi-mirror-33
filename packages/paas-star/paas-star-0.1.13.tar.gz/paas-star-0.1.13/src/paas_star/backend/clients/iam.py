import json
import aiohttp

from collections import namedtuple
from apistar.exceptions import HTTPException, BadRequest

from .routing import RoutingClient


class UnauthorizedException(HTTPException):
    default_status_code = 401


class IamClient(object):

    def __init__(self, routing: RoutingClient):
        self.routing = routing

    async def who(self, session):
        try:
            async with aiohttp.ClientSession(
                    cookies={"sso_usession": session}) as ses:
                async with ses.get(self.routing.url("/sso/oauth/iam/who"),
                                   headers={'X-Session-Info': session}) as resp:
                    if resp.status in [400, 401, 404]:
                        return None
                    buffer = await resp.read()
        except Exception as e:
            raise BadRequest(detail=str(e)) from e

        if resp.status != 200:
            raise HTTPException(detail=buffer, status_code=resp.status)
        user = json.loads(buffer).get("value")
        if not user:
            raise UnauthorizedException(f"用户不存在 [{session}]")
        return namedtuple("User", user.keys())(**user)
