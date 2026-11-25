"""Nghiệm thu trước khi bàn giao: còn ✘ thì KHÔNG giao, sửa rồi chạy lại (mã thoát 1 = còn lỗi).
  python nghiem_thu.py <video> --src <file gốc> --edl <edl.json> --master <master.mp4> --cum <phu-de.json>
                       [--brand an-binh-ai] [--moc 1,2,3] [--moc-net 12,50] [--logo x,y,w,h --moc-logo 3,8,62]
Kiểm: lặp từ ở từng đoạn cắt · đủ lời · khoảng lặng · màu chuẩn · độ nét so với master · logo che góc · âm lượng/khung đen (tu_kiem).
Bài học video 01 (04/11/2026): nghe cả bài thì Whisper gộp mất từ lặp, nên phải nghe RIÊNG từng đoạn cắt.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
from faster_whisper.vad import VadOptions, get_speech_timestamps
from whisper_vi import doc_am_thanh, model

GOI_Y = "Claude, token, Claude Token Counter, Anthropic, tiện ích, Usage, Chrome, trình duyệt, kết nối"
loi = []


def kq(dat, chu):
    print(("✔ " if dat else "✘ ") + chu)
    if not dat:
        loi.append(chu)


def nghe(file, a=None, t=None):
    seg, _ = model().transcribe(doc_am_thanh(file, a, t), language="vi", vad_filter=False, condition_on_previous_text=False,
                                initial_prompt=GOI_Y, beam_size=5, no_speech_threshold=0.9)
    return " ".join(x.text.strip() for x in seg)


def tu(t):
    return re.findall(r"[\wÀ-ỹ%]+", t.lower())


def giong(x, y):
    return difflib.SequenceMatcher(None, x, y).ratio() >= 0.7


def kiem_lap(src, edl):
    """Cuối đoạn trước trùng đầu đoạn sau (2+ từ), hoặc 2+ từ lặp liền nhau trong 1 đoạn."""
    E = json.loads(Path(edl).read_text(encoding="utf-8"))
    chu = [tu(nghe(src, max(0, a - 0.05), b - a + 0.1)) for a, b in E]
    so = 0
    for i, w in enumerate(chu):
        for k in range(2, len(w) // 2 + 1):
            for j in range(len(w) - 2 * k + 1):
                if all(giong(w[j + n], w[j + k + n]) for n in range(k)):
                    so += 1
                    kq(False, f"lặp trong đoạn {i} ({E[i][0]}s): {' '.join(w[j:j + k])}")
        if i + 1 < len(chu):
            s = chu[i + 1]
            for k in range(min(5, len(w), len(s)), 1, -1):
                # tìm k từ đầu đoạn sau ở 8 từ cuối đoạn trước
                for j in range(max(0, len(w) - 8), len(w) - k + 1):
                    if all(giong(w[j + n], s[n]) for n in range(k)):
                        so += 1
                        kq(False, f"lặp giữa đoạn {i} và {i + 1} ({E[i + 1][0]}s): {' '.join(s[:k])}")
                        break
                else:
                    continue
                break
    if not so:
        kq(True, f"không lặp từ ({len(E)} đoạn cắt, nghe riêng từng đoạn)")


def nghe_ca_bai(file):
    seg, _ = model().transcribe(doc_am_thanh(file), language="vi", vad_filter=True, condition_on_previous_text=False,
                                initial_prompt=GOI_Y, beam_size=5)
    return " ".join(x.text.strip() for x in seg)


def so_loi(can, nghe_duoc):
    """Trả về (tỉ lệ khớp, đoạn mất liền nhau dài nhất). Whisper nghe sai lẻ tẻ thì đoạn mất ngắn; cắt mất câu thì đoạn mất dài."""
    sm = difflib.SequenceMatcher(None, can, nghe_duoc, autojunk=False)
    mat = []
    for op, i1, i2, _j1, _j2 in sm.get_opcodes():
        if op in ("delete", "replace") and i2 - i1 > len(mat):
            mat = can[i1:i2]
    return sm.ratio(), mat


def kiem_du_loi(video, cum):
    """Nghe CẢ BÀI rồi so: nghe từng cụm ngắn trên tiếng đã trộn nhạc thì Whisper đoán sai (video 02 báo 59% trong khi cả bài khớp 94%)."""
    C = json.loads(Path(cum).read_text(encoding="utf-8"))
    can = [x for c in C for x in tu(c["text"])]
    ti_le, mat = so_loi(can, tu(nghe_ca_bai(video)))
    kq(ti_le >= 0.85, f"đủ lời: khớp {ti_le:.0%} với lời đã duyệt (cần ≥ 85%)")
    kq(len(mat) < 8, f"không mất đoạn lời: dài nhất {len(mat)} từ liền nhau (cần < 8): {' '.join(mat)}")


def khoang_lang(master):
    """Các khe không có lời (dài giây, giây bắt đầu). Dùng VAD vì bộ nén trên master nâng tiếng ồn phòng lên, đo năng lượng không thấy."""
    ts = get_speech_timestamps(doc_am_thanh(master), VadOptions(threshold=0.5, min_silence_duration_ms=150, speech_pad_ms=0))
    return [((b["start"] - a["end"]) / 16000, a["end"] / 16000) for a, b in zip(ts, ts[1:])]


def kiem_khoang_lang(master, toi_da=0.7):
    """Video 03 để lọt 1,4 s ở giây thứ 5: nghe chữ vẫn đủ lời nên các mục khác không bắt được."""
    lang = [(d, t) for d, t in khoang_lang(master) if d > toi_da]
    for d, t in lang:
        kq(False, f"khoảng lặng {d:.2f}s ở giây {t:.1f} (tối đa {toi_da}s)")
    if not lang:
        kq(True, f"không có khoảng lặng dài hơn {toi_da}s")


def thong_so(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=pix_fmt,color_range,color_space,width,height", "-of", "json", video],
                       capture_output=True, text=True).stdout
    return json.loads(r)["streams"][0]


def kiem_mau(video):
    s = thong_so(video)
    dat = s.get("pix_fmt") == "yuv420p" and s.get("color_range") == "tv" and s.get("color_space") == "bt709"
    kq(dat, f"màu: {s.get('pix_fmt')} · {s.get('color_range')} · {s.get('color_space')} (cần yuv420p · tv · bt709, sai là trình phát hiển thị bạc)")


def khung(video, giay):
    c = cv2.VideoCapture(video)
    c.set(cv2.CAP_PROP_POS_MSEC, giay * 1000)
    ok, f = c.read()
    c.release()
    return f if ok else None


def net(a):
    """Đo chi tiết thật: thu nhỏ 1/2 trước khi đo để không tính nhiễu li ti (Remotion làm mất nhiễu nhưng mắt không thấy khác)."""
    x = cv2.resize(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    return cv2.Laplacian(x, cv2.CV_64F).var()


def kiem_net(video, master, moc):
    """Vùng giữa khung ở cảnh toàn màn người nói: không được mềm hơn master quá nhiều."""
    for t in moc:
        o, m = khung(video, t), khung(master, t)
        if o is None or m is None:
            kq(False, f"không đọc được khung {t}s")
            continue
        H, W = o.shape[:2]
        mh, mw = m.shape[:2]
        cw = int(mh * W / H)
        cx = int(mw * 0.552) if mw > mh else mw // 2  # nguồn ngang cắt quanh mặt, nguồn dọc lấy cả khung
        m2 = cv2.resize(m[:, max(0, cx - cw // 2):cx + cw // 2], (W, H), interpolation=cv2.INTER_AREA)
        vung = (slice(H // 5, H // 2), slice(W // 5, W * 4 // 5))
        r = net(o[vung]) / max(1, net(m2[vung]))
        kq(r >= 0.7, f"độ nét {t}s: {net(o[vung]):.0f} so với master {net(m2[vung]):.0f} ({r:.0%}, cần ≥ 70%)")


def kiem_logo(video, vung, moc):
    """Logo che góc: vùng này phải gần như không đổi giữa các cảnh Flow."""
    x, y, w, h = vung
    anh = [khung(video, t)[y:y + h, x:x + w].astype(float) for t in moc]
    lech = max(np.abs(a - anh[0]).mean() for a in anh[1:])
    kq(lech < 8, f"logo góc ảnh che đủ ở {len(moc)} cảnh Flow (lệch {lech:.1f}, cần < 8)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--src", required=True)
    ap.add_argument("--edl", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--cum", required=True)
    ap.add_argument("--brand", default="an-binh-ai")
    ap.add_argument("--moc", default=None)
    ap.add_argument("--moc-net", default=None)
    ap.add_argument("--logo", default=None)
    ap.add_argument("--moc-logo", default=None)
    ap.add_argument("--goi-y", default=None, help="tên riêng của video này để Whisper nghe đúng")
    a = ap.parse_args()
    if a.goi_y:
        global GOI_Y
        GOI_Y = a.goi_y

    kiem_lap(a.src, a.edl)
    kiem_du_loi(a.video, a.cum)
    kiem_khoang_lang(a.master)
    kiem_mau(a.video)
    if a.moc_net:
        kiem_net(a.video, a.master, [float(x) for x in a.moc_net.split(",")])
    if a.logo and a.moc_logo:
        kiem_logo(a.video, [int(x) for x in a.logo.split(",")], [float(x) for x in a.moc_logo.split(",")])
    cmd = [sys.executable, str(Path(__file__).with_name("tu_kiem.py")), "xuat", a.video, "--brand", a.brand]
    if a.moc:
        cmd += ["--moc", a.moc]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    kq(r.returncode == 0, "tu_kiem: hình + âm lượng")
    print()
    if loi:
        print(f"✘ CHƯA ĐẠT: {len(loi)} lỗi. Sửa rồi chạy lại, chưa bàn giao.")
        sys.exit(1)
    print("✔ ĐẠT. Vẫn phải xem tờ soát bằng mắt trước khi bàn giao.")


if __name__ == "__main__":
    main()
