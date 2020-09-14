import scrapy
import io


from mozz_archiver.items.gemini import GeminiItem


class GeminiSpider(scrapy.Spider):
    name = 'gemini'
    allowed_domains = ['localhost']
    start_urls = ['gemini://localhost']

    static_routes = [
        "/robots.txt",
        "/favicon.txt",
    ]

    def parse(self, response, **_):
        """
        Parse crawled gemini:// pages.
        """
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

        request_payload = io.BytesIO()
        request_payload.write(response.url.encode('utf-8') + b'\r\n')
        request_payload.seek(0)

        response_payload = io.BytesIO()
        response_payload.write(response.gemini_header + b'\r\n')
        response_payload.write(response.body)
        response_payload.seek(0)

        yield GeminiItem(
            url=response.url,
            ip_address=response.ip_address,
            request_payload=request_payload,
            response_payload=response_payload
        )


