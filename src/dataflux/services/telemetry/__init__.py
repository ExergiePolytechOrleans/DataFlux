# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from bisect import bisect_left
from datetime import datetime, timezone
from queue import Empty
from dataflux.state import AppState, Buffers, LapInfo
import time
from pathlib import Path
import csv


def cs_to_datetime(date_utc: datetime, timestamp_cs: int) -> datetime:
    if not 0 <= timestamp_cs < 24 * 60 * 60 * 100:
        raise ValueError("timestamp_cs must be within one day")

    hours, rem = divmod(timestamp_cs, 60 * 60 * 100)
    minutes, rem = divmod(rem, 60 * 100)
    seconds, cs = divmod(rem, 100)

    return datetime(
        date_utc.year,
        date_utc.month,
        date_utc.day,
        hours,
        minutes,
        seconds,
        cs * 10_000,
        tzinfo=timezone.utc,
    )


def datetime_to_cs(dt: datetime) -> int:
    return (
        dt.hour * 60 * 60 * 100
        + dt.minute * 60 * 100
        + dt.second * 100
        + dt.microsecond // 10_000
    )


def telemetry_worker(state: AppState):
    while state.telemetry_thread_running:
        if not state.lora_thread_running:
            time.sleep(1)
            continue
        try:
            dataframe = state.packet_queue.get_nowait()
        except Empty:
            continue

        if not isinstance(dataframe, dict):
            print(f"Ignoring telemetry packet with unexpected type: {type(dataframe)}")
            continue

        packet_type = dataframe.get("type")
        now = datetime.now(timezone.utc)
        time_stamp = datetime_to_cs(now)

        if packet_type == "packet2":
            try:
                packet_time = int(dataframe["time_stamp"])
                speed = float(dataframe["speed"])
                vbat = float(dataframe["vbat"])
                teng = float(dataframe["teng"])
                lat = float(dataframe["lat"])
                lng = float(dataframe["lng"])
            except (KeyError, TypeError, ValueError) as exc:
                print(f"Ignoring malformed telemetry packet2: {exc}")
                continue

            if abs(packet_time - time_stamp) > 60 * 100:
                continue

            state.latest_telemetry = {
                **dataframe,
                "time_stamp": packet_time,
                "speed": speed,
                "vbat": vbat,
                "teng": teng,
                "lat": lat,
                "lng": lng,
            }
            state.telemetry_valid = True

            with state.lock:
                state.raw_buffers.timestamp.append(packet_time)
                state.raw_buffers.speed.append(speed)
                state.raw_buffers.vbat.append(vbat)
                state.raw_buffers.teng.append(teng)
                state.raw_buffers.lat.append(lat)
                state.raw_buffers.lng.append(lng)

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
        elif packet_type == "packet3":
            try:
                start_time = int(dataframe["start_time"])
                end_time = int(dataframe["duration"]) + start_time
                lap_count = int(dataframe["count"])
            except (KeyError, TypeError, ValueError) as exc:
                print(f"Ignoring malformed telemetry packet3: {exc}")
                continue

            lap: LapInfo = LapInfo(start_time, end_time, lap_count)
            state.laps.append(lap)
            state.new_laps.put(lap)


def save_lap(state: AppState, start_time: int, end_time: int, count: int) -> None:
    if state.autosave_path is None:
        print("Cannot save lap without an autosave path")
        return

    try:
        time_str = cs_to_datetime(datetime.now(timezone.utc), start_time).strftime(
            "%m_%d_%Y_%H_%M"
        )
    except ValueError:
        time_str = datetime.now(timezone.utc).strftime("%m_%d_%Y_%H_%M")

    save_path = Path(state.autosave_path) / f"{time_str}_lap_{count}.csv"
    data: Buffers = isolate_lap(state, start_time, end_time)

    try:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with save_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow(["timestamp", "speed", "vbat", "teng", "lat", "lng"])

            for row in zip(
                data.timestamp, data.speed, data.vbat, data.teng, data.lat, data.lng
            ):
                writer.writerow(row)
    except OSError as exc:
        print(f"Could not save lap to {save_path}: {exc}")


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

    try:
        save_path.parent.mkdir(parents=True, exist_ok=True)
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
    except OSError as exc:
        print(f"Could not dump buffers to {save_path}: {exc}")

    state.buffer_dump_thread = None


def autosave_worker(state: AppState, path: str) -> None:
    output_dir = Path(path)
    state.autosave_path = output_dir
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Could not create autosave directory {output_dir}: {exc}")
        state.autosave_enabled = False
        state.autosave_buffer_thread = None
        return

    ctr: int = 0
    while state.autosave_enabled:
        date_str = state.start_time.strftime("%m_%d_%Y_%H_%M")
        filename = date_str + ".csv"
        save_path = output_dir / filename
        buffer_dump(state, save_path)
        print(f"Autosave {ctr} complete")
        ctr += 1

        try:
            new_lap: LapInfo = state.new_laps.get_nowait()
        except Empty:
            pass
        else:
            save_lap(state, new_lap.start_time, new_lap.end_time, new_lap.count)

        time.sleep(30)

    state.autosave_buffer_thread = None


def lap_load_worker(state: AppState, path: str) -> None:
    state.lap_recap_buffers.timestamp.clear()
    state.lap_recap_buffers.speed.clear()
    state.lap_recap_buffers.vbat.clear()
    state.lap_recap_buffers.teng.clear()
    state.lap_recap_buffers.lat.clear()
    state.lap_recap_buffers.lng.clear()

    load_path = Path(path)

    try:
        with load_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                state.lap_recap_buffers.timestamp.append(int(row["timestamp"]))
                state.lap_recap_buffers.speed.append(float(row["speed"]))
                state.lap_recap_buffers.vbat.append(float(row["vbat"]))
                state.lap_recap_buffers.teng.append(float(row["teng"]))
                state.lap_recap_buffers.lat.append(float(row["lat"]))
                state.lap_recap_buffers.lng.append(float(row["lng"]))

    except FileNotFoundError:
        print(f"Lap file not found: {load_path}")
    except (KeyError, ValueError) as exc:
        print(f"Invalid lap file {load_path}: {exc}")
    except OSError as exc:
        print(f"Could not load lap file {load_path}: {exc}")
    else:
        state.lap_recap_updated = True

    state.lap_loader_thread = None


def closest_idx(values: list[int], target: int) -> int:
    if not values:
        raise ValueError("Cannot find closest index in an empty list")

    pos = bisect_left(values, target)

    if pos == 0:
        return 0

    if pos == len(values):
        return len(values) - 1

    before = pos - 1
    after = pos

    if abs(values[after] - target) < abs(values[before] - target):
        return after

    return before


def isolate_lap(state: AppState, start_time: int, end_time: int) -> Buffers:
    output: Buffers = Buffers()
    if not state.raw_buffers.timestamp:
        return output

    start_idx = closest_idx(state.raw_buffers.timestamp, start_time)
    end_idx = closest_idx(state.raw_buffers.timestamp, end_time)
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    output.timestamp = state.raw_buffers.timestamp[start_idx : end_idx + 1]
    output.speed = state.raw_buffers.speed[start_idx : end_idx + 1]
    output.vbat = state.raw_buffers.vbat[start_idx : end_idx + 1]
    output.teng = state.raw_buffers.teng[start_idx : end_idx + 1]
    output.lat = state.raw_buffers.lat[start_idx : end_idx + 1]
    output.lng = state.raw_buffers.lng[start_idx : end_idx + 1]

    return output
