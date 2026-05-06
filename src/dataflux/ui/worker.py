# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import datetime
import time
from datetime import datetime, timezone

from dataflux.state import AppState
from dataflux.tags import GRAPH_SERIES_SPEED, GRAPH_SERIES_TENG, GRAPH_SERIES_VBAT, GRAPH_X_AXIS_SPEED, LIVE_DATA_TENG_VALUE, LIVE_DATA_UTC_TIME_VALUE, LIVE_DATA_VBAT_VALUE, LIVE_DATA_VEHICLE_TIME_VALUE, LIVE_DATA_SPEED_VALUE


def ui_worker(state: AppState):
    last_datetime: str = ""
    last_veh_time: str = ""
    last_veh_speed: str = ""
    last_vbat: str = ""
    last_teng: str = ""
    no_data_written = False
    while state.running: 
        now = datetime.now(timezone.utc)
        formatted = now.strftime("%H:%M:%S")
        
        if formatted != last_datetime:
            dpg.set_value(LIVE_DATA_UTC_TIME_VALUE, formatted)
            last_datetime = formatted
        
        if state.serial_thread_running and state.telemetry_valid:
            x_common: list[float] | None = None
            speed_y: list[float] | None = None
            vbat_y: list[float] | None = None
            teng_y: list[float] | None = None
            with state.lock:
                # Vehicle Time
                no_data_written = False
                veh_time = state.latest_telemetry["time_stamp"]
                veh_speed = state.latest_telemetry["speed"]
                vbat = state.latest_telemetry["vbat"]
                teng = state.latest_telemetry["teng"]
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
            if formatted != last_veh_time:
                dpg.set_value(LIVE_DATA_VEHICLE_TIME_VALUE, formatted)
                last_veh_time = formatted

            # Speed
            formatted = f"{veh_speed:05.2f}"
            if formatted != last_veh_speed:
                dpg.set_value(LIVE_DATA_SPEED_VALUE, formatted)
                last_veh_speed = formatted


            # VBAT
            formatted = f"{vbat:05.2f}"
            if formatted != last_vbat:
                dpg.set_value(LIVE_DATA_VBAT_VALUE, formatted)
                last_vbat = formatted

            # TENG
            formatted = f"{teng:05.2f}"
            if formatted != last_teng:
                dpg.set_value(LIVE_DATA_TENG_VALUE, formatted)
                last_teng = formatted

            if x_common is not None:
                dpg.set_value(GRAPH_SERIES_SPEED, [x_common, speed_y])
                dpg.set_value(GRAPH_SERIES_VBAT, [x_common, vbat_y])
                dpg.set_value(GRAPH_SERIES_TENG, [x_common, teng_y])

        else:
            if not no_data_written:
                dpg.set_value(LIVE_DATA_VEHICLE_TIME_VALUE, "no_data")
                dpg.set_value(LIVE_DATA_SPEED_VALUE, "no_data")
                dpg.set_value(LIVE_DATA_VBAT_VALUE, "no_data")
                dpg.set_value(LIVE_DATA_TENG_VALUE, "no_data")
                last_veh_time = last_veh_speed = last_vbat = last_teng = "no_data"
                no_data_written = True

        time.sleep(0.05)


        
    
