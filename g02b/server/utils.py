from datetime import datetime

import cv2


def process_frame(frame):
    """Apply lightweight processing in HTTP server before distribution."""
    resized = cv2.resize(frame, (640, 360))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    label = datetime.now().strftime("%H:%M:%S")
    cv2.putText(
        processed,
        f"HTTP processed @ {label}",
        (12, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )
    return processed


def compress_frame(frame, quality=45):
    """Encode processed frame to JPEG bytes with configurable quality."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
    ok, encoded = cv2.imencode(".jpg", frame, encode_param)
    if not ok:
        return None
    return encoded.tobytes()