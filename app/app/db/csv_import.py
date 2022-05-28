import csv
from config import settings
import psycopg2
import db_api


def import_from(path: str):
    hostname = settings["db_hostname"]
    username = settings['db_username']
    password = settings['db_password']
    database = settings["db_name"]
    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    connection.set_session(autocommit=True)
    cursor = connection.cursor()
    with open(path, 'r') as file:
        read = csv.reader(file)
        read2 = [row for row in read]
        for i in range(1, len(read2)):
            reader = read2[i]

            brand = reader[0]
            category = reader[1]
            link = reader[2]
            price = reader[3]
            description = reader[4]
            seller_id = reader[5]
            shop_name = reader[6]
            product_name = reader[7]
            image_link = reader[8]
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

    connection.close()


path = '/Users/akosimov/Desktop/ozon.csv'
import_from(path)
