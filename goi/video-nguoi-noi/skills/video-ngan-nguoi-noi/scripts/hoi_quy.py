"""Kiểm hồi quy: lỗi đã sửa không được quay lại, bản đã duyệt vẫn phải đạt. Chạy sau MỖI lần sửa skill, trước khi đóng gói.
  python hoi_quy.py [--am <file giọng 18-rag/giong/giong-gon.wav> --loi <18-rag/loi.txt>]
Mẫu chữ trong hoi_quy/: dat-*.txt phải đạt, sai-*.txt phải bị bắt. Thêm mẫu mới mỗi khi gặp lỗi mới.
Phần âm thanh (tùy chọn, cần file giọng của dự án): nghi_dau_phay.py không được chèn nghỉ vào giữa "tự tin" (giây 3,1 đến 3,6)."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from kiem_chot import kiem_doc, sua_doc

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("--am")
ap.add_argument("--loi")
ap.add_argument("--kho", help="thư mục mẫu âm thanh hồi quy (giọng người dẫn, không đóng vào gói)")
a = ap.parse_args()
ND = Path(__file__).resolve().parent
hong = 0
for f in sorted((ND / "hoi_quy").glob("*.txt")):
    chu, _ = sua_doc(f.read_text(encoding="utf-8"))
    loi = kiem_doc(chu)
    can_dat = f.name.startswith("dat-")
    dung = (not loi) if can_dat else bool(loi)
    hong += not dung
    print(("✔ " if dung else "✘ ") + f.name + ("" if dung else f": {'đáng lẽ đạt mà bị bắt: ' + '; '.join(loi) if can_dat else 'đáng lẽ bị bắt mà lọt'}"))
# Cách đọc AI phải luôn được thay, kể cả trong câu lẻ
chu, _ = sua_doc("Hỏi AI một câu.")
ok = "Ây‑Ai" in chu and not kiem_doc(chu, ca_bai=False)
hong += not ok
print(("✔ " if ok else "✘ ") + "câu lẻ: AI tự thành Ây‑Ai")
# Video giới thiệu bản thân BNI (loai.txt = gioi-thieu, 24/11/2026): không ép đoạn cuối hỏi + bình luận ghim, vẫn chặn xin comment
bni, _ = sua_doc((ND / "hoi_quy" / "gioi-thieu-bni-34.txt").read_text(encoding="utf-8"))
ok = bool(kiem_doc(bni)) and not kiem_doc(bni, gioi_thieu=True) and bool(kiem_doc(bni + " Comment CÀI mình gửi nhé!", gioi_thieu=True))
hong += not ok
print(("✔ " if ok else "✘ ") + "giới thiệu BNI: không ép câu kết kênh, vẫn chặn xin comment")
# Luật 9 không được đọc nhầm mã cảnh: loai "ket-comment" + clip "TOI3" (ảnh của người dẫn) không phải "comment TOI"
import tempfile, json as _j
from kiem_chot import kiem_ket_du_an as _kk
with tempfile.TemporaryDirectory() as _t:
    Path(_t, "canh.json").write_text(_j.dumps({"canh": [{"loai": "ket-comment", "clip": "TOI3", "nhan": "X", "tieuDe": "Đi nhẹ, chơi trọn", "tuKhoa": "ZALO 09"}]}, ensure_ascii=False), encoding="utf-8")
    ok = not _kk(_t)
    Path(_t, "canh.json").write_text(_j.dumps({"canh": [{"loai": "ket-comment", "clip": "TOI3", "tieuDe": "Comment CÀI mình gửi"}]}, ensure_ascii=False), encoding="utf-8")
    ok = ok and bool(_kk(_t))
hong += not ok
print(("✔ " if ok else "✘ ") + "luật 9: mã cảnh ket-comment + TOI3 không bị bắt nhầm, tiêu đề xin comment vẫn bị chặn")
# Lặp ở chỗ nối (24/11/2026): nói hỏng sát chỗ cắt thì bắt, câu bình thường có "các bạn" ở cả hai đoạn thì không
from nghiem_thu import lap_noi
_g = lambda a, b: a == b
ok = (lap_noi("không gì đảm bảo cho các bạn".split(), "các bạn sẽ tìm được".split(), _g) == 2
      and lap_noi("đảm bảo các bạn ừ".split(), "các bạn sẽ".split(), _g) == 2
      and lap_noi("tìm được việc sau khi các bạn ra trường".split(), "các bạn có đang phải".split(), _g) == 0
      and lap_noi("được nhận lương hàng tháng đến một nghìn hai trăm euro trong suốt".split(), "được nhận lương hàng tháng".split(), _g) == 5)
hong += not ok
print(("✔ " if ok else "✘ ") + "lặp ở chỗ nối: nói hỏng sát chỗ cắt bị bắt, câu bình thường không bị bắt nhầm")
# Nhạc: chỉ bài đã kiểm quyền dùng ngoài YouTube
from kiem_chot import kiem_nhac
ok = not kiem_nhac("future-bass") and bool(kiem_nhac("cong-nghe")) and bool(kiem_nhac(""))
hong += not ok
print(("✔ " if ok else "✘ ") + "kiem_nhac: future-bass đạt, cong-nghe và nhạc mặc định bị chặn")
# Số dòng cảnh: bản đúng của video 19 đạt, bản có mốc lọt ra ngoài và cảnh chồng nhau phải bị bắt
import json
from chung import kiem_so_dong
doc_j = lambda f: json.loads((ND / "hoi_quy" / f).read_text(encoding="utf-8"))["canh"]
ok = not kiem_so_dong(doc_j("canh-dat-19.json"), 24) and len(kiem_so_dong(doc_j("canh-sai-19-moc-ngoai-chong.json"), 24)) >= 2
hong += not ok
print(("✔ " if ok else "✘ ") + "kiem_so_dong: cảnh đúng đạt, mốc ngoài cảnh và cảnh chồng nhau bị bắt")
if a.am and a.loi:
    ra = ND / "hoi_quy" / "_tam.wav"
    out = subprocess.run([sys.executable, str(ND / "nghi_dau_phay.py"), a.am, a.loi, str(ra)], capture_output=True, text=True, encoding="utf-8").stdout
    ra.unlink(missing_ok=True)
    m = re.search(r"chỗ: (\[.*?\])", out)
    cho = [float(x) for x in re.findall(r"\(([\d.]+),", m.group(1))] if m else []
    ok = not any(3.1 <= t <= 3.6 for t in cho)
    hong += not ok
    print(("✔ " if ok else "✘ ") + f"nghi_dau_phay không chèn giữa 'tự tin' (chèn ở {cho})")
if a.kho:
    # nghe_lai_giong.py: bản thật không được báo sai, bản làm hỏng phải bị bắt đúng chỗ (17-linkedin)
    K = Path(a.kho)
    chay = lambda f: subprocess.run([sys.executable, str(ND / "nghe_lai_giong.py"), str(K / f), str(K / "17-linkedin-doc-tts.txt")],
                                    capture_output=True, text=True, encoding="utf-8").stdout
    o = chay("17-linkedin-dat.wav")
    ok = "không có câu dính" in o and "0,7 giây: không" in o
    hong += not ok
    print(("✔ " if ok else "✘ ") + "nghe_lai_giong: bản đạt không bị báo dính hay lặng dài")
    o = chay("17-linkedin-hong-dinh-9.5-lang-30.wav")
    ok = "câu dính ở 9.5s" in o and "(1.2, 30.0)" in o
    hong += not ok
    print(("✔ " if ok else "✘ ") + "nghe_lai_giong: bản hỏng bị bắt câu dính 9,5 giây và lặng 1,2 giây ở giây 30")
    # thay_doan_giong.py phải cắt giữa khe lặng thật sau chữ "luôn" (34,15 đến 34,45), cách cũ cắt ở 33,92 sót đuôi chữ
    ra = K / "_tam-ghep.wav"
    o = subprocess.run([sys.executable, str(ND / "thay_doan_giong.py"), str(K / "19-4skill-giong-truoc-ghep.wav"), str(K / "19-4skill-doan-moi.wav"),
                        "--tu", "Còn đỉnh nhất là", "--sau", "Hỏi chủ đề gì", "--ra", str(ra)], capture_output=True, text=True, encoding="utf-8").stdout
    ra.unlink(missing_ok=True)
    m = re.search(r"đến ([\d.]+)s", o)
    ok = bool(m) and 34.15 <= float(m.group(1)) <= 34.45
    hong += not ok
    print(("✔ " if ok else "✘ ") + f"thay_doan_giong: cắt cuối trong khe lặng thật ({m.group(1) if m else 'không đọc được'} giây)")

# Gắn nhận diện (gan_nhan_dien.py): dựng video giả, kiểm đủ phần, đúng độ dài, có watermark, intro bị bỏ khi video ngắn
def thu_nhan_dien():
    import shutil
    import tempfile
    from gan_nhan_dien import do_dai, gan
    T = Path(tempfile.mkdtemp(prefix="hq-nhan-dien-"))
    try:
        ff = lambda *x: subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *x], check=True)
        (T / "render").mkdir()
        vid = lambda f, giay, mau, hz: ff("-f", "lavfi", "-i", f"color=c={mau}:s=1080x1920:r=30:d={giay}", "-f", "lavfi", "-i", f"sine=frequency={hz}:duration={giay}",
                                          "-c:v", "libx264", "-c:a", "aac", "-shortest", str(f))
        vid(T / "render" / "ra.mp4", 3, "white", 440)
        vid(T / "intro.mp4", 1, "blue", 660)
        vid(T / "outro.mp4", 1.5, "green", 880)
        ff("-f", "lavfi", "-i", "color=c=red:s=600x224", "-frames:v", "1", str(T / "wm.png"))
        h = {"_goc": str(T), "nhanDien": {"watermark": "wm.png", "intro": "intro.mp4", "outro": "outro.mp4", "introKhiDaiHon": 2}}
        ra = gan(T, h)
        ok1 = abs(do_dai(ra) - 5.5) < 0.25
        px = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2.5", "-i", str(ra), "-frames:v", "1", "-vf", "crop=20:20:890:1700", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            capture_output=True).stdout
        ok2 = len(px) == 1200 and px[0] > 200 and px[1] < 60  # góc dưới phải của phần chính phải là watermark đỏ
        h["nhanDien"]["introKhiDaiHon"] = 60
        ok3 = abs(do_dai(gan(T, h)) - 4.5) < 0.25
        return [("gan_nhan_dien: intro + video + outro đủ 5,5 giây", ok1), ("gan_nhan_dien: có watermark ở góc dưới phải", ok2),
                ("gan_nhan_dien: video ngắn hơn introKhiDaiHon thì bỏ intro", ok3)]
    finally:
        shutil.rmtree(T, ignore_errors=True)


for ten, ok in thu_nhan_dien():
    hong += not ok
    print(("✔ " if ok else "✘ ") + ten)


# Dò trùng chủ đề (tim_trung.py): khớp nguyên từ, không dấu, có trạng thái bài đăng
def thu_tim_trung():
    import shutil
    import tempfile
    T = Path(tempfile.mkdtemp(prefix="hq-trung-"))
    try:
        (T / "du-an" / "18-rag").mkdir(parents=True)
        (T / "du-an" / "18-rag" / "loi.txt").write_text("RAG là cách cho AI đọc tài liệu", encoding="utf-8")
        (T / "du-an" / "19-luu-tru").mkdir(parents=True)
        (T / "du-an" / "19-luu-tru" / "loi.txt").write_text("Object storage, kéo thả drag and drop", encoding="utf-8")
        (T / "BAI-DANG" / "3-da-dang" / "01-rag").mkdir(parents=True)
        chay = lambda *k: subprocess.run([sys.executable, str(ND / "tim_trung.py"), str(T), *k], capture_output=True, text=True, encoding="utf-8")
        a, b = chay("RAG"), chay("Notebook LM")
        (T / "du-an" / "21-story-cutter").mkdir()
        (T / "du-an" / "21-story-cutter" / "content.md").write_text("# Plugin AI cắt thô video\n", encoding="utf-8")
        g = subprocess.run([sys.executable, str(ND / "ghi_so_video.py"), str(T), str(T / "du-an" / "21-story-cutter"), "--tu-khoa", "Story Cutter; Premiere Pro"],
                           capture_output=True, text=True, encoding="utf-8")
        (T / "du-an" / "21-story-cutter" / "content.md").unlink()  # chỉ còn sổ: phải bắt được nhờ sổ
        c = chay("làm video giới thiệu story cutter cho dân dựng")
        subprocess.run([sys.executable, str(ND / "ghi_so_video.py"), str(T), str(T / "du-an" / "18-rag"), "--chu-de", "Claude hết token", "--tu-khoa", "Claude; hết token"], capture_output=True)
        d = chay("Biến Claude thành team 6 dev", "Frontend Design")
        return [("tim_trung: bắt video RAG đã đăng, không khớp nhầm storage, drag", a.returncode == 1 and "ĐÃ ĐĂNG" in a.stdout and "19-luu-tru" not in a.stdout),
                ("tim_trung: chủ đề mới thì báo chưa có", b.returncode == 0),
                ("ghi_so_video + tim_trung: ghi sổ xong, gõ cả câu yêu cầu vẫn bắt được từ sổ", g.returncode == 0 and c.returncode == 1 and "[sổ video] 21-story-cutter" in c.stdout),
                ("tim_trung: từ quá chung như Claude không làm khớp nhầm", d.returncode == 0)]
    finally:
        shutil.rmtree(T, ignore_errors=True)


for ten, ok in thu_tim_trung():
    hong += not ok
    print(("✔ " if ok else "✘ ") + ten)


# Luật 15, tình trạng công cụ (22-team-6-dev): bản 1 gọi /code-review, /security-review có sẵn là thứ phải cài thì bị chặn; bản 2 đạt;
# thiếu tinh-trang.json thì bị chặn. ngayKiem trong mẫu được thay bằng hôm nay để mẫu không tự hỏng theo thời gian.
def thu_cong_cu():
    import datetime
    import json as js
    import shutil
    import tempfile
    from kiem_chot import kiem_tinh_trang
    kq = []
    for ten, can_dat in (("cong-cu-dat-22v2", True), ("cong-cu-sai-22v1", False)):
        T = Path(tempfile.mkdtemp(prefix="hq-cc-"))
        try:
            for f in (ND / "hoi_quy" / ten).iterdir():
                shutil.copy(f, T / f.name)
            d = js.loads((T / "tinh-trang.json").read_text(encoding="utf-8"))
            d["ngayKiem"] = datetime.date.today().strftime("%d/%m/%Y")
            (T / "tinh-trang.json").write_text(js.dumps(d, ensure_ascii=False), encoding="utf-8")
            sai = kiem_tinh_trang(T)
            kq.append((f"kiem_tinh_trang: {ten} {'đạt' if can_dat else 'bị chặn'}", (not sai) if can_dat else bool(sai)))
            (T / "tinh-trang.json").unlink()
            kq.append((f"kiem_tinh_trang: {ten} thiếu tinh-trang.json thì bị chặn", bool(kiem_tinh_trang(T)))) if can_dat else None
        finally:
            shutil.rmtree(T, ignore_errors=True)
    return kq


for ten, ok in thu_cong_cu():
    hong += not ok
    print(("✔ " if ok else "✘ ") + ten)


# Cổng vế ngắn (13/11/2026): bản đọc rời của 23 bản 3 (1,27 giây mỗi hơi) bị chặn vì vế, bản đạt 1,88 qua
from kiem_chot import kiem_ve
ok = bool(kiem_ve((ND / "hoi_quy" / "sai-23-ve-ngan.txt").read_text(encoding="utf-8"))[0]) and not kiem_ve((ND / "hoi_quy" / "dat-23-skill-v2.txt").read_text(encoding="utf-8"))[0]
hong += not ok
print(("✔ " if ok else "✘ ") + "kiem_ve: bản vế ngắn của 23 bị chặn, bản đạt qua")


# Luật 9 (16/11/2026): câu kết không xin "Comment CÀI, mình gửi..." ở phụ đề và chữ trên hình; khung GHIM thì qua
def thu_cau_ket():
    import json as js
    import shutil
    import tempfile
    from kiem_chot import kiem_ket_du_an
    T = Path(tempfile.mkdtemp(prefix="hq-ket-"))
    try:
        (T / "loi.txt").write_text("Anh chị muốn AI tra tài liệu nào đầu tiên?\nComment CÀI\nmình gửi hướng dẫn", encoding="utf-8")
        (T / "canh.json").write_text(js.dumps({"canh": [{"loai": "ket-comment", "tieuDe": "Tra tài liệu nào?", "tuKhoa": "CÀI"}]}), encoding="utf-8")
        sai = kiem_ket_du_an(T)
        (T / "loi.txt").write_text("Anh chị muốn AI tra tài liệu nào đầu tiên?\nHướng dẫn cài từng bước\nmình để sẵn ở bình luận ghim nhé!", encoding="utf-8")
        (T / "canh.json").write_text(js.dumps({"canh": [{"loai": "ket-comment", "tieuDe": "Tra tài liệu nào?", "tuKhoa": "XEM BÌNH LUẬN GHIM"}]}), encoding="utf-8")
        return bool(sai) and not kiem_ket_du_an(T)
    finally:
        shutil.rmtree(T, ignore_errors=True)


ok = thu_cau_ket()
hong += not ok
print(("✔ " if ok else "✘ ") + "kiem_ket_du_an: phụ đề 'Comment CÀI ... gửi' bị chặn, câu chỉ về bình luận ghim qua")


# Cảnh kết (21/11/2026): trùng clip kết của 5 video gần nhất thì chặn, clip chưa dùng thì qua, choLapCanhKet thì qua
def thu_canh_ket():
    import json as js
    import os
    import shutil
    import tempfile
    from kiem_chot import kiem_canh_ket
    T = Path(tempfile.mkdtemp(prefix="hq-canhket-"))
    try:
        def du_an(ten, clip, gio=None, **them):
            d = T / ten
            (d / "render").mkdir(parents=True)
            (d / "canh.json").write_text(js.dumps({"canh": [{"loai": "ket-comment", "clip": clip, **them}]}), encoding="utf-8")
            if gio is not None:
                (d / "render" / "thanh-pham.mp4").write_bytes(b"x")
                os.utime(d / "render" / "thanh-pham.mp4", (gio, gio))
            return d
        for i, m in enumerate(["P02", "P04", "P08", "P12", "P01", "P02"]):
            du_an(f"{i:02d}-cu", m, 1_000_000 + i)
        # 00-cu (P02) cũ nhất bị đẩy khỏi 5 gần nhất, nhưng 05-cu cũng P02 nên P02 vẫn bị chặn
        lap = kiem_canh_ket(du_an("09-lap", "P02"))[0]
        moi = kiem_canh_ket(du_an("10-moi", "P38"))[0]
        cho = kiem_canh_ket(du_an("11-cho", "P02", choLapCanhKet=True))[0]
        return bool(lap) and "P38" not in lap[0].split("trùng")[0] and not moi and not cho
    finally:
        shutil.rmtree(T, ignore_errors=True)


ok = thu_canh_ket()
hong += not ok
print(("✔ " if ok else "✘ ") + "kiem_canh_ket: clip kết trùng 5 video gần nhất bị chặn, clip mới và choLapCanhKet qua")


# Cổng đo tiêu đề (13/11/2026): đo bằng phông thật; mất mạng thì bỏ qua bài này, không tính hỏng
def thu_tieu_de():
    from kiem_chu import kiem_tieu_de
    tran = [{"loai": "flow-chu", "nen": True, "tren": "MÀ KHÔNG ĐƯỢC GỌI?"}, {"loai": "danh-sach-buoc", "tren": "Không đọc hết một lúc"}]
    vua = [{"loai": "flow-chu", "nen": True, "tren": "SAO KHÔNG CHẬM?"}, {"loai": "danh-sach-buoc", "tren": "Có sẵn trong Claude"}]
    loi, nhac = kiem_tieu_de(tran + vua)
    if any("chưa đo được" in n for n in nhac):
        return None
    return len(loi) == 2 and all("«MÀ KHÔNG" in l or "«Không đọc" in l for l in loi)


kq = thu_tieu_de()
if kq is None:
    print("⚠ kiem_chu: chưa đo được phông (mất mạng?), bỏ qua")
else:
    hong += not kq
    print(("✔ " if kq else "✘ ") + "kiem_chu: 2 tiêu đề từng tràn bị bắt, 2 tiêu đề vừa qua")


# Bản dự phòng HyperFrames (skill video-ngan-hyperframes) chạy MoHinh.tsx qua shim: chỉ có các hàm dưới đây.
# Dùng thêm hàm Remotion khác thì phải thêm vào engine-hf/shim/remotion.tsx của skill đó rồi sửa danh sách này.
SHIM_CO = {"AbsoluteFill", "Img", "OffthreadVideo", "Sequence", "interpolate", "spring", "staticFile", "useCurrentFrame"}
src = (ND.parent / "engine" / "src" / "MoHinh.tsx").read_text(encoding="utf-8")
dung_ham = {x.strip() for m in re.findall(r"import\s*\{([^}]*)\}\s*from\s*'remotion'", src) for x in m.split(",") if x.strip()}
thua = dung_ham - SHIM_CO
hong += bool(thua)
print(("✔ " if not thua else "✘ ") + "MoHinh.tsx chỉ dùng hàm Remotion mà bản dự phòng HyperFrames có" + (f" (thiếu trong shim: {', '.join(sorted(thua))})" if thua else ""))
goi_khac = set(re.findall(r"from\s*'(@remotion/[^']+)'", src)) - {"@remotion/google-fonts/BeVietnamPro"}
hong += bool(goi_khac)
print(("✔ " if not goi_khac else "✘ ") + "MoHinh.tsx không dùng gói @remotion khác ngoài font" + (f": {', '.join(sorted(goi_khac))}" if goi_khac else ""))


# edit.py (thử máy học viên 24/11/2026): chữ lặp liền bị bỏ, láy một chữ giữ; chọn câu bằng chon.json thì thẻ tiêu đề hiện
# đúng dòng nói chữ tiêu đề, cảnh clip kho ≤ 7,5 giây, cảnh nối liền, mốc tự rải
def thu_edit():
    from edit import bo_lap_lien, lap_tu_chon, tach_cau
    lien_tieng = [{"word": " a", "start": i * 0.4, "end": i * 0.4 + 0.4} for i in range(30)]  # nói liền 12 giây, khe 0
    phan = tach_cau([lien_tieng], 8.0)
    ok0 = len(phan) == 2 and all(p[-1]["end"] - p[0]["start"] >= 3 for p in phan)
    ok1 = bo_lap_lien("agent là nhân viên nhân viên mà có thể".split()) == (2, 4) and bo_lap_lien("hi vọng rằng cái hi vọng rằng".split()) == (0, 4) and bo_lap_lien("kiểm tra email kiểm tra chứng từ".split()) is None
    ok2 = bo_lap_lien("đi từ từ thôi nhé".split()) is None

    def cau(so, bd, chu_):
        ws = [{"word": " " + t, "start": round(bd + i * 0.4, 2), "end": round(bd + i * 0.4 + 0.3, 2)} for i, t in enumerate(chu_.split())]
        return {"so": so, "bd": ws[0]["start"], "kt": ws[-1]["end"], "chu": chu_, "w": ws}
    cj = {"nguon": "x.mp4", "lang": [], "cau": [
        cau(1, 0.0, "xin chào mọi người hôm nay mình chia sẻ về cái sức mạnh của AI agent"),
        cau(2, 8.0, "agent thì chúng ta có thể hiểu đơn giản nó là nhân viên có thể hỗ trợ chúng ta làm việc mỗi ngày rất nhanh và chính xác hơn nhiều"),
        cau(3, 20.0, "nó làm kế toán thuế nhân sự và nghiên cứu thị trường cho mình"),
        cau(4, 26.0, "video của mình tạm đến đây thôi cảm ơn mọi người")]}
    chon = {"tieuDe": "SỨC MẠNH|AI AGENT", "doan": [
        {"cau": 1}, {"cau": 2, "minhHoa": {"loai": "flow-chu", "ten": "M01", "tren": "AGENT", "duoi": "NHÂN VIÊN AI"}},
        {"cau": 3, "minhHoa": {"loai": "danh-sach-buoc", "tren": "Agent làm gì", "buoc": [{"ten": "Kế toán"}, {"ten": "Nhân sự"}]}},
        {"cau": 4, "chu": "cảm ơn mọi người"}], "sua": {"kế toán thuế": "kế toán, thuế"}}
    doan, dong, canh, tg = lap_tu_chon(cj, chon)[:4]
    lien = all(canh[i]["den"] == canh[i + 1]["tu"] for i in range(len(canh) - 1)) and canh[-1]["den"] == "het"
    tieu = "sức mạnh" in dong[canh[0]["at"] - 1].lower()
    fc = next(c for c in canh if c["loai"] == "flow-chu")
    x = chon["doan"][1]  # câu 2 dài 10 giây: cảnh clip phải dừng trước 7,5 giây, phần còn lại về người nói
    clip_ngan = fc["den"] <= x["_dong"][1] and x["_bat"][fc["den"] - x["_dong"][0]] - x["_bat"][fc["tu"] - x["_dong"][0]] < 7.5
    ds = next(c for c in canh if c["loai"] == "danh-sach-buoc")
    cuoi = dong[-1] == "cảm ơn mọi người" and len(doan) == 3 and all(doan[i][2] < doan[i + 1][1] for i in range(len(doan) - 1)) and "nó làm kế toán," in dong
    if not (ok0 and ok1 and ok2 and lien and tieu and clip_ngan and len(ds.get("moc", [])) == 2 and 0.5 < ds["moc"][0] < 0.8 and cuoi):
        print("  ", ok1, ok2, lien, tieu, clip_ngan, ds.get("moc"), cuoi, dong, canh)
        return False
    return True


try:
    from nghiem_thu import lien_nguon
    # đoạn 0–1 liền nhau trong file gốc (liệt kê "kiểm tra email, | kiểm tra chứng từ") được miễn; đoạn 1–2 cách 60 giây thì vẫn bắt
    ok_ln = lien_nguon([[0, 67.4, 71.5], [0, 71.86, 74.2], [0, 135.0, 136.0]]) == {0}
    hong += not ok_ln
    print(("✔ " if ok_ln else "✘ ") + "nghiem_thu: lặp 2–3 chữ giữa hai đoạn liền nhau trong file gốc không bị tính, đoạn xa vẫn bị bắt")
    ok = thu_edit()
except SystemExit as e:
    ok = False
    print("  ", e)
hong += not ok
print(("✔ " if ok else "✘ ") + "edit.py: bỏ chữ lặp liền, chọn câu theo chon.json, thẻ tiêu đề đúng dòng, clip ≤ 7,5 giây, mốc tự rải")
print()
if hong:
    sys.exit(f"✘ {hong} mục hồi quy hỏng. Không đóng gói.")
print("✔ Hồi quy đạt.")
