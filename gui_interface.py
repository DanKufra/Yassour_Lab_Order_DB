import PySimpleGUI as sg
import os
import datetime
from db_utils import ACTION_ENUM

sg.change_look_and_feel('DarkAmber')  # Add a touch of color


def gui_create_db():
    # All the stuff inside your window.
    layout = [[sg.Text('Database Folder: '), sg.In(), sg.FolderBrowse()],
              [sg.Text('Database Name: '), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Create Database', layout)

    event, values = window.read()
    window.close()

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
    elif event in ('Add'):
        return ACTION_ENUM['ADD']
    elif event in ('Update'):
        return ACTION_ENUM['UPDATE']
    elif event in ('Delete'):
        return ACTION_ENUM['DELETE']
    elif event in ('Query'):
        return ACTION_ENUM['QUERY']


def gui_add_order():
    # All the stuff inside your window.
    layout = [[sg.Text('Please enter your order:')],
              [sg.Text('Distributor: '), sg.InputText(key='distributor')],
              [sg.Text('Price: '), sg.InputText(key='price')],
              [sg.CalendarButton('Order Date', key='date', disabled=False, focus=True)],
              [sg.Text('Item: '), sg.InputText(key='item')],
              [sg.Text('Description: '), sg.InputText(key='description')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Addd Order', layout)

    while True:
        event, values = window.read()

        if event in (None, 'Cancel'):
            break
        try:
            values['price'] = float(values['price'])
            break
        except ValueError:
            sg.popup("Invalid type entered for price, try again.")
    window.close()
    return values


def gui_message(message):    
    sg.popup(message)

def gui_update_order(original_order):
    # All the stuff inside your window.
    layout = [[sg.Text('Please update your order:')],
              [sg.Text('Distributor: '), sg.InputText(original_order[1], key='distributor')],
              [sg.Text('Price: '), sg.InputText(original_order[2], key='price')],
              [sg.CalendarButton('Order Date', key='date', disabled=False, focus=True, default_date_m_d_y=original_order[3])],
              [sg.Text('Item: '), sg.InputText(original_order[4], key='item')],
              [sg.Text('Description: '), sg.InputText(original_order[4], key='description')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Update Order', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        try:
            values['price'] = float(values['price'])
            break
        except ValueError:
            sg.popup("Invalid type entered for price, try again.")
    window.close()
    return values

def gui_query(unique_distributors, unique_items):
    # All the stuff inside your window.
    layout = [[sg.Text('Please enter your query:')],
              [sg.Text('id: '), sg.Combo(['<', '=', '>', '<=', '>=', 'RANGE'], key='id_filter'), sg.InputText(key='id_start'), sg.InputText(key='id_end')],
              [sg.Text('Distributor: '), sg.Combo(unique_distributors, key='distributor')],
              [sg.Text('Price: '), sg.Combo(['<', '=', '>', '<=', '>=', 'RANGE'], key='price_filter'), sg.InputText(key='price_start'), sg.InputText(key='price_end')],
              [sg.Text('Order Date: '), sg.CalendarButton('Order Date Start', key='date_start', disabled=False, focus=True), 
                                        sg.CalendarButton('Order Date End', key='date_end', disabled=False, focus=True)],
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
              [sg.Text('id: '), sg.InputText(key='id')],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    # Create the Window
    window = sg.Window('Get Order ID', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            window.close()
            return
        try:
            values['id'] = int(values['id'])
            break
        except ValueError:
            sg.popup("Invalid type entered for id, try again.")
    window.close()
    return values['id']


# gui_load_db()
# gui_add_order()
