import socket
import struct
import time
import urllib.request

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

HTTP_FRAME_URL = "http://127.0.0.1:8000/frame"

# Simple packet format: frame_id (I), chunk_id (H), total_chunks (H), payload_len (H)
HEADER_FORMAT = "!IHHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# UDP constraints
MAX_PACKET_SIZE = 1200
MAX_PAYLOAD_SIZE = MAX_PACKET_SIZE - HEADER_SIZE  # Simple payload

TARGET_FPS = 8
MAX_FRAME_BYTES = 100_000


def fetch_frame():
    """Fetch frame as JPEG bytes from HTTP server."""
    # TODO-A11: Request HTTP_FRAME_URL and read JPEG bytes from response.
    # TODO-A12: Reject non-200 response, empty body, or frame > MAX_FRAME_BYTES.
    return None


def chunk_data(data, chunk_size):
    """Split bytes into equal chunks."""
    # TODO-A13: Split `data` into list of chunks with max size `chunk_size`.
    return []


def send_frame(sock, frame_id, frame_bytes):
    """Send frame split into chunks via UDP."""
    chunks = chunk_data(frame_bytes, MAX_PAYLOAD_SIZE)
    total_chunks = len(chunks)

    # TODO-A14: For each chunk, pack UDP header with struct.pack and append payload.
    # TODO-A15: Send packet with `sock.sendto(...)` to (UDP_IP, UDP_PORT).
    # TODO-A16: Add short pacing delay (for example 1ms) to reduce burst loss.
    _ = (frame_id, total_chunks)
    return 0


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    frame_id = 0
    sent_frames = 0
    sent_bytes = 0
    stat_start = time.time()
    frame_time = 1.0 / TARGET_FPS

    print(f"[UDP-SENDER] Sending to {UDP_IP}:{UDP_PORT}")
    print(f"[UDP-SENDER] Source: {HTTP_FRAME_URL}")
    print(f"[UDP-SENDER] Target FPS: {TARGET_FPS}")
    print(f"[UDP-SENDER] Max packet size: {MAX_PACKET_SIZE} bytes")
    print(f"[UDP-SENDER] Max payload per packet: {MAX_PAYLOAD_SIZE} bytes")

    next_frame_time = time.time()

    while True:
        now = time.time()
        
        # Respect frame rate
        if now < next_frame_time:
            time.sleep(next_frame_time - now)
            now = time.time()
        
        # Fetch frame from HTTP server
        frame_bytes = fetch_frame()
        if frame_bytes is None:
            time.sleep(0.05)
            continue

        # TODO-A17: Send frame chunks, update sent counters, and increment frame_id.
        # Placeholder keeps loop timing and stats output active.
        time.sleep(0.05)

        # Statistics
        now = time.time()
        if now - stat_start >= 1.0:
            elapsed = now - stat_start
            fps = sent_frames / elapsed
            throughput_kbps = (sent_bytes * 8) / (elapsed * 1000)
            print(f"[UDP-SENDER] FPS: {fps:.1f}, Bytes/s: {sent_bytes/elapsed:.0f}, Throughput: {throughput_kbps:.1f} kbps")
            
            sent_frames = 0
            sent_bytes = 0
            stat_start = now

        next_frame_time = now + frame_time


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[UDP-SENDER] Shutting down...")