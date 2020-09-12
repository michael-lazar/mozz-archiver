import os
import pathlib
from urllib.parse import urlparse

from scrapy.http import TextResponse


def replace_url_parts(parts, **kwargs):
    # noinspection PyProtectedMember
    return parts._replace(**kwargs)


class GeminiMapResponse(TextResponse):

    @property
    def text(self):
        return self.body.decode(self.encoding)

    def urljoin(self, url):
        base_url = urlparse(self.url)
        parts = urlparse(url)

        if not parts.scheme:
            # Unspecified scheme must be interpreted as gemini://
            parts = replace_url_parts(parts, scheme='gemini')
        elif parts.scheme != 'gemini':
            # Leave non-gemini links alone
            return url

        if not parts.netloc:
            # If netloc is unspecified, use the netloc of the current page
            parts = replace_url_parts(parts, netloc=base_url.netloc)

        if parts.path:
            root_path = pathlib.PurePosixPath(base_url.path)
            link_path = pathlib.PurePosixPath(parts.path)
            if not base_url.path.endswith('/'):
                root_path = root_path.parent

            # noinspection PyTypeChecker
            path = os.path.normpath(root_path / link_path)
            if url.endswith('/') and not path.endswith('/'):
                path += '/'
            parts = replace_url_parts(parts, path=path)

        return parts.geturl()
