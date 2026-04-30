# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
from threading import Thread
import dearpygui.dearpygui as dpg
from dataflux.state import AppState
from dataflux.ui.routines import update_global_connection_status
import dataflux.ui.routines.windows
import dataflux.ui.routines.status
import dataflux.services.serial
import dataflux.services.telemetry

from dataflux.tags import WINDOW_CONNECTION_MENU, WINDOW_FILE_DIALOG_DUMP_BUFFERS

def open_connection_window(sender, app_data, user_data) -> None:
    dataflux.ui.routines.windows.update_window_connection_menu_combo() 
    dpg.show_item(WINDOW_CONNECTION_MENU)

def menu_file_disconnect(sender, app_data, user_data) -> None:
    dataflux.services.serial.disconnect_serial(user_data)
    update_global_connection_status(user_data)

def menu_file_dump_buffers(sender, app_data, user_data: AppState) -> None:
    dpg.show_item(WINDOW_FILE_DIALOG_DUMP_BUFFERS)

def window_file_dialog_dump_buffers_ok(sender, app_data, user_data: AppState) -> None:
    user_data.buffer_dump_thread = Thread(target=dataflux.services.telemetry.buffer_dump, args=(user_data, app_data["file_path_name"]), daemon=True)
    user_data.buffer_dump_thread.start()

def menu_window_select(sender, app_data, user_data: str) -> None:
    dataflux.ui.routines.windows.toggle_window(user_data)

