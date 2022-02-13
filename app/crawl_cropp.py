#!/usr/bin/python

from scrapy.cmdline import execute
execute("scrapy crawl cropp -o items.json".split())
