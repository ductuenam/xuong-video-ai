"""Đo nhịp nói của một file giọng hoặc video: tốc độ, độ dài một hơi nói liền, khoảng nghỉ.
  python do_nhip.py <file> [<file>...]
Mốc tham khảo đo từ người thật nói tự nhiên (video mẫu 12.prompt, 08/11/2026): một hơi khoảng 2,9 giây, nghỉ khoảng 0,22 giây, không có nghỉ trên 0,4 giây.
Giọng AI viết câu ngắn, chèn nghỉ sau mỗi câu chỉ đạt 0,8 đến 1,2 giây mỗi hơi, nghe rời rạc. Bỏ hết dấu phẩy thì lên 2,07 giây nhưng nghe liền quá, khó hiểu. Nên 1,6 đến 2,0 giây."""
import sys
from pathlib import Path

import numpy as np
from faster_whisper.vad import VadOptions, get_speech_timestamps

from whisper_vi import doc_am_thanh

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MOC_HOI = 1.6
MOC_TREN = 2.0  # bản bỏ hết dấu phẩy đạt 2,07 giây, người dùng nghe thấy liền quá, khó hiểu


def do(file):
    x = doc_am_thanh(str(file))
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_silence_duration_ms=120, speech_pad_ms=0))
    hoi = [(b["end"] - b["start"]) / 16000 for b in ts]
    nghi = [(b["start"] - a["end"]) / 16000 for a, b in zip(ts, ts[1:])] or [0]
    return {"dai": len(x) / 16000, "hoi": float(np.mean(hoi)), "nghi": float(np.mean(nghi)), "nghi_dai": sum(n > 0.4 for n in nghi), "so_nghi": len(nghi)}


if __name__ == "__main__":
    for f in sys.argv[1:]:
        k = do(f)
        dau = "✔" if MOC_HOI <= k["hoi"] <= MOC_TREN else "✘"
        print(f"{dau} {Path(f).name}: dài {k['dai']:.1f}s, một hơi TB {k['hoi']:.2f}s (nên {MOC_HOI} đến {MOC_TREN}), nghỉ TB {k['nghi']:.2f}s, nghỉ trên 0,4s: {k['nghi_dai']}/{k['so_nghi']}")
