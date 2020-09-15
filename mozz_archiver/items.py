import io

from scrapy import Item, Field


class GeminiResponseItem(Item):
    ip_address = Field()
    url = Field()
    header = Field()
    body = Field(serializer=lambda _: "<body>")
    status = Field()
    meta = Field()
    params = Field()
    charset = Field()

    def __str__(self):
        return f"GeminiResponseItem <{self['header'].decode('utf-8')}>"

    @classmethod
    def from_response(cls, response):
        return cls(
            ip_address=response.ip_address,
            url=response.url,
            header=response.gemini_header,
            body=response.body,
            status=response.gemini_status,
            meta=response.gemini_meta,
            params=response.gemini_params,
            charset=response.charset,
        )

    def get_request_payload(self):
        request_payload = io.BytesIO()
        request_payload.write(self['url'].encode('utf-8') + b'\r\n')
        request_payload.seek(0)
        return request_payload

    def get_response_payload(self):
        response_payload = io.BytesIO()
        response_payload.write(self['header'] + b'\r\n')
        response_payload.write(self['body'])
        response_payload.seek(0)
        return response_payload
