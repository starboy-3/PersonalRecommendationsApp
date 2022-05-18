# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
# from itemadapter import ItemAdapter
from dynaconf import settings

class AppPipeline:
    def __init__(self):
        self.cur = None
        self.connection = None

    def open_spider(self, spider):
        hostname = settings.db_hostname # localhost
        username = settings.db_username # 'postgres'
        password = settings.password # TODO: password
        database = settings.db_name # 'app' #TODO:
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()


    def process_item(self, item, spider):
        self.cur.execute() # FIXME:
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
