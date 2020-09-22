from scrapy.resolver import dnscache
from twisted.internet.interfaces import IHostnameResolver, IResolutionReceiver
from twisted.internet._resolver import HostResolution
from zope.interface.declarations import implementer, provider


class HostnameResolver:

    def __init__(self, reactor):
        self.reactor = reactor

    @classmethod
    def from_crawler(cls, crawler, reactor):
        return cls(reactor)

    def install_on_reactor(self):
        pass


@implementer(IHostnameResolver)
class CachingHostnameResolver:
    """
    Experimental caching resolver. Resolves IPv4 and IPv6 addresses,
    does not support setting a timeout value for DNS requests.
    """

    def __init__(self, reactor, cache_size):
        self.reactor = reactor
        self.original_resolver = reactor.nameResolver
        dnscache.limit = cache_size

    @classmethod
    def from_crawler(cls, crawler, reactor):
        if crawler.settings.getbool('DNSCACHE_ENABLED'):
            cache_size = crawler.settings.getint('DNSCACHE_SIZE')
        else:
            cache_size = 0
        return cls(reactor, cache_size)

    def install_on_reactor(self):
        self.reactor.installNameResolver(self)

    def resolveHostName(
        self,
        resolutionReceiver,
        hostName,
        portNumber=0,
        addressTypes=None,
        transportSemantics="TCP",
    ):

        cached_addresses = dnscache.get(hostName)
        if cached_addresses:
            resolutionReceiver.resolutionBegan(HostResolution(hostName))
            for address in cached_addresses:
                resolutionReceiver.addressResolved(address)
            resolutionReceiver.resolutionComplete()
            return resolutionReceiver

        @provider(IResolutionReceiver)
        class CachingResolutionReceiver:

            def __init__(self):
                self.addresses = []

            def resolutionBegan(self, resolution):
                resolutionReceiver.resolutionBegan(resolution)

            def addressResolved(self, address):
                resolutionReceiver.addressResolved(address)
                self.addresses.append(address)

            def resolutionComplete(self):
                resolutionReceiver.resolutionComplete()
                if self.addresses:
                    dnscache[hostName] = tuple(self.addresses)

        return self.original_resolver.resolveHostName(
            CachingResolutionReceiver(),
            hostName,
            portNumber,
            addressTypes,
            transportSemantics,
        )
