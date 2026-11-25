"""Nghe lời tiếng Việt bằng faster-whisper. Có GPU NVIDIA thì chạy GPU, không thì chạy CPU (chậm hơn nhiều)."""
import os
import site
import subprocess
import sys
from pathlib import Path

import numpy as np

_MODEL = None


def _nap_dll_cuda():
    """Windows: cho ctranslate2 thấy cuBLAS/cuDNN cài qua pip."""
    if not hasattr(os, "add_dll_directory"):
        return
    for sp in site.getsitepackages():
        for sub in ("cublas", "cudnn"):
            d = Path(sp) / "nvidia" / sub / "bin"
            if d.is_dir():
                os.add_dll_directory(str(d))
                os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]


def doc_am_thanh(file, ss=None, t=None):
    """FFmpeg ra mono 16 kHz float32."""
    cmd = ["ffmpeg", "-nostdin", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    if t is not None:
        cmd += ["-t", str(t)]
    cmd += ["-i", str(file), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def model(ten="large-v3"):
    global _MODEL
    if _MODEL is None:
        _nap_dll_cuda()
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        from faster_whisper import WhisperModel

        try:
            _MODEL = WhisperModel(ten, device="cuda", compute_type="float16")
        except Exception as e:
            print(f"  (không dùng được GPU: {e}; chạy CPU)", file=sys.stderr)
            _MODEL = WhisperModel(ten, device="cpu", compute_type="int8")
    return _MODEL


def nghe(file, goi_y=None, ss=None, t=None, vad=True):
    """Danh sách câu có từng từ; giây tính theo file gốc."""
    off = float(ss or 0)
    segs, _ = model().transcribe(doc_am_thanh(file, ss, t), language="vi", word_timestamps=True, vad_filter=vad, initial_prompt=goi_y, beam_size=5)
    return [{"start": round(s.start + off, 2), "end": round(s.end + off, 2), "text": s.text.strip(),
             "words": [{"start": round(w.start + off, 2), "end": round(w.end + off, 2), "word": w.word, "prob": round(w.probability, 3)} for w in (s.words or [])]}
            for s in segs]


if __name__ == "__main__":
    # Nghe thử nhanh từ dòng lệnh (thử máy học viên 24/11/2026): python whisper_vi.py <file> [--giay 20]
    import argparse
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Nghe lời tiếng Việt trong file âm thanh/video, in từng câu kèm giây.")
    ap.add_argument("file")
    ap.add_argument("--giay", type=float, default=None, help="chỉ nghe chừng này giây đầu (vd 20)")
    a = ap.parse_args()
    for c in nghe(a.file, t=a.giay):
        print(f"[{c['start']:.1f}-{c['end']:.1f}] {c['text']}")
