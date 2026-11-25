"""Tự nghe lại file giọng AI, tìm chỗ sai trước khi dựng.
  python nghe_lai_giong.py <file giọng> <file lời chuẩn>
Nghe KHÔNG gợi ý tên riêng, để Whisper không tự sửa lỗi phát âm thành chữ đúng. Liệt kê: chỗ khác lời, câu dính (khe nghỉ gần 0 sau dấu chấm), đoạn lặng dài.
Máy vẫn không thay được tai người: từ tiếng Anh nghe khác có thể chỉ do Whisper không biết từ đó, phải đọc danh sách và cân nhắc."""
import argparse
import difflib
import re
import sys

import numpy as np

from whisper_vi import doc_am_thanh, model

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("giong")
ap.add_argument("loi")
a = ap.parse_args()
tu = lambda t: re.findall(r"[\wÀ-ỹ]+", t.lower())
goc = open(a.loi, encoding="utf-8").read()
am = doc_am_thanh(a.giong)

# File dài nghe một lần thì Whisper có thể bịa chữ rồi bỏ cả đoạn cuối ("hãy subscribe cho kênh...", 23-skill-ben-trong
# 89 giây: báo khớp 68% dù giọng đúng). Cắt thành khúc khoảng 30 giây tại chỗ lặng nhất gần mốc cắt, nghe từng khúc rồi cộng giờ.
class _Tu:
    def __init__(self, w, lech):
        self.word, self.start, self.end = w.word, w.start + lech, w.end + lech


def _nghe(doan, lech):
    s, _ = model().transcribe(doan, language="vi", word_timestamps=True, vad_filter=False, condition_on_previous_text=False, beam_size=5)
    return [_Tu(w, lech) for x in s for w in (x.words or [])]


KHUC = 30 * 16000
if len(am) <= 45 * 16000:
    W = _nghe(am, 0)
else:
    nl = np.array([np.sqrt((am[k:k + 320] ** 2).mean()) for k in range(0, len(am) - 320, 320)])
    cat, dau = [], 0
    while len(am) - dau > 45 * 16000:
        a0, a1 = (dau + KHUC - 5 * 16000) // 320, (dau + KHUC + 5 * 16000) // 320
        dau = (a0 + int(np.argmin(nl[a0:a1]))) * 320
        cat.append(dau)
    moc_cat = [0] + cat + [len(am)]
    W = [w for b, c in zip(moc_cat, moc_cat[1:]) for w in _nghe(am[b:c], b / 16000)]
ng = [re.sub(r"[^\wÀ-ỹ]", "", w.word.lower()) for w in W]
ng2 = [x for x in ng if x]
vt = [w for w, x in zip(W, ng) if x]
can = tu(goc)
sm = difflib.SequenceMatcher(None, can, ng2, autojunk=False)
print(f"khớp lời: {sm.ratio():.0%}")
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != "equal":
        gio = f"{vt[j1].start:.1f}s" if j1 < len(vt) else "cuối"
        print(f"  {gio}: lời [{' '.join(can[i1:i2])}] nghe thành [{' '.join(ng2[j1:j2])}]")
# Câu dính: từ cuối câu trong lời chuẩn so với từ đầu câu sau
cuoi, dem = set(), 0
for dong in goc.splitlines():
    for cau in re.split(r"[.?!]+", dong):
        n = len(tu(cau))
        if n:
            dem += n
            cuoi.add(dem - 1)
ban_do = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            ban_do[i1 + k] = j1 + k
# Đo lặng trên sóng âm, khung 10 ms, dB so với mức to của giọng (phân vị 95). Giờ chữ của Whisper chỉ dùng để
# biết chỗ cần đo: khi nghe không gợi ý, Whisper có thể lệch hoặc bịa câu (17-linkedin, 18-rag: báo dính và lặng
# 1,84 giây sai), nên khung đo rộng từ 0,3 giây trước tới 0,8 giây sau chữ cuối câu.
e = np.array([np.sqrt((am[k:k + 160] ** 2).mean()) for k in range(0, len(am) - 160, 160)]) + 1e-9
db = 20 * np.log10(e / np.percentile(e, 95))
lang = db < -40


def lang_dai_nhat(t0, t1):
    dai = dem_o = 0
    for x in lang[max(0, int(t0 * 100)):int(t1 * 100)]:
        dem_o = dem_o + 1 if x else 0
        dai = max(dai, dem_o)
    return dai / 100


dinh = 0
for i in sorted(cuoi):
    j = ban_do.get(i)
    if j is not None and j + 1 < len(vt):
        nghi = lang_dai_nhat(vt[j].end - 0.3, vt[j].end + 0.8)
        if nghi < 0.15:
            dinh += 1
            print(f"  ✘ câu dính ở {vt[j].end:.1f}s: [{can[i]}] nghỉ {nghi:.2f}s")
print("không có câu dính" if not dinh else f"{dinh} chỗ câu dính")
dai, k = [], 0
while k < len(lang):
    if lang[k]:
        k0 = k
        while k < len(lang) and lang[k]:
            k += 1
        if (k - k0) / 100 > 0.7 and k0 > 0 and k < len(lang):
            dai.append((round((k - k0) / 100, 2), round(k0 / 100, 1)))
    k += 1
print("khoảng lặng trên 0,7 giây:", dai or "không")
