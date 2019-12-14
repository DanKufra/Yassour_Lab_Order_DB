import argparse as argparse
import numpy as np
import pandas as pd
from gui_interface import gui_create_db, gui_load_db, gui_option_window, \
    gui_add_order, gui_update_order, gui_update_item, gui_message, gui_get_order_id, gui_query, gui_show_query_table
from db_utils import db_connect, init_db, create_order, update_order, get_order_by_id, delete_order_by_id, get_next_order_id, \
    query_db_utils, ACTION_ENUM, COLUMN_INDEX


def create_new_db():
    db_path = gui_create_db()
    init_db(db_path)
    return db_path


def load_db():
    db_path = gui_load_db()
    return db_path


def add_order_to_db(db_path):
    order_values, items_values = gui_add_order()
    if order_values is None or items_values is None:
        gui_message('Order not added properly.')
        return
    order_id = get_next_order_id(db_path)
    for i, item in enumerate(items_values):
        id = create_order(db_path=db_path, item_id=i+1, order_id=order_id, distributor=order_values['distributor'],
                          order_date=order_values['date_picked'],
                          sivug_number=order_values['sivug_number'], grant_number=order_values['grant_number'],
                          SAP_number=order_values['SAP_number'],
                          price=item['price'], item=item['item'], description=item['description'])
    # TODO how to catch failure?
    gui_message('Order added to DB.')


def update_order_in_db(db_path, order_id=None, item_id=None):
    # if order id is None then get it via gui, otherwise we get it as an argument
    if order_id is None:
        order_id, item_id = gui_get_order_id()
    if order_id is None:
        gui_message('Order id not picked properly.')
        return
    original_order = get_order_by_id(db_path, order_id, item_id)

    if original_order is None:
        gui_message('Order id does not exist.')
        return

    # if item_id is None then update just the order values, otherwise update the item #TODO
    if item_id is None:
        order = gui_update_order(original_order[0])
    else:
        order = gui_update_item(original_order[0])
    if order is None:
        gui_message('Order not updated properly.')
        return

    if item_id is None:
        id = update_order(db_path=db_path, order_id=order_id, distributor=order['distributor'], SAP_number=order['SAP_number'],
                          grant_number=order['grant_number'], sivug_number=order['sivug_number'], order_date=order['date'])
    else:
        id = update_order(db_path=db_path, order_id=order_id, item_id=item_id, item=order['item'],
                          price=order['price'], description=order['description'])
    # TODO how to catch failure?
    gui_message('Order updated in DB.')


def delete_order_in_db(db_path):
    order_id, item_id = gui_get_order_id()
    if order_id is None:
        gui_message('Order not deleted properly.')
        return
    items = get_order_by_id(db_path=db_path, order_id=order_id, item_id=item_id)
    if len(items) == 0:
        gui_message('Order id does not exist.')
        return
    id = delete_order_by_id(db_path=db_path, order_id=order_id, item_id=item_id)
    # TODO how to catch failure?
    gui_message('Order deleted from DB.')


def create_query(values):
    query = "SELECT * FROM orders"
    num_conds = 0
    if values['id_filter'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if values['id_filter'] == 'RANGE':
            query += '(order_id >= %d and order_id <= %d )' % (values['id_start'], values['id_end'])
        else:
            query += '(order_id %s %d)' % (values['id_filter'], values['id_start'])
        num_conds += 1
    if values['price_filter'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        if values['price_filter'] == 'RANGE':
            query += '(price >= %f and price <= %f )' % (values['price_start'], values['price_end'])
        else:
            query += '(price %s %f)' % (values['price_filter'], values['price_start'])
    if values['distributor'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(distributor = "%s" ) ' % values['distributor']
    if values['item'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(item = "%s" ) ' % values['item']
    if values['SAP_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(SAP_number = "%s" ) ' % values['SAP_number']
    if values['grant_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(grant_number = "%s" ) ' % values['grant_number']
    if values['sivug_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(sivug_number = "%s" ) ' % values['sivug_number']
    return query


def query_db(db_path):
    con = db_connect(db_path)
    cur = con.cursor()
    unique_distributors_sql = "SELECT distinct(distributor) FROM orders ORDER BY distributor ASC"
    unique_items_sql = "SELECT distinct(item) FROM orders ORDER BY item ASC"
    unique_grant_sql = "SELECT distinct(grant_number) FROM orders ORDER BY grant_number ASC"
    unique_sivug_sql = "SELECT distinct(sivug_number) FROM orders ORDER BY sivug_number ASC"
    cur.execute(unique_distributors_sql)
    unique_distributors = cur.fetchall()
    cur.execute(unique_items_sql)
    unique_items = cur.fetchall()
    cur.execute(unique_grant_sql)
    unique_grants = cur.fetchall()
    cur.execute(unique_sivug_sql)
    unique_sivugs = cur.fetchall()
    con.close()
    query_values = gui_query(unique_distributors, unique_items, unique_grants, unique_sivugs)
    if query_values is None:
        gui_message('Query cancelled.')
        return
    query_sql = create_query(query_values)
    items = query_db_utils(db_path, query_sql)

    df = pd.DataFrame(items, columns=['Id', 'Order Id', 'Distributor', 'Price', 'Order Date', 'Item', 'Description',
                                      'SAP Number', 'Grant Number', 'Sivug Number', 'Date Added'])
    gui_show_query_table(db_path, df)


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
