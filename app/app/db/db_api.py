import psycopg2


def insert_shop(name: str, rating: float, cursor: psycopg2.extensions.cursor):
    cursor.execute(
        """
        insert into shops(name, rating) values (%s, %s) returning seller_id
        """,
        (name, rating, )
    )
    return cursor.fetchone()  # returns seller_id of inserted shop


def select_shop_by_name(name: str, cursor: psycopg2.extensions.cursor) -> list:
    cursor.execute(
        """
        select name, rating from shops where name = %s
        """,
        name
    )
    return cursor.fetchone()  # list of (name, rating, seller_id)]


def get_all_shops(cursor: psycopg2.extensions.cursor) -> list:
    cursor.execute("select * from shops")
    return cursor.fetchall()  # returns (seller_id: autoincrement, int, name: str, rating: float)


def insert_product(name: str, brand: str, description: str, category: str, price: int, shop_name: str,
                   cursor: psycopg2.extensions.cursor):  # !!! Только в рублях !!!
    shop_id = select_shop_by_name(name, cursor)  # == seller_id
    if len(shop_id) == 0:
        raise DropItem(f"Shop {shop_name} doesn't exist in shops table")
    insert_product_by_seller_id(name, brand, description, category, price, shop_id, cursor)


def insert_product_by_seller_id(name: str, brand: str, description: str, category: str, price: int, seller_id: int,
                                cursor: psycopg2.extensions.cursor):  # !!! Только в рублях !!!
    cursor.execute(
        """
        insert into products(name, brand, description, category, price, seller_id) values (%s, %s, %s, %s, %s, %s)
        """,
        (name, brand, description, category, price, seller_id, )
    )


def get_product_by_seller_id(seller_id: int, cursor: psycopg2.extensions.cursor):
    cursor.execute(
        """
        select * from products where seller_id = %s
        """,
        (seller_id, )
    )
    return cursor.fetchall()
