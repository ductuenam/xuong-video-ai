"""Cắt lời người nói: đề xuất EDL (bỏ khoảng lặng + câu nói lại) và kiểm tra bản cắt bằng Whisper. Port từ edl-tool.py v2 (whisper-cpp → faster-whisper).
  python edl_tool.py propose <video nguồn> --out <du-an>/edl.json   # → edl.json + <edl>-cau.json (câu + từ) + bảng câu (NG = nói lại)
  python edl_tool.py verify  <video nguồn> <edl.json>                # ghép audio theo EDL rồi nghe lại → đọc xem mất/thừa chữ
  python edl_tool.py map     <edl.json> <edl-cau.json> từ1 từ2 ...   # giây trên timeline của các từ khoá (đặt cảnh trám/chữ)
Chạy trên file NGUỒN GỐC (chưa nén/chuẩn âm). Câu nào có 1 trong 3 câu SAU giống ≥60% → bỏ câu TRƯỚC (giữ lần nói sau). Luôn đọc lại bảng câu."""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

from chung import tim_ffmpeg
from whisper_vi import nghe


def pauses(src, db=-32, d=0.18):
    r = subprocess.run([tim_ffmpeg(), "-nostdin", "-i", str(src), "-vn", "-af", f"silencedetect=n={db}dB:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return list(zip(s, e))


def sim(x, y):
    """Giống nhau: theo cả câu, khối trùng dài nhất so với câu ngắn hơn, hoặc tỉ lệ từ (bắt câu nói dở rồi nói lại)."""
    x, y = x.lower(), y.lower()
    m = difflib.SequenceMatcher(None, x, y)
    blk = max((b.size for b in m.get_matching_blocks()), default=0)
    wx, wy = re.findall(r"\w+", x), set(re.findall(r"\w+", y))
    wo = sum(w in wy for w in wx) / len(wx) if len(wx) >= 4 else 0
    return max(m.ratio(), blk / max(1, min(len(x), len(y))), wo - 0.1)


def propose(src, out):
    out = Path(out)
    S = nghe(src)
    out.with_name(out.stem + "-cau.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
    P = pauses(src)

    def snap(t, side):  # mép câu vào khoảng lặng gần nhất, giữ đệm 0,08–0,12s
        for p0, p1 in P:
            if side == "a" and p0 - 0.3 <= t <= p1 + 0.05:
                return round(p1 - 0.08, 2)
            if side == "b" and p0 - 0.05 <= t <= p1 + 0.3:
                return round(p0 + 0.12, 2)
        return round(t, 2)

    keep = []
    for i, s in enumerate(S):
        ng = any(sim(s["text"], y["text"]) >= 0.6 for y in S[i + 1:i + 4])
        print(f"{'NG ' if ng else '   '}{s['start']:7.2f}-{s['end']:7.2f}  {s['text']}")
        if not ng:
            keep.append([snap(s["start"], "a"), snap(s["end"], "b")])
    out.write_text(json.dumps(keep), encoding="utf-8")
    print(f"→ {out}: {len(keep)} đoạn, tổng {round(sum(b - a for a, b in keep), 2)}s")


def verify(src, edl):
    E = json.loads(Path(edl).read_text(encoding="utf-8"))
    rough = Path(edl).with_name(Path(edl).stem + "-nghe-thu.wav")
    fc = ";".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.03:.3f}:d=0.03[a{i}]" for i, (a, b) in enumerate(E))
    fc += ";" + "".join(f"[a{i}]" for i in range(len(E))) + f"concat=n={len(E)}:v=0:a=1[o]"
    subprocess.run([tim_ffmpeg(), "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[o]", "-ar", "48000", str(rough)], check=True)
    for s in nghe(rough, vad=False):
        print(f"{s['start']:7.2f}  {s['text']}")
    print(f"→ nghe thử: {rough}")


def tl(E, s):
    """Giây trong source → giây trên timeline đã cắt (None nếu bị cắt bỏ)."""
    t = 0
    for a, b in E:
        if a <= s <= b:
            return t + s - a
        t += b - a
    return None


def tmap(edl, cau, keys):
    E = json.loads(Path(edl).read_text(encoding="utf-8"))
    for s in json.loads(Path(cau).read_text(encoding="utf-8")):
        for w in s["words"]:
            x = tl(E, w["start"])
            if x is not None and any(w["word"].strip().lower().startswith(k.lower()) for k in keys):
                print(f"{x:7.2f}  (src {w['start']:.2f})  {w['word'].strip()}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "propose":
        propose(sys.argv[2], sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "edl.json")
    elif c == "verify":
        verify(sys.argv[2], sys.argv[3])
    elif c == "map":
        tmap(sys.argv[2], sys.argv[3], sys.argv[4:])
