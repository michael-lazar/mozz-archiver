import logging
import time
from io import BytesIO
from urllib.parse import urldefrag, urlparse

from scrapy.http import Response
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import SSL4ClientEndpoint, connectProtocol
from twisted.internet.error import ConnectionDone, TimeoutError
from twisted.internet.protocol import connectionDone
from twisted.internet.ssl import CertificateOptions, TLSVersion
from twisted.protocols.basic import LineReceiver
from twisted.protocols.policies import TimeoutMixin
from twisted.python.failure import Failure

from mozz_archiver.response.gemini import GeminiMapResponse

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

        endpoint = SSL4ClientEndpoint(
            reactor,
            remote_host,
            remote_port,
            self.context_factory,
            timeout=10
        )

        protocol = GeminiClientProtocol(request, maxsize, warnsize, timeout)
        connectProtocol(endpoint, protocol)
        return protocol.finished


class GeminiClientProtocol(LineReceiver, TimeoutMixin):

    # Map Gemini -> HTTP for interoperability with scrapy middleware
    HTTP_CODE_MAP = {
        '10': 200,
        '11': 200,
        '20': 200,
        '30': 302,
        '31': 301,
        '40': 500,
        '41': 503,
        '42': 500,
        '43': 502,
        '44': 429,
        '50': 400,
        '51': 404,
        '52': 410,
        '53': 400,
        '59': 400,
        '60': 403,
        '61': 403,
        '62': 403,
    }

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
        self.response_header = line
        self.setRawMode()

    def rawDataReceived(self, data):
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
        self.setTimeout(None)

        if self.finished.called:
            return

        self.request.meta['download_latency'] = time.time() - self.start_time

        if reason.check(ConnectionDone):
            response = self.build_response()
            self.finished.callback(response)
        else:
            self.finished.errback(reason)

    def build_response(self):
        """
        Convert the response data into a pseudo-HTTP response.
        """
        header = self.response_header.decode('utf-8')
        header_parts = header.strip().split(maxsplit=1)
        if len(header_parts) == 0:
            status, meta = '', ''
        elif len(header_parts) == 1:
            status, meta = header_parts[0], ''
        else:
            status, meta = header_parts

        headers = {
            'gemini-header': header,
            'gemini-status': status,
            'gemini-meta': meta,
        }
        if status.startswith('2'):
            headers['Content-Type'] = meta
        elif status.startswith('3'):
            headers['Location'] = meta
        elif status == '44':
            headers['Retry-After'] = meta

        http_status = self.HTTP_CODE_MAP.get(status, 400)

        if status.startswith('2') and meta.startswith('text/gemini'):
            meta_keys = {}
            for param in meta.split(';'):
                parts = param.strip().split('=', maxsplit=1)
                if len(parts) == 2:
                    meta_keys[parts[0].lower()] = parts[1]

            response = GeminiMapResponse(
                self.request_url,
                headers=headers,
                status=http_status,
                body=self.response_body.getvalue(),
                certificate=self.transport.getPeerCertificate(),
                ip_address=self.transport.getPeer().host,
                encoding=meta_keys.get('charset', 'UTF-8')
            )
        else:
            response = Response(
                self.request_url,
                headers=headers,
                status=http_status,
                body=self.response_body.getvalue(),
                certificate=self.transport.getPeerCertificate(),
                ip_address=self.transport.getPeer().host
            )

        return response
