import logging

import scrapy

logger = logging.getLogger(__name__)


class GeminiSpider(scrapy.Spider):
    name = 'gemini'
    allowed_domains = ["localhost"]
    start_urls = ['gemini://localhost']

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
            redirects = response.request.meta.get('redirects', 0) + 1
            if redirects > 6:
                logger.warning(f'Spider reached maximum redirects (6) for URL: {redirect_url}')
            else:
                yield response.follow(redirect_url, meta={'redirects': redirects})

        # Crawl "text/gemini" documents for embedded links
        for request in response.follow_all():
            yield request


class GeminiSpiderProd(GeminiSpider):
    name = 'gemini-prod'
    allowed_domains = []
    start_urls = [
        'gemini://gus.guru/known-hosts',
        'gemini://mozz.us/files/gemini-links.gmi',
        'gemini://gemini.circumlunar.space/servers/',
    ]
