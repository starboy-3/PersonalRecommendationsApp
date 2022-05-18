#!/usr/bin/python

from scrapy.cmdline import execute
execute("scrapy crawl ozon -o items.csv".split())
