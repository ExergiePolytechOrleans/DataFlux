# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
import sys
from threading import Thread
import dearpygui.dearpygui as dpg

from dataflux.state import AppState
import dataflux.config
import dataflux.ui.windows
import dataflux.ui.worker
import dataflux.services.telemetry


def _asset_path(relative_path: str) -> str:
    path = Path(relative_path)
    candidates: list[Path] = []

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir is not None:
        candidates.append(Path(bundle_dir) / path)

    candidates.extend((
        Path.cwd() / path,
        Path(__file__).resolve().parents[2] / path,
    ))

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Missing asset {relative_path!r}. Searched: {searched}")


def run() -> None:
    state: AppState = AppState()

    # Create application context and viewport
    dpg.create_context()

    map_path = _asset_path("assets/images/map.png")
    map_image = dpg.load_image(map_path)
    if map_image is None:
        raise RuntimeError(f"Failed to load map image: {map_path}")
    width, height, channels, data = map_image
    dataflux.config.MAP_IMAGE_WIDTH = width
    dataflux.config.MAP_IMAGE_HEIGHT = height

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="texture_tab")

    dpg.create_viewport(title='DataFlux', width=600, height=600)

    # Add Inter font to registry and bind as main app font
    with dpg.font_registry():
        app_font = dpg.add_font(_asset_path("assets/fonts/Inter-Regular.ttf"), 18*2)
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

    

