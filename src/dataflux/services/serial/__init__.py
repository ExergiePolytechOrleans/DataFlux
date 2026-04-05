# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import serial.tools.list_ports


def list_serial_ports() -> list[str]:
    ports = serial.tools.list_ports.comports()
    valid_ports: list[str] = []
    for port in ports:
        if port.vid is not None and port.pid is not None:
            valid_ports.append(port.device)

    return valid_ports



