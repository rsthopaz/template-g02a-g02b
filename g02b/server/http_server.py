import json
import socket
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

HOST = "0.0.0.0"
PORT = 8000
MAX_REQUEST_BYTES = 64 * 1024
MAX_FRAME_BYTES = 100_000

ROOT_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = ROOT_DIR / "client"


class SimpleFrameServer:
    """Raw-socket HTTP server that stores latest JPEG uploaded by browser screen share."""

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.lock = threading.Lock()

        self.latest_frame = None
        self.latest_frame_time = None

        self.start_time = time.time()
        self.frames_uploaded = 0
        self.frames_served = 0
        self.last_frame_size = 0

    def _read_request(self, client_sock):
        data = b""
        while b"\r\n\r\n" not in data and len(data) < MAX_REQUEST_BYTES:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            data += chunk

        if b"\r\n\r\n" not in data:
            return None, None, None, b""

        raw_head, body = data.split(b"\r\n\r\n", 1)
        lines = raw_head.decode("iso-8859-1", errors="ignore").split("\r\n")
        if not lines:
            return None, None, None, b""

        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            return None, None, None, b""

        method = parts[0].upper()
        target = parts[1]
        headers = {}

        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

        return method, target, headers, body

    def _send_response(self, client_sock, status, reason, body=b"", content_type=None, extra_headers=None):
        if body is None:
            body = b""
        if isinstance(body, str):
            body = body.encode("utf-8")

        headers = [
            f"HTTP/1.1 {status} {reason}",
            f"Content-Length: {len(body)}",
            "Connection: close",
        ]
        if content_type:
            headers.append(f"Content-Type: {content_type}")
        if extra_headers:
            headers.extend(extra_headers)

        response = ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8") + body
        client_sock.sendall(response)

    def _send_json(self, client_sock, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self._send_response(
            client_sock,
            status,
            "OK" if status < 400 else "Error",
            body,
            content_type="application/json",
            extra_headers=["Cache-Control: no-store"],
        )

    def _serve_static(self, client_sock, filename, content_type):
        path = (CLIENT_DIR / filename).resolve()
        if not str(path).startswith(str(CLIENT_DIR.resolve())) or not path.exists():
            self._send_response(client_sock, 404, "Not Found")
            return

        body = path.read_bytes()
        self._send_response(client_sock, 200, "OK", body, content_type=content_type)

    def _handle_get_frame(self, client_sock):
        with self.lock:
            frame = self.latest_frame
            if frame is not None:
                self.frames_served += 1

        # TODO-B1: Return 404 JSON when there is no uploaded frame yet.
        # TODO-B2: Return 200 image/jpeg with Cache-Control no-store when frame exists.
        _ = frame
        self._send_json(client_sock, 501, {"error": "TODO-B1/TODO-B2"})

    def _handle_upload_frame(self, client_sock, headers, initial_body):
        # TODO-B3: Parse and validate Content-Length (1..MAX_FRAME_BYTES).
        # TODO-B4: Read request body until full JPEG payload is received.
        # TODO-B5: Save latest frame bytes and update upload statistics.
        _ = (headers, initial_body)
        self._send_json(client_sock, 501, {"error": "TODO-B3/TODO-B5"})

    def stats(self):
        uptime = max(time.time() - self.start_time, 0.001)
        with self.lock:
            last_upload_age_ms = None
            if self.latest_frame_time is not None:
                last_upload_age_ms = int(max((time.time() - self.latest_frame_time) * 1000, 0))

            return {
                "uptime_sec": round(uptime, 2),
                "frames_uploaded": self.frames_uploaded,
                "frames_served": self.frames_served,
                "upload_fps": round(self.frames_uploaded / uptime, 2),
                "last_frame_size": self.last_frame_size,
                "last_upload_age_ms": last_upload_age_ms,
            }

    def handle_client(self, client_sock, addr):
        try:
            method, target, headers, body = self._read_request(client_sock)
            if method is None:
                self._send_response(client_sock, 400, "Bad Request")
                return

            path = urlsplit(target).path

            if method == "GET":
                # TODO-B6: Route GET endpoints: /, /index.html, /app.js, /frame, and /stats.
                _ = path
                self._send_response(client_sock, 501, "Not Implemented")
            elif method == "POST":
                # TODO-B7: Route POST /upload-frame and reject unsupported POST paths.
                _ = (path, headers, body)
                self._send_response(client_sock, 501, "Not Implemented")
            else:
                self._send_response(client_sock, 405, "Method Not Allowed")

        except Exception as exc:
            print(f"[HTTP-SERVER] Client handler error from {addr}: {exc}")
            try:
                self._send_response(client_sock, 500, "Internal Server Error")
            except Exception:
                pass
        finally:
            client_sock.close()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(16)
        self.running = True

        print(f"[HTTP-SERVER] Listening on http://127.0.0.1:{self.port}")
        print("[HTTP-SERVER] Open the page and click 'Start Sharing Window'.")
        print("[HTTP-SERVER] Browser uploads JPEG frames to POST /upload-frame")
        print("[HTTP-SERVER] UDP sender reads latest frame from GET /frame")

        try:
            while self.running:
                client_sock, addr = self.sock.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        if self.sock:
            self.sock.close()
        self.running = False


if __name__ == "__main__":
    server = SimpleFrameServer()
    server.run()