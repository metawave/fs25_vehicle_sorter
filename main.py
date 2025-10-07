import os.path
import sys

import FreeSimpleGUI as sg

from model import Vehicle
from vehicle_xml import VehiclesXml

# look and feel
sg.theme("systemdefault")
standard_font = ("San Francisco", 14)
title_font = ("San Francisco", 16)
sg.set_options(font=standard_font)

# savegame chooser upper left
initial_folder = ""
if sys.platform.startswith("win32"):
    initial_folder = os.path.expanduser("~\\Documents\\My Games\\FarmingSimulator2025")
elif sys.platform.startswith("darwin"):
    initial_folder = os.path.expanduser("~/Library/Application Support/FarmingSimulator2025")

savegame_chooser = [
    sg.Text("Savegame"), sg.InputText(key="savegame_input", enable_events=True),
    sg.FolderBrowse("Browse", key="savegame_browse", initial_folder=initial_folder)
]

# shuffle list left
shuffle_list = [
    sg.Listbox(values=[], key="vehicle_list", size=(50, 30), enable_events=True),
    sg.Column([
        [sg.Button("Top", key="vehicle_up_top", disabled=True)],
        [sg.Button("+5", key="vehicle_up_five", disabled=True)],
        [sg.Button(sg.SYMBOL_UP, key="vehicle_up", disabled=True)],
        [sg.Button(sg.SYMBOL_DOWN, key="vehicle_down", disabled=True)],
        [sg.Button("-5", key="vehicle_down_five", disabled=True)],
        [sg.Button("Bottom", key="vehicle_down_bottom", disabled=True)],
        [sg.HSeparator()],
        [sg.Button("Sort by name", key="vehicle_sort_by_name")]
    ]),
    sg.Column([
        [sg.Column([
            [sg.Text("Vehicle Details:", font=title_font)],
            [sg.Text("ID")],
            [sg.Text("Operating Time [h]")],
            [sg.Text("License plate")],
            [sg.Text("Attached to")]
        ]), sg.Column([
            [sg.Text("", font=title_font)],
            [sg.Text("", key="vehicle_detail_id")],
            [sg.Text("", key="vehicle_detail_operating_time")],
            [sg.Text("", key="vehicle_detail_license_plates")],
            [sg.Text("", key="vehicle_detail_attached_to")]
        ])]
    ], vertical_alignment="top", expand_x=True)
]

# save and exit
save_and_exit = [
    sg.Button("Save", key="savegame_save", disabled=True), sg.HSeparator(), sg.Button("Exit")
]

# All the stuff inside your window.
layout = [savegame_chooser,
          shuffle_list,
          save_and_exit
          ]

vehicles_xml = VehiclesXml()


def selected_vehicle(ui_state: {}) -> Vehicle | None:
    if ui_state['vehicle_list'] is not None and len(ui_state['vehicle_list']) == 1:
        return ui_state['vehicle_list'][0]
    return None


# Create the Window
window = sg.Window('FS25 Vehicle Sorter', layout)


# UI functions
def move_selected_vehicle_up(ui_state: {}, positions=1):
    if selected_vehicle(ui_state) is not None:
        new_vehicle_index = vehicles_xml.move_up(selected_vehicle(ui_state), positions)
        window['vehicle_list'].update(values=vehicles_xml.vehicles_list, set_to_index=[new_vehicle_index])


def move_selected_vehicle_down(ui_state: {}, positions=1):
    if selected_vehicle(ui_state) is not None:
        new_vehicle_index = vehicles_xml.move_down(selected_vehicle(ui_state), positions)
        window['vehicle_list'].update(values=vehicles_xml.vehicles_list, set_to_index=[new_vehicle_index])


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
        break

    if event == 'savegame_input':
        vehicles_xml = VehiclesXml()
        try:
            vehicles_xml.load_savegame(values['savegame_input'])
        except FileNotFoundError:
            sg.PopupOK("Please select a valid savegame!", title="No valid savegame")

        window['vehicle_list'].update(vehicles_xml.vehicles_list)
        window['savegame_save'].update(disabled=False)

    if event == 'savegame_save':
        vehicles_xml.save_savegame()
        window['vehicle_list'].update(vehicles_xml.vehicles_list)

    if event == 'vehicle_list':
        current_vehicle = selected_vehicle(values)
        if current_vehicle is not None:
            window['vehicle_up_top'].update(disabled=False)
            window['vehicle_up_five'].update(disabled=False)
            window['vehicle_up'].update(disabled=False)
            window['vehicle_down'].update(disabled=False)
            window['vehicle_down_five'].update(disabled=False)
            window['vehicle_down_bottom'].update(disabled=False)
            window['vehicle_detail_id'].update(current_vehicle.id)
            window['vehicle_detail_operating_time'].update(current_vehicle.operating_time)
            window['vehicle_detail_license_plates'].update(current_vehicle.license_plates)
            attached_to = vehicles_xml.get_attached_to(current_vehicle)
            if attached_to is not None:
                window['vehicle_detail_attached_to'].update(str(attached_to.id) + ': ' + attached_to.name)
            else:
                window['vehicle_detail_attached_to'].update("Nothing")
        else:
            window['vehicle_up_top'].update(disabled=True)
            window['vehicle_up_five'].update(disabled=True)
            window['vehicle_up'].update(disabled=True)
            window['vehicle_down'].update(disabled=True)
            window['vehicle_down_five'].update(disabled=True)
            window['vehicle_down_bottom'].update(disabled=True)

    if event == 'vehicle_up_top':
        move_selected_vehicle_up(values, 9999)

    if event == 'vehicle_up_five':
        move_selected_vehicle_up(values, 5)

    if event == 'vehicle_up':
        move_selected_vehicle_up(values, 1)

    if event == 'vehicle_down':
        move_selected_vehicle_down(values, 1)

    if event == 'vehicle_down_five':
        move_selected_vehicle_down(values, 5)

    if event == 'vehicle_down_bottom':
        move_selected_vehicle_down(values, 9999)

    if event == 'vehicle_sort_by_name':
        if vehicles_xml.vehicles_list is not None and len(vehicles_xml.vehicles_list) > 0:
            vehicles_xml.sort_vehicles_by_name()
            window['vehicle_list'].update(vehicles_xml.vehicles_list)

    print('Event ', event)
    print('You entered', values)

window.close()
