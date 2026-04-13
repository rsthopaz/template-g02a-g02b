import json
import socket
import struct
import threading
import time
from pathlib import Path

import cv2

from utils import compress_frame, process_frame

HOST = "0.0.0.0"
PORT = 8000
CAMERA_INDEX = 0
JPEG_QUALITY = 45

ROOT_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = ROOT_DIR / "client"


class SimpleFrameServer:
    """Simple HTTP server using raw sockets to serve processed frames."""

    def __init__(self, host=HOST, port=PORT, camera_index=CAMERA_INDEX, quality=JPEG_QUALITY):
        self.host = host
        self.port = port
        self.camera_index = camera_index
        self.quality = quality
        self.running = False
        self.sock = None
        self.cap = None
        self.lock = threading.Lock()

        # Stats
        self.frame_count = 0
        self.last_frame_size = 0
        self.start_time = time.time()

    def _open_camera(self, camera_index):
        """Open camera with backend fallbacks for better Windows compatibility."""
        backends = [getattr(cv2, "CAP_DSHOW", None), getattr(cv2, "CAP_MSMF", None), None]
        for backend in backends:
            if backend is None:
                cap = cv2.VideoCapture(camera_index)
            else:
                cap = cv2.VideoCapture(camera_index, backend)

            if cap is not None and cap.isOpened():
                return cap
            if cap is not None:
                cap.release()
        return None

    def _camera_ready(self, cap, retries=15, wait_sec=0.03):
        """Check whether an opened camera can produce at least one valid frame."""
        for _ in range(retries):
            ok, frame = cap.read()
            if ok and frame is not None and getattr(frame, "size", 0) > 0:
                return True
            time.sleep(wait_sec)
        return False

    def start_camera(self):
        """Initialize camera capture."""
        self.cap = self._open_camera(self.camera_index)
        if not self.cap or not self._camera_ready(self.cap):
            if self.cap:
                self.cap.release()
                self.cap = None
            raise RuntimeError(f"Failed to open camera {self.camera_index}")

    def switch_camera(self, camera_index):
        """Switch active camera source."""
        with self.lock:
            new_cap = self._open_camera(camera_index)
            if not new_cap:
                return False
            if not self._camera_ready(new_cap):
                new_cap.release()
                return False

            old_cap = self.cap
            self.cap = new_cap
            self.camera_index = camera_index
            if old_cap:
                old_cap.release()
            return True

    def get_frame(self):
        """Capture, process, and compress frame."""
        with self.lock:
            # TODO-A5: Read one frame from camera (`self.cap.read()`).
            # TODO-A6: Process frame with `process_frame` and compress with `compress_frame`.
            # TODO-A7: Update `frame_count` and `last_frame_size` before returning bytes.
            return None

    def _send_response(self, client_sock, status, reason, body=b"", content_type=None):
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

        response = ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8") + body
        client_sock.sendall(response)

    def _send_json(self, client_sock, status, payload):
        reason = "OK" if status < 400 else "Error"
        body = json.dumps(payload)
        self._send_response(client_sock, status, reason, body, content_type="application/json")

    def _serve_static(self, client_sock, filename, content_type):
        path = (CLIENT_DIR / filename).resolve()
        if not str(path).startswith(str(CLIENT_DIR.resolve())) or not path.exists():
            self._send_response(client_sock, 404, "Not Found")
            return

        body = path.read_bytes()
        self._send_response(client_sock, 200, "OK", body, content_type=content_type)

    def handle_client(self, client_sock, addr):
        """Handle HTTP request from client."""
        try:
            request = client_sock.recv(4096).decode('utf-8', errors='ignore')
            if not request:
                return

            header_block, _, body = request.partition('\r\n\r\n')
            lines = header_block.split('\r\n')
            if not lines:
                self._send_response(client_sock, 400, "Bad Request")
                return

            first_line_parts = lines[0].split()
            if len(first_line_parts) < 2:
                self._send_response(client_sock, 400, "Bad Request")
                return

            method = first_line_parts[0].upper()
            path = first_line_parts[1].split('?', 1)[0]

            if method == 'GET':
                if path in ('/', '/index.html'):
                    self._serve_static(client_sock, "index.html", "text/html; charset=utf-8")
                elif path == '/app.js':
                    self._serve_static(client_sock, "app.js", "application/javascript; charset=utf-8")
                elif path == '/frame':
                    # TODO-A8: Call `get_frame()` and decide between 200 OK or 500 error.
                    # TODO-A9: Build HTTP response headers for JPEG (`Content-Type`, `Content-Length`).
                    response = b"HTTP/1.1 501 Not Implemented\r\nContent-Length: 0\r\n\r\n"
                    client_sock.sendall(response)
                elif path == '/stats':
                    # TODO-A10: Return JSON stats from `self.stats()` with Content-Type application/json.
                    response = b"HTTP/1.1 501 Not Implemented\r\nContent-Length: 0\r\n\r\n"
                    client_sock.sendall(response)
                else:
                    self._send_response(client_sock, 404, "Not Found")
            elif method == 'POST' and path == '/camera':
                try:
                    payload = json.loads(body or "{}")
                    camera_index = int(payload["camera_index"])
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    self._send_json(client_sock, 400, {"ok": False, "error": "invalid camera_index"})
                    return

                if self.switch_camera(camera_index):
                    self._send_json(client_sock, 200, {"ok": True, "camera_index": self.camera_index})
                else:
                    self._send_json(client_sock, 400, {"ok": False, "error": f"cannot open camera {camera_index}"})
            else:
                self._send_response(client_sock, 405, "Method Not Allowed")

        except Exception as e:
            print(f"[HTTP-SERVER] Client handler error: {e}")
        finally:
            client_sock.close()

    def run(self):
        """Start the HTTP server and listen for connections."""
        self.start_camera()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.running = True

        print(f"[HTTP-SERVER] Simple HTTP server listening on {self.host}:{self.port}")
        print(f"[HTTP-SERVER] Camera index: {self.camera_index}")
        print(f"[HTTP-SERVER] JPEG quality: {self.quality}")
        print(f"[HTTP-SERVER] Access frames at: http://localhost:{self.port}/frame")

        try:
            while self.running:
                try:
                    client_sock, addr = self.sock.accept()
                    # Handle client in thread
                    thread = threading.Thread(target=self.handle_client, args=(client_sock, addr))
                    thread.daemon = True
                    thread.start()
                except KeyboardInterrupt:
                    break
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.sock:
            self.sock.close()
        if self.cap:
            with self.lock:
                self.cap.release()
        self.running = False

    def stats(self):
        """Get server statistics."""
        uptime = max(time.time() - self.start_time, 0.001)
        return {
            "uptime_sec": round(uptime, 2),
            "frames_served": self.frame_count,
            "avg_fps": round(self.frame_count / uptime, 2),
            "last_frame_size": self.last_frame_size,
            "camera_index": self.camera_index,
        }


if __name__ == "__main__":
    server = SimpleFrameServer()
    server.run()