# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread

from serial import Serial
import serial

import dataflux.telemetry_common.telemetry_common
from dataflux.state import AppState


def connect_lora(state: AppState, device: str) -> bool:
    if not device:
        print("No LoRa port selected")
        state.connection_status_dirty = True
        return False

    if state.lora_port is not None:
        state.lora_port.close()
        state.lora_port = None

    try:
        state.lora_port = Serial(port=device, baudrate=115200)
    except serial.SerialException as exc:
        print(f"Could not open LoRa port {device!r}: {exc}")
        state.lora_port = None
        state.lora_thread_running = False
        state.connection_status_dirty = True
        return False

    state.lora_thread = Thread(target=lora_reader_worker, args=(state,), daemon=True)

    state.lora_thread_running = True
    state.connection_status_dirty = True
    state.lora_thread.start()
    return True


def disconnect_lora(state: AppState) -> None:
    if state.lora_port is None:
        return

    state.lora_thread_running = False
    try:
        state.lora_port.close()
    except OSError:
        pass
    state.lora_port = None
    state.connection_status_dirty = True


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

        except Exception:
            break

    disconnect_lora(state)


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
    telemetry_common = dataflux.telemetry_common.telemetry_common
    if len(body) < telemetry_common.LORA_HEADER_SIZE:
        return None

    lora = telemetry_common.unpack_lora_header(
        body[: telemetry_common.LORA_HEADER_SIZE]
    )
    payload = body[telemetry_common.LORA_HEADER_SIZE :]

    if lora.size != len(payload):
        print(
            f"Serial size mismatch header says {lora.size} actual payload is {len(payload)}"
        )
        return None

    calc_crc = telemetry_common.crc16_ccitt(payload)

    if calc_crc != lora.crc16:
        print("crc mismatch")
        return None

    base = {
        "source": lora.source,
        "dest": lora.dest,
        "version": lora.version,
    }

    if lora.version == 1:
        pkt = telemetry_common.unpack_packet1(payload)
        return {
            **base,
            "type": "packet1",
            "ping": pkt.ping.decode("ascii", errors="replace"),
        }

    if lora.version == 2:
        pkt = telemetry_common.unpack_packet2(payload)
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

    if lora.version == 3:
        pkt = telemetry_common.unpack_packet3(payload)
        return {
            **base,
            "type": "packet3",
            "start_time": pkt.start_time,
            "duration": pkt.duration,
            "count": pkt.count,
        }

    print("Unknown payload")
    return None
