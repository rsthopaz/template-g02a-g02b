from datetime import datetime

import cv2


def process_frame(frame):
    """Apply lightweight processing in HTTP server before distribution."""
    # TODO-A1: Resize frame to 640x360 so payload size stays predictable.
    # TODO-A2: Draw timestamp text on the processed frame.
    return frame


def compress_frame(frame, quality=45):
    """Encode processed frame to JPEG bytes with configurable quality."""
    # TODO-A3: Encode frame as JPEG with cv2.imencode using `quality`.
    # TODO-A4: Return encoded bytes, or None if encoding fails.
    return None