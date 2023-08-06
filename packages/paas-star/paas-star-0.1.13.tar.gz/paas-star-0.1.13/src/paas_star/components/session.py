from apistar import http
from star_builder import Component, Cookie

from ..backend.iam import Iam


class Session(object):
    def __init__(self, sid: str, iam: Iam):
        self.sid = sid
        self.iam = iam
        self.user = None
    
    async def get_user(self):
        self.user = self.sid and (await self.iam.who(self.sid))


class SessionComponent(Component):

    async def resolve(self, iam: Iam,
                x_session_info: http.Header,
                x_user_info: http.Header,
                session: Cookie,
                token: Cookie) -> Session:

        sid = x_session_info or x_user_info or session or token
        session = Session(sid, iam)
        await session.get_user()
        return session
