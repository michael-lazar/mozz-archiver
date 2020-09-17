import os
import pathlib
from urllib.parse import urlparse

from scrapy.http import Response


def replace_url_parts(parts, **kwargs):
    # noinspection PyProtectedMember
    return parts._replace(**kwargs)


class GeminiResponse(Response):
    """
    Response that encapsulates a gemini:// response.
    """

    def __init__(self, url, gemini_header, **kwargs):
        super(GeminiResponse, self).__init__(url, **kwargs)

        self.is_gemini_map = False
        self._text = None

        header = gemini_header.decode('utf-8')
        header_parts = header.strip().split(maxsplit=1)
        if len(header_parts) == 0:
            status, meta = '', ''
        elif len(header_parts) == 1:
            status, meta = header_parts[0], ''
        else:
            status, meta = header_parts

        params = {}
        charset = None
        if status.startswith('2'):
            for param in meta.split(';'):
                parts = param.strip().split('=', maxsplit=1)
                if len(parts) == 2:
                    params[parts[0].lower()] = parts[1]

            if meta.startswith('text/'):
                charset = params.get('charset', 'utf-8')
                self._text = self.body.decode(charset)

            if meta.startswith('text/gemini'):
                self.is_gemini_map = True

        self.gemini_header = gemini_header
        self.gemini_status = status
        self.gemini_meta = meta
        self.gemini_params = params
        self.charset = charset

    @property
    def text(self):
        return self._text

    def get_links(self):
        if self.is_gemini_map:
            for line in self.text.splitlines(keepends=False):
                if line.startswith('=>'):
                    link = line[2:].strip().split(maxsplit=1)[0]
                    yield link

    def get_parent_url(self):
        """
        Generate the parent URL by removing the last path component.

        This can be used to crawl "up" a directory and search for hidden directory
        listing pages.
        """
        parts = urlparse(self.url)
        path = pathlib.PurePosixPath(parts.path).parent
        url_parts = replace_url_parts(parts, path=str(path), params='', query='', fragment='')
        parent_url = url_parts.geturl()
        return parent_url

    def get_redirect_url(self):
        if self.gemini_status.startswith('3'):
            return self.gemini_meta
        else:
            return None

    def follow_all(self, urls=None, gemini_only=True, **kwargs):
        if not urls:
            urls = []
            for link in self.get_links():
                url = self.urljoin(link)
                if not gemini_only or url.startswith('gemini://'):
                    urls.append(url)

        return super().follow_all(urls=urls, **kwargs)

    def urljoin(self, link_url):
        """
        Convert potentially relative gemini links into full URLs.

        The base Response class has a method for this, but it doesn't seem to
        work properly for all of the edge cases that I tested for gemini://
        URLs. This was copied over from the method that I use for portal.mozz.us.
        """
        base_parts = urlparse(self.url)
        link_parts = urlparse(link_url)

        if not link_parts.scheme:
            # Unspecified scheme must be interpreted as gemini://
            link_parts = replace_url_parts(link_parts, scheme='gemini')
        elif link_parts.scheme != 'gemini':
            # Leave non-gemini links alone
            return link_url

        if not link_parts.netloc:
            # If netloc is unspecified, use the netloc of the current page
            link_parts = replace_url_parts(link_parts, netloc=base_parts.netloc)

        if link_parts.path:
            root_path = pathlib.PurePosixPath(base_parts.path)
            link_path = pathlib.PurePosixPath(link_parts.path)
            if not base_parts.path.endswith('/'):
                root_path = root_path.parent

            # noinspection PyTypeChecker
            path = os.path.normpath(root_path / link_path)
            if link_url.endswith('/') and not path.endswith('/'):
                path += '/'
            link_parts = replace_url_parts(link_parts, path=path)

        return link_parts.geturl()
