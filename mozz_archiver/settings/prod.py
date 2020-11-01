from mozz_archiver.settings.local import *

WARC_DEBUG = False
WARC_GZIP = True
WARC_FILE_PREFIX = 'gemini_oct2020'
WARC_FILE_DIRECTORY = '/mnt/volume_nyc1_01/'
WARC_IS_PART_OF = "gemini-crawl-oct2020"

LOG_FILE = "crawl.log"
JOBDIR = f"crawls/{WARC_IS_PART_OF}"

URL_DENY_LIST = [
    "gemini://gemini.spam.works/mirrors/textfiles/",  # Mirror of www.textfiles.com
    "gemini://fkfd.me/git/cgi/",  # git frontend, very slow to respond
    "gemini://fkfd.me/cgi/",  # git frontend, very slow to respond
    "gemini://gemini.conman.org/test/redirhell",  # I need to fix my crawler...
]
