# db_utils.py
import os
import sqlite3
import datetime

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname('/cs/usr/dan_kufra/Avital_DB/'), 'database.sqlite3')
order_sql = """
CREATE TABLE orders (
     id integer PRIMARY KEY,
     distributor text NOT NULL,
     price real NOT NULL,
     order_date timestamp NOT NULL,
     description text NOT NULL)
"""


def init_db(path):
	if os.path.exists(path):
		return
	else:
		con = db_connect()
		cur = con.cursor()
		cur.execute(order_sql)

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

def create_order(distributor, price, order_date, description):
	con = db_connect()
	cur = con.cursor()
	order_insert_sql = "INSERT INTO orders (distributor, price, order_date, description) VALUES (?, ?, ?, ?)"
	cur.execute(order_insert_sql, (distributor, price, order_date, description))
	con.commit()
	return cur.lastrowid 

def update_order(id, distributor=None, price=None, order_date=None, description=None):
	con = db_connect()
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
	if description is not None:
		update_sql = "UPDATE orders SET description = ? WHERE id = ?"
		cur.execute(update_sql, (description, id))
	return cur.lastrowid 



def create_query(id=None, distributor=None, price=None, order_date=None):
	pass


if __name__ == '__main__':
	# test db
	init_db(DEFAULT_PATH)
	id = create_order("bob", 9.99, datetime.datetime.now(), 'labels')
	results = get_order_by_id(id)
	for row in results:
		print(row)



#TODOS
"""
1. Create load gui, update gui and search gui.
2. Create simple not range filter for id
3. Extend to range filter for id.
4. Extend to filters for all types.
"""