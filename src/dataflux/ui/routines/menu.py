# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg

from dataflux.state import AppState
from dataflux.tags import MENU_FILE_CONNECT, MENU_FILE_DISCONNECT

def update_menu_file_connection_status(state: AppState) -> None:
    if state.serial_port is None:
        dpg.enable_item(MENU_FILE_CONNECT)
        dpg.disable_item(MENU_FILE_DISCONNECT)
    else:
        dpg.disable_item(MENU_FILE_CONNECT)
        dpg.enable_item(MENU_FILE_DISCONNECT)
