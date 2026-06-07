# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from queue import Empty
from threading import Thread

from serial import Serial
import serial

from dataflux.state import AppState


def connect_serial(state: AppState, device: str) -> bool:
    if not device:
        print("No serial console port selected")
        state.connection_status_dirty = True
        return False

    if state.serial_port is not None:
        state.serial_port.close()
        state.serial_port = None

    try:
        state.serial_port = Serial(
            port=device, baudrate=115200, timeout=0.05, write_timeout=0.1
        )
    except serial.SerialException as exc:
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
    try:
        state.serial_port.close()
    except OSError:
        pass
    state.serial_port = None
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
        except TypeError:
            break
        except serial.SerialException:
            break
        except OSError:
            break

        if line:
            text = line.decode("utf-8", errors="replace")
            state.serial_data_queue.put(text)
            state.serial_status_queue.put(0.05)

        if port.writable():
            try:
                data: str = state.serial_send_queue.get_nowait()
            except Empty:
                pass
            else:
                state.serial_data_queue.put(data + "\n")
                state.serial_status_queue.put(0.05)
                port.write(data.encode("utf-8"))

    disconnect_serial(state)
