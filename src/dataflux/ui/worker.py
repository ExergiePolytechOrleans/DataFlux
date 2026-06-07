# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone
from queue import Empty
import time

import dearpygui.dearpygui as dpg
import dpg_map as dpgm

from dataflux.state import AppState
from dataflux.tags import (
    DEFAULT_LAT,
    DEFAULT_LNG,
    GRAPH_SERIES_SPEED,
    GRAPH_SERIES_SPEED_LR,
    GRAPH_SERIES_TENG,
    GRAPH_SERIES_TENG_LR,
    GRAPH_SERIES_VBAT,
    GRAPH_SERIES_VBAT_LR,
    GRAPH_X_AXIS_SPEED_LR,
    GRAPH_X_AXIS_TENG_LR,
    GRAPH_X_AXIS_VBAT_LR,
    LIVE_DATA_SPEED_VALUE,
    LIVE_DATA_TENG_VALUE,
    LIVE_DATA_UTC_TIME_VALUE,
    LIVE_DATA_VBAT_VALUE,
    LIVE_DATA_VEHICLE_TIME_VALUE,
    MENU_FILE_AUTOSAVE_BUFFERS,
    STATUS_LORA_STATUS_BOX,
    STATUS_SERIAL_STATUS_BOX,
    THEME_STATUS_CONNECTED,
    THEME_STATUS_CONNECTED_BRIGHT,
)
from dataflux.ui.routines import update_global_connection_status
from dataflux.ui.routines.serial import append_text_to_console


