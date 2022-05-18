#!/usr/bin/python

from scrapy.cmdline import execute
execute("scrapy crawl easy -o items.json".split())
