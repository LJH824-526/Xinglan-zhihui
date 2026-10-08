"""Minimal client for the blender_mcp addon socket server (127.0.0.1:9876)."""
import argparse
import json
import socket
import sys

HOST, PORT = "127.0.0.1", 9876


def send_command(cmd_type, params=None, timeout=30):
    payload = {"type": cmd_type, "params": params or {}}
    with socket.create_connection((HOST, PORT), timeout=timeout) as s:
        s.sendall(json.dumps(payload).encode("utf-8"))
        buf = b""
        while True:
            data = s.recv(65536)
            if not data:
                break
            buf += data
            try:
                return json.loads(buf.decode("utf-8"))
            except json.JSONDecodeError:
                continue
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command")
    ap.add_argument("-p", "--params", help="params as JSON string")
    ap.add_argument("-f", "--codefile", help="python file, sent as execute_code")
    args = ap.parse_args()

    params = json.loads(args.params) if args.params else {}
    if args.codefile:
        with open(args.codefile, encoding="utf-8") as f:
            params = {"code": f.read()}

    try:
        resp = send_command(args.command, params)
    except Exception as e:
        print(json.dumps({"status": "client_error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(resp, ensure_ascii=False, indent=2))
