# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import serial.tools.list_ports

from dataflux.state import AppState


def list_serial_ports(state: AppState) -> list[str]:
    valid_ports: list[str] = []

    for port in state.ports:
        if port.vid is not None and port.pid is not None:
            valid_ports.append(port.device)

    return valid_ports


def ports_worker(state: AppState) -> None:
    while state.ports_thread_running:
        state.ports = serial.tools.list_ports.comports()
        time.sleep(5)
