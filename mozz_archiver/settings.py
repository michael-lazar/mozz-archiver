# Scrapy settings for mozz_archiver project

BOT_NAME = 'mozz_archiver'

SPIDER_MODULES = ['mozz_archiver.spiders']
NEWSPIDER_MODULE = 'mozz_archiver.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'mozz-archiver (+https://github.com/michael-lazar/mozz-archiver)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_IP = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 10

# The maximum response size (in bytes) that downloader will download.
DOWNLOAD_MAXSIZE = 1073741824  # 1024 MB

# The response size (in bytes) that downloader will start to warn.
DOWNLOAD_WARNSIZE = 1  # 32 MB

# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 180

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True

DOWNLOADER_CLIENT_TLS_VERBOSE_LOGGING = True

DOWNLOAD_HANDLERS = {
    'gemini': 'mozz_archiver.downloaders.gemini.GeminiDownloadHandler'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'mozz_archiver.middlewares.MozzArchiverSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'mozz_archiver.middlewares.MozzArchiverDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'mozz_archiver.pipelines.MozzArchiverPipeline': 300,
}

