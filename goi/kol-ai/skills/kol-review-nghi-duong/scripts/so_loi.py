"""Nghe lại clip/thành phẩm bằng Whisper và so với lời đã viết.

  so_loi.py <tệp.mp4>=<tệp lời .txt hoặc chuỗi> [...] [--model large-v3] [--json ra.json]
In: chữ THIẾU / THỪA, chữ/giây, khoảng lặng > 0,7 giây, giây nói chữ cuối.
"""
import argparse, difflib, json, re, sys
from pathlib import Path

def chuan(s):
    return re.findall(r"[\wÀ-ỹ]+", s.lower().replace("đ", "đ"))

_m = None
def nghe(p, model):
    global _m
    from faster_whisper import WhisperModel
    if _m is None:
        try: _m = WhisperModel(model, device="cuda", compute_type="float16")
        except Exception: _m = WhisperModel("medium", device="cpu", compute_type="int8")
    seg, _ = _m.transcribe(str(p), language="vi", word_timestamps=True, beam_size=5, vad_filter=False)
    w = []
    for s in seg:
        for x in s.words:
            for t in chuan(x.word):
                w.append((t, x.start, x.end))
    return w

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("cap", nargs="+"); a.add_argument("--model", default="large-v3"); a.add_argument("--json")
    x = a.parse_args(); kq = {}
    for cap in x.cap:
        tep, loi = cap.split("=", 1)
        loi = Path(loi).read_text(encoding="utf-8") if Path(loi).exists() else loi
        w = nghe(tep, x.model); goc = chuan(loi); nghe_duoc = [t for t, _, _ in w]
        sm = difflib.SequenceMatcher(a=goc, b=nghe_duoc, autojunk=False)
        thieu, thua = [], []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op in ("delete", "replace"): thieu.append(" ".join(goc[i1:i2]) + (f" (nghe: {' '.join(nghe_duoc[j1:j2])} @{w[j1][1]:.1f}s)" if op == "replace" else ""))
            if op == "insert": thua.append(f"{' '.join(nghe_duoc[j1:j2])} @{w[j1][1]:.1f}s")
        lang = [(round(w[i][2], 2), round(w[i + 1][1] - w[i][2], 2)) for i in range(len(w) - 1) if w[i + 1][1] - w[i][2] > 0.7]
        noi = (w[-1][2] - w[0][1]) if w else 0
        r = {"khop": round(sm.ratio(), 3), "thieu": thieu, "thua": thua, "chu_giay": round(len(w) / noi, 2) if noi else 0,
             "bat_dau": round(w[0][1], 2) if w else None, "ket_thuc": round(w[-1][2], 2) if w else None, "lang_dai": lang,
             "nghe": " ".join(nghe_duoc)}
        kq[tep] = r
        print(f"\n== {tep}: khớp {r['khop']:.0%}, {r['chu_giay']} chữ/giây, nói {r['bat_dau']}–{r['ket_thuc']} giây")
        print("  nghe:", r["nghe"])
        for t in thieu: print("  THIẾU/SAI:", t)
        for t in thua: print("  THỪA:", t)
        for t in lang: print(f"  lặng {t[1]} giây sau giây {t[0]}")
    if x.json: Path(x.json).write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
