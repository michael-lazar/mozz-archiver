# Scrapy settings for mozz_archiver project

PROJECT_URL = "https://github.com/michael-lazar/mozz-archiver"

BOT_NAME = 'mozz_archiver'
VERSION = '0.0.1'

SPIDER_MODULES = ['mozz_archiver.spiders']
NEWSPIDER_MODULE = 'mozz_archiver.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = f'mozz-archiver (+{PROJECT_URL})'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Print WARC export to stdout instead of a file
WARC_DEBUG = True

# Enable gzip compression on generated WARC files
WARC_GZIP = False

# Max size in bytes of an individual WARC file (for file rotation)
WARC_FILE_MAX_SIZE = 2014 ** 3  # 1 GB

# Prefix to append to the beginning of WARC filenames
WARC_FILE_PREFIX = 'test'

# Directory to save WARC files
WARC_FILE_DIRECTORY = '.'

# These params will be placed into the generated "warcinfo" record
WARC_VERSION = "WARC/1.1"
WARC_OPERATOR = 'Michael Lazar (michael@mozz.us)'
WARC_SOFTWARE = f'mozz-archiver/{VERSION} ({PROJECT_URL})'
WARC_IS_PART_OF = None
WARC_DESCRIPTION = None
WARC_FORMAT = 'WARC file version 1.1'
WARC_CONFORMS_TO = 'http://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/'

EXTENSIONS = {
    'mozz_archiver.extensions.warc.WARCExporter': 0,
}

DOWNLOAD_HANDLERS = {
    'gemini': 'mozz_archiver.downloaders.gemini.GeminiDownloadHandler',
}

# Disable a bunch of unnecessary middleware for gemini://
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_IP = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0

# The maximum response size (in bytes) that downloader will download.
DOWNLOAD_MAXSIZE = 1073741824  # 1024 MB

# The response size (in bytes) that downloader will start to warn.
DOWNLOAD_WARNSIZE = 33554432  # 32 MB

# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 60

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True

MEMDEBUG_ENABLED = True