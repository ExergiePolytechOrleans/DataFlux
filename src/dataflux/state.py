# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Lock, Thread
from serial import Serial
from queue import Queue

from serial.tools.list_ports_common import ListPortInfo


@dataclass
class Buffers:
    timestamp: list[int] = field(default_factory=list)
    speed: list[float] = field(default_factory=list)
    vbat: list[float] = field(default_factory=list)
    teng: list[float] = field(default_factory=list)
    lat: list[float] = field(default_factory=list)
    lng: list[float] = field(default_factory=list)


@dataclass
class LapInfo:
    start_time: int = field(default_factory=int)
    end_time: int = field(default_factory=int)
    count: int = field(default_factory=int)


@dataclass
class AppState:
    running: bool = True
    start_time: datetime = datetime.now()

    ports: list[ListPortInfo] = field(default_factory=list)
    ports_thread: Thread | None = None
    ports_thread_running: bool = False

    lora_port: Serial | None = None
    lora_thread: Thread | None = None
    lora_thread_running: bool = False

    serial_port: Serial | None = None
    serial_thread: Thread | None = None
    serial_data_queue: Queue | None = field(default_factory=Queue)
    serial_send_queue: Queue | None = field(default_factory=Queue)
    serial_thread_running: bool = False

    telemetry_thread: Thread | None = None
    telemetry_thread_running: bool = False

    lora_status_queue: Queue = field(default_factory=Queue)

    serial_status_queue: Queue = field(default_factory=Queue)

    connection_status_dirty: bool = True

    packet_queue: Queue = field(default_factory=Queue)
    latest_telemetry: dict = field(default_factory=dict)
    telemetry_valid: bool = False

    raw_buffers: Buffers = field(default_factory=Buffers)
    live_buffers: Buffers = field(default_factory=Buffers)
    live_buffers_updated: bool = False
    live_buffer_len: int = 30

    lap_recap_buffers: Buffers = field(default_factory=Buffers)
    lap_recap_updated: bool = False

    lap_lock: Lock = field(default_factory=Lock)
    new_laps: Queue = field(default_factory=Queue)
    laps: list[LapInfo] = field(default_factory=list)

    buffer_dump_thread: Thread | None = None
    autosave_buffer_thread: Thread | None = None
    autosave_enabled: bool = False
    autosave_path: Path | None = None

    lap_loader_thread: Thread | None = None

    live_map_pending_recenter: bool = False
    live_map_pending_zoom_in: bool = False
    live_map_pending_zoom_out: bool = False

    lock: Lock = field(default_factory=Lock)
