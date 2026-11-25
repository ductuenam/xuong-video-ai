"""Cổng nghiệm thu trước khi bàn giao. Còn dấu ✘ thì KHÔNG giao: sửa rồi chạy lại (mã thoát 1 = còn lỗi).
  python nghiem_thu.py <thư mục dự án>
Kiểm: lặp từ ở từng đoạn cắt, đủ lời, khoảng lặng, màu chuẩn, độ nét so với master, che logo góc, âm lượng, khung đen.
Máy không bắt được mọi lỗi: sau khi đạt vẫn phải xem to-soat.jpg bằng mắt.
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from chung import doc
from faster_whisper.vad import VadOptions, get_speech_timestamps
from whisper_vi import doc_am_thanh, model

CHUAN_LUFS = -16
VUNG_NHAN_GOC = (756, 1668, 300, 112)  # nhãn che logo góc trên cảnh Flow, xem NhanGoc trong engine
GOI_Y = None
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


def lap_noi(w, s, so_sanh=None):
    """Số từ lặp ở chỗ nối hai đoạn (0 là không lặp). Lặp 2–3 từ chỉ tính khi nằm sát chỗ cắt (cuối đoạn trước, cho phép
    thêm 1 từ lỡ), vì "...các bạn ra trường. | Các bạn có đang..." là câu bình thường (sửa 24/11/2026, lệnh edit video).
    Từ 4 từ trùng trở lên thì dò xa 60 từ, bắt đoạn nói lại dài."""
    g = so_sanh or giong
    for k in range(min(6, len(w), len(s)), 1, -1):
        tu_j = max(0, len(w) - 60) if k >= 4 else max(0, len(w) - k - 1)
        for j in range(tu_j, len(w) - k + 1):
            if all(g(w[j + n], s[n]) for n in range(k)):
                return k
    return 0


def lien_nguon(doan):
    """Chỉ số i mà đoạn i và i+1 vốn liền nhau trong file gốc (chỉ bỏ khoảng lặng < 0,8 giây): lặp 2–3 chữ ở đó là người nói
    liệt kê ("kiểm tra email, | kiểm tra chứng từ"), không phải do cắt (bản edit 30 giây 24/11/2026 bị báo nhầm)."""
    return {i for i in range(len(doan) - 1) if doan[i][0] == doan[i + 1][0] and 0 <= doan[i + 1][1] - doan[i][2] < 0.8}


def kiem_lap(src, edl, lien=()):
    """Nghe riêng từng đoạn cắt, vì nghe cả bài thì Whisper gộp mất từ lặp."""
    chu = [tu(nghe(src, max(0, a - 0.05), b - a + 0.1)) for a, b in edl]
    so = 0
    for i, w in enumerate(chu):
        for k in range(2, len(w) // 2 + 1):
            for j in range(len(w) - 2 * k + 1):
                if all(giong(w[j + n], w[j + k + n]) for n in range(k)):
                    so += 1
                    kq(False, f"lặp trong đoạn {i} (giây {edl[i][0]}): {' '.join(w[j:j + k])}")
        if i + 1 < len(chu):
            k = lap_noi(w, chu[i + 1])
            if k and k <= 3 and i in lien:
                print(f"  (lặp {k} chữ giữa đoạn {i} và {i + 1} nhưng hai đoạn liền nhau trong file gốc: người nói liệt kê, không tính)")
            elif k:
                so += 1
                kq(False, f"lặp giữa đoạn {i} và {i + 1} (giây {edl[i + 1][0]}): {' '.join(chu[i + 1][:k])}")
    if not so:
        kq(True, f"không lặp từ ({len(edl)} đoạn cắt)")


def kiem_du_loi(video, cum):
    """Nghe cả bài rồi so với lời đã duyệt. Whisper nghe sai lẻ tẻ thì đoạn mất ngắn, cắt mất câu thì đoạn mất dài."""
    can = [x for c in cum for x in tu(c["text"])]
    am = doc_am_thanh(video)

    def mot_luot(vad, hai_nua=False):
        # hai_nua: nghe hai nửa gối nhau 1,5 giây. Video dài hơn 30 giây chút ít, Whisper hay kết khung 30 giây sớm rồi
        # nhảy qua phần lời cuối (bản 31,8 giây 24/11/2026 mất 25 chữ cuối dù âm thanh còn đủ).
        manh = [am] if not hai_nua else [am[:len(am) // 2 + 24000], am[len(am) // 2 - 24000:]]
        chu_ = []
        for m_ in manh:
            seg, _ = model().transcribe(m_, language="vi", vad_filter=vad, condition_on_previous_text=False, initial_prompt=GOI_Y, beam_size=5)
            chu_ += [x.text.strip() for x in seg]
        sm_ = difflib.SequenceMatcher(None, can, tu(" ".join(chu_)), autojunk=False)
        mat_ = []
        for op, i1, i2, _j1, _j2 in sm_.get_opcodes():
            if op in ("delete", "replace") and i2 - i1 > len(mat_):
                mat_ = can[i1:i2]
        # tỉ lệ: nghe cả bài dùng ratio như cũ; nghe hai nửa thì đếm số chữ của lời đã duyệt nghe thấy (phần gối bị trùng chữ)
        tl_ = sum(b.size for b in sm_.get_matching_blocks()) / max(len(can), 1) if hai_nua else sm_.ratio()
        return tl_, mat_
    tl, mat = mot_luot(True)
    if len(mat) >= 8 or tl < 0.85:
        # Bản edit 30 giây 24/11/2026: nghe cả bài bỏ sót 25 chữ cuối dù âm thanh còn đủ. Nghe thêm hai nửa gối nhau, lấy lượt
        # tốt hơn; lời bị cắt thật thì cả hai lượt đều thiếu nên vẫn bị bắt (đã thử chèn câu giả: bị bắt 20 chữ).
        tl2, mat2 = mot_luot(True, hai_nua=True)
        if (len(mat2), -tl2) < (len(mat), -tl):
            print("  (nghe cả bài sót lời, dùng lượt nghe hai nửa gối nhau)")
            tl, mat = tl2, mat2
    kq(tl >= 0.85, f"đủ lời: khớp {tl:.0%} với lời đã duyệt (cần ≥ 85%)")
    kq(len(mat) < 8, f"không mất đoạn lời: dài nhất {len(mat)} từ liền nhau (cần < 8): {' '.join(mat)}")


def kiem_khoang_lang(master, toi_da=0.7):
    """Dùng VAD vì bộ nén trên master nâng tiếng ồn phòng lên, đo năng lượng không thấy."""
    ts = get_speech_timestamps(doc_am_thanh(master), VadOptions(threshold=0.5, min_silence_duration_ms=150, speech_pad_ms=0))
    lang = [((b["start"] - a["end"]) / 16000, a["end"] / 16000) for a, b in zip(ts, ts[1:])]
    lang = [(d, t) for d, t in lang if d > toi_da]
    for d, t in lang:
        kq(False, f"khoảng lặng {d:.2f}s ở giây {t:.1f} (tối đa {toi_da}s)")
    if not lang:
        kq(True, f"không có khoảng lặng dài hơn {toi_da}s")


def kiem_mau(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=pix_fmt,color_range,color_space", "-of", "json", video], capture_output=True, text=True).stdout
    s = json.loads(r)["streams"][0]
    dat = s.get("pix_fmt") == "yuv420p" and s.get("color_range") == "tv" and s.get("color_space") == "bt709"
    kq(dat, f"màu: {s.get('pix_fmt')} · {s.get('color_range')} · {s.get('color_space')} (cần yuv420p · tv · bt709, sai là trình phát hiển thị bạc)")


def khung(video, giay):
    c = cv2.VideoCapture(video)
    c.set(cv2.CAP_PROP_POS_MSEC, giay * 1000)
    ok, f = c.read()
    c.release()
    return f if ok else None


def net(a):
    x = cv2.resize(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    return cv2.Laplacian(x, cv2.CV_64F).var()


def kiem_net(video, master, moc):
    """Vùng mặt ở cảnh người nói không được mềm hơn master quá nhiều. Vùng đo tránh thẻ trên trần và phụ đề."""
    for t in moc:
        o, m = khung(video, t), khung(master, t)
        if o is None or m is None:
            kq(False, f"không đọc được khung giây {t}")
            continue
        H, W = o.shape[:2]
        vung = (slice(int(H * 0.32), int(H * 0.62)), slice(W // 5, W * 4 // 5))
        r = net(o[vung]) / max(1, net(m[vung]))
        kq(r >= 0.7, f"độ nét giây {t}: {r:.0%} so với master (cần ≥ 70%)")


def kiem_logo(video, moc):
    """Logo Flow ở góc bị nhãn che: vùng nhãn phải gần như không đổi giữa các cảnh Flow."""
    x, y, w, h = VUNG_NHAN_GOC
    anh = [khung(video, t)[y:y + h, x:x + w].astype(float) for t in moc]
    lech = max(np.abs(a - anh[0]).mean() for a in anh[1:])
    kq(lech < 8, f"nhãn che logo đủ ở {len(moc)} cảnh Flow (lệch {lech:.1f}, cần < 8)")


def kiem_am_hinh(video):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", video, "-vf", "scale=480:-2,format=yuv420p,blackdetect=d=0.2:pix_th=0.10", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    kq(abs(lufs - CHUAN_LUFS) <= 1.5, f"âm lượng {lufs:.1f} LUFS (chuẩn {CHUAN_LUFS} ±1,5)")
    den = re.findall(r"black_start:([\d.]+)", r)
    kq(not den, f"không có khung đen ({'giây ' + ', '.join(den) if den else 'sạch'})")


def kiem_luat_chot(da):
    """Video giọng AI: chữ đã gửi lên máy đọc phải đúng luật đã chốt (đọc đúng AI, có cảm xúc). Xem references/da-chot.json."""
    if not doc(da / "doan.json").get("giong"):
        return
    from kiem_chot import kiem_doc, loai_du_an
    gt = "gioi-thieu" in loai_du_an(da).split()
    gui = sorted((da / "giong").glob("*.da-gui.txt"))
    ca_bai = [f for f in gui if "ca-bai" in f.stem]
    if not ca_bai:
        kq(False, "luật đã chốt: không thấy giong/ca-bai.da-gui.txt, giọng không tạo qua tao_giong.py nên chưa qua cổng kiểm")
        return
    sai = []
    for f in gui:
        sai += [f"{f.name}: {l}" for l in kiem_doc(f.read_text(encoding="utf-8"), ca_bai=f in ca_bai, gioi_thieu=gt)]
    kq(not sai, f"luật đã chốt: {len(gui)} bản đã gửi máy đọc" + ("" if not sai else " có lỗi: " + "; ".join(sai)))


def kiem_cong_cu(da):
    """Luật 15: tình trạng hiện tại của từng công cụ đã kiểm ở nguồn gốc (tinh-trang.json); món có sẵn không gọi là thứ phải cài."""
    from kiem_chot import kiem_tinh_trang
    sai = kiem_tinh_trang(da)
    if (da / "tinh-trang.json").exists() or sai:
        kq(not sai, "tình trạng công cụ (có sẵn, plugin chính thức, cài thêm)" + ("" if not sai else ": " + "; ".join(sai)))


def kiem_cau_ket(da):
    """Luật 9 (16/11/2026): lời đọc, phụ đề và chữ trên hình không xin 'comment <TỪ KHÓA>' hay 'comment ... gửi/nhận'."""
    from kiem_chot import kiem_ket_du_an
    sai = kiem_ket_du_an(da)
    kq(not sai, "câu kết không xin bình luận đổi tài liệu (chỉ về bình luận ghim)" + ("" if not sai else ": " + "; ".join(sai)))


def so_list(p):
    return [float(x) for x in p.read_text(encoding="utf-8").split(",") if x] if p.exists() else []


def main():
    global GOI_Y
    da = Path(sys.argv[1])
    video, master = str(da / "render/ra.mp4"), str(da / "render/master.mp4")
    if (da / "goi-y.txt").exists():
        GOI_Y = (da / "goi-y.txt").read_text(encoding="utf-8").strip()
    kiem_luat_chot(da)
    kiem_cong_cu(da)
    kiem_cau_ket(da)
    edl = doc(da / "edl-master.json")
    dj = json.loads((da / "doan.json").read_text(encoding="utf-8")) if (da / "doan.json").exists() else {}
    dn = dj.get("doan", [])
    kiem_lap(master, edl, lien_nguon(dn) if len(dn) == len(edl) else ())
    kiem_du_loi(video, doc(da / "phu-de.json"))
    kiem_khoang_lang(master)
    kiem_mau(video)
    kiem_net(video, master, so_list(da / "moc-net.txt"))
    logo = so_list(da / "moc-logo.txt")
    if len(logo) >= 2:
        kiem_logo(video, logo)
    kiem_am_hinh(video)
    print()
    if loi:
        print(f"✘ CHƯA ĐẠT: {len(loi)} lỗi. Sửa rồi chạy lại, chưa bàn giao.")
        sys.exit(1)
    print("✔ ĐẠT phần máy kiểm. Vẫn phải xem to-soat.jpg bằng mắt trước khi bàn giao.")


if __name__ == "__main__":
    main()
