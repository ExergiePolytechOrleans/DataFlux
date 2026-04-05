# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import dearpygui.dearpygui as dpg

from dataflux.services.serial import list_serial_ports
from dataflux.tags import WINDOW_CONNECTION_MENU_COMBO

def update_window_connection_menu_combo() -> None:
    ports: list[str] = list_serial_ports()
    dpg.configure_item(WINDOW_CONNECTION_MENU_COMBO, items=ports)
