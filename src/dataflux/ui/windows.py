# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.callbacks.menu

from dataflux.tags import MENU_FILE_CONNECT, MENU_FILE_DISCONNECT, WINDOW_CONNECTION_MENU, WINDOW_CONNECTION_MENU_COMBO


def build_windows() -> None:
    
    with dpg.window(label='DataFlux',tag="main_window", no_collapse=True):
        with dpg.menu_bar():
            with dpg.menu(label='File'):
                dpg.add_menu_item(label="Connect", enabled=True, tag=MENU_FILE_CONNECT, callback=dataflux.callbacks.menu.open_connection_window)
                dpg.add_menu_item(label="Disonnect", enabled=False, tag=MENU_FILE_DISCONNECT)
                dpg.add_menu_item(label="Quit")
            with dpg.menu(label='Window'):
                dpg.add_menu_item(label="Live Data", user_data="page_live_data")
                dpg.add_menu_item(label="Lap Recap", user_data="page_lap_recap")

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

    with dpg.window(label="Connection Menu", tag=WINDOW_CONNECTION_MENU, show=False, modal=True, no_collapse=True, width=300):
        dpg.add_combo([], tag=WINDOW_CONNECTION_MENU_COMBO)
        dpg.add_button(label="Connect")
