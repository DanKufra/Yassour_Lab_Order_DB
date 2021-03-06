import argparse as argparse
import numpy as np
import pandas as pd
import locale
from gui_interface import gui_create_db, gui_load_db, gui_option_window, \
    gui_add_order, gui_update_order, gui_update_item, gui_message, \
    gui_get_order_id, gui_query, gui_show_query_table, gui_grants, gui_sivugim, gui_sivug_summary, gui_double_check_window
from db_utils import db_connect, init_db, create_order, update_order, get_order_by_id, delete_order_by_id, get_next_order_id, \
    query_db_utils, ACTION_ENUM, COLUMN_INDEX
from grant_consts import GRANT_DICTS

locale.setlocale(locale.LC_ALL, 'en_US')

TAX_CONST = 1.17

def create_new_db():
    db_path = gui_create_db()
    init_db(db_path)
    return db_path


def load_db():
    db_path = gui_load_db()
    return db_path


def add_order_to_db(db_path):
    unique_distributors = get_unique(db_path, 'distributor')
    unique_grants = get_unique(db_path, 'grant_number')
    unique_sivugs = get_unique(db_path, 'sivug_number')

    order_values, items_values = gui_add_order(unique_distributors, unique_grants, unique_sivugs)
    print(order_values, items_values)
    if order_values is None or items_values is None:
        gui_message('Order not added properly.')
        return
    order_id = get_next_order_id(db_path)
    for i, item in enumerate(items_values):
        id = create_order(db_path=db_path, item_id=i+1, order_id=order_id, distributor=order_values['distributor'],
                          order_date=order_values['date_picked'], grant_number=order_values['grant_number'],
                          SAP_number=order_values['SAP_number'], order_file=order_values['order_file'], price_quote_file=order_values['price_quote_file'],
                          price=item['price'], item=item['item'], amount=item['amount'], sivug_number=item['sivug_number'], description=item['description'])
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

    # if item_id is None then update just the order values, otherwise update the item
    unique_distributors = get_unique(db_path, 'distributor')
    unique_grants = get_unique(db_path, 'grant_number')
    unique_sivugs = get_unique(db_path, 'sivug_number')
    if item_id is None:
        order, items_values = gui_update_order(original_order[0], unique_distributors, unique_grants, unique_sivugs)
    else:
        order = gui_update_item(original_order[0])
    if order is None:
        gui_message('Order not updated properly.')
        return

    if item_id is None:
        id = update_order(db_path=db_path, order_id=order_id, distributor=order['distributor'], SAP_number=order['SAP_number'],
                          grant_number=order['grant_number'], order_date=order['date_picked'],
                          order_file=order['order_file'], price_quote_file=order['price_quote_file'])
        for i, item in enumerate(items_values):
            id = create_order(db_path=db_path, item_id=i + 1, order_id=order_id,
                              distributor=order['distributor'],
                              order_date=order['date_picked'], grant_number=order['grant_number'],
                              SAP_number=order['SAP_number'], order_file=order['order_file'],
                              price_quote_file=order['price_quote_file'],
                              price=item['price'], item=item['item'], amount=item['amount'],
                              sivug_number=item['sivug_number'], description=item['description'])
    else:
        id = update_order(db_path=db_path, order_id=order_id, item_id=item_id, item=order['item'], amount=order['amount'],
                          price=order['price'], description=order['description'], sivug_number=order['sivug_number'])
    gui_message('Order updated in DB.')


