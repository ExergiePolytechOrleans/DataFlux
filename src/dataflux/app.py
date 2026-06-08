# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone
from pathlib import Path
import sys
from threading import Thread
import traceback
import dearpygui.dearpygui as dpg

from dataflux.state import AppState
import dpg_map as dpgm
from dataflux.tags import TEXT_SERIAL_CONSOLE
import dataflux.services.ports
import dataflux.ui.windows
import dataflux.ui.worker
import dataflux.services.telemetry


def _asset_path(relative_path: str) -> str:
    path = Path(relative_path)
    candidates: list[Path] = []

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir is not None:
        candidates.append(Path(bundle_dir) / path)

    candidates.extend(
        (
            Path.cwd() / path,
            Path(__file__).resolve().parents[2] / path,
        )
    )

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Missing asset {relative_path!r}. Searched: {searched}")


def run() -> None:
    state: AppState = AppState()
    state.start_time = datetime.now(timezone.utc)

    dpgm.configure(
        user_agent="DataFlux/0.1 contact:h3cx@h3cx.dev",
        cache_dir="./.cache",
        disk_cache_max_bytes=200_000_000,
    )

    dpg.create_context()
    try:
        dpg.configure_app(manual_callback_management=True)

        dpg.create_viewport(title="DataFlux", width=600, height=600)

        with dpg.font_registry():
            app_font = dpg.add_font(
                _asset_path("assets/fonts/Inter-Regular.ttf"), 18 * 2
            )
            mono_font = dpg.add_font(
                _asset_path("assets/fonts/JetBrainsMono-Regular.ttf"),
                size=36,
                label="mono_font",
            )
        dpg.bind_font(app_font)

        dataflux.ui.windows.build_windows(state)

        dpg.setup_dearpygui()
        dpg.show_viewport()

        vp_w = dpg.get_viewport_client_width()
        vp_h = dpg.get_viewport_client_height()
        dpg.configure_item("main_window", pos=(0, 0), width=vp_w, height=vp_h)
        dpg.set_primary_window("main_window", True)
        dpg.bind_item_font(TEXT_SERIAL_CONSOLE, mono_font)

        state.telemetry_thread_running = True
        state.telemetry_thread = Thread(
            target=dataflux.services.telemetry.telemetry_worker,
            args=(state,),
            daemon=True,
        )
        state.telemetry_thread.start()

        state.ports_thread_running = True
        state.ports_thread = Thread()
        state.ports_thread.start()

        ui_updater = dataflux.ui.worker.UiFrameUpdater()
        while dpg.is_dearpygui_running():
            jobs = dpg.get_callback_queue()
            try:
                dpg.run_callbacks(jobs)
                ui_updater.update(state)
            except Exception:
                traceback.print_exc()
            dpg.render_dearpygui_frame()
    finally:
        state.running = False
        state.telemetry_thread_running = False
        state.ports_thread_running = False
        state.lora_thread_running = False
        state.serial_thread_running = False

        try:
            dataflux.services.lora.disconnect_lora(state)
            dataflux.services.serial_console.disconnect_serial(state)
        finally:
            dpg.destroy_context()
