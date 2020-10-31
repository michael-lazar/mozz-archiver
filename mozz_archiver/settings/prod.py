from mozz_archiver.settings.local import *

WARC_DEBUG = False
WARC_GZIP = True
WARC_FILE_PREFIX = 'gemini_oct2020'
WARC_FILE_DIRECTORY = '/mnt/volume_nyc1_01/'
WARC_IS_PART_OF = "gemini-crawl-oct2020"

LOG_FILE = "crawl.log"
JOBDIR = f"crawls/{WARC_IS_PART_OF}"
DUPEFILTER_DEBUG = False