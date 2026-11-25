"""Thay một đoạn trong file giọng bằng đoạn mới, cắt ở giữa khe nghỉ.
  python thay_doan_giong.py <file gốc> <file đoạn mới> --tu "vài từ đầu đoạn cũ" --sau "vài từ đầu câu ngay sau đoạn cũ" --ra <file ra.wav>
Bỏ --sau nếu đoạn cũ kéo tới hết bài."""
import argparse
import re
import subprocess
import sys

import numpy as np

from whisper_vi import nghe

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("goc")
ap.add_argument("moi")
ap.add_argument("--tu", required=True)
ap.add_argument("--sau")
ap.add_argument("--ra", required=True)
ap.add_argument("--nghi", type=float, default=0.25, help="giây nghỉ thêm trước đoạn mới")
a = ap.parse_args()
chuan = lambda t: re.sub(r"[^\wÀ-ỹ]", "", t.lower())
W = [w for s in nghe(a.goc, goi_y=a.tu + ", " + (a.sau or "")) for w in s["words"]]
ch = [chuan(w["word"]) for w in W]


def tim(cum, bat_dau=0):
    can = [chuan(x) for x in cum.split()]
    for i in range(bat_dau, len(ch) - len(can) + 1):
        if ch[i:i + len(can)] == can:
            return i
    sys.exit(f"✘ Không thấy [{cum}] trong file gốc")


# Giờ chữ Whisper hay sớm 0,2 đến 0,3 giây: cắt theo đó thì sót đuôi chữ cũ (19-4skill-P2: còn mẩu "luôn" 0,15 giây
# sau đoạn mới, nghe như vấp). Chỉ dùng giờ chữ để khoanh vùng, chỗ cắt là giữa khe lặng thật dài nhất trên sóng âm.
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.goc, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, "f4")
e = np.array([np.sqrt((x[k:k + 160] ** 2).mean()) for k in range(0, len(x) - 160, 160)]) + 1e-9
lang = 20 * np.log10(e / np.percentile(e, 95)) < -40


def khe(t):
    a0, a1 = max(0, int((t - 0.35) * 100)), min(len(lang), int((t + 0.5) * 100))
    tot, k = None, a0
    while k < a1:
        if lang[k]:
            k0 = k
            while k < a1 and lang[k]:
                k += 1
            if tot is None or k - k0 > tot[1] - tot[0]:
                tot = (k0, k)
        k += 1
    if tot is None or tot[1] - tot[0] < 6:
        sys.exit(f"✘ Quanh giây {t:.2f} không có khe lặng thật (≥ 60 ms), không cắt để khỏi cắt giữa chữ. Chọn --tu/--sau ở ranh giới câu khác.")
    return (tot[0] + tot[1]) / 200


i = tim(a.tu)
cat_dau = khe((W[i - 1]["end"] + W[i]["start"]) / 2) if i else 0
loc = [f"[0:a]atrim=0:{cat_dau:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=out:st={max(0, cat_dau - 0.02):.3f}:d=0.02[a]",
       f"[1:a]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.02,adelay={int(a.nghi * 1000)}:all=1[b]"]
if a.sau:
    j = tim(a.sau, i + 1)
    cat_cuoi = khe((W[j - 1]["end"] + W[j]["start"]) / 2)
    loc += [f"[0:a]atrim={cat_cuoi:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02[c]", "[a][b][c]concat=n=3:v=0:a=1[o]"]
    print(f"thay {cat_dau:.2f}s đến {cat_cuoi:.2f}s")
else:
    loc += ["[a][b]concat=n=2:v=0:a=1[o]"]
    print(f"thay từ {cat_dau:.2f}s đến hết")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.goc, "-i", a.moi, "-filter_complex", ";".join(loc), "-map", "[o]", a.ra], check=True)
print("xong", a.ra)
