import db_api
import psycopg2


def main():
    try:
        connection = psycopg2.connect(user="u_shops",
                                      password="HSEPAassword2022",
                                      host="77.37.164.38",
                                      port="5432",
                                      database="shops")
        cursor = connection.cursor()


    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")



main()
