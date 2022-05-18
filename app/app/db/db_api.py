import psycopg2

def insert_shop(name: str, rating: float, cursor: psycopg2.extensions.cursor):
    cursor.execute(
        """
        insert into shops(name, rating) values (%s, %s)
        """,
        (name, rating, )
    )

def select_shop_by_name(name: str, cursor: psycopg2.extensions.cursor) -> list:
    cursor.execute(
        """
        select name, rating from shops where name = %s
        """,
        name
    )
    return cursor.fetchall() # list of (name, rating, seller_id)

def insert_product(name: str, , cursor: psycopg2.extensions.cursor):

