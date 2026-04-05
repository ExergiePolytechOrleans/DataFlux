# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.callbacks.menu
import dataflux.callbacks.serial

from dataflux.state import AppState
from dataflux.tags import MENU_FILE_CONNECT, MENU_FILE_DISCONNECT, STATUS_SERIAL_STATUS_BOX, STATUS_SERIAL_STATUS_TEXT, THEME_STATUS_CONNECTED, THEME_STATUS_DISCONNECTED, WINDOW_CONNECTION_MENU, WINDOW_CONNECTION_MENU_COMBO
from dataflux.ui.colors import STATUS_GREEN_DARK, STATUS_RED_DARK

def build_windows(state: AppState) -> None:
    
    with dpg.window(label='DataFlux',tag="main_window", no_collapse=True):
        with dpg.menu_bar():
            with dpg.menu(label='File'):
                dpg.add_menu_item(label="Connect", enabled=True, tag=MENU_FILE_CONNECT, callback=dataflux.callbacks.menu.open_connection_window)
                dpg.add_menu_item(label="Disonnect", enabled=False, tag=MENU_FILE_DISCONNECT, callback=dataflux.callbacks.menu.menu_file_disconnect, user_data=state)
                dpg.add_menu_item(label="Quit")
            with dpg.menu(label='Window'):
                dpg.add_menu_item(label="Live Data", user_data="page_live_data")
                dpg.add_menu_item(label="Lap Recap", user_data="page_lap_recap")

        with dpg.child_window(tag="content_area", autosize_x=True, height=-32, border=False):
            with dpg.group(tag="page_live_data", show=True):
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

        with dpg.theme(tag=THEME_STATUS_CONNECTED):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STATUS_GREEN_DARK)

        with dpg.theme(tag=THEME_STATUS_DISCONNECTED):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STATUS_RED_DARK)

        with dpg.child_window(tag="footer_bar", autosize_x=True, height=28, border=False, no_scrollbar=True):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=200, height=28, border=False, tag=STATUS_SERIAL_STATUS_BOX):
                    with dpg.table(header_row=False, resizable=False, policy=dpg.mvTable_SizingStretchProp, borders_innerV=False, borders_innerH=False, borders_outerH=False, borders_outerV=False, no_host_extendX=False, no_pad_innerX=True):
                        dpg.add_table_column(init_width_or_weight=1.0)
                        dpg.add_table_column(width_fixed=True)
                        dpg.add_table_column(init_width_or_weight=1.0)
                        with dpg.table_row():
                            with dpg.table_cell():
                                pass

                            with dpg.table_cell():
                                dpg.add_text("Serial: Disconnected", tag=STATUS_SERIAL_STATUS_TEXT)

                            with dpg.table_cell():
                                pass

    dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_DISCONNECTED)

    with dpg.window(label="Connection Menu", tag=WINDOW_CONNECTION_MENU, show=False, modal=True, no_collapse=True, width=300):
        dpg.add_combo([], tag=WINDOW_CONNECTION_MENU_COMBO)
        dpg.add_button(label="Connect", callback=dataflux.callbacks.serial.connection_window_connect_serial, user_data=state)
