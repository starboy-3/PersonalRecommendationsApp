import psycopg2

def insert_shop(name: str, seller_id: int, cursor: psycopg2.extensions.cursor):
    cursor.execute(
        """
        insert into shops(seller_id, name) values (%s, %s) ON CONFLICT ON CONSTRAINT shop_id DO NOTHING
        """,
        (seller_id, name,)
    )


def select_shop_by_name(name: str, cursor: psycopg2.extensions.cursor) -> list:
    cursor.execute(
        """
        select seller_id, name from shops where name = %s
        """,
        name
    )
    return cursor.fetchone()  # list of (name, rating, seller_id)]


def get_all_shops(cursor: psycopg2.extensions.cursor) -> list:
    cursor.execute("select * from shops")
    return cursor.fetchall()  # returns (seller_id: autoincrement, int, name: str, rating: float)

def insert_product_by_seller_id(name: str, brand: str, description: str, category: str, price: int, seller_id: int,
                                image_link: str, link: str,
                                cursor: psycopg2.extensions.cursor):  # !!! Только в рублях !!!
    cursor.execute(
        """
        insert into products(brand, category, link, price, description, seller_id, name, image_link) values (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (brand, category, link, price, description, seller_id, name, image_link,)
    )


def get_product_by_seller_id(seller_id: int, cursor: psycopg2.extensions.cursor):
    cursor.execute(
        """
        select * from products where seller_id = %s
        """,
        (seller_id,)
    )
    return cursor.fetchall()
