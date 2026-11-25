"""Dung video co chen canh can: hinh va tieng di theo hai danh sach doan rieng.

Tieng lay lien tu cac canh noi (co the cat bo khoang im). Hinh cat sang canh can
1,5-2,5 giay trong luc tieng van chay, dat de len cho noi giua hai canh noi hoac len
cho vua cat bo khoang im, nen nguoi xem khong thay mat doi hay hinh nhay.

Dung: python dung_chen_can.py ke-hoach.json ra.mp4 [--nen-phong -36] [--fps 24]

ke-hoach.json:
{
  "tieng": [["s1.mp4", 0, 9.6], ["s2.mp4", 0, 9.85], ["s3.mp4", 0, 1.25], ["s3.mp4", 2.3, 9.99]],
  "hinh":  [["s1.mp4", 0, 9.2], ["can1.mp4", 0.2, 2.6], ["s2.mp4", 2.0, 9.85], ...]
}
Doan hinh co the them phan tu thu 4 la muc phong, vd ["s2.mp4", 20.76, 24.9, 1.12]:
dung cho doan sau cu cat bo cum noi lap (cat nhay nhu nguoi ban hang that).
Tong do dai hai danh sach phai bang nhau (lech toi da 0,05 giay). Script in ra moc
thoi gian tung doan hinh tren thanh pham de soat.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from khoa_mat import cong, cong_ke_hoach  # noqa: E402

HIEU_CHINH = -15.6  # muc dB cua on nau sau loc, giong dung_video.py


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ke_hoach")
    ap.add_argument("ra")
    ap.add_argument("--nen-phong", type=float, default=-36.0)
    ap.add_argument("--fps", default="24")
    args = ap.parse_args()
    cong(Path(args.ke_hoach).resolve().parent, "clip")  # mặt, chân từng cảnh phải qua cổng trước khi dựng
    kh = json.load(open(args.ke_hoach, encoding="utf-8"))
    tieng, hinh = kh["tieng"], kh["hinh"]
    cong_ke_hoach(Path(args.ke_hoach).resolve().parent, [d[0] for d in hinh])
    dt = sum(b - a for _, a, b in tieng)
    dh = sum(d[2] - d[1] for d in hinh)
    if abs(dt - dh) > 0.05:
        raise SystemExit(f"Tiếng dài {dt:.3f}s, hình dài {dh:.3f}s: phải bằng nhau")

    files = []
    for f in [d[0] for d in tieng + hinh]:
        if f not in files:
            files.append(f)
    idx = {f: i for i, f in enumerate(files)}
    lenh = ["ffmpeg", "-hide_banner", "-v", "error", "-y"]
    for f in files:
        lenh += ["-i", f]
    loc = []
    t = 0.0
    print("Mốc hình trên thành phẩm:")
    for k, d in enumerate(hinh):
        f, a, b = d[:3]
        z = float(d[3]) if len(d) > 3 else 1.0
        phong = (f"crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.29," if z > 1 else "")
        loc.append(
            f"[{idx[f]}:v]trim={a}:{b},setpts=PTS-STARTPTS,{phong}"
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,"
            f"fps={args.fps}[v{k}]"
        )
        print(f"  {t:6.2f}-{t + b - a:6.2f}  {f} [{a}-{b}]" + (f" phong {z}" if z > 1 else ""))
        t += b - a
    for k, (f, a, b) in enumerate(tieng):
        d = b - a
        loc.append(
            f"[{idx[f]}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,"
            f"afade=t=in:st=0:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{k}]"
        )
    loc.append("".join(f"[v{k}]" for k in range(len(hinh))) + f"concat=n={len(hinh)}:v=1:a=0[v]")
    loc.append("".join(f"[a{k}]" for k in range(len(tieng))) + f"concat=n={len(tieng)}:v=0:a=1[g]")
    loc.append("[g]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[an]")
    if args.nen_phong < 0:
        he_so = 10 ** ((args.nen_phong - HIEU_CHINH) / 20)
        loc.append(
            f"anoisesrc=color=brown:amplitude=1:sample_rate=44100:duration={dt + 0.5:.2f},"
            f"highpass=f=60,lowpass=f=2500,volume={he_so:.6f},aformat=channel_layouts=stereo[nen]"
        )
        loc.append("[an][nen]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        loc.append("[an]anull[a]")
    lenh += [
        "-filter_complex", ";".join(loc), "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", args.ra,
    ]
    subprocess.run(lenh, check=True)
    print(f"Xong {args.ra} ({dt:.2f} giây)")


if __name__ == "__main__":
    main()
