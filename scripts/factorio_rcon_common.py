from __future__ import annotations

import os
import socket
import struct


SERVERDATA_RESPONSE_VALUE = 0
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2


def get_rcon_connection_settings() -> tuple[str, int, str]:
    host = os.environ.get("FACTORIO_RCON_HOST", "127.0.0.1")
    port = int(os.environ.get("FACTORIO_RCON_PORT", "27015"))
    password = os.environ.get("FACTORIO_RCON_PASSWORD")

    if not password:
        raise RuntimeError("FACTORIO_RCON_PASSWORD is not set")

    return host, port, password


def build_packet(request_id: int, packet_type: int, body: str) -> bytes:
    payload = struct.pack("<ii", request_id, packet_type)
    payload += body.encode("utf-8")
    payload += b"\x00\x00"
    size = struct.pack("<i", len(payload))
    return size + payload


def recv_exact(sock: socket.socket, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length

    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise RuntimeError("unexpected EOF from RCON socket")
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def read_packet(sock: socket.socket) -> tuple[int, int, str]:
    size_bytes = recv_exact(sock, 4)
    size = struct.unpack("<i", size_bytes)[0]
    payload = recv_exact(sock, size)

    request_id, packet_type = struct.unpack("<ii", payload[:8])
    body = payload[8:-2].decode("utf-8", errors="replace")
    return request_id, packet_type, body


def authenticate(sock: socket.socket, password: str) -> None:
    auth_request_id = 1
    sock.sendall(build_packet(auth_request_id, SERVERDATA_AUTH, password))

    while True:
        response_id, response_type, _response_body = read_packet(sock)

        if response_id == -1:
            raise RuntimeError("RCON authentication failed")

        if response_type == SERVERDATA_AUTH_RESPONSE:
            if response_id != auth_request_id:
                raise RuntimeError(f"unexpected auth response id: {response_id}")
            return


def execute(sock: socket.socket, command: str) -> None:
    command_request_id = 2
    sock.sendall(build_packet(command_request_id, SERVERDATA_EXECCOMMAND, command))

    while True:
        try:
            response_id, response_type, _response_body = read_packet(sock)
        except TimeoutError:
            return
        except socket.timeout:
            return

        if response_id == command_request_id and response_type == SERVERDATA_RESPONSE_VALUE:
            return


def run_rcon_command(
    command: str,
    *,
    connect_timeout_seconds: float = 5.0,
    socket_timeout_seconds: float = 1.0,
) -> None:
    host, port, password = get_rcon_connection_settings()

    with socket.create_connection((host, port), timeout=connect_timeout_seconds) as sock:
        sock.settimeout(socket_timeout_seconds)
        authenticate(sock, password)
        execute(sock, command)  