#!/usr/bin/python

# from scrapy import cmdline
# cmdline.execute("scrapy crawl ya_market".split())


from scrapy.cmdline import execute
execute("scrapy crawl asos -o items.json".split())