# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from serial import Serial
import serial.tools.list_ports

from dataflux.state import AppState


def list_serial_ports() -> list[str]:
    ports = serial.tools.list_ports.comports()
    valid_ports: list[str] = []
    for port in ports:
        if port.vid is not None and port.pid is not None:
            valid_ports.append(port.device)

    return valid_ports

def connect_serial(state: AppState, device: str) -> None:
    if state.serial_port is not None:
        state.serial_port.close()
        state.serial_port = None

    state.serial_port = Serial(port=device, baudrate=115200)

def disconnect_serial(state: AppState) -> None:
    if state.serial_port is not None:
        state.serial_port.close()
        state.serial_port = None



