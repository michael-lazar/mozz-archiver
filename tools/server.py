import sqlite3
import argparse
import pathlib
from urllib.parse import urlparse

from warcio.archiveiterator import ArchiveIterator

from jetforce import GeminiServer, Status

parser = argparse.ArgumentParser()
parser.add_argument('--warc-dir', default="warc")
parser.add_argument('--index', default="index.sqlite")
args = parser.parse_args()

conn = sqlite3.connect(args.index, isolation_level=None)
conn.row_factory = sqlite3.Row

warc_dir = pathlib.Path(args.warc_dir).resolve()


def proxy_request(environ, send_status):
    url = environ['GEMINI_URL']

    # Attempt some URL normalization, but don't fail if the URL is malformed
    try:
        url_parts = urlparse(url)
        if url_parts.path == "/":
            url = url.strip("/")
        if url_parts.port == 1965:
            url = url.replace(":1965", "", 1)
    except Exception:
        pass

    c = conn.execute('SELECT * FROM requests WHERE url=?', (url,))
    row = c.fetchone()
    if not row:
        send_status(Status.PROXY_ERROR, "ARCHIVE-ERROR: URL not found in archive")
        return

    if row['error_message']:
        send_status(Status.PROXY_ERROR, f"ARCHIVE-ERROR: {row['error_message']}")
        return

    warc_file = warc_dir / row['warc_filename']
    with warc_file.open("rb") as fp:
        fp.seek(int(row["warc_offset"]))
        iterator = iter(ArchiveIterator(fp))
        record = next(iterator)
        content = record.content_stream()
        while data := content.read(2 ** 14):
            yield data


if __name__ == "__main__":
    c = conn.execute('SELECT COUNT(*) FROM requests')
    result = c.fetchone()
    print(f'Loaded WARC index with {result[0]} entries')

    server = GeminiServer(proxy_request)
    server.run()
