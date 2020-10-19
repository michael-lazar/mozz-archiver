import logging

import scrapy

logger = logging.getLogger(__name__)


class GeminiSpider(scrapy.Spider):
    name = 'gemini'
    allowed_domains = []
    start_urls = ["gemini://gus.guru/known-hosts"]

    def parse(self, response, **_):
        """
        Parse crawled gemini:// pages.
        """
        if not response.url.startswith('gemini://'):
            logger.warning(f'Spider received unexpected URL: {response.url}')
            return

        yield response.follow('/favicon.txt')

        # Try going up one directory
        parent_url = response.get_parent_url()
        yield response.follow(parent_url)

        # We received a 3x response and need to follow the redirect
        redirect_url = response.get_redirect_url()
        if redirect_url:
            yield response.follow(redirect_url)

        # Crawl "text/gemini" documents for embedded links
        for request in response.follow_all():
            yield request
