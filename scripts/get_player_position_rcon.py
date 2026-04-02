from __future__ import annotations

import os
import socket
import struct
import sys


SERVERDATA_RESPONSE_VALUE = 0
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2


def _build_packet(request_id: int, packet_type: int, body: str) -> bytes:
    payload = struct.pack("<ii", request_id, packet_type)
    payload += body.encode("utf-8")
    payload += b"\x00\x00"
    size = struct.pack("<i", len(payload))
    return size + payload


def _recv_exact(sock: socket.socket, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length

    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise RuntimeError("unexpected EOF from RCON socket")
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def _read_packet(sock: socket.socket) -> tuple[int, int, str]:
    size_bytes = _recv_exact(sock, 4)
    size = struct.unpack("<i", size_bytes)[0]
    payload = _recv_exact(sock, size)

    request_id, packet_type = struct.unpack("<ii", payload[:8])
    body = payload[8:-2].decode("utf-8", errors="replace")
    return request_id, packet_type, body


def _authenticate(sock: socket.socket, password: str) -> None:
    auth_request_id = 1
    sock.sendall(_build_packet(auth_request_id, SERVERDATA_AUTH, password))

    first_id, first_type, _first_body = _read_packet(sock)
    second_id, second_type, _second_body = _read_packet(sock)

    valid_ids = {first_id, second_id}
    valid_types = {first_type, second_type}

    if -1 in valid_ids:
        raise RuntimeError("RCON authentication failed")

    if SERVERDATA_AUTH_RESPONSE not in valid_types:
        raise RuntimeError("RCON auth response not received")


def _execute(sock: socket.socket, command: str) -> str:
    command_request_id = 2
    terminator_request_id = 3

    sock.sendall(_build_packet(command_request_id, SERVERDATA_EXECCOMMAND, command))
    sock.sendall(_build_packet(terminator_request_id, SERVERDATA_RESPONSE_VALUE, ""))

    response_chunks: list[str] = []

    while True:
        response_id, response_type, response_body = _read_packet(sock)

        if response_id == terminator_request_id:
            break

        if response_id != command_request_id:
            raise RuntimeError(f"unexpected RCON response id: {response_id}")

        if response_type != SERVERDATA_RESPONSE_VALUE:
            raise RuntimeError(f"unexpected RCON response type: {response_type}")

        if response_body:
            response_chunks.append(response_body)

    return "".join(response_chunks).strip()


def main() -> int:
    host = os.environ.get("FACTORIO_RCON_HOST", "127.0.0.1")
    port = int(os.environ.get("FACTORIO_RCON_PORT", "27015"))
    password = os.environ.get("FACTORIO_RCON_PASSWORD")

    if not password:
        print("FACTORIO_RCON_PASSWORD is not set", file=sys.stderr)
        return 1

    command = (
        "/c "
        "local p = game.player.position; "
        "rcon.print('{\"x\":' .. p.x .. ',\"y\":' .. p.y .. '}')"
    )

    try:
        with socket.create_connection((host, port), timeout=5.0) as sock:
            sock.settimeout(5.0)
            _authenticate(sock, password)
            response_body = _execute(sock, command)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"RCON probe failed: {exc}", file=sys.stderr)
        return 1

    if not response_body:
        print("RCON probe returned empty response", file=sys.stderr)
        return 1

    print(response_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())