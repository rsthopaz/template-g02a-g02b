# [G02a] Webcam Web App

## Goal
Bangun web app yang menampilkan webcam dari HTTP server, lalu kirim frame tersebut via UDP secara real-time.

## Komponen Utama
1. **`server/http_server.py`**: HTTP server yang melayani frame (`GET /frame`) dari webcam dengan dukungan switching kamera
2. **`client/index.html` + `client/app.js`**: Web UI dengan dropdown pemilihan kamera dan tampilkan frame dari HTTP server
3. **`server/udp_sender.py`**: Fetch frame dari HTTP, chunk, dan kirim via UDP
4. **`client/udp_receiver.py`**: Terima UDP packets, reassemble, decode, dan display frame
5. **`server/utils.py`**: Helper functions untuk process & compress frame

## Packet Format
```
[frame_id:4] [chunk_id:2] [total_chunks:2] [payload_len:2] [payload:N]
Header: 10 bytes | Max packet: 1200 bytes | Max payload: 1190 bytes
```

## HTTP Endpoints (server/http_server.py)
- `GET /` atau `GET /index.html`: Halaman web dengan dropdown pemilihan kamera
- `GET /app.js`: JavaScript client untuk UI
- `GET /frame`: Ambil frame JPEG terbaru dari kamera yang dipilih
- `GET /stats`: Statistik server (frames served, FPS, active camera index)
- `POST /camera`: Switch kamera (JSON body: `{"camera_index": 0}` atau `1`)

## Konstrain Teknis
- UDP packet max: 1200 bytes
- Frame max: 100,000 bytes (compressed)
- Target FPS: 8
- Frame timeout: 2 detik
- UDP: fire-and-forget (tidak ada ACK/retry)

## Jalankan

**Terminal 1 (HTTP Server):**
```bash
py .\server\http_server.py
```

**Buka Browser (Camera Control + Preview):**
```
http://127.0.0.1:8000/
```
- Gunakan dropdown "Camera" untuk memilih kamera (0 atau 1)
- Kamera akan switched otomatis saat dropdown diubah
- Preview frame ditampilkan di halaman

**Terminal 2 (UDP Receiver - untuk student/display):**
```bash
py .\client\udp_receiver.py
```

**Terminal 3 (UDP Sender - broadcast ke receiver):**
```bash
py .\server\udp_sender.py
```

## Monitoring
Setiap component menampilkan metrik per detik:
- HTTP Server: frames served, avg FPS, active camera index
- UDP Sender: FPS, throughput (kbps)
- UDP Receiver: packets/s, frames/s reconstructed

## Troubleshooting
- **Camera tidak terbuka**: Dropdown akan show error. Coba ubah camera index di dropdown atau ubah `CAMERA_INDEX` di http_server.py
- **Frame tidak switch saat dropdown diubah**: Pastikan POST /camera endpoint berfungsi (check browser console)
- **UDP Receiver tidak dapat frame**: Pastikan HTTP server dan UDP sender sudah berjalan, dan frame berhasil dimuat di browser
- **Low throughput**: Turunkan JPEG quality atau check CPU usage
