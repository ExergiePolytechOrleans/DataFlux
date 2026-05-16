# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.callbacks.menu
import dataflux.callbacks.serial

from dataflux.state import AppState
from dataflux.tags import (
    BUTTON_SERIAL_CONSOLE_SEND,
    CHILD_WINDOW_SERIAL_CONSOLE,
    GRAPH_SERIES_SPEED,
    GRAPH_SERIES_TENG,
    GRAPH_SERIES_VBAT,
    GRAPH_X_AXIS_SPEED,
    GRAPH_X_AXIS_TENG,
    GRAPH_X_AXIS_VBAT,
    GRAPH_Y_AXIS_SPEED,
    GRAPH_Y_AXIS_TENG,
    GRAPH_Y_AXIS_VBAT,
    INPUT_SERIAL_CONSOLE,
    LIVE_DATA_TENG_VALUE,
    LIVE_DATA_UTC_TIME_VALUE,
    LIVE_DATA_VBAT_VALUE,
    LIVE_DATA_VEHICLE_TIME_VALUE,
    LIVE_DATA_SPEED_VALUE,
    MENU_IO_CONNECT_LORA,
    MENU_IO_DISCONNECT_LORA,
    MENU_FILE_DUMP_BUFFERS,
    MENU_IO_CONNECT_SERIAL,
    MENU_IO_DISCONNECT_SERIAL,
    PAGE_LAP_RECAP,
    PAGE_LIVE_DATA,
    PAGE_SERIAL_CONSOLE,
    STATUS_LORA_STATUS_BOX,
    STATUS_LORA_STATUS_TEXT,
    STATUS_SERIAL_STATUS_BOX,
    STATUS_SERIAL_STATUS_TEXT,
    SUB_PAGE_DATA_GRAPHS,
    SUB_PAGE_MAP,
    TEXT_SERIAL_CONSOLE,
    THEME_STATUS_CONNECTED,
    THEME_STATUS_CONNECTED_BRIGHT,
    THEME_STATUS_DISCONNECTED,
    WINDOW_LORA_CONNECTION_MENU,
    WINDOW_LORA_CONNECTION_MENU_COMBO,
    WINDOW_FILE_DIALOG_DUMP_BUFFERS,
    WINDOW_SERIAL_CONNECTION_MENU,
    WINDOW_SERIAL_CONNECTION_MENU_COMBO,
)
from dataflux.ui.colors import STATUS_GREEN_BRIGHT, STATUS_GREEN_DARK, STATUS_RED_DARK


def _add_live_data_row(label: str, value: str, tag: str, units: str) -> None:
    with dpg.table_row():
        with dpg.table_cell():
            dpg.add_text(label)
        with dpg.table_cell():
            dpg.add_text(value, tag=tag)
        with dpg.table_cell():
            dpg.add_text(units)


