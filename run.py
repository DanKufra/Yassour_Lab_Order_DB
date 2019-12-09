import argparse as argparse
from gui_interface import gui_create_db, gui_load_db, gui_option_window, \
    gui_add_order, gui_update_order, gui_success_message, gui_get_order_id
from db_utils import init_db, create_order, update_order, get_order_by_id, delete_order_by_id, ACTION_ENUM


def create_new_db():
    db_path = gui_create_db()
    init_db(db_path)
    return db_path


def load_db():
    db_path = gui_create_db()
    return db_path


def add_order_to_db(db_path):
    order = gui_add_order()
    id = create_order(db_path=db_path, distributor=order['distributor'], price=order['price'],
                      order_date=order['date'], description=order['description'])
    # TODO how to catch failure?
	gui_success_message(True, 'added')

def update_order_in_db(db_path):
    order_id = gui_get_order_id()
    original_order = get_order_by_id(db_path, order_id)
    order = gui_update_order(original_order)
    id = update_order(db_path=db_path, id=order_id, distributor=order['distributor'], price=order['price'],
                      order_date=order['date'], description=order['description'])
    # TODO how to catch failure?
    gui_success_message(True, 'updated')

def delete_order_in_db(db_path):
    order_id = gui_get_order_id()
    id = delete_order_by_id(db_path=db_path, id=order_id)
    # TODO how to catch failure?
    gui_success_message(True, 'deleted')

def query_db(db_path):
    id = delete_order_by_id(db_path=db_path, id=order_id)
    # TODO how to catch failure?
    gui_success_message(True, 'deleted')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str,
                        help='What mode to run our db interface in')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    # Either create a new db or load an existing one
    if args.mode == 'new':
        db_path = create_new_db()
    elif args.mode == 'load':
        db_path = load_db()

    # Open gui window that decides whether to add order, update order, filter order
    action = gui_option_window()

    # # Depending on choice then call appropriate gui window:
    if action == ACTION_ENUM['ADD']:
        add_order_to_db()
    elif action == ACTION_ENUM['UPDATE']:
        update_order_in_db()
    elif action == ACTION_ENUM['DELETE']:
        delete_order_in_db()
	elif action == ACTION_ENUM['QUERY']:
		query_db()