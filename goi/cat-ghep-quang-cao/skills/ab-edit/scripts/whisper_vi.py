"""Nghe lời tiếng Việt bằng faster-whisper (GPU NVIDIA) — dùng chung cho edl_tool, livestream, phụ đề.
  python whisper_vi.py <file audio/video> --out <tên.json>     → [{start,end,text,words:[{start,end,word,prob}]}]
"""
import argparse
import json
import os
import site
import subprocess
import sys
from pathlib import Path

from chung import CFG, tim_ffmpeg


def _nap_dll_cuda():
    # Windows: cho ctranslate2 thấy cuBLAS/cuDNN cài qua pip
    for sp in site.getsitepackages():
        for sub in ("cublas", "cudnn"):
            d = Path(sp) / "nvidia" / sub / "bin"
            if d.is_dir():
                os.add_dll_directory(str(d))
                os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]


def doc_am_thanh(file, ss=None, t=None):
    """FFmpeg → mono 16 kHz float32 (tránh lỗi PyAV mới với faster-whisper)."""
    import numpy as np

    cmd = [tim_ffmpeg(), "-nostdin", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    if t is not None:
        cmd += ["-t", str(t)]
    cmd += ["-i", str(file), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


_MODEL = None


def model(ten=None):
    global _MODEL
    if _MODEL is None:
        _nap_dll_cuda()
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        from faster_whisper import WhisperModel

        ten = ten or CFG.get("whisper_model", "large-v3")
        try:
            _MODEL = WhisperModel(ten, device="cuda", compute_type="float16")
        except Exception as e:
            print(f"  (không dùng được GPU: {e}; chạy CPU)", file=sys.stderr)
            _MODEL = WhisperModel(ten, device="cpu", compute_type="int8")
    return _MODEL


def nghe(file, goi_y=None, ss=None, t=None, vad=True):
    """Trả danh sách câu có từng từ; giây tính theo file gốc (đã cộng ss)."""
    off = float(ss or 0)
    segs, _ = model().transcribe(doc_am_thanh(file, ss, t), language="vi", word_timestamps=True,
                                 vad_filter=vad, initial_prompt=goi_y, beam_size=5)
    out = []
    for s in segs:
        out.append({
            "start": round(s.start + off, 2), "end": round(s.end + off, 2), "text": s.text.strip(),
            "words": [{"start": round(w.start + off, 2), "end": round(w.end + off, 2), "word": w.word, "prob": round(w.probability, 3)}
                      for w in (s.words or [])],
        })
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--goi-y")
    a = ap.parse_args()
    S = nghe(a.file, a.goi_y)
    Path(a.out).write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✔ {len(S)} câu, {sum(len(s['words']) for s in S)} từ → {a.out}")
