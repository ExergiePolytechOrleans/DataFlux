# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from queue import Empty
from threading import Thread

from serial import Serial
import serial

from dataflux.state import AppState


def _close_serial_port(state: AppState) -> None:
    if state.serial_port is None:
        return

    try:
        state.serial_port.close()
    except (OSError, serial.SerialException) as exc:
        print(f"Could not close serial console port: {exc}")
    finally:
        state.serial_port = None


def connect_serial(state: AppState, device: str | None) -> bool:
    if not device:
        print("No serial console port selected")
        state.connection_status_dirty = True
        return False

    _close_serial_port(state)

    try:
        state.serial_port = Serial(
            port=device, baudrate=115200, timeout=0.05, write_timeout=0.1
        )
    except (OSError, serial.SerialException, ValueError) as exc:
        print(f"Could not open serial console port {device!r}: {exc}")
        state.serial_port = None
        state.serial_thread_running = False
        state.connection_status_dirty = True
        return False

    state.serial_thread = Thread(target=serial_worker, args=(state,), daemon=True)

    state.serial_thread_running = True
    state.connection_status_dirty = True
    state.serial_thread.start()
    return True


def disconnect_serial(state: AppState) -> None:
    if state.serial_port is None:
        return

    state.serial_thread_running = False
    _close_serial_port(state)
    state.connection_status_dirty = True


def serial_worker(state: AppState) -> None:
    while state.serial_thread_running:
        port = state.serial_port
        if port is None:
            break
        if port.closed:
            print("Port closed")
            break
        if port.port is not None and not os.path.exists(port.port):
            break

        try:
            line = port.readline()
        except (TypeError, OSError, serial.SerialException) as exc:
            print(f"Serial console read failed: {exc}")
            break

        if line:
            text = line.decode("utf-8", errors="replace")
            state.serial_data_queue.put(text)
            state.serial_status_queue.put(0.05)

        try:
            writable = port.writable()
        except (OSError, serial.SerialException) as exc:
            print(f"Serial console write check failed: {exc}")
            break

        if not writable:
            continue

        try:
            data = state.serial_send_queue.get_nowait()
        except Empty:
            continue

        if data is None:
            continue

        text_to_send = str(data)
        try:
            port.write(text_to_send.encode("utf-8"))
        except (OSError, serial.SerialException, TypeError) as exc:
            print(f"Serial console write failed: {exc}")
            break

        state.serial_data_queue.put(text_to_send + "\n")
        state.serial_status_queue.put(0.05)

    disconnect_serial(state)
