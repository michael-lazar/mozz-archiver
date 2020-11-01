"""
This custom sqlite scheduler backend is derived from:
https://github.com/filyph/scrapy-sqlite

Modified work, Copyright (c) 2020 Michael Lazar
Original work, Copyright (c) 2017 Filip Hanes

Modified work is not licensed, all rights reserved.
Original work is distributed under the following license.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import sqlite3
import pickle
import logging

from scrapy.utils.misc import load_object, create_instance
from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.pqueues import DownloaderInterface
from scrapy.exceptions import IgnoreRequest
from scrapy import signals

logger = logging.getLogger(__name__)


SQL_INITIALIZE_TABLE = """
CREATE TABLE IF NOT EXISTS "scheduler" (
    downloading BOOLEAN,
    slot TEXT,
    priority INTEGER,
    url TEXT,
    request_data BLOB
);
CREATE INDEX IF NOT EXISTS request_state_index
    ON "scheduler" (downloading, slot, priority);
"""


class Scheduler(object):
    """
    Custom scrapy scheduler that cuts out ~3 levels of cruft and abstraction.

    The primary motivation for writing my own scheduler was the desire to be
    as tolerant as possible to unexpected crashes (e.g. OOM kills) without
    losing state. Consistency >>> performance. This scheduler is tuned for
    large, multi-site crawls. In the case of data loss, crawling the same URL
    twice is better than not crawling it at all.

    This class is loosely based off the scrapy-sqlite package but I ended up
    changing quite a bit. It prioritizes breadth-first domain crawling in the
    same way as the DownloaderAwarePriorityQueue.
    """

    def __init__(self, dupefilter, conn, stats, downloader_interface, crawler):
        self.dupefilter = dupefilter
        self.conn = conn
        self.stats = stats
        self.downloader_interface = downloader_interface
        self.crawler = crawler

        crawler.signals.connect(
            self.on_request_left_downloader, signal=signals.request_left_downloader
        )

    @staticmethod
    def connect_db(database):
        conn = sqlite3.connect(database, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.executescript(SQL_INITIALIZE_TABLE)
        return conn

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        dupefilter = create_instance(dupefilter_cls, settings, crawler)

        jobdir = settings.get('JOBDIR')
        if jobdir:
            dbname = '{spider}.sqlite3'.format(spider=crawler.spider.name)
            database = os.path.join(jobdir, dbname)
        else:
            database = ":memory:"

        downloader_interface = DownloaderInterface(crawler)
        conn = cls.connect_db(database)
        return cls(dupefilter, conn, crawler.stats, downloader_interface, crawler)

    def __len__(self):
        c = self.conn.execute('SELECT COUNT(*) FROM "scheduler" WHERE downloading=false;')
        result = c.fetchone()
        if result:
            return int(result[0])

    def has_pending_requests(self):
        return bool(len(self))

    def open(self, spider):
        self.spider = spider

        # Reschedule any unfinished downloads
        self.conn.execute('UPDATE "scheduler" SET downloading=false;')

        if self.has_pending_requests():
            spider.log("Resuming crawl ({} requests scheduled)".format(len(self)))

    def close(self, reason):
        self.conn.close()

    def begin_immediate_transaction(self, cursor):
        cursor.execute('BEGIN IMMEDIATE TRANSACTION')

    def encode_request(self, request):
        request_dict = request_to_dict(request, self.spider)
        return pickle.dumps(request_dict)

    def decode_request(self, request_data):
        request_dict = pickle.loads(request_data)
        return request_from_dict(request_dict, self.spider)

    def enqueue_request(self, request):
        request_data = self.encode_request(request)
        slot = self.downloader_interface.get_slot_key(request)

        if not request.dont_filter and self.dupefilter.request_seen(request):
            self.dupefilter.log(request, self.spider)
            return False

        self.dupefilter.file.flush()

        c = self.conn.cursor()
        c.execute(
            'INSERT INTO "scheduler" VALUES (?,?,?,?,?);',
            (False, slot, request.priority, request.url, request_data)
        )
        self.stats.inc_value('scheduler/enqueued', spider=self.spider)
        return True

    def next_request(self):
        # Prioritize the slot that has the minimum number of active downloads
        c = self.conn.cursor()
        c.execute(
            'SELECT slot FROM "scheduler" GROUP BY slot '
            'ORDER BY SUM(downloading) LIMIT 1;'
        )
        rows = c.fetchone()
        if not rows:
            return None

        slot = rows[0]

        c = self.conn.cursor()
        c.execute(
            'SELECT rowid, request_data FROM "scheduler" '
            'WHERE downloading=? AND slot=? '
            'ORDER BY priority DESC LIMIT 1',
            (False, slot)
        )
        row = c.fetchone()
        if not row:
            return None

        row_id, request_data = row
        self.conn.execute(
            'UPDATE "scheduler" SET downloading=? WHERE rowid=?',
            (True, row_id)
        )

        request = self.decode_request(request_data)
        self.stats.inc_value('scheduler/dequeued/sqlite', spider=self.spider)

        # Stash the row id so we can delete the request from the table once it
        # has either finished downloading or raised an exception.
        request.row_id = row_id

        # If a request is rejected by the downloader middleware, it will never
        # reach the downloader to trigger the request left downloader signal.
        # One solution would be to add a custom DownloaderMiddleware that
        # implemented the process_exception() method and triggered a custom
        # signal. This solution is slightly more hacky, but accomplished the
        # same thing without needing any extra custom classes.
        assert request.errback is None
        request.errback = self.on_request_error

        return request

    def on_request_error(self, failure):
        if failure.check(IgnoreRequest):
            self.remove_request(failure.request)

    def on_request_left_downloader(self, request, *_):
        self.remove_request(request)

    def remove_request(self, request):
        if hasattr(request, 'row_id'):
            self.conn.execute(
                'DELETE FROM "scheduler" WHERE rowid=?', (request.row_id,)
            )
