
# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import dearpygui.dearpygui as dpg
import time
import threading
from serial import Serial
import serial.tools.list_ports

running = True
serial_connected = False

def quit_app(sender, app_data, user_data):
    global running
    running = False
    dpg.destroy_context()


def serial_worker():
    global serial_connected
    global serial_port
    global running
    while running and serial_connected:
        if not serial_port.is_open:
            serial_connected = False
        print(serial_port.read())
    serial_connected = False
    serial_port.close()
    dpg.enable_item("menu_file_connect")
    dpg.disable_item("menu_file_disconnect")

serial_port: Serial | None = None
serial_thread: threading.Thread | None = None

def telemetry_worker():
    speed_data_x = [-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
    speed_data_y = [5,6,7,8,9,10,9,8,7,6,5]
    while running:
        time.sleep(0.1)
        y_val = speed_data_y.pop(0)

        speed_data_y.append(y_val)
        dpg.set_value("speed_series", [speed_data_x, speed_data_y])
        dpg.set_axis_limits("x_axis_speed", speed_data_x[0], speed_data_x[-1])

def show_page(sender, app_data, user_data):
    pages = ["page_live_data", "page_lap_recap"]

    for page in pages:
        dpg.hide_item(page)

    dpg.show_item(user_data)

def show_connection_menu(sender, app_data, user_data):
    ports = serial.tools.list_ports.comports() 
    port_names = []
    for port in ports:
        if port.vid is not None and port.pid is not None:
            port_names.append(port.device)

    dpg.configure_item("serial_combo", items=port_names)
    dpg.show_item("connection_menu")

def disconnect_serial(sender, app_data, user_data):
    global serial_connected
    serial_connected = False

def connect_to_serial(sender, app_data, user_data):
    global serial_port
    global serial_connected
    global serial_thread
    port = dpg.get_value("serial_combo")
    print("Connecting to " + port)
    serial_port = Serial(port=port, baudrate=115200)
    serial_connected = True
    dpg.enable_item("menu_file_disconnect")
    dpg.disable_item("menu_file_connect")
    serial_thread = threading.Thread(target=serial_worker, daemon=True)
    serial_thread.start()


dpg.create_context()
dpg.create_viewport(title='DataFlux', width=600, height=600)

with dpg.font_registry():
    app_font = dpg.add_font("./Inter-Regular.ttf", 18)

dpg.bind_font(app_font)

with dpg.window(label='DataFlux',tag="main_window", no_collapse=True):
    with dpg.menu_bar():
        with dpg.menu(label='File'):
            dpg.add_menu_item(label="Connect", callback=show_connection_menu, enabled=True, tag="menu_file_connect")
            dpg.add_menu_item(label="Disonnect", callback=disconnect_serial, enabled=False, tag="menu_file_disconnect")
            dpg.add_menu_item(label="Quit", callback=quit_app)
        with dpg.menu(label='Window'):
            dpg.add_menu_item(label="Live Data", callback=show_page, user_data="page_live_data")
            dpg.add_menu_item(label="Lap Recap", callback=show_page, user_data="page_lap_recap")

    with dpg.child_window(tag="content_area", autosize_x=True, autosize_y=True, border=False):
        with dpg.group(tag="page_live_data", show=True):
            dpg.add_text("Live Data")
            dpg.add_separator()
            with dpg.group(horizontal=True):
                with dpg.child_window(tag="realtime_stats", width=250, autosize_y=True, border=True):
                    dpg.add_text("Speed: 25kmh")

                with dpg.child_window(tag="data_graphs", autosize_x=True, autosize_y=True, border=True):
                    with dpg.plot(label="Speed", height=250, width=-1, no_inputs=True):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis_speed")
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Speed", tag="y_axis_speed")
                        dpg.set_axis_limits("y_axis_speed", 0, 50)
                        dpg.add_line_series([], [], parent=y_axis, tag="speed_series")

        with dpg.group(tag="page_lap_recap", show=False):
            dpg.add_text("Lap Recap")
            dpg.add_separator()

with dpg.window(label="Connection Menu", tag="connection_menu", show=False, modal=True, no_collapse=True, width=300):
    dpg.add_combo([], tag="serial_combo")
    dpg.add_button(label="Connect", callback=connect_to_serial)

worker = threading.Thread(target=telemetry_worker, daemon=True)
worker.start()

dpg.setup_dearpygui()
dpg.show_viewport()


vp_w = dpg.get_viewport_client_width()
vp_h = dpg.get_viewport_client_height()
dpg.configure_item("main_window", pos=(0, 0), width=vp_w, height=vp_h)
dpg.set_primary_window("main_window", True)

dpg.start_dearpygui()

running = False
dpg.destroy_context()
