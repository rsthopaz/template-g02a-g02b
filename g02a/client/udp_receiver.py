import socket
import struct
import time
import cv2
import numpy as np

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Simple packet header format: frame_id (I), chunk_id (H), total_chunks (H), payload_len (H)
HEADER_FORMAT = "!IHHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

FRAME_TIMEOUT = 2.0
MAX_ACTIVE_FRAMES = 20


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(FRAME_TIMEOUT)

    frames = {}
    display_window = "UDP Frame Receiver"
    cv2.namedWindow(display_window, cv2.WINDOW_AUTOSIZE)

    received_packets = 0
    received_frames = 0
    stat_start = time.time()

    print(f"[UDP-RECEIVER] Listening on {UDP_IP}:{UDP_PORT}")
    print(f"[UDP-RECEIVER] Display: {display_window}")
    print("[UDP-RECEIVER] Simple UDP streaming (no HMAC, no CRC32)")

    try:
        while True:
            try:
                packet, addr = sock.recvfrom(1200)
                received_packets += 1

                # TODO-A19: Validate header size, then unpack frame/chunk metadata.
                # TODO-A20: Buffer each chunk by frame_id and evict old incomplete frames.
                # TODO-A21: Reassemble full frame in order, decode JPEG, and display via OpenCV.
                # Placeholder mode: receiver currently counts packet rate only.
                _ = (packet, addr, frames)

            except socket.timeout:
                pass

            # Statistics
            now = time.time()
            if now - stat_start >= 1.0:
                elapsed = now - stat_start
                pps = received_packets / elapsed
                fps = received_frames / elapsed
                print(f"[UDP-RECEIVER] Packets/s: {pps:.0f}, Frames/s: {fps:.1f}, Active frames: {len(frames)}")
                
                received_packets = 0
                received_frames = 0
                stat_start = now

    except KeyboardInterrupt:
        print("\n[UDP-RECEIVER] Shutting down...")
    finally:
        sock.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()