import io
import logging
import os
import socket
import sys
from datetime import datetime

from scrapy import signals
from warcio.warcwriter import WARCWriter

logger = logging.getLogger(__name__)


class WARCExporter:
    """
    Archive responses using the WARC file format.

    References:
        https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/
    """

    def __init__(self, settings):
        self.settings = settings
        self.hostname = socket.gethostname()
        self.ip_address = socket.gethostbyname(self.hostname)
        self.debug = self.settings.getbool('WARC_DEBUG', 'False')
        self.serial = 0
        self._writer = None

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        return ext

    @property
    def writer(self):
        """
        Rotating file writer that will increment once the max size has been reached.
        """
        if not self._writer:
            self._writer = self.build_writer()

        max_file_size = self.settings.getint('WARC_FILE_MAX_SIZE')
        if not self.debug and max_file_size and self._writer.out.tell() > max_file_size:
            self.serial += 1
            self._writer.out.close()
            self._writer = self.build_writer()

        return self._writer

    def build_writer(self):
        """
        Initialize a new WARC file and write the "warcinfo" header.
        """
        directory = self.settings.get('WARC_FILE_DIRECTORY', '.')
        filename = self.build_filename()

        if self.debug:
            fp = sys.stdout.buffer
        else:
            fp = open(os.path.join(directory, filename), 'wb')

        logger.debug(f"Generating WARC file {filename}")
        writer = WARCWriter(
            fp,
            gzip=self.settings.getbool('WARC_GZIP', True),
            warc_version=self.settings['WARC_VERSION'],
        )

        headers = {
            'hostname': self.hostname,
            'ip': self.ip_address,
            'http-header-user-agent': self.settings["USER_AGENT"],
            'robots': 'classic' if self.settings["ROBOTSTXT_OBEY"] else 'none',
            'operator': self.settings.get("WARC_OPERATOR"),
            'software': self.settings.get("WARC_SOFTWARE"),
            'isPartOf': self.settings.get("WARC_IS_PART_OF"),
            'description': self.settings.get("WARC_DESCRIPTION"),
            'format': self.settings.get("WARC_FORMAT"),
            'conformsTo': self.settings.get("WARC_CONFORMS_TO"),
        }
        warcinfo_record = writer.create_warcinfo_record(filename, headers)
        writer.write_record(warcinfo_record)
        return writer

    def build_filename(self):
        """
        Build a filename using the naming convention recommended in the spec.
        """
        filename = '{prefix}-{timestamp}-{serial}-{crawlhost}.warc'.format(
            prefix=self.settings['WARC_FILE_PREFIX'],
            timestamp=datetime.utcnow().strftime('%Y%m%d%H%M%S'),
            serial=str(self.serial).zfill(6),
            crawlhost=self.ip_address
        )
        if self.settings['WARC_GZIP']:
            filename += '.gz'

        return filename

    def engine_stopped(self):
        if self._writer:
            self._writer.out.close()
            self._writer = None

    def build_warc_metadata_payload(self, metadata):
        payload = io.BytesIO()
        for key, val in metadata.items():
            payload.write(f"{key}: {val}\r\n".encode('utf-8'))
        payload.seek(0)
        return payload

    def response_received(self, response, request, spider):
        request_payload = io.BytesIO()
        request_payload.write(response.url.encode('utf-8') + b'\r\n')
        request_payload.seek(0)

        response_payload = io.BytesIO()
        response_payload.write(response.gemini_header + b'\r\n')
        response_payload.write(response.body)
        response_payload.seek(0)

        response_record = self.writer.create_warc_record(
            response.url,
            'response',
            payload=response_payload,
            warc_content_type='application/gemini; msgtype=response',
            warc_headers_dict={'WARC-IP-Address': response.ip_address},
        )
        request_record = self.writer.create_warc_record(
            response.url,
            'request',
            payload=request_payload,
            warc_content_type='application/gemini; msgtype=request',
            warc_headers_dict={'WARC-IP-Address': response.ip_address},
        )
        self.writer.write_request_response_pair(request_record, response_record)

        if self.settings.getbool('WARC_WRITE_METADATA', 'False'):
            metadata = {
                'fetchTimeMs': int(response.meta["download_latency"] * 1000),
            }
            referrer = request.headers.get('Referer')
            if referrer is not None:
                metadata['via'] = referrer.decode()

            metadata_payload = self.build_warc_metadata_payload(metadata)
            metadata_record = self.writer.create_warc_record(
                response.url,
                'metadata',
                payload=metadata_payload,
                warc_headers_dict={
                    'WARC-Date': response_record.rec_headers.get_header('WARC-Date'),
                    'WARC-Concurrent-To': response_record.rec_headers.get_header('WARC-Record-ID')
                },
            )
            self.writer.write_record(metadata_record)
