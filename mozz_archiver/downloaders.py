import logging
import time
from io import BytesIO
from urllib.parse import urldefrag, urlparse

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import SSL4ClientEndpoint, connectProtocol, HostnameEndpoint, wrapClientTLS
from twisted.internet.error import ConnectionDone, ConnectionLost
from twisted.internet.protocol import connectionDone
from twisted.internet.ssl import CertificateOptions, TLSVersion
from twisted.internet._sslverify import ClientTLSOptions
from twisted.protocols.basic import LineReceiver
from twisted.protocols.policies import TimeoutMixin

from mozz_archiver.responses import GeminiResponse

logger = logging.getLogger(__name__)


class GeminiDownloadHandler:
    """
    Scrapy download handler for gemini:// scheme URLs.

    This implementation is *heavily* based on scrapy's HTTP 1.1 and telnet
    handlers as references. I did, however, make several attempts to simplify
    the code and use idiomatic twisted patterns. Some integrity checks had to
    be removed since gemini does not use a Content-Length or checksum. Since
    scrapy is built around HTTP requests/responses, this code will take the
    gemini response and generate a pseudo-HTTP response with an equivalent
    status code and headers. This is necessary to retain compatibility with
    most of the library's middleware.
    """
    lazy = False

    def __init__(self, settings, crawler=None):
        self.crawler = crawler

        self.default_maxsize = settings.getint('DOWNLOAD_MAXSIZE')
        self.default_warnsize = settings.getint('DOWNLOAD_WARNSIZE')
        self.fail_on_dataloss = settings.getbool('DOWNLOAD_FAIL_ON_DATALOSS')

        self.context_factory = CertificateOptions(
            verify=False,
            raiseMinimumTo=TLSVersion.TLSv1_2,
            fixBrokenPeers=True,
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def download_request(self, request, spider):
        bindaddress = request.meta.get('bindaddress')
        timeout = request.meta.get('download_timeout')

        maxsize = getattr(spider, 'download_maxsize', self.default_maxsize)
        warnsize = getattr(spider, 'download_warnsize', self.default_warnsize)

        parts = urlparse(request.url)
        remote_host = bindaddress or parts.hostname
        remote_port = parts.port or 1965

        hostname = HostnameEndpoint(reactor, remote_host, remote_port)
        # The recommended helper method for this (optionsForClientTLS) does not
        # allow setting up a client context that accepts unverified certificates.
        # So we are forced to use the private ClientTLSOptions method instead.
        options = ClientTLSOptions(remote_host, self.context_factory.getContext())
        # noinspection PyTypeChecker
        endpoint = wrapClientTLS(options, hostname)

        logger.debug(f"Creating download request for {request.url}")
        protocol = GeminiClientProtocol(request, maxsize, warnsize, timeout)
        connectProtocol(endpoint, protocol)
        return protocol.finished


class GeminiClientProtocol(LineReceiver, TimeoutMixin):

    def __init__(self, request, maxsize, warnsize, timeout):
        self.request = request
        self.maxsize = maxsize
        self.warnsize = warnsize
        self.timout = timeout

        self.reached_warnsize = False

        self.request_url = urldefrag(self.request.url).url
        self.response_header = b''
        self.response_body = BytesIO()
        self.response_size = 0

        # Ideally this timer would start exactly when we send out the TCP SYN,
        # but I don't know how to hook into that event with twisted.
        self.start_time = time.time()

        self.finished = Deferred(self.cancel)

    def cancel(self, _):
        self.transport.abortConnection()

    def connectionMade(self):
        self.setTimeout(self.timout)
        self.sendLine(self.request_url.encode("utf-8"))

    def timeoutConnection(self):
        logger.error(
            f"Getting {self.request} took longer than {self.timout} seconds."
        )
        self.transport.abortConnection()

    def lineReceived(self, line):
        logger.debug(f"Line received, {self.request.url}")
        self.response_header = line
        self.setRawMode()

    def rawDataReceived(self, data):
        logger.debug(f"Data received ({len(data)}), {self.request.url}")

        self.response_body.write(data)
        self.response_size += len(data)

        if self.maxsize and self.response_size > self.maxsize:
            logger.error(
                f"Received ({self.response_size}) bytes larger than download "
                f"max size ({self.maxsize}) in request {self.request}."
            )

            # Clear buffer earlier to avoid keeping data in memory for a long time.
            self.response_body.truncate(0)
            self.finished.cancel()

        if self.warnsize and self.response_size > self.warnsize and not self.reached_warnsize:
            self.reached_warnsize = True
            logger.warning(
                f"Received more bytes than download warn size "
                f"({self.warnsize}) in request {self.request}."
            )

    def connectionLost(self, reason=connectionDone):
        logger.debug(f"Connection lost ({reason}), {self.request.url}")

        self.setTimeout(None)

        if self.finished.called:
            return

        self.request.meta['download_latency'] = time.time() - self.start_time

        # Many gemini servers kill the connection uncleanly, i.e. ConnectionLost
        if reason.check(ConnectionDone, ConnectionLost):
            response = self.build_response()
            self.finished.callback(response)
        else:
            self.finished.errback(reason)

    def build_response(self):
        """
        Convert the response data into a pseudo-HTTP response.
        """
        return GeminiResponse(
            self.request_url,
            gemini_header=self.response_header,
            body=self.response_body.getvalue(),
            certificate=self.transport.getPeerCertificate(),
            ip_address=self.transport.getPeer().host,
        )
