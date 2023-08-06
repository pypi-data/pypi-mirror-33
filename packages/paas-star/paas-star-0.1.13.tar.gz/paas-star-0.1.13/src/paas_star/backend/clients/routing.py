from urllib.parse import urljoin


class RoutingClient(object):
    """The routing Client
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def url(self, path):
        return urljoin(f'http://{self.host}:{self.port}', path)
