# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
from dataflux.state import AppState
from dataflux.tags import STATUS_SERIAL_STATUS_BOX, STATUS_SERIAL_STATUS_TEXT, THEME_STATUS_CONNECTED, THEME_STATUS_CONNECTED_BRIGHT, THEME_STATUS_DISCONNECTED
from time import sleep

def update_status_connection_status(state: AppState):
    if state.serial_port is None:
        dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_DISCONNECTED)
        dpg.set_value(STATUS_SERIAL_STATUS_TEXT, "Serial: Disconnected")
    else:
        dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_CONNECTED)
        dpg.set_value(STATUS_SERIAL_STATUS_TEXT, "Serial: Connected")

def flash_status_connection_status(duration: float) -> None:
    dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_CONNECTED_BRIGHT)
    sleep(duration) 
    dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, THEME_STATUS_CONNECTED)
