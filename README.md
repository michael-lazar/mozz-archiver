# mozz-archiver

A crawler for [gemini://](https://gemini.circumlunar.space/)

![Spider Moon](logo.jpg)

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

## Example Output

### warcinfo

```
WARC/1.1
WARC-Type: warcinfo
WARC-Record-ID: <urn:uuid:76b03672-2f7e-4cd0-baa4-4116526b37e8>
WARC-Filename: test-20200917163920-000000-10.0.0.232.warc
WARC-Date: 2020-09-17T16:39:20.029734Z
WARC-Block-Digest: sha1:76ZTSZFVDNFFSILAMSTVV5MNWOXII4Z6
Content-Type: application/warc-fields
Content-Length: 441

hostname: ubuntu-s-1vcpu-1gb-nyc1-01
ip: 104.248.235.140
http-header-user-agent: mozz-archiver
robots: classic
operator: Michael Lazar (michael@mozz.us)
software: mozz-archiver/0.0.1 (https://github.com/michael-lazar/mozz-archiver)
isPartOf: testcrawl-20200917
description: testcrawl with WARC output
format: WARC file version 1.1
conformsTo: http://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/
```

### request

```
WARC/1.1
WARC-IP-Address: 174.138.124.169
WARC-Type: request
WARC-Record-ID: <urn:uuid:1d0cf87c-b70a-4df6-9ff8-dd599494058c>
WARC-Target-URI: gemini://mozz.us/cgi-bin/fortune
WARC-Date: 2020-09-17T16:39:20.181428Z
WARC-Concurrent-To: <urn:uuid:ac548616-a66c-44bd-bdfb-faa7eceaae75>
WARC-Payload-Digest: sha1:JXUFJYMU5K7IRZDVPH64R7GSDAJIXLBC
WARC-Block-Digest: sha1:JXUFJYMU5K7IRZDVPH64R7GSDAJIXLBC
Content-Type: application/gemini; msgtype=request
Content-Length: 34

gemini://mozz.us/cgi-bin/fortune
```

### response

```
WARC/1.1
WARC-IP-Address: 174.138.124.169
WARC-Type: response
WARC-Record-ID: <urn:uuid:ac548616-a66c-44bd-bdfb-faa7eceaae75>
WARC-Target-URI: gemini://mozz.us/cgi-bin/fortune
WARC-Date: 2020-09-17T16:39:20.181428Z
WARC-Payload-Digest: sha1:R5HBAWL54A42TXG7GFOUE2LPSQ5MF7J6
WARC-Block-Digest: sha1:R5HBAWL54A42TXG7GFOUE2LPSQ5MF7J6
Content-Type: application/gemini; msgtype=response
Content-Length: 758

20 text/plain
			 ___====-_  _-====___
		  _--~~~#####// '  ` \\#####~~~--_
		-~##########// (    ) \\##########~-_
	       -############//  |\^^/|  \\############-
	     _~############//   (O||O)   \\############~_ 
	    ~#############((     \\//     ))#############~  
	   -###############\\    (oo)    //###############-
	  -#################\\  / `' \  //#################- 
	 -###################\\/  ()  \//###################-
	_#/|##########/\######(  (())  )######/\##########|\#_
	|/ |#/\#/\#/\/  \#/\##|  \()/  |##/\#/  \/\#/\#/\#| \|
	`  |/  V  V  `   V  )||  |()|  ||(  V   '  V /\  \|  '
	   `   `  `      `  / |  |()|  | \  '      '<||>  '
			   (  |  |()|  |  )\        /|/
			  __\ |__|()|__| /__\______/|/
			 (vvv(vvvv)(vvvv)vvv)______|/
```

## License

This software is not currently licensed for public distribution. 

All rights reserved until I figure out what I want to do with it.

Copyright (c) 2020 michael-lazar
