"""Phụ đề: chữ theo loi.txt (mỗi dòng 1 cụm, đúng lời người nói, đúng chính tả tên riêng), giờ lấy từ Whisper trên master.
  python lap_phu_de.py <thư mục dự án>
Ghi phu-de.json. Tỉ lệ khớp thấp nghĩa là loi.txt lệch lời thật, phải sửa loi.txt."""
import difflib
import json
import re
import sys
from pathlib import Path

from chung import ghi
from whisper_vi import nghe

KHOP_TOI_THIEU = 0.8


def chuan(t):
    return re.sub(r"[^\w%]", "", t.lower())


da = Path(sys.argv[1])
CUM = [x.strip() for x in (da / "loi.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
goi = (da / "goi-y.txt").read_text(encoding="utf-8").strip() if (da / "goi-y.txt").exists() else None
W = [w for s in nghe(da / "render" / "master.mp4", goi_y=goi) for w in s["words"]]
wt = [chuan(w["word"]) for w in W]
toks, cum_cua = [], []
for i, c in enumerate(CUM):
    for t in c.split():
        toks.append(chuan(t))
        cum_cua.append(i)
gio = [None] * len(toks)
for a, b, n in difflib.SequenceMatcher(None, toks, wt, autojunk=False).get_matching_blocks():
    for k in range(n):
        gio[a + k] = (W[b + k]["start"], W[b + k]["end"])
biet = [i for i, g in enumerate(gio) if g]
ti_le = len(biet) / max(1, len(toks))
print(f"khớp {len(biet)}/{len(toks)} từ ({ti_le:.0%})")
if ti_le < KHOP_TOI_THIEU:
    sys.exit(f"✘ loi.txt lệch lời thật quá nhiều (cần ≥ {KHOP_TOI_THIEU:.0%}). Sửa loi.txt theo đúng lời đã chọn rồi chạy lại.")
for i in range(len(gio)):  # nội suy từ không khớp
    if gio[i] is None:
        tr = max((x for x in biet if x < i), default=None)
        sa = min((x for x in biet if x > i), default=None)
        if tr is not None and sa is not None:
            t = gio[tr][1] + (i - tr) / (sa - tr) * (gio[sa][0] - gio[tr][1])
        elif tr is not None:
            t = gio[tr][1] + 0.2 * (i - tr)
        else:
            t = gio[sa][0] - 0.2 * (sa - i)
        gio[i] = (t, t + 0.18)
kq = []
for i, c in enumerate(CUM):
    idx = [k for k, x in enumerate(cum_cua) if x == i]
    kq.append({"text": c, "start": round(gio[idx[0]][0], 2), "end": round(gio[idx[-1]][1], 2)})
for a, b in zip(kq, kq[1:]):
    b["start"] = max(b["start"], a["start"] + 0.05)
    a["end"] = max(a["end"], a["start"] + 0.3)
ghi(da / "phu-de.json", kq, 0)
for i, x in enumerate(kq):
    print(f'{i + 1:2d} {x["start"]:6.2f} {x["end"]:6.2f} {x["text"]}')
