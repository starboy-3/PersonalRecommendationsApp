#!/usr/bin/python

from scrapy.cmdline import execute
execute("scrapy crawl wildberries -o items.json".split())
