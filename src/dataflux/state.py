# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field
from threading import Lock, Thread
from serial import Serial

@dataclass
class AppState:
    running: bool = True

    serial_port: Serial | None = None
    serial_thread: Thread | None = None

    telemetry_thread: Thread | None = None

    lock: Lock = field(default_factory=Lock)
