import db_api
import psycopg2
from dynaconf import settings


def main():
    hostname = settings["db_hostname"]
    username = settings['db_username']
    password = settings['db_password']
    database = settings["db_name"]
    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    try:
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from shops"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows")
        mobile_records = cursor.fetchall()

        print("Print each row and it's columns values")
        for row in mobile_records:
            print("Seller_id  = ", row[0],)
            print("Name = ", row[1], )
            print("Rating = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


main()
