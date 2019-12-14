import PySimpleGUI as sg
import os
import datetime
from db_utils import ACTION_ENUM, COLUMN_INDEX
sg.change_look_and_feel('TealMono')  # Add a touch of color


def gui_create_db():
    # All the stuff inside your window.
    layout = [[sg.Text('Database Folder: '), sg.In(), sg.FolderBrowse()],
              [sg.Text('Database Name: '), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Create Database', layout)

    event, values = window.read()
    window.close()

    if event in (None, 'Cancel'):
        sg.popup("Cancel", "No filename supplied")
        raise SystemExit("Cancelling: no filename supplied supplied")

    database_file_path = os.path.join(values[0], values[1] + '.sqlite3')

    if os.path.exists(database_file_path):
        sg.popup("Cancel", "File already exists")
        raise SystemExit("Cancelling: File already exists")
    else:
        sg.popup('The filename you chose was ', database_file_path)
    window.close()
    return database_file_path


def gui_load_db():
    # All the stuff inside your window.
    layout = [[sg.Text('Please load database file')],
              [sg.Text('Database File: '), sg.In(), sg.FileBrowse()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Load Database', layout)

    event, database_file_path = window.read()

    window.close()

    database_file_path = database_file_path[0]

    if not database_file_path:
        sg.popup("Cancel", "No filename supplied")
        raise SystemExit("Cancelling: no filename supplied")
    else:
        sg.popup('The filename you chose was ', database_file_path)

    window.close()
    return database_file_path


def gui_option_window():
    # All the stuff inside your window.
    layout = [[sg.Text('Please pick an action:')],
              [sg.Button('Add'), sg.Button('Update'), sg.Button('Delete'), sg.Button('Query')],
              [sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Database Action Options', layout)

    event, values = window.read()
    window.close()

    if event in (None, 'Cancel'):
        return ACTION_ENUM['EXIT']
    elif event in 'Add':
        return ACTION_ENUM['ADD']
    elif event in 'Update':
        return ACTION_ENUM['UPDATE']
    elif event in 'Delete':
        return ACTION_ENUM['DELETE']
    elif event in 'Query':
        return ACTION_ENUM['QUERY']


def gui_add_order():
    get_item = True
    order_values = None
    items_values = None
    cur_date = datetime.datetime.now()
    cur_date = '%s-%s-%s' % (cur_date.year, cur_date.month, cur_date.day)
    # create order
    layout = [[sg.Text('Please enter your order:')],
              [sg.Text('Distributor: '), sg.InputText(key='distributor')],
              [sg.CalendarButton('Order Date', key='date', disabled=False, focus=True,
                                 target='date_picked', format='%Y-%m-%d'), sg.InputText(cur_date, key='date_picked')],
              [sg.Text('SAP number: '), sg.InputText(key='SAP_number')],
              [sg.Text('Grant: '), sg.InputText(key='grant_number')],
              [sg.Text('Sivug: '), sg.InputText(key='sivug_number')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Add Order', layout)

    while True:
        event, order_values = window.read()
        if event in (None, 'Cancel'):
            get_item = False
            order_values = None
            break
        if event in ('Ok'):
            break
    window.close()

    if get_item:
        # add items to order
        layout = [[sg.Text('Please enter your item:')],
                  [sg.Text('Item: '), sg.InputText(key='item')],
                  [sg.Text('Price: '), sg.InputText(key='price')],
                  [sg.Text('Description: '), sg.InputText(key='description')],
                  [sg.Button('Add'), sg.Exit('Finished')]]
        # Create the Window
        window = sg.Window('Add item', layout)
        items_values = []
        while True:  # The Event Loop
            event, values = window.read()
            if event in (None, 'Finished'):
                break
            if event in ('Add'):
                try:
                    values['price'] = float(values['price'])
                except ValueError:
                    sg.popup("Invalid type entered for price, try again.")
                items_values.append(values)
                # Update the "output" text element to be the value of "input" element
                window['item'].update('')
                window['price'].update('')
                window['description'].update('')
        window.close()

    return order_values, items_values


def gui_message(message):    
    sg.popup(message)


def gui_update_order(original_order):
    # All the stuff inside your window.
    layout = [[sg.Text('Please update your order:')],
              [sg.Text('Distributor: '), sg.InputText(original_order[COLUMN_INDEX['distributor']], key='distributor')],
              [sg.Text('SAP Number: '), sg.InputText(original_order[COLUMN_INDEX['SAP_number']], key='SAP_number')],
              [sg.Text('Grant Number: '), sg.InputText(original_order[COLUMN_INDEX['grant_number']], key='grant_number')],
              [sg.Text('Sivug Number: '), sg.InputText(original_order[COLUMN_INDEX['sivug_number']], key='sivug_number')],
              [sg.CalendarButton('Order Date', key='date', disabled=False, focus=True, target='date_picked', format='%Y-%m-%d'),
               sg.InputText(original_order[COLUMN_INDEX['order_date']], key='date_picked')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Update Order', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            values = None
            break
        if event in 'Ok':
            break
    window.close()
    return values


def gui_update_item(original_order):
    # All the stuff inside your window.
    layout = [[sg.Text('Please update your order:')],
              [sg.Text('Item: '), sg.InputText(original_order[COLUMN_INDEX['item']], key='item')],
              [sg.Text('Price: '), sg.InputText(original_order[COLUMN_INDEX['price']], key='price')],
              [sg.Text('Description: '), sg.InputText(original_order[COLUMN_INDEX['description']], key='description')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Update Order', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            values = None
            break
        if event in 'Ok':
            try:
                values['price'] = float(values['price'])
                break
            except ValueError:
                sg.popup("Invalid type entered for price, try again.")
    window.close()
    return values


def gui_query(unique_distributors, unique_items, unique_grants, unique_sivugs):
    # All the stuff inside your window.
    cur_date = datetime.datetime.now()
    cur_date = '%s-%s-%s' % (cur_date.year, cur_date.month, cur_date.day)
    #TODO fix calender for mac?
    layout = [[sg.Text('Please enter your query:')],
              [sg.Text('id: '), sg.Combo(['<', '=', '>', '<=', '>=', 'RANGE'], key='id_filter'), sg.InputText(key='id_start'), sg.InputText(key='id_end')],
              [sg.Text('Distributor: '), sg.Combo(unique_distributors, key='distributor')],
              [sg.Text('SAP number: '), sg.Combo(unique_grants, key='SAP_number')],
              [sg.Text('Grant number: '), sg.Combo(unique_grants, key='grant_number')],
              [sg.Text('Sivug number: '), sg.Combo(unique_sivugs, key='sivug_number')],
              [sg.Text('Price: '), sg.Combo(['<', '=', '>', '<=', '>=', 'RANGE'], key='price_filter'), sg.InputText(key='price_start'), sg.InputText(key='price_end')],
              [sg.CalendarButton('Start Order Date', key='start_date', disabled=False, focus=True, target='start_date_picked', format='%Y-%m-%d'),
               sg.InputText(cur_date, key='start_date_picked'),
               sg.CalendarButton('End Order Date', key='end_date', disabled=False, focus=True, target='end_date_picked', format='%Y-%m-%d'),
               sg.InputText(cur_date, key='end_date_picked')],
              [sg.Text('Item: '), sg.Combo(unique_items, key='item')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Query Orders', layout)
    while True:
        success = True
        event, values = window.read()
        if event in (None, 'Cancel'):
            window.close()
            return
        # validate id input
        try:
            if values['id_filter'] is not '':
                if values['id_start'] is not '':
                    values['id_start'] = int(values['id_start'])
                else:
                    raise ValueError
                if values['id_filter'] == 'RANGE':
                    if values['id_end'] is not '':
                        values['id_end'] = int(values['id_end'])
                    else:   
                        raise ValueError
        except ValueError:
            success = False
            sg.popup("Invalid type entered for id, try again.")
        # validate price input
        try:
            if values['price_filter'] is not '':
                if values['price_start'] is not '':
                    values['price_start'] = float(values['price_start'])
                if values['price_filter'] == 'RANGE':
                    if values['price_end'] is not '':
                        values['price_end'] = float(values['price_end'])
                    else:
                        raise ValueError
        except ValueError:
            sg.popup("Invalid type entered for price, try again.")
            success = False
        if success:
            break
    window.close()
    return values


def gui_get_order_id():
    # All the stuff inside your window.
    layout = [[sg.Text('Please enter your order id:')],
              [sg.Text('Order id: '), sg.InputText(key='order_id')],
              [sg.Text('Item id: '), sg.InputText(key='item_id')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Get Order ID', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            window.close()
            return None, None
        try:
            values['order_id'] = int(values['order_id'])
            if values['item_id'] != '':
                values['item_id'] = int(values['item_id'])
            else:
                values['item_id'] = None
            break
        except ValueError:
            sg.popup("Invalid type entered for id, try again.")
    window.close()
    return values['order_id'], values['item_id']


def gui_show_query_table(db_path, df):
    sg.set_options(auto_size_buttons=True)

    data = df.values.tolist()               # read everything else into a list of rows
    # Uses the first row (which should be column names) as columns names
    header_list = list(df.columns.values)

    layout = [[sg.Table(values=data,
                        headings=header_list,
                        display_row_numbers=False,
                        auto_size_columns=False,
                        num_rows=min(25, len(data)),
                        alternating_row_color='lightblue',
                        key='query_table',
                        select_mode='extended')],
              [sg.Button('Show total'), sg.Button('Update Order'), sg.Button('Update Item'), sg.Button('Exit')]]

    window = sg.Window('Table', layout, grab_anywhere=False)
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            window.close()
            return
        elif event in ('Show total'):
            sg.popup("Total amount: %f" %(df['Price'].sum()))
        elif event in ('Update Order'):
            try:
                row = df.iloc[values['query_table'][0]]
                from run import update_order_in_db
                update_order_in_db(db_path, int(row['Order Id']))
            except IndexError:
                sg.popup("Must select row for update.")
        elif event in ('Update Item'):
            try:
                row = df.iloc[values['query_table'][0]]
                from run import update_order_in_db
                update_order_in_db(db_path, int(row['Order Id']), int(row['Id']))
            except IndexError:
                sg.popup("Must select row for update.")
    window.close()

