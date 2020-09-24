# Scrapy settings for mozz_archiver project

PROJECT_URL = "https://github.com/michael-lazar/mozz-archiver"

BOT_NAME = 'mozz_archiver'
VERSION = '1.1.0'

SPIDER_MODULES = ['mozz_archiver.spiders']
NEWSPIDER_MODULE = 'mozz_archiver.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = f'mozz-archiver'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Print WARC export to stdout instead of a file
WARC_DEBUG = False

# Enable gzip compression on generated WARC files
WARC_GZIP = True

# Max size in bytes of an individual WARC file (for file rotation)
WARC_FILE_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB

# Prefix to append to the beginning of WARC filenames
WARC_FILE_PREFIX = 'gemini_sept2020'

# Directory to save WARC files
WARC_FILE_DIRECTORY = '/mnt/volume_nyc1_01/'

# These params will be placed into the generated "warcinfo" record
WARC_VERSION = "WARC/1.1"
WARC_OPERATOR = 'Michael Lazar (michael@mozz.us)'
WARC_SOFTWARE = f'mozz-archiver/{VERSION} ({PROJECT_URL})'
WARC_IS_PART_OF = "gemini-crawl-sept2020"
WARC_DESCRIPTION = "Geminispace crawl for historical archive"
WARC_FORMAT = 'WARC file version 1.1'
WARC_CONFORMS_TO = 'http://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/'

EXTENSIONS = {
    'mozz_archiver.extensions.WARCExporter': 0,
}

DOWNLOAD_HANDLERS = {
    'gemini': 'mozz_archiver.downloaders.GeminiDownloadHandler',
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
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1

# The maximum response size (in bytes) that downloader will download.
DOWNLOAD_MAXSIZE = 1024 * 1024 * 100  # 100 MB

# The response size (in bytes) that downloader will start to warn.
DOWNLOAD_WARNSIZE = 1024 * 1024 * 32  # 32 MB

# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 60

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True

MEMDEBUG_ENABLED = True

# Enable breadth-first crawl order
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

REACTOR_THREADPOOL_MAXSIZE = 30

DNS_RESOLVER = "mozz_archiver.resolvers.CachingHostnameResolver"

LOG_ENABLED = True
LOG_FILE = "crawl.log"

JOBDIR = f"crawls/{WARC_IS_PART_OF}"

TELNETCONSOLE_USERNAME = "scrapy"
TELNETCONSOLE_PASSWORD = "password"

SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.DownloaderAwarePriorityQueue"
