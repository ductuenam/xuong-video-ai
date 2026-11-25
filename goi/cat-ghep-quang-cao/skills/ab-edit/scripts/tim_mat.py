"""Đo vị trí mặt người nói trong video (MediaPipe) — thay face-match.swift của bản Mac.
  python tim_mat.py <video> [--so-khung 12] [--tu 5 --den 60]
In: cx cy (tâm mặt, tỉ lệ 0..1 của khung đã xoay đúng chiều), w h (cỡ mặt), dùng cho master_nguoi_noi.py và bố cục khung trung/cận.
"""
import argparse
import json
import statistics
import subprocess

import numpy as np

from chung import SKILL, thoi_luong, tim_ffmpeg

MODEL = SKILL / "models" / "blaze_face_short_range.tflite"  # storage.googleapis.com/mediapipe-models (chính thức)


def khung(video, t, w=540):
    """Lấy 1 khung (FFmpeg tự xoay theo cờ) → mảng RGB rộng w."""
    p = subprocess.run([tim_ffmpeg("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                        "-of", "json", str(video)], capture_output=True, text=True).stdout
    st = json.loads(p)["streams"][0]
    rot = abs(int(next((d.get("rotation", 0) for d in st.get("side_data_list", [])), 0)))
    W, H = (st["height"], st["width"]) if rot in (90, 270) else (st["width"], st["height"])
    h = round(w * H / W / 2) * 2
    raw = subprocess.run([tim_ffmpeg(), "-v", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1", "-vf", f"scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--so-khung", type=int, default=12)
    ap.add_argument("--tu", type=float, default=None)
    ap.add_argument("--den", type=float, default=None)
    a = ap.parse_args()
    import mediapipe as mp

    dur = thoi_luong(a.video)
    t0, t1 = a.tu if a.tu is not None else dur * 0.05, a.den if a.den is not None else dur * 0.95
    # MediaPipe Tasks (bản ≥ 0.10 bỏ mp.solutions); model chính thức đi kèm skill trong models/
    opt = mp.tasks.vision.FaceDetectorOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL)), min_detection_confidence=0.5)
    det = mp.tasks.vision.FaceDetector.create_from_options(opt)
    kq = []
    for i in range(a.so_khung):
        t = t0 + (t1 - t0) * i / max(1, a.so_khung - 1)
        img = khung(a.video, t)
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(img)))
        if r.detections:
            b = max(r.detections, key=lambda d: d.bounding_box.width).bounding_box
            H, W = img.shape[:2]
            kq.append(((b.origin_x + b.width / 2) / W, (b.origin_y + b.height / 2) / H, b.width / W, b.height / H))
    if not kq:
        raise SystemExit("Không thấy mặt trong các khung đã lấy.")
    cx, cy, w, h = (round(statistics.median(x[k] for x in kq), 3) for k in range(4))
    print(json.dumps({"cx": cx, "cy": cy, "w": w, "h": h, "so_khung_thay_mat": len(kq)}))


if __name__ == "__main__":
    main()
