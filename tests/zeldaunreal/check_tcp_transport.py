#!/usr/bin/env python3
"""Black-box test of the actual cycle debug TCP server, without a ROM."""
import json
from pathlib import Path
import socket
import subprocess
import sys


def exchange(sock, stream, command):
    sock.sendall((json.dumps(command, separators=(",", ":")) + "\n").encode())
    raw = stream.readline()
    assert raw.endswith(b"\n"), repr(raw)
    return json.loads(raw)


def main(binary):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    proc = subprocess.Popen([binary, str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ready = proc.stdout.readline().decode().strip()
        assert ready == "READY", f"Server startup failed: {ready!r}"
        with socket.create_connection(("127.0.0.1", port), timeout=2) as sock:
            sock.settimeout(2)
            with sock.makefile("rb") as stream:
                response = exchange(sock, stream, {"cmd": "zelda_bridge_probe", "room": 119, "id": 731})
                assert response == {"id": 731, "ok": True, "room": 119, "bridge": "ok"}, response
                response = exchange(sock, stream, {"cmd": "zelda_bridge_probe", "room": 129, "id": 732})
                assert response["ok"] is False and response["id"] == 732, response
                response = exchange(sock, stream, {"cmd": "nonexistent_zelda_command", "id": 733})
                assert response["ok"] is False and response["id"] == 733, response
                response = exchange(sock, stream, {"cmd": "help", "id": 734})
                assert response["ok"] is True and any(
                    item.get("name") == "zelda_bridge_probe" for item in response["commands"]
                ), response
        print("Cycle TCP loopback framing, dispatch, errors and help: PASS")
        return 0
    finally:
        proc.terminate()
        try:
            _, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, err = proc.communicate(timeout=3)
        if proc.returncode not in (0, -15):
            sys.stderr.write(err.decode(errors="replace"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
