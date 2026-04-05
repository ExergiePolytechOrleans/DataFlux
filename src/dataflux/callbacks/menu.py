# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import dearpygui.dearpygui as dpg
from dataflux.ui.routines import update_global_connection_status
import dataflux.ui.routines.windows
import dataflux.ui.routines.status
import dataflux.services.serial

from dataflux.tags import WINDOW_CONNECTION_MENU

def open_connection_window(sender, app_data, user_data) -> None:
    dataflux.ui.routines.windows.update_window_connection_menu_combo() 
    dpg.show_item(WINDOW_CONNECTION_MENU)

def menu_file_disconnect(sender, app_data, user_data) -> None:
    dataflux.services.serial.disconnect_serial(user_data)
    update_global_connection_status(user_data)

