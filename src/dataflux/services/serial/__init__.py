# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from concurrent.futures import thread
import os
from queue import Empty
from sys import base_exec_prefix
from threading import Thread
import time
from serial import Serial
import serial.tools.list_ports
import dearpygui.dearpygui as dpg
from dataflux import telemetry_common
from dataflux.tags import TEXT_SERIAL_CONSOLE
import dataflux.telemetry_common.telemetry_common
import dataflux.ui.routines.status
import dataflux.ui.routines

from dataflux.state import AppState


def list_serial_ports() -> list[str]:
    ports = serial.tools.list_ports.comports()
    valid_ports: list[str] = []
    for port in ports:
        if port.vid is not None and port.pid is not None:
            valid_ports.append(port.device)

    return valid_ports


def connect_lora(state: AppState, device: str) -> None:
    if state.lora_port is not None:
        state.lora_port.close()
        state.lora_port = None

    state.lora_port = Serial(port=device, baudrate=115200)
    state.lora_thread = Thread(target=lora_reader_worker, args=(state,), daemon=True)
    state.lora_status_thread = Thread(
        target=lora_status_worker, args=(state,), daemon=True
    )

    state.lora_thread_running = True
    state.lora_status_thread.start()
    state.lora_thread.start()


def connect_serial(state: AppState, device: str) -> None:
    if state.serial_port is not None:
        state.serial_port.close()
        state.serial_port = None

    state.serial_port = Serial(
        port=device, baudrate=115200, timeout=0.05, write_timeout=0.1
    )
    state.serial_thread = Thread(target=serial_worker, args=(state,), daemon=True)
    state.serial_status_thread = Thread(
        target=serial_status_worker, args=(state,), daemon=True
    )

    state.serial_thread_running = True
    state.serial_status_thread.start()
    state.serial_thread.start()


def disconnect_lora(state: AppState) -> None:
    if state.lora_port is not None:
        state.lora_thread_running = False
        state.lora_port.close()
        state.lora_port = None


def disconnect_serial(state: AppState) -> None:
    if state.serial_port is not None:
        state.serial_thread_running = False
        state.serial_port.close()
        state.serial_port = None


def lora_status_worker(state: AppState) -> None:
    while state.lora_thread_running:
        try:
            duration = state.lora_status_queue.get_nowait()
        except Empty:
            continue
        dataflux.ui.routines.status.flash_status_connection_status(duration)


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

        line = port.readline()

        if line:
            text = line.decode("utf-8", errors="replace")
            state.serial_data_queue.put(text)

        if port.writable():
            try:
                data: str = state.serial_send_queue.get_nowait()
            except Empty:
                pass
            else:
                state.serial_data_queue.put(data + "\n")
                port.write(data.encode("utf-8"))
                print("Wrote data: " + data)
    disconnect_serial(state)
    dataflux.ui.routines.update_global_connection_status(state)


def serial_status_worker(state: AppState) -> None:
    while state.serial_thread_running:
        time.sleep(1)


def lora_reader_worker(state: AppState) -> None:
    while state.lora_thread_running:
        port = state.lora_port
        if port is None:
            break
        if port.closed:
            print("Port closed")
            break

        try:
            packet = read_one_uart_packet(port)
            if packet is None:
                continue

            parsed = parse_uart_packet(packet)
            if parsed is not None:
                state.packet_queue.put(parsed)
                state.lora_status_queue.put(0.1)

        except Exception as e:
            print(f"Serial parser error: {e}")
            break
    disconnect_lora(state)
    dataflux.ui.routines.update_global_connection_status(state)


def read_one_uart_packet(port: Serial) -> bytes | None:
    first = port.read(1)
    if not first:
        return None

    if first != dataflux.telemetry_common.telemetry_common.UART_MAGIC[:1]:
        return None

    rest_magic = port.read(3)
    if len(rest_magic) != 3:
        return None

    if first + rest_magic != dataflux.telemetry_common.telemetry_common.UART_MAGIC:
        return None

    size_bytes = port.read(1)
    if len(size_bytes) != 1:
        return None

    body_size = size_bytes[0]

    body = port.read(body_size)
    if len(body) != body_size:
        return None

    return body


def parse_uart_packet(body: bytes) -> dict | None:
    if len(body) < dataflux.telemetry_common.telemetry_common.LORA_HEADER_SIZE:
        return None

    lora = dataflux.telemetry_common.telemetry_common.unpack_lora_header(
        body[: dataflux.telemetry_common.telemetry_common.LORA_HEADER_SIZE]
    )
    payload = body[dataflux.telemetry_common.telemetry_common.LORA_HEADER_SIZE :]

    if lora.size != len(payload):
        print(
            f"Serial size mismatch header says {lora.size} actual payload is {len(payload)}"
        )
        return None

    calc_crc = dataflux.telemetry_common.telemetry_common.crc16_ccitt(payload)

    if calc_crc != lora.crc16:
        print("crc mismatch")
        return None

    base = {
        "source": lora.source,
        "dest": lora.dest,
        "version": lora.version,
    }

    if lora.version == 1:
        pkt = dataflux.telemetry_common.telemetry_common.unpack_packet1(payload)
        return {
            **base,
            "type": "packet1",
            "ping": pkt.ping.decode("ascii", errors="replace"),
        }

    if lora.version == 2:
        pkt = dataflux.telemetry_common.telemetry_common.unpack_packet2(payload)
        return {
            **base,
            "type": "packet2",
            "time_stamp": pkt.time_stamp,
            "vbat": pkt.vbat,
            "teng": pkt.teng,
            "lat": pkt.lat,
            "lng": pkt.lng,
            "speed": pkt.speed,
        }

    print("Unknown payload")
    return None
