# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg

from dataflux.tags import CHILD_WINDOW_SERIAL_CONSOLE, TEXT_SERIAL_CONSOLE


def append_text_to_console(text: str) -> None:
    old = dpg.get_value(TEXT_SERIAL_CONSOLE)
    dpg.set_value(TEXT_SERIAL_CONSOLE, old + text)

    def scroll_to_bottom() -> None:
        dpg.set_y_scroll(
            CHILD_WINDOW_SERIAL_CONSOLE,
            dpg.get_y_scroll_max(CHILD_WINDOW_SERIAL_CONSOLE),
        )

    frame = dpg.get_frame_count()
    dpg.set_frame_callback(frame + 1, scroll_to_bottom)
    dpg.set_frame_callback(frame + 2, scroll_to_bottom)
