"""Chèn khoảng nghỉ ngắn vào những dấu phẩy, dấu chấm mà giọng AI đọc dính, để người nghe kịp hiểu.
  python nghi_dau_phay.py <file giọng> <loi.txt> <file ra> [--phay 0.15] [--cham 0.25]
Lấy vị trí dấu câu từ loi.txt, giờ từng chữ từ Whisper. Chỗ nào nghỉ ít hơn mức cần thì chèn thêm im lặng cho đủ;
chỗ đã đủ thì giữ nguyên. Không đổi tốc độ nói. Bản đọc vẫn phải giữ dấu phẩy ở chỗ chuyển ý (xem kich-ban.md)."""
import argparse
import re
import subprocess
import sys

import numpy as np

from whisper_vi import nghe

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("giong")
ap.add_argument("loi")
ap.add_argument("ra")
ap.add_argument("--phay", type=float, default=0.15)
ap.add_argument("--cham", type=float, default=0.25)
a = ap.parse_args()
chuan = lambda s: re.sub(r"[^\wÀ-ỹ]", "", s.lower())
loi = open(a.loi, encoding="utf-8").read()
# Mỗi dấu câu: (chữ đứng trước, mức nghỉ cần)
dau = [(chuan(m.group(1)), a.phay if m.group(2) == "," else a.cham) for m in re.finditer(r"(\S+?)([,.?!])(?=\s|$)", loi)]
dau = [(t, n) for t, n in dau if t]
W = [w for s in nghe(a.giong) for w in s["words"]]
c = [chuan(w["word"]) for w in W]
# Giờ chữ của Whisper lệch ở ranh giới, nên đo lặng trên sóng âm: khung 10 ms, lặng là dưới -38 dB so với đỉnh
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.giong, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, "f4")
H = 160
e = np.array([np.sqrt((x[i:i + H] ** 2).mean()) for i in range(0, len(x) - H, H)]) + 1e-9
db = 20 * np.log10(e / np.percentile(e, 95))
lang = db < -38
# Các đoạn lặng liền nhau trên sóng âm: (đầu, cuối) theo khung 10 ms
doan_lang, i = [], 0
while i < len(lang):
    if lang[i]:
        k0 = i
        while i < len(lang) and lang[i]:
            i += 1
        doan_lang.append((k0, i - 1))
    i += 1
chen, bo_qua, j = [], [], 0
for t, can in dau:
    k = next((i for i in range(j, min(j + 40, len(c) - 1)) if c[i] == t or c[i].endswith(t)), None)
    if k is None:
        continue
    j = k + 1
    giua = int((W[k]["end"] + W[k + 1]["start"]) / 2 * 100)
    # Giờ chữ của Whisper có thể lệch tới 0,3 giây so với chỗ lặng thật (15-omni-voice: lệch 0,2 giây sớm,
    # cửa sổ ±0,15 giây trượt mất chỗ nghỉ có sẵn nên chèn chồng, giọng rời rạc lại). Lấy đoạn lặng dài nhất trong ±0,35 giây.
    gan = [(b - a + 1, a, b) for a, b in doan_lang if b >= giua - 35 and a <= giua + 35]
    if gan:
        dai, l, r = max(gan)
        co, p = dai / 100, (l + r) // 2
    else:
        # Không có đoạn lặng: tìm chỗ nhỏ tiếng nhất KÉO DÀI ít nhất 80 ms, lệch về sau vì giờ chữ Whisper hay sớm.
        # Không lấy một khung lẻ: khe giữa hai âm tiết trong một từ ("tự | tin") cũng nhỏ tiếng một khung,
        # chèn vào đó là giọng vấp (18-rag, giây 3,27). Chỗ đó vẫn to hơn -30 dB thì bỏ qua, không chèn.
        a0, a1 = max(0, giua - 10), min(len(db) - 8, giua + 60)
        tb = np.array([db[i:i + 8].mean() for i in range(a0, a1 + 1)]) if a1 > a0 else np.array([0.0])
        k0 = int(np.argmin(tb))
        if tb[k0] > -30:
            bo_qua.append(round(giua / 100, 2))
            continue
        co, p = 0.0, a0 + k0 + 4
    if co < can - 0.02:
        chen.append((p / 100, round(can - co, 3)))
print(f"{len(dau)} dấu câu, chèn thêm nghỉ ở {len(chen)} chỗ:", [(round(x, 2), y) for x, y in chen])
if bo_qua:
    print(f"bỏ qua {len(bo_qua)} chỗ không tìm được khe lặng thật (không chèn để khỏi cắt giữa từ):", bo_qua)
if not chen:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.giong, "-ar", "48000", a.ra], check=True)
    sys.exit(0)
# Cắt thành đoạn, chèn im lặng giữa các đoạn
moc = [0.0] + [x for x, _ in chen]
loc, nhan = [], []
for i, (x, them) in enumerate(chen):
    loc.append(f"[0:a]atrim={moc[i]:.3f}:{x:.3f},asetpts=PTS-STARTPTS[d{i}];anullsrc=r=48000:cl=mono,atrim=0:{them:.3f}[n{i}]")
    nhan += [f"[d{i}]", f"[n{i}]"]
i = len(chen)
loc.append(f"[0:a]atrim={moc[-1]:.3f},asetpts=PTS-STARTPTS[d{i}]")
nhan.append(f"[d{i}]")
fc = "[0:a]aresample=48000,aformat=channel_layouts=mono[g];" + ";".join(loc).replace("[0:a]", "[g]", 0)
# dùng nhánh đã đổi mẫu cho mọi đoạn
fc = "[0:a]aresample=48000,aformat=channel_layouts=mono,asplit=" + str(i + 1) + "".join(f"[s{k}]" for k in range(i + 1)) + ";" + ";".join(
    p.replace("[0:a]", f"[s{n}]", 1) for n, p in enumerate(loc)) + ";" + "".join(nhan) + f"concat=n={len(nhan)}:v=0:a=1[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.giong, "-filter_complex", fc, "-map", "[o]", "-ar", "48000", a.ra], check=True)
print("xong", a.ra)
