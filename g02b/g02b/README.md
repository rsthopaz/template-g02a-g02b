# [G02b] Browser Window _Mirror_

## Goal
Buat aplikasi mirroring sederhana seperti ClassPoint:
- Teacher share window/tab dari browser.
- Browser mengirim frame JPEG ke HTTP server.
- UDP sender mengambil frame dari HTTP server lalu broadcast ke student receiver.

## Komponen Utama
1. **`server/http_server.py`**
	- Raw socket HTTP server.
	- Endpoint wajib:
	  - `GET /` untuk halaman teacher.
	  - `POST /upload-frame` untuk upload JPEG dari browser.
	  - `GET /frame` untuk mengambil frame terbaru.
	  - `GET /stats` untuk monitoring.

2. **`client/index.html` + `client/app.js`**
	- Tombol Start/Stop sharing window.
	- Pakai `navigator.mediaDevices.getDisplayMedia()`.
	- Capture ke canvas, encode JPEG, upload ke `POST /upload-frame`.

3. **`server/udp_sender.py`**
	- Fetch frame dari `http://127.0.0.1:8000/frame`.
	- Chunk dan kirim via UDP.

4. **`client/udp_receiver.py`**
	- Terima UDP packet.
	- Reassemble frame, decode JPEG, tampilkan hasil mirroring.

## Format Packet UDP
```
[frame_id:4] [chunk_id:2] [total_chunks:2] [payload_len:2] [payload:N]
Header: 10 bytes
Max packet: 1200 bytes
```

## Constraint
- Max UDP packet: 1200 bytes
- Max frame upload: 100000 bytes
- Target stream: 8 FPS
- Frame timeout receiver: 2 detik
- UDP mode: fire-and-forget (tanpa ACK/retry)

## Cara Menjalankan
1. Terminal 1: `py .\server\http_server.py`
2. Buka browser: `http://127.0.0.1:8000/`
3. Klik **Start Sharing Window**, pilih window/tab presentasi.
4. Terminal 2: `py .\client\udp_receiver.py`
5. Terminal 3: `py .\server\udp_sender.py`

## Monitoring
- HTTP server: `frames_uploaded`, `frames_served`, `upload_fps`
- UDP sender: FPS dan throughput
- UDP receiver: packets/s dan reconstructed frames/s

## Catatan
- `getDisplayMedia` butuh browser modern dan context aman (`localhost` sudah aman).
- Jika belum ada upload dari browser, endpoint `/frame` akan kosong.
