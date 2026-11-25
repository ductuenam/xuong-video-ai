"""Tách video (clip Muse hoặc thành phẩm) thành từng cảnh và làm tờ soi cho 3 agent soát.

Vì sao: video lookbook có cảnh cận mặt, cận quần áo, phụ kiện; phải có agent tự soi
"tuyệt đối không để lỗi như tay buông mà túi vẫn lơ lửng", da mặt phải thật. Mỗi agent cần đúng loại ảnh của mình.

Dùng: python tach_canh_soi.py video.mp4 thu_muc_ra [--fps 8]
Ra trong thu_muc_ra:
  canh.json                 : danh sách cảnh [{so, tu, den}] (dò cắt cảnh theo độ đổi hình)
  cNN-toan.jpg              : mỗi cảnh, đủ khung ở --fps (mặc định 8/giây), có ghi giây
  cNN-mat.jpg               : vùng 45% trên khung, 4 khung/giây (agent soi da mặt)
  cNN-giua.jpg              : vùng giữa (vai tới đùi: tay, túi, khuy, thắt lưng) (agent soi phụ kiện)
  cNN-duoi.jpg              : vùng 40% dưới (chân, giày, tất, gấu váy)
  mat-lon/cNN-tTT.png       : khung gốc độ phân giải đầy đủ ở giữa mỗi cảnh (soi da kỹ)
"""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def doc(clip, fps, w):
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", clip], capture_output=True, text=True, timeout=60).stdout.strip().split(",")
    W, H = int(info[0]), int(info[1]); h = round(H * w / W)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=300).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3), W, H


def to_xem(khung, tu, fps, ra, cot=8):
    if not khung: return
    w, h = khung[0].size; hang = (len(khung) + cot - 1) // cot
    o = Image.new("RGB", (w * cot, h * hang), "black"); d = ImageDraw.Draw(o)
    for i, k in enumerate(khung):
        x, y = (i % cot) * w, (i // cot) * h; o.paste(k, (x, y))
        d.rectangle([x, y, x + 44, y + 13], fill="black"); d.text((x + 2, y + 1), f"{tu + i / fps:.2f}", fill="yellow")
    o.save(ra, quality=88)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("ra"); ap.add_argument("--fps", type=float, default=8)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    ra = Path(a.ra); ra.mkdir(parents=True, exist_ok=True); (ra / "mat-lon").mkdir(exist_ok=True)
    # dò cắt cảnh ở 24 khung/giây, ảnh nhỏ
    nho, W, H = doc(a.clip, 24, 90)
    g = nho.mean(axis=3)
    d = np.array([0] + [np.abs(g[i] - g[i - 1]).mean() for i in range(1, len(g))])
    nguong = max(4 * np.median(d[1:]), 12)
    cat = [0] + [i for i in range(1, len(d)) if d[i] > nguong and i - 0 > 6] + [len(g)]
    gon = [cat[0]]
    for c in cat[1:]:
        if c - gon[-1] >= 8: gon.append(c)
    gon[-1] = len(g)
    canh = [{"so": i + 1, "tu": round(gon[i] / 24, 3), "den": round(gon[i + 1] / 24, 3)} for i in range(len(gon) - 1)]
    (ra / "canh.json").write_text(json.dumps(canh, ensure_ascii=False, indent=1), encoding="utf-8")
    lon, _, _ = doc(a.clip, a.fps, 360)
    vung, _, _ = doc(a.clip, 4, 540)
    for c in canh:
        s = c["so"]
        i0, i1 = int(c["tu"] * a.fps), int(c["den"] * a.fps)
        to_xem([Image.fromarray(k).resize((180, round(180 * k.shape[0] / k.shape[1]))) for k in lon[i0:i1]], c["tu"], a.fps, ra / f"c{s:02d}-toan.jpg")
        j0, j1 = int(c["tu"] * 4), max(int(c["tu"] * 4) + 1, int(c["den"] * 4))
        for ten, (y0, y1) in {"mat": (0, .45), "giua": (.3, .75), "duoi": (.6, 1)}.items():
            ks = []
            for k in vung[j0:j1]:
                hh = k.shape[0]; im = Image.fromarray(k[int(y0 * hh):int(y1 * hh)])
                ks.append(im.resize((im.width // 1, im.height // 1)))
            to_xem(ks, c["tu"], 4, ra / f"c{s:02d}-{ten}.jpg", cot=4)
        t = (c["tu"] + c["den"]) / 2
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", a.clip, "-frames:v", "1",
                        str(ra / "mat-lon" / f"c{s:02d}-t{t:.1f}.png")], timeout=60)
    print(f"{len(canh)} cảnh → {ra}")
    for c in canh: print(f"  cảnh {c['so']}: {c['tu']:.2f}–{c['den']:.2f}")


if __name__ == "__main__":
    main()
