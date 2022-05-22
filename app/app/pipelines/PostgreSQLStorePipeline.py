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
        # FIXME            retrieving fields from item
        db_api.insert_shop(name=shop_name, seller_id=seller_id, cursor=cursor)
        db_api.insert_product_by_seller_id(name=product_name,
                                           brand=brand,
                                           description=description,
                                           seller_id=seller_id,
                                           image_link=image_link,
                                           link=link,
                                           price=price,
                                           category=category,
                                           cursor=cursor)
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
