# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from ast import arg
from threading import Thread
import dearpygui.dearpygui as dpg
from dataflux.state import AppState
from dataflux.ui.routines import update_global_connection_status
import dataflux.ui.routines.windows
import dataflux.ui.routines.status
import dataflux.services.serial
import dataflux.services.telemetry

from dataflux.tags import (
    GRAPH_X_AXIS_SPEED,
    GRAPH_X_AXIS_TENG,
    GRAPH_X_AXIS_VBAT,
    WINDOW_FILE_DIALOG_AUTOSAVE_BUFFERS,
    WINDOW_FILE_DIALOG_LOAD_LAP,
    WINDOW_LORA_CONNECTION_MENU,
    WINDOW_FILE_DIALOG_DUMP_BUFFERS,
    WINDOW_SERIAL_CONNECTION_MENU,
)


def open_lora_connection_window(sender, app_data, user_data: AppState) -> None:
    dataflux.ui.routines.windows.update_window_lora_connection_menu_combo(user_data)
    dpg.show_item(WINDOW_LORA_CONNECTION_MENU)


def open_serial_connection_window(sender, app_data, user_data: AppState) -> None:
    dataflux.ui.routines.windows.update_window_serial_connection_menu_combo(user_data)
    dpg.show_item(WINDOW_SERIAL_CONNECTION_MENU)


def menu_io_disconnect_lora(sender, app_data, user_data: AppState) -> None:
    dataflux.services.serial.disconnect_lora(user_data)
    update_global_connection_status(user_data)


def menu_io_disconnect_serial(sender, app_data, user_data: AppState) -> None:
    dataflux.services.serial.disconnect_serial(user_data)
    update_global_connection_status(user_data)


def menu_file_dump_buffers(sender, app_data, user_data: AppState) -> None:
    dpg.show_item(WINDOW_FILE_DIALOG_DUMP_BUFFERS)


def menu_file_load_lap(sender, app_data, user_data: AppState) -> None:
    dpg.show_item(WINDOW_FILE_DIALOG_LOAD_LAP)


def menu_file_quit(sender, app_data, user_data) -> None:
    dpg.stop_dearpygui()


def window_file_dialog_dump_buffers_ok(sender, app_data, user_data: AppState) -> None:
    user_data.buffer_dump_thread = Thread(
        target=dataflux.services.telemetry.buffer_dump,
        args=(user_data, app_data["file_path_name"]),
        daemon=True,
    )
    user_data.buffer_dump_thread.start()


def menu_file_autosave_buffers(sender, app_state, user_data: AppState) -> None:
    if user_data.autosave_enabled:
        user_data.autosave_enabled = False
        user_data.autosave_buffer_thread = None
    else:
        dpg.show_item(WINDOW_FILE_DIALOG_AUTOSAVE_BUFFERS)


def window_file_dialog_autosave_buffers_ok(
    sender, app_data, user_data: AppState
) -> None:
    user_data.autosave_enabled = True
    user_data.autosave_buffer_thread = Thread(
        target=dataflux.services.telemetry.autosave_worker,
        args=(user_data, app_data["file_path_name"]),
        daemon=True,
    )
    user_data.autosave_buffer_thread.start()


def window_file_dialog_load_lap_ok(sender, app_data, user_data: AppState) -> None:
    user_data.lap_loader_thread = Thread(
        target=dataflux.services.telemetry.lap_load_worker,
        args=(user_data, app_data["file_path_name"]),
        daemon=True,
    )
    user_data.lap_loader_thread.start()


def menu_window_select(sender, app_data, user_data: str) -> None:
    dataflux.ui.routines.windows.toggle_window(user_data)


def menu_data_timeframe(sender, app_data, user_data: tuple[AppState, int]) -> None:
    app_state, timeframe = user_data
    app_state.live_buffer_len = timeframe
    dpg.set_axis_limits(GRAPH_X_AXIS_SPEED, ymin=-(timeframe), ymax=0)
    dpg.set_axis_limits(GRAPH_X_AXIS_VBAT, ymin=-(timeframe), ymax=0)
    dpg.set_axis_limits(GRAPH_X_AXIS_TENG, ymin=-(timeframe), ymax=0)
