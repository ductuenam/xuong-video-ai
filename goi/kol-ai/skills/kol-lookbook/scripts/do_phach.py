"""Đo lưới phách cố định cho bài nhạc MỚI trước khi lập kế hoạch dựng (lập 22/11/2026).
Dùng: python do_phach.py nhac.mp3 [--bpm-tu 90 --bpm-den 140]
In: chu kỳ phách (giây), nhịp/phút, pha tốt nhất (đặt nhac_tu = pha + k*chu_ky sao cho rơi vào phách MẠNH), điểm khớp.
Vì sao: video mẫu 3 bản nền phòng đo bằng khung 10 ms ra 0,5682 (105 nhịp) — SAI, agent đo khung 5 ms ra 0,5265 (114 nhịp),
6/8 điểm cắt trượt phách, bị CHẶN. Đo trên dải trầm < 150 Hz (giống agent chấm), khung 5 ms, quét mịn chu kỳ và pha;
in cả các ứng viên gần nhịp đôi/nửa để người dựng chọn. Đặt "phach" và "nhac_tu" vào kế hoạch.
Nếu hai dòng đầu điểm sát nhau (< 0,1) thì bài nhịp không rõ (glamor-06: 92,7 và 114,7 nhịp/phút): ưu tiên bài khác có
một ứng viên trội; bắt buộc dùng thì lấy chu kỳ agent chấm đo được (glamor-06 = 0,5265, nhac_tu 0,636)."""
import argparse, subprocess, sys
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("nhac"); ap.add_argument("--bpm-tu", type=float, default=90); ap.add_argument("--bpm-den", type=float, default=140)
a = ap.parse_args()
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
sr = 8000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.nhac, "-af", "lowpass=f=150", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, timeout=120).stdout
x = np.frombuffer(raw, np.int16).astype(float); hop = 40; n = len(x) // hop; fr = sr / hop  # 5 ms
e = np.sqrt((x[:n*hop].reshape(n, hop) ** 2).mean(1)); o = np.maximum(np.diff(e, prepend=e[0]), 0); o = (o - o.mean()) / (o.std() + 1e-9); L = len(o)
def diem(P, ph):
    idx = ((ph + np.arange(0, (L - 2) / fr - P, P)) * fr).astype(int); return o[idx].mean()
# quét TOÀN dải chu kỳ (bước 0,5 ms) với pha thô, rồi tinh chỉnh 4 đỉnh tốt nhất — tự tương quan đã bỏ sót chu kỳ đúng (video mẫu 3)
tho = []
for P in np.arange(60 / a.bpm_den, 60 / a.bpm_tu, 0.0005):
    tho.append(max(((diem(P, ph), P, ph) for ph in np.arange(0, P, 0.01))))
tho.sort(reverse=True)
ket = []
for sc0, P0, _ in tho[:12]:
    ket.append(max(((diem(P, ph), P, ph) for P in np.arange(P0 - 0.001, P0 + 0.001, 0.0001) for ph in np.arange(0, P, 0.0025))))
seen = set()
for sc, P, ph in sorted(ket, reverse=True):
    key = round(P, 3)
    if key in seen: continue
    seen.add(key)
    # phách mạnh: so 2 pha cách nhau một phách trên chu kỳ đôi
    m0, m1 = diem(2 * P, ph), diem(2 * P, ph + P)
    manh = ph if m0 >= m1 else ph + P
    print(f"chu kỳ {P:.4f} s ({60/P:.1f} nhịp/phút)  pha {ph:.3f}  phách mạnh ở {manh:.3f}  điểm khớp {sc:.2f}")
print(f"bài dài {len(x)/sr:.2f} s — chọn dòng điểm cao nhất; nhac_tu = 'phách mạnh', phach = chu kỳ.")