def build_windows(state: AppState) -> None:

    with dpg.window(label="DataFlux", tag="main_window", no_collapse=True):
        dpg.set_global_font_scale(0.5)
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="Dump Buffers",
                    enabled=True,
                    tag=MENU_FILE_DUMP_BUFFERS,
                    callback=dataflux.callbacks.menu.menu_file_dump_buffers,
                )
                dpg.add_menu_item(label="Quit")
            with dpg.menu(label="IO"):
                dpg.add_menu_item(
                    label="Connect LoRa",
                    enabled=True,
                    tag=MENU_IO_CONNECT_LORA,
                    callback=dataflux.callbacks.menu.open_lora_connection_window,
                    user_data=state,
                )
                dpg.add_menu_item(
                    label="Disonnect LoRa",
                    enabled=False,
                    tag=MENU_IO_DISCONNECT_LORA,
                    callback=dataflux.callbacks.menu.menu_io_disconnect_lora,
                    user_data=state,
                )
                dpg.add_menu_item(
                    label="Connect Serial",
                    enabled=True,
                    tag=MENU_IO_CONNECT_SERIAL,
                    callback=dataflux.callbacks.menu.open_serial_connection_window,
                    user_data=state,
                )
                dpg.add_menu_item(
                    label="Disonnect Serial",
                    enabled=False,
                    tag=MENU_IO_DISCONNECT_SERIAL,
                    callback=dataflux.callbacks.menu.menu_io_disconnect_serial,
                    user_data=state,
                )
            with dpg.menu(label="Window"):
                dpg.add_menu_item(
                    label="Live Graphs",
                    user_data=SUB_PAGE_DATA_GRAPHS,
                    callback=dataflux.callbacks.menu.menu_window_select,
                )
                dpg.add_menu_item(
                    label="Live Map",
                    user_data=SUB_PAGE_MAP,
                    callback=dataflux.callbacks.menu.menu_window_select,
                )
                dpg.add_menu_item(
                    label="Lap Recap",
                    user_data=PAGE_LAP_RECAP,
                    callback=dataflux.callbacks.menu.menu_window_select,
                )
                dpg.add_menu_item(
                    label="Serial Console",
                    user_data=PAGE_SERIAL_CONSOLE,
                    callback=dataflux.callbacks.menu.menu_window_select,
                )
            with dpg.menu(label="Data"):
                with dpg.menu(label="Timeframe"):
                    dpg.add_menu_item(
                        label="30s",
                        user_data=(state, 30),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="60s",
                        user_data=(state, 60),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="5m",
                        user_data=(state, 60 * 5),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="10m",
                        user_data=(state, 60 * 10),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="15m",
                        user_data=(state, 60 * 15),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="30m",
                        user_data=(state, 60 * 30),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="1h",
                        user_data=(state, 60 * 60),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )
                    dpg.add_menu_item(
                        label="2h",
                        user_data=(state, 60 * 120),
                        callback=dataflux.callbacks.menu.menu_data_timeframe,
                    )

        with dpg.child_window(
            tag="content_area", autosize_x=True, height=-32, border=False
        ):
            with dpg.group(tag=PAGE_LIVE_DATA, show=True):
                with dpg.group(horizontal=True):
                    with dpg.child_window(
                        tag="realtime_stats", width=260, autosize_y=True, border=True
                    ):
                        with dpg.table(
                            header_row=False,
                            resizable=False,
                            policy=dpg.mvTable_SizingFixedFit,
                            borders_innerH=False,
                            borders_innerV=False,
                            borders_outerH=False,
                            borders_outerV=False,
                            no_host_extendX=True,
                        ):
                            dpg.add_table_column(width_fixed=True)
                            dpg.add_table_column(
                                width_stretch=True, init_width_or_weight=1.0
                            )
                            dpg.add_table_column(width_fixed=True)
                            _add_live_data_row(
                                "UTC Time", "no_data", LIVE_DATA_UTC_TIME_VALUE, ""
                            )
                            _add_live_data_row(
                                "Vehicle Time",
                                "no_data",
                                LIVE_DATA_VEHICLE_TIME_VALUE,
                                "",
                            )
                            _add_live_data_row(
                                "Speed", "no_data", LIVE_DATA_SPEED_VALUE, "km/h"
                            )
                            _add_live_data_row(
                                "Battery Voltage", "no_data", LIVE_DATA_VBAT_VALUE, "V"
                            )
                            _add_live_data_row(
                                "Engine Temp", "no_data", LIVE_DATA_TENG_VALUE, "°C"
                            )

                    with dpg.child_window(
                        tag=SUB_PAGE_DATA_GRAPHS,
                        autosize_x=True,
                        autosize_y=True,
                        border=True,
                        show=True,
                    ):
                        with dpg.plot(
                            label="Speed", height=250, width=-1, no_inputs=True
                        ):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(
                                dpg.mvXAxis, label="Time", tag=GRAPH_X_AXIS_SPEED
                            )
                            y_axis_speed = dpg.add_plot_axis(
                                dpg.mvYAxis, label="Speed", tag=GRAPH_Y_AXIS_SPEED
                            )
                            dpg.set_axis_limits(GRAPH_Y_AXIS_SPEED, ymin=0, ymax=50)
                            dpg.set_axis_limits(GRAPH_X_AXIS_SPEED, ymin=-30, ymax=0)
                            dpg.add_line_series(
                                [], [], parent=y_axis_speed, tag=GRAPH_SERIES_SPEED
                            )
                        with dpg.plot(
                            label="Battery Voltage",
                            height=250,
                            width=-1,
                            no_inputs=True,
                        ):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(
                                dpg.mvXAxis, label="Time", tag=GRAPH_X_AXIS_VBAT
                            )
                            y_axis_vbat = dpg.add_plot_axis(
                                dpg.mvYAxis, label="Voltage", tag=GRAPH_Y_AXIS_VBAT
                            )
                            dpg.set_axis_limits(GRAPH_Y_AXIS_VBAT, ymin=0, ymax=20)
                            dpg.set_axis_limits(GRAPH_X_AXIS_VBAT, ymin=-30, ymax=0)
                            dpg.add_line_series(
                                [], [], parent=y_axis_vbat, tag=GRAPH_SERIES_VBAT
                            )
                        with dpg.plot(
                            label="Engine Temp", height=250, width=-1, no_inputs=True
                        ):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(
                                dpg.mvXAxis, label="Time", tag=GRAPH_X_AXIS_TENG
                            )
                            y_axis_teng = dpg.add_plot_axis(
                                dpg.mvYAxis, label="Temperature", tag=GRAPH_Y_AXIS_TENG
                            )
                            dpg.set_axis_limits(GRAPH_Y_AXIS_TENG, ymin=0, ymax=120)
                            dpg.set_axis_limits(GRAPH_X_AXIS_TENG, ymin=-30, ymax=0)
                            dpg.add_line_series(
                                [], [], parent=y_axis_teng, tag=GRAPH_SERIES_TENG
                            )

                    with dpg.child_window(
                        tag=SUB_PAGE_MAP,
                        autosize_x=True,
                        autosize_y=True,
                        border=True,
                        show=False,
                        no_scrollbar=True,
                    ):
                        with dpg.drawlist(width=500, height=500, tag="map_drawlist"):
                            dpg.draw_image("texture_tab", (0, 0), (500, 500))
                            dpg.draw_circle(
                                (0, 0),
                                10,
                                color=(255, 0, 0, 255),
                                fill=(255, 0, 0, 255),
                            )

            with dpg.group(tag=PAGE_LAP_RECAP, show=False):
                dpg.add_text("Lap Recap")
                dpg.add_separator()

            with dpg.group(tag=PAGE_SERIAL_CONSOLE, show=False):
                with dpg.child_window(
                    tag=CHILD_WINDOW_SERIAL_CONSOLE,
                    width=-1,
                    height=-40,
                    border=True,
                    horizontal_scrollbar=False,
                ):
                    dpg.add_text(tag=TEXT_SERIAL_CONSOLE, wrap=0)
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag=INPUT_SERIAL_CONSOLE, width=-100)
                    dpg.add_button(
                        tag=BUTTON_SERIAL_CONSOLE_SEND,
                        label="Send",
                        width=100,
                        callback=dataflux.callbacks.serial.serial_console_button_send,
                        user_data=state,
                    )

        with dpg.theme(tag=THEME_STATUS_CONNECTED):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STATUS_GREEN_DARK)

        with dpg.theme(tag=THEME_STATUS_CONNECTED_BRIGHT):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STATUS_GREEN_BRIGHT)

        with dpg.theme(tag=THEME_STATUS_DISCONNECTED):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, STATUS_RED_DARK)

        with dpg.child_window(
            tag="footer_bar",
            autosize_x=True,
            height=28,
            border=False,
            no_scrollbar=True,
        ):
            with dpg.group(horizontal=True):
                with dpg.child_window(
                    width=200, height=28, border=False, tag=STATUS_LORA_STATUS_BOX
                ):
                    with dpg.table(
                        header_row=False,
                        resizable=False,
                        policy=dpg.mvTable_SizingStretchProp,
                        borders_innerV=False,
                        borders_innerH=False,
                        borders_outerH=False,
                        borders_outerV=False,
                        no_host_extendX=False,
                        no_pad_innerX=True,
                    ):
                        dpg.add_table_column(init_width_or_weight=1.0)
                        dpg.add_table_column(width_fixed=True)
                        dpg.add_table_column(init_width_or_weight=1.0)
                        with dpg.table_row():
                            with dpg.table_cell():
                                pass
                            with dpg.table_cell():
                                dpg.add_text(
                                    "LoRa: Disconnected",
                                    tag=STATUS_LORA_STATUS_TEXT,
                                )
                            with dpg.table_cell():
                                pass
                with dpg.child_window(
                    width=200, height=28, border=False, tag=STATUS_SERIAL_STATUS_BOX
                ):
                    with dpg.table(
                        header_row=False,
                        resizable=False,
                        policy=dpg.mvTable_SizingStretchProp,
                        borders_innerV=False,
                        borders_innerH=False,
                        borders_outerH=False,
                        borders_outerV=False,
                        no_host_extendX=False,
                        no_pad_innerX=True,
                    ):
                        dpg.add_table_column(init_width_or_weight=1.0)
                        dpg.add_table_column(width_fixed=True)
                        dpg.add_table_column(init_width_or_weight=1.0)
                        with dpg.table_row():
                            with dpg.table_cell():
                                pass
                            with dpg.table_cell():
                                dpg.add_text(
                                    "Serial: Disconnected",
                                    tag=STATUS_SERIAL_STATUS_TEXT,
                                )
                            with dpg.table_cell():
                                pass

    dpg.bind_item_theme(STATUS_LORA_STATUS_BOX, THEME_STATUS_DISCONNECTED)
    dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_DISCONNECTED)

    with dpg.window(
        label="LoRa Connection Menu",
        tag=WINDOW_LORA_CONNECTION_MENU,
        show=False,
        modal=True,
        no_collapse=True,
        width=400,
        no_resize=True,
    ):
        dpg.add_combo([], tag=WINDOW_LORA_CONNECTION_MENU_COMBO)
        dpg.add_button(
            label="Connect",
            callback=dataflux.callbacks.serial.connection_window_connect_lora,
            user_data=state,
        )

    with dpg.window(
        label="Serial Connection Menu",
        tag=WINDOW_SERIAL_CONNECTION_MENU,
        show=False,
        modal=True,
        no_collapse=True,
        width=400,
        no_resize=True,
    ):
        dpg.add_combo([], tag=WINDOW_SERIAL_CONNECTION_MENU_COMBO)
        dpg.add_button(
            label="Connect",
            callback=dataflux.callbacks.serial.connection_window_connect_serial,
            user_data=state,
        )

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        tag=WINDOW_FILE_DIALOG_DUMP_BUFFERS,
        width=700,
        height=400,
        modal=True,
        callback=dataflux.callbacks.menu.window_file_dialog_dump_buffers_ok,
        user_data=state,
    ):
        dpg.add_file_extension(".csv")
