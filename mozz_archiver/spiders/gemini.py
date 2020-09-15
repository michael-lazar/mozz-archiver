import scrapy

from mozz_archiver.items import GeminiResponseItem


class GeminiSpider(scrapy.Spider):
    name = 'gemini'
    allowed_domains = ['mozz.us']
    start_urls = ['gemini://mozz.us']

    static_routes = [
        "/robots.txt",
        "/favicon.txt",
    ]

    def parse(self, response, **_):
        """
        Parse crawled gemini:// pages.
        """
        if not response.url.startswith('gemini://'):
            return

        for route in self.static_routes:
            yield response.follow(route)

        # We're not at the root URL, try going up one directory
        parent_url = response.get_parent_url()
        if parent_url:
            yield response.follow(parent_url)

        # We received a 3x response and need to follow the redirect
        redirect_url = response.get_redirect_url()
        if redirect_url:
            yield response.follow(redirect_url)

        # Crawl "text/gemini" documents for embedded links
        for request in response.follow_all():
            yield request

        yield GeminiResponseItem.from_response(response)
