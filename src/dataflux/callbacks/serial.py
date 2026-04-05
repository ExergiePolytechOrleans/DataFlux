# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.services.serial
import dataflux.ui.routines

from dataflux.state import AppState
from dataflux.tags import WINDOW_CONNECTION_MENU, WINDOW_CONNECTION_MENU_COMBO


def connection_window_connect_serial(sender, app_data, user_data: AppState) -> None:
    device = dpg.get_value(WINDOW_CONNECTION_MENU_COMBO)
    dataflux.services.serial.connect_serial(user_data, device)
    dataflux.ui.routines.update_global_connection_status(user_data)
    dpg.hide_item(WINDOW_CONNECTION_MENU)
    
