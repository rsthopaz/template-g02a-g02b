const frameImage = document.getElementById("http-frame");
const statusText = document.getElementById("status");
const statsText = document.getElementById("stats");
const cameraSelect = document.getElementById("camera-select");

const FRAME_REFRESH_MS = 120;
const STATS_REFRESH_MS = 1000;

function refreshFrame() {
    frameImage.src = `/frame?t=${Date.now()}`;
}

async function applyCameraSelection() {
    const cameraIndex = Number(cameraSelect.value);
    try {
        const response = await fetch("/camera", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ camera_index: cameraIndex }),
        });

        if (!response.ok) {
            statusText.textContent = "Camera switch endpoint not available yet";
            return;
        }

        const data = await response.json();
        statusText.textContent = `HTTP source: camera ${data.camera_index}`;
        refreshFrame();
        await refreshStats();
    } catch {
        statusText.textContent = "Cannot change camera source";
    }
}

async function refreshStats() {
    try {
        const response = await fetch("/stats", { cache: "no-store" });
        if (!response.ok) {
            statusText.textContent = "HTTP server active, stats unavailable";
            return;
        }

        const data = await response.json();
        if (typeof data.camera_index === "number") {
            cameraSelect.value = String(data.camera_index);
            statusText.textContent = `HTTP source: camera ${data.camera_index} processed in server`;
        } else {
            statusText.textContent = "HTTP source: camera processed in server";
        }
        statsText.textContent = `frames=${data.frames_served} | avg_fps=${data.avg_fps} | last_size=${data.last_frame_size}B`;
    } catch {
        statusText.textContent = "Cannot reach HTTP server";
    }
}

frameImage.addEventListener("error", () => {
    statusText.textContent = "Waiting for /frame endpoint...";
});

refreshFrame();
refreshStats();

cameraSelect.addEventListener("change", () => {
    applyCameraSelection();
});

setInterval(refreshFrame, FRAME_REFRESH_MS);
setInterval(refreshStats, STATS_REFRESH_MS);