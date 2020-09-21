class HostnameResolver:

    def __init__(self, reactor):
        self.reactor = reactor

    @classmethod
    def from_crawler(cls, crawler, reactor):
        return cls(reactor)

    def install_on_reactor(self):
        pass
