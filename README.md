# mozz-archiver

A crawler for [gemini://](https://gemini.circumlunar.space/)

## About

This is a general purpose 
crawler for geminispace built using [Scrapy](https://docs.scrapy.org/en/latest/index.html) and some elbow grease.

The objective of this project is to archive geminispace for historical preservation.

All crawled pages are saved using the [WARC/1.1](https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/) file format. The resulting archive will be made publicly available.

## How to restrict access

### Robots.txt

You can restrict this crawler from scraping your gemini server by placing a ``/robots.txt`` file in the root directory.

Wildcard matching is supported according the [Google Robots.txt Specification](https://developers.google.com/search/reference/robots_txt).

The following user agents will be respected:
- ``"*"``
- ``"mozz-archiver"``

Alternatively, you can simply block this crawler's IP address (I won't hold it against you).

If this is not sufficient for your gemini server, send me an email and we can work something out.

## License

This software is not currently licensed for public distribution. 

All rights reserved until I figure out what I want to do with it.

Copyright (c) 2020 michael-lazar
