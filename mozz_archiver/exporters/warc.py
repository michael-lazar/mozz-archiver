import socket

from scrapy.exporters import BaseItemExporter
from warcio.warcwriter import WARCWriter


class WARCItemExporter(BaseItemExporter):
    """
    Export requests/responses according to the WARC 1.1 specification.
    """

    def __init__(self, crawler, file, **kwargs):
        super().__init__(**kwargs)
        self.settings = crawler.settings

        gzip = self.settings.get("WARC_GZIP", True)
        warc_version = self.settings["WARC_VERSION"]
        self.writer = WARCWriter(file, gzip=gzip, warc_version=warc_version)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(crawler, *args, **kwargs)

    def start_exporting(self):
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

    def export_item(self, item):
        request_record = self.writer.create_warc_record(
            item['url'],
            'request',
            payload=item['request_payload'],
            warc_content_type='application/gemini; msgtype=request',
            warc_headers_dict={'WARC-IP-Address': item['ip_address']},
        )
        response_record = self.writer.create_warc_record(
            item['url'],
            'response',
            payload=item['response_payload'],
            warc_content_type='application/gemini; msgtype=response',
            warc_headers_dict={'WARC-IP-Address': item['ip_address']},
        )
        self.writer.write_request_response_pair(request_record, response_record)

