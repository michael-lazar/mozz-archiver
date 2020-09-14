from scrapy import Item, Field


class GeminiItem(Item):
    url = Field()
    ip_address = Field()
    request_payload = Field()
    response_payload = Field()


