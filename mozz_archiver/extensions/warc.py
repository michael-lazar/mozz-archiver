import io
import logging
import sys
import socket

from scrapy import signals
from warcio.warcwriter import WARCWriter

logger = logging.getLogger(__name__)


class WARCExporter:

    def __init__(self, settings):
        self.settings = settings
        self.writer = WARCWriter(
            sys.stdout.buffer,
            gzip=self.settings.getbool('WARC_GZIP', True),
            warc_version=self.settings['WARC_VERSION'],
        )

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings)

        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)

        return ext

    def engine_started(self):
        headers = {
            'ip': socket.gethostbyname(socket.gethostname()),
            'http-header-user-agent': self.settings["USER_AGENT"],
            'robots': 'classic' if self.settings["ROBOTSTXT_OBEY"] else 'none',
            'hostname': self.settings.get("WARC_HOSTNAME"),
            'operator': self.settings.get("WARC_OPERATOR"),
            'software': self.settings.get("WARC_SOFTWARE"),
            'isPartOf': self.settings.get("WARC_IS_PART_OF"),
            'description': self.settings.get("WARC_DESCRIPTION"),
            'format': self.settings.get("WARC_FORMAT"),
            'conformsTo': self.settings.get("WARC_CONFORMS_TO"),
        }

        filename = self.writer.out.name
        warcinfo_record = self.writer.create_warcinfo_record(filename, headers)
        self.writer.write_record(warcinfo_record)

    def response_received(self, response, request, spider):

        request_payload = io.BytesIO()
        request_payload.write(response.url.encode('utf-8') + b'\r\n')
        request_payload.seek(0)

        response_payload = io.BytesIO()
        response_payload.write(response.gemini_header + b'\r\n')
        response_payload.write(response.body)
        response_payload.seek(0)

        request_record = self.writer.create_warc_record(
            response.url,
            'request',
            payload=request_payload,
            warc_content_type='application/gemini; msgtype=request',
            warc_headers_dict={'WARC-IP-Address': response.ip_address},
        )
        response_record = self.writer.create_warc_record(
            response.url,
            'response',
            payload=response_payload,
            warc_content_type='application/gemini; msgtype=response',
            warc_headers_dict={'WARC-IP-Address': response.ip_address},
        )
        self.writer.write_request_response_pair(request_record, response_record)
