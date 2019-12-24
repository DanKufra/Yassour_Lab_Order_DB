import os
import sqlite3
import datetime

ACTION_ENUM = {'ADD': 0, 'UPDATE': 1, 'DELETE': 2, 'QUERY': 3, 'EXIT': 4}

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname('/cs/usr/dan_kufra/Avital_DB/'), 'database.sqlite3')
COLUMN_INDEX = {'id' : 0, 'order_id': 1, 'distributor': 2,
                'price': 3, 'order_date': 4, 'item': 5,
                'description': 6, 'SAP_number': 7, 'grant_number': 8,
                'sivug_number': 9, 'order_file': 10, 'price_quote_file': 11, 'date_added': 12}
order_sql = """
CREATE TABLE orders (
     id integer NOT NULL,
     order_id integer NOT NULL,
     distributor text NOT NULL,
     price real NOT NULL,
     order_date timestamp NOT NULL,
     item text NOT NULL,
     description text NOT NULL,
     SAP_number integer,
     grant_number integer,
     sivug_number integer,
     order_file text    ,
     price_quote_file text,
     date_added timestamp NOT NULL)
"""


def init_db(db_path):
    if os.path.exists(db_path):
        return
    else:
        con = db_connect(db_path)
        cur = con.cursor()
        cur.execute(order_sql)
        con.close()


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_order(db_path, order_id, item_id, distributor, price, order_date, item, description,
                 SAP_number=None, grant_number=None, sivug_number=None, order_file=None, price_quote_file=None):
    con = db_connect(db_path)
    cur = con.cursor()
    columns_to_add = 'id, order_id, distributor, price, order_date, item, description, date_added'
    if SAP_number is not None:
        columns_to_add += ', SAP_number'
    if grant_number is not None:
        columns_to_add += ', grant_number'
    if sivug_number is not None:
        columns_to_add += ', sivug_number'
    if order_file is not None:
        columns_to_add += ', order_file'
    if price_quote_file is not None:
        columns_to_add += ', price_quote_file'
    values_to_add = '?'
    for i in range(len(columns_to_add.split(',')) - 1):
        values_to_add += ',?'
    order_insert_sql = "INSERT INTO orders (%s) VALUES (%s)" % (columns_to_add, values_to_add)
    cur.execute(order_insert_sql, (item_id, order_id, distributor, price, order_date, item, description, datetime.datetime.now(), SAP_number, grant_number, sivug_number, order_file, price_quote_file))
    con.commit()
    con.close()
    return cur.lastrowid


def update_order(db_path, order_id, item_id=None, distributor=None, price=None, order_date=None, item=None, description=None,
                 SAP_number=None, grant_number=None, sivug_number=None, order_file=None, price_quote_file=None):
    con = db_connect(db_path)
    cur = con.cursor()

    if price is not None and item_id is not None:
        update_sql = "UPDATE orders SET price = ? WHERE ((order_id = ?) AND (id = ?))"
        cur.execute(update_sql, (price, order_id, item_id))
        con.commit()
    if item is not None and item_id is not None:
        update_sql = "UPDATE orders SET item = ? WHERE ((order_id) = ? AND (id = ?))"
        cur.execute(update_sql, (item, order_id, item_id))
        con.commit()
    if description is not None and item_id is not None:
        update_sql = "UPDATE orders SET description = ? WHERE ((order_id = ?) AND (id = ?))"
        cur.execute(update_sql, (description, order_id, item_id))
        con.commit()
    if order_date is not None:
        update_sql = "UPDATE orders SET order_date = ? WHERE order_id = ?"
        cur.execute(update_sql, (order_date, order_id))
        con.commit()
    if SAP_number is not None:
        update_sql = "UPDATE orders SET SAP_number = ? WHERE order_id = ?"
        cur.execute(update_sql, (SAP_number, order_id))
        con.commit()
    if grant_number is not None:
        update_sql = "UPDATE orders SET grant_number = ? WHERE order_id = ?"
        cur.execute(update_sql, (grant_number, order_id))
        con.commit()
    if sivug_number is not None:
        update_sql = "UPDATE orders SET sivug_number = ? WHERE order_id = ?"
        cur.execute(update_sql, (sivug_number, order_id))
        con.commit()
    if distributor is not None:
        update_sql = "UPDATE orders SET distributor = ? WHERE order_id = ?"
        cur.execute(update_sql, (distributor, order_id))
        con.commit()
    if order_file is not None:
        update_sql = "UPDATE orders SET order_file = ? WHERE order_id = ?"
        cur.execute(update_sql, (order_file, order_id))
        con.commit()
    if price_quote_file is not None:
        update_sql = "UPDATE orders SET price_quote_file = ? WHERE order_id = ?"
        cur.execute(update_sql, (price_quote_file, order_id))
        con.commit()
    con.close()
    return cur.lastrowid


def get_next_order_id(db_path):
    con = db_connect(db_path)
    cur = con.cursor()
    max_order_id_sql = "SELECT MAX(order_id) FROM orders"
    cur.execute(max_order_id_sql)
    item = cur.fetchall()
    if item[0][0] is None:
        item = 1
    else:
        item = item[0][0] + 1
    con.close()
    return item


def get_order_by_id(db_path, order_id, item_id=None):
    con = db_connect(db_path)
    cur = con.cursor()
    order_id_get_sql = "SELECT * FROM orders WHERE (order_id = %d)" % order_id
    if item_id is not None:
        order_id_get_sql += " AND (id =%d)" % item_id
    cur.execute(order_id_get_sql)
    item = cur.fetchall()
    con.close()
    return item


def delete_order_by_id(db_path, order_id, item_id=None):
    con = db_connect(db_path)
    cur = con.cursor()
    order_id_get_sql = "DELETE FROM orders WHERE (order_id = %d)" % order_id
    if item_id is not None:
        order_id_get_sql += " AND (id =%d)" % item_id
    cur.execute(order_id_get_sql)
    con.commit()
    con.close()


def query_db_utils(db_path, query_sql):
    con = db_connect(db_path)
    cur = con.cursor()
    cur.execute(query_sql)
    items = cur.fetchall()
    con.close()
    return items