def delete_order_in_db(db_path, order_id=None, item_id=None):
    if order_id is None and item_id is None:
        order_id, item_id = gui_get_order_id()
    if order_id is None:
        gui_message('Order not deleted properly.')
        return
    items = get_order_by_id(db_path=db_path, order_id=order_id, item_id=item_id)
    if len(items) == 0:
        gui_message('Order id does not exist.')
        return
    else:
        df = pd.DataFrame(items, columns=['Id', 'Order Id', 'Distributor', 'Price', 'Order Date', 'Item', 'Description',
                                          'SAP Number', 'Grant Number', 'Sivug Number', 'Order File',
                                          'Price Quote File', 'Date Added', 'Amount'])
        double_check_event, double_check_values = gui_double_check_window("Are you sure you want to Delete this item?", df)
        if double_check_event in (None, 'No'):
            gui_message("Item not deleted")
        elif double_check_event in ('Yes'):
            id = delete_order_by_id(db_path=db_path, order_id=order_id, item_id=item_id)
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
        num_conds += 1
    #TODO fix this
    # if values['start_date_picked'] != '':
    #     if num_conds == 0:
    #         query += ' WHERE '
    #     if num_conds > 0:
    #         query += ' AND '
    #     query += '(date_added >= %s)' % (values['start_date_picked'])
    #     num_conds += 1
    # if values['end_date_picked'] != '':
    #     if num_conds == 0:
    #         query += ' WHERE '
    #     if num_conds > 0:
    #         query += ' AND '
    #     query += '(order_date <= %s)' % (values['end_date_picked'])
    #     num_conds += 1
    if values['amount_filter'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        if values['price_filter'] == 'RANGE':
            query += '(amount >= %f and amount <= %f )' % (values['amount_start'], values['amount_end'])
        else:
            query += '(amount %s %f)' % (values['amount_filter'], values['amount_start'])
        num_conds += 1
    if values['distributor'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(distributor = "%s" ) ' % values['distributor']
        num_conds += 1
    if values['item'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(item = "%s" ) ' % values['item']
        num_conds += 1
    if values['SAP_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(SAP_number = "%s" ) ' % values['SAP_number']
        num_conds += 1
    if values['grant_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(grant_number = "%s" ) ' % values['grant_number']
        num_conds += 1
    if values['sivug_number'] != '':
        if num_conds == 0:
            query += ' WHERE '
        if num_conds > 0:
            query += ' AND '
        query += '(sivug_number = "%s" ) ' % values['sivug_number']
        num_conds += 1

    print(query)
    return query


def get_unique(db_path, field):
    con = db_connect(db_path)
    cur = con.cursor()
    unique_sql = "SELECT distinct(%s) FROM orders ORDER BY %s ASC" % (field, field)
    cur.execute(unique_sql)
    unique = cur.fetchall()
    return unique


def query_db(db_path):
    unique_distributors = get_unique(db_path, 'distributor')
    unique_SAP = get_unique(db_path, 'SAP_number')
    unique_items = get_unique(db_path, 'item')
    unique_grants = get_unique(db_path, 'grant_number')
    unique_sivugs = get_unique(db_path, 'sivug_number')

    query_values = gui_query(unique_distributors, unique_SAP, unique_items, unique_grants, unique_sivugs)
    if query_values is None:
        gui_message('Query cancelled.')
        return
    query_sql = create_query(query_values)
    again = True
    while again:
        items = query_db_utils(db_path, query_sql)
        if len(items) == 0:
            gui_message("No such items exist in DB. Try again!")
            return
        df = pd.DataFrame(items, columns=['Id', 'Order Id', 'Distributor', 'Price', 'Order Date', 'Item', 'Description',
                                          'SAP Number', 'Grant Number', 'Sivug Number', 'Order File',
                                          'Price Quote File', 'Date Added', 'Amount'])
        again = gui_show_query_table(db_path, df)


def show_grant_totals(db_path):
    con = db_connect(db_path)
    cur = con.cursor()
    grant_info_df = pd.DataFrame(columns=['Grant Number', 'Grant Total',
                                          'Grant Spent', 'Grant Remaining',
                                          'Percentage Spent'])
    for grant in GRANT_DICTS.keys():
        if grant in ["3015002026", "3186000162"]:
            currency_const = 3.5
        else:
            currency_const = 1.0
        cur_grant = GRANT_DICTS[grant]
        # get total money for that grant
        grant_total = np.sum([cur_grant[sivug]['Amount'] for sivug in cur_grant])
        grant_spent_sql = "SELECT price, amount FROM orders WHERE grant_number = %s" %grant
        cur.execute(grant_spent_sql)
        grant_item_prices = cur.fetchall()
        if len(grant_item_prices) > 0:
            grant_spent = 0
            for item in grant_item_prices:
                grant_spent += item[0] * item[1] * TAX_CONST / currency_const
        else:
            grant_spent = 0
        grant_remaining = grant_total - grant_spent
        percentage_spent = np.round(grant_spent / float(grant_total), decimals=2) * 100.0
        grant_remaining = locale.format_string("%.2f", grant_remaining, grouping=True)
        grant_total = locale.format_string("%.2f", grant_total, grouping=True)
        grant_spent = locale.format_string("%.2f", grant_spent, grouping=True)
        cur_grant_info = {"Grant Number": grant, "Grant Total": grant_total,
                          "Grant Spent": grant_spent, "Grant Remaining": grant_remaining,
                          "Percentage Spent": percentage_spent}
        grant_info_df = grant_info_df.append(cur_grant_info, ignore_index=True)
    gui_grants(db_path, grant_info_df)


def show_sivugim(db_path, grant_info, all_grants=False):
    con = db_connect(db_path)
    cur = con.cursor()
    cur_grant = GRANT_DICTS[grant_info['Grant Number']]
    sivug_info_df = pd.DataFrame(columns=['Sivug Number', 'Sivug Total',
                                          'Sivug Spent', 'Sivug Remaining',
                                          'Percentage Spent'])
    for sivug in cur_grant.keys():
        if grant_info['Grant Number'] in ["3015002026", "3186000162"]:
            currency_const = 3.5
        else:
            currency_const = 1.0
        cur_sivug = cur_grant[sivug]
        sivug_total = cur_sivug['Amount']
        sivug_spent_sql = "SELECT price, amount FROM orders WHERE sivug_number = %s" % sivug
        if not all_grants:
            sivug_spent_sql += " AND grant_number = %s" % grant_info['Grant Number']
        cur.execute(sivug_spent_sql)
        sivug_item_prices = cur.fetchall()
        if len(sivug_item_prices) > 0:
            sivug_spent = 0
            for item in sivug_item_prices:
                sivug_spent += item[0] * item[1] * TAX_CONST / currency_const
        else:
            sivug_spent = 0
        sivug_remaining = sivug_total - sivug_spent
        if sivug_total == 0.0:
            percentage_spent = 0.0
        else:
            percentage_spent = np.round(sivug_spent / float(sivug_total), decimals=2) * 100.0
        sivug_remaining = locale.format_string("%.2f", sivug_remaining, grouping=True)
        sivug_total = locale.format_string("%.2f", sivug_total, grouping=True)
        sivug_spent = locale.format_string("%.2f", sivug_spent, grouping=True)
        cur_sivug_info = {"Sivug Number": sivug, "Sivug Total": sivug_total,
                          "Sivug Spent": sivug_spent, "Sivug Remaining": sivug_remaining,
                          "Percentage Spent": percentage_spent}
        sivug_info_df = sivug_info_df.append(cur_sivug_info, ignore_index=True)
    # get all sivugim totals
    gui_sivugim(db_path, grant_info, sivug_info_df, all_grants)


def show_grant_and_sivugim(db_path):
    con = db_connect(db_path)
    cur = con.cursor()
    sivug_info_df = pd.DataFrame(columns=['Grant Number', 'Sivug Number', 'Sivug Total',
                                          'Sivug Spent', 'Sivug Remaining',
                                          'Percentage Spent', 'Shared Index', 'Amount Shared Total',
                                          'Amount Shared Spent', 'Amount Shared Remaining'])
    for grant in GRANT_DICTS.keys():
        if grant in ["3015002026", "3186000162"]:
            currency_const = 3.5
        else:
            currency_const = 1.0
        cur_grant = GRANT_DICTS[grant]
        shared_dict = {}
        for sivug in cur_grant.keys():
            cur_sivug = cur_grant[sivug]
            if cur_sivug['Shared'] is None:
                continue
            if cur_sivug['Shared'] not in shared_dict.keys():
                shared_dict[cur_sivug['Shared']] = {'Total': 0, 'Spent': 0}
            shared_dict[cur_sivug['Shared']]['Total'] += cur_sivug['Amount']

        shared_spent_sql = "SELECT sivug_number, price, amount FROM orders WHERE grant_number = %s" % grant
        cur.execute(shared_spent_sql)
        sivug_item_prices = cur.fetchall()
        for item in sivug_item_prices:
            try:
                shared_dict[cur_grant[str(item[0])]['Shared']]['Spent'] += item[1] * item[2] * TAX_CONST / currency_const
            except KeyError:
                print("Check your Sivugim! Sivug number %s of them does not exist." % str(item[0]))

        for k, v in shared_dict.items():
            shared_dict[k]['Remaining'] = v['Total'] - v['Spent']
            shared_dict[k]['Total'] = locale.format_string("%.2f", shared_dict[k]['Total'], grouping=True)
            shared_dict[k]['Spent'] = locale.format_string("%.2f", shared_dict[k]['Spent'], grouping=True)
            shared_dict[k]['Remaining'] = locale.format_string("%.2f", shared_dict[k]['Remaining'], grouping=True)

        for sivug in cur_grant.keys():
            cur_sivug = cur_grant[sivug]
            sivug_total = cur_sivug['Amount']
            sivug_spent_sql = "SELECT price, amount FROM orders WHERE sivug_number = %s AND grant_number = %s" % (sivug, grant)
            cur.execute(sivug_spent_sql)
            sivug_item_prices = cur.fetchall()
            if len(sivug_item_prices) > 0:
                sivug_spent = 0
                for item in sivug_item_prices:
                    sivug_spent = item[0] * item[1] / currency_const
            else:
                sivug_spent = 0
            sivug_remaining = sivug_total - sivug_spent
            if sivug_total == 0.0:
                percentage_spent = 0.0
            else:
                percentage_spent = np.round(sivug_spent / float(sivug_total), decimals=2) * 100.0
            sivug_remaining = locale.format_string("%.2f", sivug_remaining, grouping=True)
            sivug_total = locale.format_string("%.2f", sivug_total, grouping=True)
            sivug_spent = locale.format_string("%.2f", sivug_spent, grouping=True)

            if cur_sivug['Shared'] is not None:
                sivug_shared_total = shared_dict[cur_sivug['Shared']]['Total']
                sivug_shared_spent = shared_dict[cur_sivug['Shared']]['Spent']
                sivug_shared_remaining = shared_dict[cur_sivug['Shared']]['Remaining']
            else:
                sivug_shared_total = sivug_total
                sivug_shared_spent = sivug_spent
                sivug_shared_remaining = sivug_remaining

            cur_sivug_info = {"Grant Number": grant, "Sivug Number": sivug, "Sivug Total": sivug_total,
                              "Sivug Spent": sivug_spent, "Sivug Remaining": sivug_remaining,
                              "Percentage Spent": percentage_spent, "Shared Index": str(cur_sivug['Shared']),
                              "Amount Shared Total": sivug_shared_total,
                              "Amount Shared Spent": sivug_shared_spent,
                              "Amount Shared Remaining": sivug_shared_remaining}
            sivug_info_df = sivug_info_df.append(cur_sivug_info, ignore_index=True)
    gui_sivug_summary(db_path, sivug_info_df)


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
        elif action == ACTION_ENUM['GRANTS']:
            show_grant_totals(db_path)
        elif action == ACTION_ENUM['GRANTS_SIVUG']:
            show_grant_and_sivugim(db_path)
        elif action == ACTION_ENUM['EXIT']:
            break
