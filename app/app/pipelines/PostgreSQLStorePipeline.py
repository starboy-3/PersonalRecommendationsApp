import psycopg2
from config import settings
import db_api

class PostgreSQLStorePipeline:
    def __init__(self):
        self.cur = None
        self.connection = None

    def open_spider(self, spider):
        hostname = settings["db_hostname"]
        username = settings['db_username']
        password = settings['db_password']
        database = settings["db_name"]
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        self.connection.set_session(autocommit=True)

    def process_item(self, item, spider):
        db_api.insert_shop(name=item['shop_name'], seller_id=item['seller_id'], cursor=item['cursor'])
        db_api.insert_product_by_seller_id(name=item['product_name'],
                                           brand=item['brand'],
                                           description=item['description'],
                                           seller_id=item['seller_id'],
                                           image_link=item['image_link'],
                                           link=item['link'],
                                           price=item['price'],
                                           category=item['category'],
                                           cursor=item['cursor'])
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
