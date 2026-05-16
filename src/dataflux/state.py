# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from threading import Lock, Thread
from serial import Serial
from queue import Queue


@dataclass
class Buffers:
    timestamp: list[int] = field(default_factory=list)
    speed: list[float] = field(default_factory=list)
    vbat: list[float] = field(default_factory=list)
    teng: list[float] = field(default_factory=list)
    lat: list[float] = field(default_factory=list)
    lng: list[float] = field(default_factory=list)


@dataclass
class AppState:
    running: bool = True

    lora_port: Serial | None = None
    lora_thread: Thread | None = None
    lora_thread_running: bool = False

    serial_port: Serial | None = None
    serial_thread: Thread | None = None
    serial_data_queue: Queue | None = field(default_factory=Queue)
    serial_thread_running: bool = False

    telemetry_thread: Thread | None = None
    telemetry_thread_running: bool = False

    lora_status_thread: Thread | None = None
    lora_status_queue: Queue = field(default_factory=Queue)

    serial_status_thread: Thread | None = None
    serial_status_queue: Queue = field(default_factory=Queue)

    ui_worker_thread: Thread | None = None

    packet_queue: Queue = field(default_factory=Queue)
    latest_telemetry: dict = field(default_factory=dict)
    telemetry_valid: bool = False

    raw_buffers: Buffers = field(default_factory=Buffers)
    live_buffers: Buffers = field(default_factory=Buffers)
    live_buffers_updated: bool = False
    live_buffer_len: int = 30

    buffer_dump_thread: Thread | None = None

    lock: Lock = field(default_factory=Lock)
