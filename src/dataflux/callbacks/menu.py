# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import dearpygui.dearpygui as dpg
import dataflux.ui.routines.windows

from dataflux.tags import WINDOW_CONNECTION_MENU

def open_connection_window(sender, app_data, user_data) -> None:
    dataflux.ui.routines.windows.update_window_connection_menu_combo() 
    dpg.show_item(WINDOW_CONNECTION_MENU)
