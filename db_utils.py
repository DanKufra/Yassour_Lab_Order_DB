import os
import sqlite3
import datetime

ACTION_ENUM = {'ADD': 0, 'UPDATE': 1, 'DELETE': 2, 'QUERY': 3, 'EXIT': 4}

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname('/cs/usr/dan_kufra/Avital_DB/'), 'database.sqlite3')
order_sql = """
CREATE TABLE orders (
     id integer PRIMARY KEY,
     distributor text NOT NULL,
     price real NOT NULL,
     order_date timestamp NOT NULL,
     item text NOT NULL,
     description text NOT NULL)
"""


def init_db(db_path):
    if os.path.exists(db_path):
        return
    else:
        con = db_connect(db_path)
        cur = con.cursor()
        cur.execute(order_sql)


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_order(db_path, distributor, price, order_date, item, description):
    con = db_connect(db_path)
    cur = con.cursor()
    order_insert_sql = "INSERT INTO orders (distributor, price, order_date, item, description) VALUES (?, ?, ?, ?, ?)"
    cur.execute(order_insert_sql, (distributor, price, order_date, item, description))
    con.commit()
    return cur.lastrowid


def update_order(db_path, id, distributor=None, price=None, order_date=None, item=None, description=None):
    con = db_connect(db_path)
    cur = con.cursor()
    if distributor is not None:
        update_sql = "UPDATE orders SET distributor = ? WHERE id = ?"
        cur.execute(update_sql, (distributor, id))
    if price is not None:
        update_sql = "UPDATE orders SET price = ? WHERE id = ?"
        cur.execute(update_sql, (price, id))
    if order_date is not None:
        update_sql = "UPDATE orders SET order_date = ? WHERE id = ?"
        cur.execute(update_sql, (order_date, id))
    if item is not None:
        update_sql = "UPDATE orders SET item = ? WHERE id = ?"
        cur.execute(update_sql, (item, id))
    if description is not None:
        update_sql = "UPDATE orders SET description = ? WHERE id = ?"
        cur.execute(update_sql, (description, id))
    con.commit()
    return cur.lastrowid


def get_order_by_id(db_path, id):
    con = db_connect(db_path)
    cur = con.cursor()
    order_id_get_sql = "SELECT * FROM orders WHERE id = %d" % id
    cur.execute(order_id_get_sql)
    item = cur.fetchall()
    if len(item) > 0:
        return item[0]
    else:
        return None


def delete_order_by_id(db_path, id):
    #TODO how to delete?
    con = db_connect(db_path)
    cur = con.cursor()
    order_id_get_sql = "DELETE FROM orders WHERE id = %d" % id
    cur.execute(order_id_get_sql)
    con.commit()


def query_db_utils(db_path, query_sql):
    con = db_connect(db_path)
    cur = con.cursor()
    cur.execute(query_sql)
    items = cur.fetchall()
    return items