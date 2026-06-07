# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.services.lora
import dataflux.services.serial_console
import dataflux.ui.routines

from dataflux.state import AppState
from dataflux.tags import (
    INPUT_SERIAL_CONSOLE,
    WINDOW_LORA_CONNECTION_MENU,
    WINDOW_LORA_CONNECTION_MENU_COMBO,
    WINDOW_SERIAL_CONNECTION_MENU,
    WINDOW_SERIAL_CONNECTION_MENU_COMBO,
)


def connection_window_connect_lora(sender, app_data, user_data: AppState) -> None:
    device = dpg.get_value(WINDOW_LORA_CONNECTION_MENU_COMBO)
    connected = dataflux.services.lora.connect_lora(user_data, device)
    dataflux.ui.routines.update_global_connection_status(user_data)
    if connected:
        dpg.hide_item(WINDOW_LORA_CONNECTION_MENU)


def connection_window_connect_serial(sender, app_data, user_data: AppState) -> None:
    device = dpg.get_value(WINDOW_SERIAL_CONNECTION_MENU_COMBO)
    connected = dataflux.services.serial_console.connect_serial(user_data, device)
    dataflux.ui.routines.update_global_connection_status(user_data)
    if connected:
        dpg.hide_item(WINDOW_SERIAL_CONNECTION_MENU)


def serial_console_button_send(sender, app_data, user_data: AppState) -> None:
    text = dpg.get_value(INPUT_SERIAL_CONSOLE)
    dpg.set_value(INPUT_SERIAL_CONSOLE, "")
    if text is None:
        return

    text = str(text)
    if not text:
        return

    if user_data.serial_port is None or not user_data.serial_thread_running:
        print("Serial console is not connected")
        return

    user_data.serial_send_queue.put(text)
    print("Put into send queue: " + text)
