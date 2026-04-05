# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from threading import Lock, Thread
from serial import Serial
from queue import Queue

@dataclass
class AppState:
    running: bool = True

    serial_port: Serial | None = None
    serial_thread: Thread | None = None
    serial_thread_running: bool = False

    telemetry_thread: Thread | None = None

    serial_status_thread: Thread | None = None
    serial_status_queue: Queue = field(default_factory=Queue)

    packet_queue: Queue = field(default_factory=Queue)
    latest_telemetry: dict = field(default_factory=dict)

    lock: Lock = field(default_factory=Lock)
