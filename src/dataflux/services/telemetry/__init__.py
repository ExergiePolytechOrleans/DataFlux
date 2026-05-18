# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from queue import Empty
from dataflux.state import AppState, Buffers
import time
from pathlib import Path
import csv


def telemetry_worker(state: AppState):
    while state.telemetry_thread_running:
        if not state.lora_thread_running:
            time.sleep(1)
            continue
        try:
            dataframe = state.packet_queue.get_nowait()
        except Empty:
            continue

        if dataframe["type"] == "packet2":
            state.latest_telemetry = dataframe
            state.telemetry_valid = True
            with state.lock:
                state.raw_buffers.timestamp.append(dataframe["time_stamp"])
                state.raw_buffers.speed.append(dataframe["speed"])
                state.raw_buffers.vbat.append(dataframe["vbat"])
                state.raw_buffers.teng.append(dataframe["teng"])
                state.raw_buffers.lat.append(dataframe["lat"])
                state.raw_buffers.lng.append(dataframe["lng"])

                state.live_buffers_updated = True
                state.live_buffers.timestamp.clear()
                state.live_buffers.speed.clear()
                state.live_buffers.vbat.clear()
                state.live_buffers.teng.clear()
                state.live_buffers.lat.clear()
                state.live_buffers.lng.clear()

                if not state.raw_buffers.timestamp:
                    return

                last_timestamp = state.raw_buffers.timestamp[-1]
                cutoff = last_timestamp - (state.live_buffer_len * 100)

                i = len(state.raw_buffers.timestamp) - 1

                while i >= 0 and state.raw_buffers.timestamp[i] >= cutoff:
                    elapsed_seconds = (
                        state.raw_buffers.timestamp[i] - last_timestamp
                    ) / 100.0
                    state.live_buffers.timestamp.append(elapsed_seconds)
                    state.live_buffers.speed.append(state.raw_buffers.speed[i])
                    state.live_buffers.vbat.append(state.raw_buffers.vbat[i])
                    state.live_buffers.teng.append(state.raw_buffers.teng[i])
                    state.live_buffers.lat.append(state.raw_buffers.lat[i])
                    state.live_buffers.lng.append(state.raw_buffers.lng[i])
                    i -= 1

                state.live_buffers.timestamp.reverse()
                state.live_buffers.speed.reverse()
                state.live_buffers.vbat.reverse()
                state.live_buffers.teng.reverse()
                state.live_buffers.lat.reverse()
                state.live_buffers.lng.reverse()
        elif dataframe["type"] == "packet3":
            print(dataframe["type"])
            print(dataframe["start_time"])
            print(dataframe["duration"])
            print(dataframe["count"])


def buffer_dump(state: AppState, path: str) -> None:
    save_path = Path(path)
    if save_path.is_dir():
        save_path = save_path / "output.csv"

    with state.lock:
        local_raw_buffers = Buffers(
            timestamp=list(state.raw_buffers.timestamp),
            speed=list(state.raw_buffers.speed),
            vbat=list(state.raw_buffers.vbat),
            teng=list(state.raw_buffers.teng),
            lat=list(state.raw_buffers.lat),
            lng=list(state.raw_buffers.lng),
        )

    with save_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["timestamp", "speed", "vbat", "teng", "lat", "lng"])

        for row in zip(
            local_raw_buffers.timestamp,
            local_raw_buffers.speed,
            local_raw_buffers.vbat,
            local_raw_buffers.teng,
            local_raw_buffers.lat,
            local_raw_buffers.lng,
        ):
            writer.writerow(row)

    state.buffer_dump_thread = None


def autosave_worker(state: AppState, path: str) -> None:
    output_dir = Path(path)
    ctr: int = 0
    while state.autosave_enabled:
        date_str = state.start_time.strftime("%m_%d_%Y_%H_%M")
        filename = date_str + ".csv"
        save_path = output_dir / filename
        buffer_dump(state, save_path)
        print(f"Autosave {ctr} complete")
        ctr += 1
        time.sleep(30)
