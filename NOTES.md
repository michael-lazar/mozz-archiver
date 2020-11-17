# Mozz Gemini Crawl 2020

## About this Collection

This is an early attempt to archive all publicly facing gemini:// servers for historical preservation. Even though the gemini community is still young, I believe that it's important to record the ecosystem while many of the original servers are still accessible. This archive is comprised of three separate gemini crawls that were made between September 2020 to November 2020.

Each crawl is slightly different as bugs were discovered and the crawling software was refined. Gemini servers were checked for robots.txt files and exclusion rules were obeyed. All gemini requests were recorded verbatim (including malformed & invalid responses) using the WARC 1.1 standard format. The raw log output from the crawling tool was also saved, which includes additional metadata for URLs that failed to download for reasons like TLS errors and robots.txt rules.

## Details

### Summary
 
Crawl           | September  | October    | November
---             | ---        | ---        | ---
Date            | 2020-09-24 | 2020-10-31 | 2020-11-07
Size            | 9.3 GB     | 12.9 GB    | 13.5 GB
Domains seen    | 283        | 276        | 314
Total Responses | 51,995     | 71,632     | 65,347
2x Responses    | 43,425     | 61,771     | 56,680

### September Crawl (1 of 3)

Download: https://archive.org/details/mozz-gemini-crawl-2020-1

This was my first attempt at a global crawl of geminispace. The crawling software crashed after about 3 hours due to an out-of-memory error and unfortunately I was unable to resume it after that. However, a significant amount of URLs were successfully scraped during that window. I also noticed afterwards that some domains were downloaded twice - both with and without the ":1965" at the end of the URL. I changed this behavior so that later crawls would remove the default port number from request URLs.

### October Crawl (2 of 3)

Download: https://archive.org/details/mozz-gemini-crawl-2020-2

This was my second attempt at a global crawl of geminispace. Changes were made to the software to be more resilient against unexpected crashes. This time, the crawler was able to finish successfully. It got tripped up by a few infinite redirect loops and unresponsive domains that I had to manually intervene and block. There was also a bug in the software that caused root URLs to be marked as duplicates. For example, if "gemini://mozz.us" redirected to "gemini://mozz.us/", the latter URL was marked as a duplicate and skipped. This caused the crawler to miss several important gemini home pages.

### November Crawl (3 of 3)

Download: https://archive.org/details/mozz-gemini-crawl-2020-3

This was my third attempt at a global crawl of geminispace. All known bugs from the previous two crawls were fixed. There was a noticeable increase in TLS handshake errors this time around, which I attribute to gemini server admins who were playing around with their TLS settings.

### Operating System Details

Crawling was performed from an ephemeral VPS running Linux.

*Ubuntu 20.04.1 LTS (GNU/Linux 5.4.0-45-generic x86_64)*

```
$ python3 -m OpenSSL.debug
pyOpenSSL: 19.1.0
cryptography: 3.1
cffi: 1.14.2
cryptography's compiled against OpenSSL: OpenSSL 1.1.1g  21 Apr 2020
cryptography's linked OpenSSL: OpenSSL 1.1.1g  21 Apr 2020
Pythons's OpenSSL: OpenSSL 1.1.1g  21 Apr 2020
Python executable: /usr/bin/python3
Python version: 3.8.5 (default, Jul 28 2020, 12:59:40)
[GCC 9.3.0]
Platform: linux
sys.path: ['/root', '/usr/lib/python38.zip', '/usr/lib/python3.8', '/usr/lib/python3.8/lib-dynload', '/usr/local/lib/python3.8/dist-packages', '/usr/lib/python3/dist-packages']
```
