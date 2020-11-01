import logging

from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)


class URLDenyMiddleware:
    """
    Downloader middleware that will ignore requests based on URL patterns.
    """

    def __init__(self, urls, crawler):
        self.urls = tuple(urls)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        urls = crawler.settings.getlist('URL_DENY_LIST', [])
        return cls(urls, crawler)

    def process_request(self, request, spider):
        if request.url.startswith(self.urls):
            logger.debug("Forbidden by URL deny list: %(request)s",
                         {'request': request}, extra={'spider': spider})
            self.crawler.stats.inc_value('urldeny/forbidden')
            raise IgnoreRequest("Forbidden by URL deny list")
