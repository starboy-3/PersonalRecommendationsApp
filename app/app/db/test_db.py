import db_api
import psycopg2
from config import settings


def main():
    hostname = settings["db_hostname"]
    username = settings['db_username']
    password = settings['db_password']
    database = settings["db_name"]
    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    connection.set_session(autocommit=True)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "insert into shops(name, rating) values (%s, %s) RETURNING seller_id;",
            ("d", 4.7, )
        )
        id = cursor.fetchall()
        print(id)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


main()
