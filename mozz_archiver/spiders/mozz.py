import scrapy

from mozz_archiver.response.gemini import GeminiMapResponse


class MozzSpider(scrapy.Spider):
    name = 'mozz'
    allowed_domains = ['localhost']
    start_urls = ['gemini://localhost/']

    def parse(self, response):
        if isinstance(response, GeminiMapResponse):
            for line in response.text.splitlines(keepends=False):
                if line.startswith('=>'):
                    url = line[2:].strip().split(maxsplit=1)[0]
                    yield response.follow(url)
