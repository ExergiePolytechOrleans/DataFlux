# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg

from dataflux.tags import TEXT_SERIAL_CONSOLE


def append_text_to_console(text: str) -> None:
    old = dpg.get_value(TEXT_SERIAL_CONSOLE)
    dpg.set_value(TEXT_SERIAL_CONSOLE, old + text)
