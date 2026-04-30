# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import dearpygui.dearpygui as dpg

import dataflux.config
from dataflux.services.serial import list_serial_ports
from dataflux.tags import PAGE_LAP_RECAP, PAGE_LIVE_DATA, SUB_PAGE_DATA_GRAPHS, SUB_PAGE_MAP, WINDOW_CONNECTION_MENU_COMBO

def update_window_connection_menu_combo() -> None:
    ports: list[str] = list_serial_ports()
    dpg.configure_item(WINDOW_CONNECTION_MENU_COMBO, items=ports)


def hide_all_but(tag: str) -> None:
    arr = [PAGE_LIVE_DATA, PAGE_LAP_RECAP]
    for item in arr:
        if tag == item:
            dpg.show_item(item)
        else:
            dpg.hide_item(item)

def toggle_window(tag: str) -> None:
    if tag == SUB_PAGE_DATA_GRAPHS:
        dpg.show_item(SUB_PAGE_DATA_GRAPHS)
        dpg.hide_item(SUB_PAGE_MAP)
        hide_all_but(PAGE_LIVE_DATA)
    elif tag == SUB_PAGE_MAP:
        dpg.show_item(SUB_PAGE_MAP)
        dpg.hide_item(SUB_PAGE_DATA_GRAPHS)
        hide_all_but(PAGE_LIVE_DATA)
    else:
        hide_all_but(tag)


        
