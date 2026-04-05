# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from queue import Empty
from sys import base_exec_prefix
from threading import Thread
from serial import Serial
import serial.tools.list_ports
from dataflux import telemetry_common
import dataflux.telemetry_common.telemetry_common
import dataflux.ui.routines.status

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
    state.serial_thread = Thread(target=serial_reader_worker, args=(state,), daemon=True)
    state.serial_status_thread = Thread(target=serial_status_worker, args=(state,), daemon=True)

    state.serial_thread_running = True
    state.serial_status_thread.start()
    state.serial_thread.start()

def disconnect_serial(state: AppState) -> None:
    if state.serial_port is not None:
        state.serial_thread_running = False
        state.serial_port.close()
        state.serial_port = None

def serial_status_worker(state: AppState) -> None:
    while state.serial_thread_running:
        try:
            duration = state.serial_status_queue.get(timeout=0.1)
        except Empty:
            continue
        dataflux.ui.routines.status.flash_status_connection_status(duration)


    

def serial_reader_worker(state: AppState) -> None:
    while state.serial_thread_running:
        port = state.serial_port
        if port is None:
            break

        try:
            packet = read_one_uart_packet(port)
            if packet is None:
                continue

            parsed = parse_uart_packet(packet)
            if parsed is not None:
                state.packet_queue.put(parsed)
                state.serial_status_queue.put(0.1)
                print(parsed)

        except Exception as e:
            print(f"Serial parser error: {e}")

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

    lora = dataflux.telemetry_common.telemetry_common.unpack_lora_header(body[:dataflux.telemetry_common.telemetry_common.LORA_HEADER_SIZE])
    payload = body[dataflux.telemetry_common.telemetry_common.LORA_HEADER_SIZE:]

    if lora.size != len(payload):
        print(f"Serial size mismatch header says {lora.size} actual payload is {len(payload)}")
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
            "ping": pkt.ping.decode("ascii", errors="replace")
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


