# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg

from dataflux.state import AppState
from dataflux.tags import (
    MENU_IO_CONNECT_LORA,
    MENU_IO_CONNECT_SERIAL,
    MENU_IO_DISCONNECT_LORA,
    MENU_IO_DISCONNECT_SERIAL,
)


def update_menu_file_connection_status(state: AppState) -> None:
    if state.lora_port is None:
        dpg.enable_item(MENU_IO_CONNECT_LORA)
        dpg.disable_item(MENU_IO_DISCONNECT_LORA)
    else:
        dpg.disable_item(MENU_IO_CONNECT_LORA)
        dpg.enable_item(MENU_IO_DISCONNECT_LORA)

    if state.serial_port is None:
        dpg.enable_item(MENU_IO_CONNECT_SERIAL)
        dpg.disable_item(MENU_IO_DISCONNECT_SERIAL)
    else:
        dpg.disable_item(MENU_IO_CONNECT_SERIAL)
        dpg.enable_item(MENU_IO_DISCONNECT_SERIAL)