class UiFrameUpdater:
    def __init__(self) -> None:
        self.last_datetime: str = ""
        self.last_veh_time: str = ""
        self.last_veh_speed: str = ""
        self.last_vbat: str = ""
        self.last_teng: str = ""
        self.no_data_written = False
        self.lora_flash_until = 0.0
        self.serial_flash_until = 0.0
        self.last_map_update = 0.0

    def update(self, state: AppState) -> None:
        for updater in (
            self._update_connection_status,
            self._update_status_flashes,
            self._update_autosave_menu,
            self._update_utc_time,
            self._drain_serial_console,
            self._update_lap_recap,
            self._update_live_telemetry,
            self._update_live_map,
        ):
            try:
                updater(state)
            except Exception as exc:
                print(f"UI update failed in {updater.__name__}: {exc}")

    def _update_connection_status(self, state: AppState) -> None:
        if not state.connection_status_dirty:
            return

        update_global_connection_status(state)
        state.connection_status_dirty = False

    def _update_status_flashes(self, state: AppState) -> None:
        now = time.monotonic()

        self.lora_flash_until = self._drain_flash_queue(
            state.lora_status_queue, STATUS_LORA_STATUS_BOX, self.lora_flash_until, now
        )
        self.serial_flash_until = self._drain_flash_queue(
            state.serial_status_queue,
            STATUS_SERIAL_STATUS_BOX,
            self.serial_flash_until,
            now,
        )

        if state.lora_port is not None:
            theme = (
                THEME_STATUS_CONNECTED_BRIGHT
                if now < self.lora_flash_until
                else THEME_STATUS_CONNECTED
            )
            dpg.bind_item_theme(STATUS_LORA_STATUS_BOX, theme)

        if state.serial_port is not None:
            theme = (
                THEME_STATUS_CONNECTED_BRIGHT
                if now < self.serial_flash_until
                else THEME_STATUS_CONNECTED
            )
            dpg.bind_item_theme(STATUS_SERIAL_STATUS_BOX, theme)

    def _drain_flash_queue(
        self, queue, tag: str, flash_until: float, now: float
    ) -> float:
        if queue is None:
            return flash_until

        while True:
            try:
                duration = queue.get_nowait()
            except Empty:
                return flash_until

            try:
                flash_until = max(flash_until, now + float(duration))
            except (TypeError, ValueError):
                continue
            dpg.bind_item_theme(tag, THEME_STATUS_CONNECTED_BRIGHT)

    def _update_autosave_menu(self, state: AppState) -> None:
        dpg.set_value(MENU_FILE_AUTOSAVE_BUFFERS, state.autosave_enabled)

    def _update_utc_time(self, state: AppState | None = None) -> None:
        formatted = datetime.now(timezone.utc).strftime("%H:%M:%S")

        if formatted != self.last_datetime:
            dpg.set_value(LIVE_DATA_UTC_TIME_VALUE, formatted)
            self.last_datetime = formatted

    def _drain_serial_console(self, state: AppState) -> None:
        if state.serial_data_queue is None:
            return

        while True:
            try:
                text = state.serial_data_queue.get_nowait()
            except Empty:
                break

            if text is not None:
                append_text_to_console(str(text))

    def _update_lap_recap(self, state: AppState) -> None:
        if not state.lap_recap_updated:
            return

        state.lap_recap_updated = False
        timestamps = state.lap_recap_buffers.timestamp

        if timestamps:
            t0 = timestamps[0]
            x_common = [(t - t0) / 100.0 for t in timestamps]
        else:
            x_common = []

        dpg.set_value(GRAPH_SERIES_SPEED_LR, [x_common, state.lap_recap_buffers.speed])
        dpg.set_value(GRAPH_SERIES_VBAT_LR, [x_common, state.lap_recap_buffers.vbat])
        dpg.set_value(GRAPH_SERIES_TENG_LR, [x_common, state.lap_recap_buffers.teng])

        if not x_common:
            return

        axis_min = x_common[0]
        axis_max = x_common[-1]
        dpg.set_axis_limits(GRAPH_X_AXIS_SPEED_LR, ymin=axis_min, ymax=axis_max)
        dpg.set_axis_limits(GRAPH_X_AXIS_VBAT_LR, ymin=axis_min, ymax=axis_max)
        dpg.set_axis_limits(GRAPH_X_AXIS_TENG_LR, ymin=axis_min, ymax=axis_max)

    def _update_live_telemetry(self, state: AppState) -> None:
        if not (state.lora_thread_running and state.telemetry_valid):
            self._write_no_data()
            return

        x_common: list[float] | None = None
        speed_y: list[float] | None = None
        vbat_y: list[float] | None = None
        teng_y: list[float] | None = None

        with state.lock:
            self.no_data_written = False
            try:
                veh_time = int(state.latest_telemetry["time_stamp"])
                veh_speed = float(state.latest_telemetry["speed"])
                vbat = float(state.latest_telemetry["vbat"])
                teng = float(state.latest_telemetry["teng"])
            except (KeyError, TypeError, ValueError):
                state.telemetry_valid = False
                self._write_no_data()
                return

            if state.live_buffers_updated:
                x_common = list(state.live_buffers.timestamp)
                speed_y = list(state.live_buffers.speed)
                vbat_y = list(state.live_buffers.vbat)
                teng_y = list(state.live_buffers.teng)
                state.live_buffers_updated = False

        hours = veh_time // 360000
        minutes = (veh_time % 360000) // 6000
        seconds = (veh_time % 6000) // 100
        formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        if formatted != self.last_veh_time:
            dpg.set_value(LIVE_DATA_VEHICLE_TIME_VALUE, formatted)
            self.last_veh_time = formatted

        formatted = f"{veh_speed:05.2f}"
        if formatted != self.last_veh_speed:
            dpg.set_value(LIVE_DATA_SPEED_VALUE, formatted)
            self.last_veh_speed = formatted

        formatted = f"{vbat:05.2f}"
        if formatted != self.last_vbat:
            dpg.set_value(LIVE_DATA_VBAT_VALUE, formatted)
            self.last_vbat = formatted

        formatted = f"{teng:05.2f}"
        if formatted != self.last_teng:
            dpg.set_value(LIVE_DATA_TENG_VALUE, formatted)
            self.last_teng = formatted

        if x_common is not None:
            dpg.set_value(GRAPH_SERIES_SPEED, [x_common, speed_y])
            dpg.set_value(GRAPH_SERIES_VBAT, [x_common, vbat_y])
            dpg.set_value(GRAPH_SERIES_TENG, [x_common, teng_y])

    def _write_no_data(self) -> None:
        if self.no_data_written:
            return

        dpg.set_value(LIVE_DATA_VEHICLE_TIME_VALUE, "no_data")
        dpg.set_value(LIVE_DATA_SPEED_VALUE, "no_data")
        dpg.set_value(LIVE_DATA_VBAT_VALUE, "no_data")
        dpg.set_value(LIVE_DATA_TENG_VALUE, "no_data")
        self.last_veh_time = self.last_veh_speed = self.last_vbat = self.last_teng = (
            "no_data"
        )
        self.no_data_written = True

    def _update_live_map(self, state: AppState) -> None:
        now = time.monotonic()
        if state.live_map_pending_recenter:
            with state.lock:
                try:
                    lat = float(state.latest_telemetry.get("lat", DEFAULT_LAT))
                except (TypeError, ValueError):
                    lat = DEFAULT_LAT

                try:
                    lon = float(state.latest_telemetry.get("lng", DEFAULT_LNG))
                except (TypeError, ValueError):
                    lon = DEFAULT_LNG
            try:
                dpgm.set_center(lat=lat, lon=lon, map_tag="live_map")
            except Exception as exc:
                print(f"Could not recenter map: {exc}")
            state.live_map_pending_recenter = False

        if state.live_map_pending_zoom_in:
            try:
                zl: int = dpgm.get_zoom(map_tag="live_map")
                dpgm.set_zoom(zoom=zl + 1, map_tag="live_map")
            except Exception as exc:
                print(f"Could not zoom map in: {exc}")
            state.live_map_pending_zoom_in = False

        if state.live_map_pending_zoom_out:
            try:
                zl: int = dpgm.get_zoom(map_tag="live_map")
                dpgm.set_zoom(zoom=zl - 1, map_tag="live_map")
            except Exception as exc:
                print(f"Could not zoom map out: {exc}")
            state.live_map_pending_zoom_out = False

        if now - self.last_map_update < 0.1:
            return

        if not (state.lora_thread_running and state.telemetry_valid):
            return

        with state.lock:
            try:
                lat = float(state.latest_telemetry["lat"])
                lon = float(state.latest_telemetry["lng"])
            except (KeyError, TypeError, ValueError):
                return

        try:
            dpgm.update_marker("vehicle", lat=lat, lon=lon, map_tag="live_map")
        except Exception as exc:
            print(f"Could not update map marker: {exc}")
            return
        self.last_map_update = now
