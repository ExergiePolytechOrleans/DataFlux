# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg

from dataflux.state import AppState
import dataflux.ui.windows

def run() -> None:
    state: AppState = AppState()

    # Create application context and viewport
    dpg.create_context()
    dpg.create_viewport(title='DataFlux', width=600, height=600)

    # Add Inter font to registry and bind as main app font
    with dpg.font_registry():
        app_font = dpg.add_font("./Inter-Regular.ttf", 18)
    dpg.bind_font(app_font)

    dataflux.ui.windows.build_windows(state)

    dpg.setup_dearpygui()
    dpg.show_viewport()


    vp_w = dpg.get_viewport_client_width()
    vp_h = dpg.get_viewport_client_height()
    dpg.configure_item("main_window", pos=(0, 0), width=vp_w, height=vp_h)
    dpg.set_primary_window("main_window", True)

    dpg.start_dearpygui()

    dpg.destroy_context()

    



