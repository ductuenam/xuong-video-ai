"""So lời Muse nói với lời đã viết, in từng chữ kèm mốc giây, đánh dấu chữ thiếu và chữ thừa.

Muse hay bỏ hẳn một vế, nuốt chữ đầu câu, hoặc tự thêm ý không có nguồn. Đọc bản Whisper
bằng mắt dễ sót, nên script căn hai bản theo từng chữ rồi in ra chỗ lệch.

Dùng: python so_loi.py canh1.mp4=loi1.txt canh2.mp4=loi2.txt ... [--model large-v3]
Nạp mô hình MỘT lần cho mọi cảnh. Đừng chạy nhiều lệnh song song: mỗi lệnh large-v3 chiếm
khoảng 4 GB RAM, 4 lệnh cùng lúc làm máy nghẽn, 7 phút chưa ra chữ.
In:
- Bảng chữ: mốc giây đầu/cuối từng chữ (dùng chọn điểm cắt tiếng).
- THIẾU: chữ có trong lời mà Muse không nói (hoặc Whisper nghe nhầm, cần nghe lại).
- THỪA: chữ Muse nói thêm. Ý thêm vào phải soát với nguon.md.
Whisper viết gọn số và size ("5XL", "60"), nên lệch ở các chữ đó thường không phải lỗi.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

from faster_whisper import WhisperModel


def chuan(s):
    return re.sub(r"[^\w\s]", " ", s.lower()).split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cap", nargs="+", help="video.mp4=loi.txt")
    ap.add_argument("--model", default=None, help="mặc định: whisper_model trong cau-hinh.json, không có thì large-v3")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if not a.model:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from chung import doc_cau_hinh
        a.model = (doc_cau_hinh(bat_buoc=False) or {}).get("whisper_model") or "large-v3"
    try:
        import ctranslate2
        gpu = ctranslate2.get_cuda_device_count() > 0
    except Exception:
        gpu = False
    m = WhisperModel(a.model, device="cuda" if gpu else "cpu", compute_type="float16" if gpu else "int8")
    for cap in a.cap:
        video, tep = cap.rsplit("=", 1)
        loi = open(tep, encoding="utf-8").read()
        print(f"===== {video}")
        segs, _ = m.transcribe(video, language="vi", word_timestamps=True, condition_on_previous_text=False)
                               # khong dua loi vao initial_prompt: Whisper se 'nghe' ra chu Muse da bo
        tu = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
        nghe = [chuan(t)[0] if chuan(t) else "" for t, _, _ in tu]
        viet = chuan(loi)
        print("Bảng chữ (giây):")
        print("  " + "  ".join(f"{t}[{a_:.2f}-{b:.2f}]" for t, a_, b in tu))
        sm = difflib.SequenceMatcher(a=viet, b=nghe, autojunk=False)
        loi_lech = 0
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                continue
            loi_lech += 1
            moc = f"{tu[j1][1]:.2f}" if j1 < len(tu) else (f"{tu[-1][2]:.2f}" if tu else "?")
            if op in ("delete", "replace"):
                print(f"THIẾU  quanh {moc}s: {' '.join(viet[i1:i2])}" + (f"  (nghe thành: {' '.join(nghe[j1:j2])})" if op == "replace" else ""))
            if op == "insert":
                print(f"THỪA   quanh {moc}s: {' '.join(nghe[j1:j2])}")
        if tu:
            print(f"Bắt đầu nói {tu[0][1]:.2f}s, hết lời {tu[-1][2]:.2f}s, {len(tu)} chữ, "
                  f"{len(tu) / max(0.1, tu[-1][2] - tu[0][1]):.1f} chữ/giây")
        print("Khớp hoàn toàn" if not loi_lech else f"{loi_lech} chỗ lệch, nghe lại các mốc trên")


if __name__ == "__main__":
    main()
