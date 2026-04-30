# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
import dearpygui.dearpygui as dpg

from dataflux.state import AppState
import dataflux.config
import dataflux.ui.windows
import dataflux.ui.worker
import dataflux.services.telemetry

def run() -> None:
    state: AppState = AppState()

    # Create application context and viewport
    dpg.create_context()

    width, height, channels, data = dpg.load_image("map.png")
    dataflux.config.MAP_IMAGE_WIDTH = width
    dataflux.config.MAP_IMAGE_HEIGHT = height

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="texture_tab")

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

    state.ui_worker_thread = Thread(target=dataflux.ui.worker.ui_worker, args=(state,), daemon=True)
    state.ui_worker_thread.start()

    state.telemetry_thread_running = True
    state.telemetry_thread = Thread(target=dataflux.services.telemetry.telemetry_worker, args=(state, ), daemon=True)
    state.telemetry_thread.start()

    dpg.start_dearpygui()

    dpg.destroy_context()

    


