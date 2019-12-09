import argparse as argparse
import numpy as np
from gui_interface import gui_create_db, gui_load_db, gui_option_window, \
    gui_add_order, gui_update_order, gui_message, gui_get_order_id, gui_query
from db_utils import db_connect, init_db, create_order, update_order, get_order_by_id, delete_order_by_id, query_db_utils, ACTION_ENUM


def create_new_db():
    db_path = gui_create_db()
    init_db(db_path)
    return db_path


def load_db():
    db_path = gui_load_db()
    return db_path


def add_order_to_db(db_path):
    order = gui_add_order()
    if order is None:
        gui_message('Order not added properly.')
        return
    id = create_order(db_path=db_path, distributor=order['distributor'], price=order['price'],
                      order_date=order['date'], item=order['item'], description=order['description'])
    # TODO how to catch failure?
    gui_message('Order added to DB.')


def update_order_in_db(db_path):
    order_id = gui_get_order_id()
    if order_id is None:
        gui_message('Order id not picked properly.')
        return
    original_order = get_order_by_id(db_path, order_id)
    if original_order is None:
        gui_message('Order id does not exist.')
        return

    order = gui_update_order(original_order)
    if order is None:
        gui_message('Order not updated properly.')
        return
    id = update_order(db_path=db_path, id=order_id, distributor=order['distributor'], price=order['price'],
    	order_date=order['date'], description=order['description'])
    # TODO how to catch failure?
    gui_message('Order updated in DB.')

def delete_order_in_db(db_path):
    order_id = gui_get_order_id()
    if order_id is None:
        gui_message('Order not deleted properly.')
        return
    id = delete_order_by_id(db_path=db_path, id=order_id)
    # TODO how to catch failure?
    gui_message('Order deleted from DB.')

def create_query(values):
    query = "SELECT * FROM orders WHERE "
    num_conds = 0
    if values['id_filter'] != '':
        if values['id_filter'] == 'RANGE':
            query += '(id >= %d and id <= %d )' %(values['id_start'],values['id_end']) 
        else:
            query += '(id %s %d)' %(values['id_filter'], values['id_start'])
        num_conds += 1
    if values['price_filter'] != '':
        if num_conds > 0:
            query += ' AND '
        if values['price_filter'] == 'RANGE':
            query += '(price >= %f and price <= %f )' %(values['price_start'],values['price_end']) 
        else:
            query += '(price %s %f)' %(values['price_filter'], values['price_start'])

    if values['distributor'] != '':
        if num_conds > 0:
            query += ' AND '
        query += '(distributor = "%s" ) ' % values['distributor'] 

    if values['item'] != '':
        if num_conds > 0:
            query += ' AND '
        query += '(item = "%s" ) ' % values['item']
    return query

def query_db(db_path):
    con = db_connect(db_path)
    cur = con.cursor()
    unique_distributors_sql = "SELECT distinct(distributor) FROM orders ORDER BY distributor ASC"
    unique_items_sql = "SELECT distinct(item) FROM orders ORDER BY item ASC"
    cur.execute(unique_distributors_sql)
    unique_distributors = cur.fetchall()
    cur.execute(unique_items_sql)
    unique_items = cur.fetchall()
    query_values = gui_query(unique_distributors, unique_items)
    query_sql = create_query(query_values)
    print(query_sql)
    print(query_db_utils(db_path, query_sql))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str,
                        help='What mode to run our db interface in',
                        default='load')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    # Either create a new db or load an existing one
    if args.mode == 'new':
        db_path = create_new_db()
    elif args.mode == 'load':
        db_path = load_db()
    while True:
	    # Open gui window that decides whether to add order, update order, filter order
	    action = gui_option_window()

	    # # Depending on choice then call appropriate gui window:
	    if action == ACTION_ENUM['ADD']:
	        add_order_to_db(db_path)
	    elif action == ACTION_ENUM['UPDATE']:
	        update_order_in_db(db_path)
	    elif action == ACTION_ENUM['DELETE']:
	        delete_order_in_db(db_path)
	    elif action == ACTION_ENUM['QUERY']:
	        query_db(db_path)
	    elif action == ACTION_ENUM['EXIT']:
	        break