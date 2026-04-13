const startButton = document.getElementById("start-share");
const stopButton = document.getElementById("stop-share");
const localPreview = document.getElementById("local-preview");
const mirroredFrame = document.getElementById("mirrored-frame");
const statusText = document.getElementById("status");
const statsText = document.getElementById("stats");

const CAPTURE_FPS = 8;
const JPEG_QUALITY = 0.6;
const MAX_DIMENSION = 1280;
const FRAME_REFRESH_MS = 150;
const STATS_REFRESH_MS = 1000;

let displayStream = null;
let uploadTimer = null;
let mirrorTimer = null;
let isUploading = false;
let localUploadedFrames = 0;
let localStartTimeMs = Date.now();

const uploadCanvas = document.createElement("canvas");
const uploadCtx = uploadCanvas.getContext("2d", { alpha: false });

function setStatus(text) {
    statusText.textContent = text;
}

function refreshMirroredFrame() {
    mirroredFrame.src = `/frame?t=${Date.now()}`;
}

function scaleToMax(width, height, maxDimension) {
    const maxSide = Math.max(width, height);
    if (maxSide <= maxDimension) {
        return [width, height];
    }
    const ratio = maxDimension / maxSide;
    return [Math.round(width * ratio), Math.round(height * ratio)];
}

async function refreshStats() {
    try {
        const response = await fetch("/stats", { cache: "no-store" });
        if (!response.ok) {
            setStatus("HTTP server active, stats unavailable");
            return;
        }

        const data = await response.json();
        const age = data.last_upload_age_ms == null ? "-" : `${data.last_upload_age_ms}ms`;
        statsText.textContent =
            `uploaded=${data.frames_uploaded} | served=${data.frames_served} | ` +
            `upload_fps=${data.upload_fps} | last_size=${data.last_frame_size}B | age=${age}`;
    } catch {
        setStatus("Cannot reach HTTP server");
    }
}

function stopSharing() {
    if (uploadTimer) {
        clearInterval(uploadTimer);
        uploadTimer = null;
    }
    if (mirrorTimer) {
        clearInterval(mirrorTimer);
        mirrorTimer = null;
    }

    if (displayStream) {
        for (const track of displayStream.getTracks()) {
            track.stop();
        }
        displayStream = null;
    }

    localPreview.srcObject = null;
    startButton.disabled = false;
    stopButton.disabled = true;
    setStatus("Sharing stopped. Click 'Start Sharing Window' to continue.");
}

function uploadCurrentFrame() {
    if (!displayStream || isUploading) {
        return;
    }
    if (!localPreview.videoWidth || !localPreview.videoHeight) {
        return;
    }

    // TODO-B18: Scale source frame with `scaleToMax` and draw it to uploadCanvas.
    // TODO-B19: Convert canvas to JPEG blob using `toBlob` and JPEG_QUALITY.
    // TODO-B20: POST blob to `/upload-frame` and update status message on success/failure.
    // TODO-B21: Update localUploadedFrames and local FPS indicator.
}

async function startSharing() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        setStatus("Your browser does not support getDisplayMedia");
        return;
    }

    try {
        // TODO-B22: Request display stream with `getDisplayMedia` at CAPTURE_FPS.
        // TODO-B23: Attach stream to localPreview and start playback.
        // TODO-B24: Enable/disable buttons and reset local upload counters.
        // TODO-B25: Start periodic upload and mirrored-frame refresh timers.
        // TODO-B26: Stop sharing automatically when browser capture track ends.
        setStatus("TODO-B22..B26: implement screen capture + upload pipeline.");
    } catch {
        setStatus("Screen share canceled or permission denied");
    }
}

startButton.addEventListener("click", startSharing);
stopButton.addEventListener("click", stopSharing);

mirroredFrame.addEventListener("error", () => {
    if (!displayStream) {
        setStatus("Waiting for first uploaded frame...");
    }
});

refreshStats();
setInterval(refreshStats, STATS_REFRESH_MS);