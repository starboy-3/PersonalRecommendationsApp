import psycopg2
from dynaconf import settings


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
        self.cur.execute("insert into quotes_content(content,author) values(%s,%s)", (item['content'], item['author']))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
