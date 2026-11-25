"""Tach khung day cho vong soat do that.

Dung: python tach_khung_soat.py canh.mp4 [canh2.mp4 ...] --out-dir soat --fps 4
Moi trang gom 3 giay (12 khung o 4 khung/giay), co ghi giay tren tung khung,
de nguoi soat thay ro tay, vai, chi tiet nho ma bang 1 khung/giay bo sot.
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def dai_video(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip", nargs="+")
    ap.add_argument("--out-dir", default="soat")
    ap.add_argument("--fps", type=float, default=4)
    ap.add_argument("--giay-moi-trang", type=float, default=3)
    ap.add_argument("--rong", type=int, default=300)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in args.clip:
        ten = Path(p).stem
        tam = out_dir / f"_{ten}"
        tam.mkdir(exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", p, "-vf", f"fps={args.fps},scale={args.rong}:-2",
             str(tam / "k_%04d.jpg")],
            check=True,
        )
        khung = sorted(tam.glob("k_*.jpg"))
        moi_trang = int(args.fps * args.giay_moi_trang)
        trang = []
        for so, dau in enumerate(range(0, len(khung), moi_trang), start=1):
            nhom = khung[dau:dau + moi_trang]
            anh = [Image.open(k).convert("RGB") for k in nhom]
            w, h = anh[0].size
            cot = 6
            bang = Image.new("RGB", (w * cot, h * ((len(anh) + cot - 1) // cot)), "black")
            for i, im in enumerate(anh):
                giay = (dau + i) / args.fps
                ImageDraw.Draw(im).text((4, 4), f"{giay:.2f}s", fill="yellow", stroke_width=2,
                                        stroke_fill="black", font_size=20)
                bang.paste(im, ((i % cot) * w, (i // cot) * h))
            ra = out_dir / f"{ten}_trang{so:02d}.jpg"
            bang.save(ra, quality=88)
            trang.append(str(ra))
        for k in khung:
            k.unlink()
        tam.rmdir()
        print(f"{p}: {dai_video(p):.1f}s, {len(khung)} khung, {len(trang)} trang")
        for t in trang:
            print("  ", t)


if __name__ == "__main__":
    main()
