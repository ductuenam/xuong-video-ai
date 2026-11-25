"""Tờ so sánh cạnh nhau: video thử của lô với video mẫu đã đạt, cho người chấm (agent sku-cc-cham-so-mau).

Dùng: python to_so_sanh.py <du_an> [--mau <thư mục video mẫu>]
  Video thử: <du_an>/thanh-pham/*.mp4 có nhạc (bỏ bản -khong-nhac).
  Video mẫu: mặc định thư mục video-mau/ trong skill (cài từ gói), hoặc --mau.
Ra <du_an>/so-sanh/:
  to-so-sanh.jpg   mỗi hàng một video, 6 khung cách đều; các hàng MẪU ở trên, THỬ ở dưới
  so-lieu.txt      độ dài, độ sáng nhạc, nhịp gõ, độ nét, độ rực màu, độ lệch khung đầu-cuối (máy đi bao xa)
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import GOC_SKILL, can, chay, doc_du_an, in_utf8, thoi_luong  # noqa: E402
from dung import do_nhac, nhac_dat  # noqa: E402

W, H = 180, 320


def khung(f, n=6):
    d = thoi_luong(f)
    ra = []
    for k in range(n):
        t = 0.6 + (d - 1.2) * k / (n - 1)  # né 0,4 giây mờ vào ở đầu và khung cuối
        raw = chay([can("ffmpeg"), "-v", "error", "-ss", f"{max(0, t):.2f}", "-i", str(f), "-frames:v", "1",
                    "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        ra.append(np.frombuffer(raw, np.uint8).reshape(H, W, 3) if len(raw) == W * H * 3 else np.zeros((H, W, 3), np.uint8))
    return ra


def so_lieu(fr):
    a = np.stack(fr).astype(np.float32)
    xam = a.mean(3)
    net = float(np.abs(np.diff(xam, axis=2)).mean())
    mx, mn = a.max(3), a.min(3)
    ruc = float(((mx - mn) / (mx + 1e-6)).mean() * 100)
    lech = float(np.abs(xam[0] - xam[-1]).mean())
    return net, ruc, lech


def main():
    in_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("--mau", default=str(GOC_SKILL / "video-mau"))
    a = ap.parse_args()
    d, _ = doc_du_an(a.du_an)
    mau = sorted(p for p in Path(a.mau).glob("*.mp4"))[:3]
    thu = sorted(p for p in (d / "thanh-pham").glob("*.mp4") if "khong-nhac" not in p.name)
    if not mau or not thu:
        sys.exit(f"✘ Cần ít nhất 1 video mẫu ({a.mau}) và 1 thành phẩm có nhạc ({d / 'thanh-pham'}).")
    ra = d / "so-sanh"
    ra.mkdir(exist_ok=True)
    hang, dong = [], ["loại | tên | dài (giây) | nhạc sáng (Hz) | nhịp gõ/giây | cổng nhạc | độ nét | độ rực màu % | máy đi (lệch khung đầu-cuối)"]
    for loai, ds in (("MẪU", mau), ("THỬ", thu)):
        for f in ds:
            fr = khung(f)
            vien = np.full((H, 8, 3), 255 if loai == "MẪU" else 60, np.uint8)
            hang.append(np.concatenate([vien] + [np.concatenate([x, np.zeros((H, 4, 3), np.uint8)], 1) for x in fr], 1))
            s, g = do_nhac(f)
            net, ruc, lech = so_lieu(fr)
            dong.append(f"{loai} | {f.stem} | {thoi_luong(f):.2f} | {s or 0:.0f} | {g or 0:.2f} | "
                        f"{'qua' if nhac_dat(s, g) else 'TRƯỢT'} | {net:.1f} | {ruc:.0f} | {lech:.0f}")
    anh = np.concatenate([np.concatenate([h, np.zeros((6, h.shape[1], 3), np.uint8)], 0) for h in hang], 0)
    p = ra / "to-so-sanh.jpg"
    tam = ra / "_tam.rgb"
    tam.write_bytes(anh.tobytes())
    chay([can("ffmpeg"), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{anh.shape[1]}x{anh.shape[0]}",
          "-i", str(tam), "-frames:v", "1", "-q:v", "3", str(p)], check=True)
    tam.unlink()
    (ra / "so-lieu.txt").write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong))
    print(f"\n✔ Tờ so sánh: {p}\n  (viền trắng bên trái = MẪU, viền tối = THỬ)")


if __name__ == "__main__":
    main()
