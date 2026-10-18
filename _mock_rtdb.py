"""Local stand-in for a Firebase Realtime Database, so the app's sync engine can be
tested end to end before a real project exists.

Speaks the same REST shape the app uses:  GET/PUT/OPTIONS  /trips/<code>.json
Run:  env -u PYTHONPATH python _mock_rtdb.py    (listens on 127.0.0.1:8811)
"""
import json
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STORE = pathlib.Path(__file__).with_name("_mock_rtdb.json")
PORT = 8811


def read_store():
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def write_store(data):
    STORE.write_text(json.dumps(data, indent=1), encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Max-Age", "600")

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        key = self.path.split("?")[0].lstrip("/")
        if not key.endswith(".json"):
            return self._json(400, {"error": "bad path"})
        node = read_store()
        for part in key[:-5].split("/"):
            node = node.get(part, {}) if isinstance(node, dict) else {}
        print(f"GET  {key} -> {'hit' if node else 'null'}", flush=True)
        self._json(200, node if node else None)

    def do_PUT(self):
        key = self.path.split("?")[0].lstrip("/")
        if not key.endswith(".json"):
            return self._json(400, {"error": "bad path"})
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"null"
        try:
            payload = json.loads(raw)
        except Exception:
            return self._json(400, {"error": "bad json"})
        data = read_store()
        parts = key[:-5].split("/")
        node = data
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = payload
        write_store(data)
        items = len(payload.get("items", {})) if isinstance(payload, dict) else 0
        print(f"PUT  {key} <- {items} items", flush=True)
        self._json(200, payload)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"mock RTDB on http://127.0.0.1:{PORT}/trips/<code>.json", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
