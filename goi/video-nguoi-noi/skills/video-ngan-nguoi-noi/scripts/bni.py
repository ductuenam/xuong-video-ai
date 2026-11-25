"""Video giới thiệu bản thân 30 giây theo khung BNI, chạy một lệnh. Bản 2.1 (25/11/2026): khung "tôi là ai → làm gì, cho ai →
vì sao tin → nhờ giới thiệu ai → câu dễ nhớ + tên", lời theo từng người.

  python bni.py "<dự án>"

Đọc references/bni-cong-thuc.md trước khi viết lời. Trong thư mục dự án (<Xưởng>/du-an/<yyyy-mm-dd>_bni-<tên>/) cần có:
  doc-tts.txt  lời đọc một đoạn, 95–110 chữ, theo giọng người đó (không ép dấu chấm than)
  loi.txt      phụ đề cắt từ đúng chữ của doc-tts.txt, mỗi dòng ≤ 28 ký tự
  bni.json     {"phan": [số dòng loi.txt của 5 nhịp: tôi là ai, làm gì cho ai, vì sao tin, nhờ giới thiệu ai, câu dễ nhớ + tên],
                "mo": ["TÊN", "THƯƠNG HIỆU"],
                "chuDe": {"tren": "<dòng trên>", "duoi": "<dòng dưới>", "viec": [["ý", "phụ"], ...] 0–3},
                "bangChung": ["DÒNG 1", "DÒNG 2"],
                "xin": {"tren": "<dòng trên>", "duoi": "<dòng dưới>", "dong": [["ai", "dấu hiệu"], ...] 0–3},
                "ghiNho": "<chữ thẻ kết ≤ 18 ký tự>", "lienHe": "<ít nhất 2 chữ, vd ZALO 09xx...>",
                "nganh": ["tu-khoa-nghe", ...], "tamTrang": "vui|am-ap|cam-xuc|chuyen-nghiep|manh-me",
                "giongAI": {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural"},   (tùy chọn)
                "canh": {"mo", "chu", "bang", "xin", "ket"}, "nhac": "NH000x",       (tùy chọn, đè lựa chọn tự động)
                "giongTuQuay": "<file trong anh-video-cua-toi/>",                      (tùy chọn)
                "soBni": {"ten", "chuDe", "xin", "cauDeNho", "giong", "mang": [...]}}
  "viec" hoặc "dong" rỗng thì thẻ đó thành cảnh có chữ. Khóa cũ "giup", "khachTot" vẫn đọc được.

Script tự làm:
  0. Kiểm trước (✘ là dừng): dòng phụ đề dài, ghiNho dài, số chữ, lời lệch phụ đề, lời trùng tuần cũ (sổ BNI), chép nguyên văn ví dụ.
  1. Ảnh, video của người dẫn trong <Xưởng>/anh-video-cua-toi/ làm cảnh (tối đa 5, theo thứ tự tên tệp: mở, làm gì,
     bằng chứng, nhờ giới thiệu, kết; đặt tên 1-…, 2-… để định thứ tự). Không có thì chế độ không mặt:
     cảnh kho khớp "nganh", rồi cảnh hợp mọi nghề, cuối cùng nền màu tự tạo.
  2. loai.txt, nhạc theo tamTrang (đổi bài so với tuần trước), kenh-rieng.json (tên kênh, giọng riêng cho video này).
  3. Giọng (giongTuQuay hoặc tao_giong.py), cắt nghỉ, chèn nghỉ dấu phẩy; giọng phải dài 22–30 giây.
  4. canh.json rồi dung.py --het. Xong chép sang <Xưởng>/thanh-pham/ và ghi sổ <Xưởng>/mau-cua-toi/bni/so-bni.json.
"""
import csv
import datetime
import difflib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

from chung import XUONG, doc, duong_dan, ghi, ho_so, kho_canh

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ND = Path(__file__).resolve().parent
CONG_THUC = ND.parent / "references" / "bni-cong-thuc.md"
ANH = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}
AM = {".m4a", ".mp3", ".wav", ".aac"}
# Cảnh hợp mọi nghề khi không khớp được ngành: nền màu dịu, cảnh đời thường đẹp. Mã nào không có trên máy thì bỏ qua.
UU_TIEN = {
    "mo": ["CA0116", "CA0182", "CA0110", "CA0175"],
    "chu": ["CA0110", "CA0116", "CA0175", "CA0113"],
    "bang": ["CA0110", "CA0116", "CA0113", "CA0175"],
    "xin": ["CA0175", "CA0116", "CA0110", "CA0113"],
    "ket": ["CA0116", "CA0110", "CA0175", "CA0113"],
}
# Cảnh gắn một thành phố (Hồ Gươm, phố cổ, Landmark 81...): chỉ dùng khi "nganh" có tên thành phố đó (thử 25/11/2026: spa Đà Nẵng
# suýt lấy cảnh Hồ Gươm). Dò trong mô tả và từ khóa cảnh.
DIA_DANH = ("ha-noi", "sai-gon", "hoi-an", "landmark", "ho-guom", "long-bien", "pho-co")
HOAT_HINH = ("tí hon", "đất sét", "hoạt hình", "cartoon", "đồ chơi")
# Nền màu dịu tự tạo khi kho cảnh trống: kem cam, xanh ngọc nhạt, tím hồng nhạt
NEN_MEM = [("0xF6D9C4", "0xE9B7A0", "0xF3E6D8"), ("0xCFE8E4", "0xA9D3CF", "0xE6F2EF"), ("0xE8DDF0", "0xD6C3E6", "0xF4EDF7")]
# Giọng bài -> từ khóa tâm trạng trong cột tam_trang của tai-nguyen/nhac/chi-muc.csv
TAM_TRANG = {
    "vui": ["vui", "tre-trung", "thoai-mai"],
    "am-ap": ["thoai-mai", "hy-vong", "cam-xuc"],
    "cam-xuc": ["cam-xuc", "truyen-cam-hung", "hy-vong"],
    "chuyen-nghiep": ["tu-tin", "truyen-cam-hung", "hy-vong"],
    "manh-me": ["manh-me", "tu-tin", "kich-thich"],
}
DONG_TOI_DA, GHI_NHO_TOI_DA = 28, 18
CHU_IT, CHU_NHIEU = 85, 118          # số chữ đọc chấp nhận (khuyên 95–110; giọng miễn phí đo 25/11/2026 khoảng 3,5–4 chữ/giây kể cả nghỉ)
GIAY_IT, GIAY_NHIEU = 22.0, 30.0     # độ dài giọng sau khi chèn nghỉ
TRUNG_TUAN_CU = 0.60                 # lời giống một tuần cũ từ mức này là chặn
CHUOI_CHEP = 8                       # trùng nguyên 8 chữ liền với tệp công thức là chép ví dụ


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


def khong_dau(s):
    s = unicodedata.normalize("NFD", str(s).lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def chu(t):
    return re.findall(r"\w+", str(t).lower())


def giay(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def clip_toi(f, ra):
    """Ảnh hoặc video của người dẫn thành clip dọc 1080x1920, 8 giây, không tiếng."""
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if f.suffix.lower() in ANH:
        # Nền là chính ảnh đó làm mờ. Ảnh dọc: giữ trọn, thu vào khung 1080x1600 sát đáy (chừa 320 px phía trên cho ô tên).
        # Ảnh ngang (sân khấu, lớp học): cao 1000, cắt giữa rộng 1080, đặt ở y 330 (giữa ô tên và phụ đề ~1420); trước đây ảnh ngang
        # thu nhỏ sát đáy, nằm đè dưới phụ đề (thử ảnh Founder 25/11/2026). Rồi phóng chậm 1,00 -> 1,06 trong 8 giây.
        import cv2
        import numpy as np
        a = cv2.imdecode(np.fromfile(str(f), "u1"), cv2.IMREAD_UNCHANGED)
        if a is not None and a.ndim == 3 and a.shape[2] == 4:
            # Ảnh chân dung tách nền (PNG trong suốt): đặt lên nền kem sáng, không thì nền mờ thành màu đen
            al = a[:, :, 3:4].astype("f4") / 255
            phang = (a[:, :, :3] * al + np.array([236, 242, 246], "f4") * (1 - al)).astype("u1")
            f = ra.with_suffix(".phang.jpg")
            cv2.imencode(".jpg", phang, [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tofile(str(f))
        ngang = a is not None and a.shape[1] > a.shape[0] * 1.1
        fg, y, neo = (("scale=-2:1000,crop='min(iw,1080)':1000", "330", "ih/2-(ih/zoom/2)") if ngang else
                      ("scale=1080:1600:force_original_aspect_ratio=decrease", "H-h", "ih-(ih/zoom)"))
        nen = ra.with_suffix(".nen.png")
        ff("-i", f, "-filter_complex",
           "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2[bg];"
           f"[0]{fg}[fg];[bg][fg]overlay=(W-w)/2:{y}",
           "-frames:v", 1, nen)
        ff("-loop", "1", "-i", nen, "-t", 8, "-vf",
           f"scale=2160:3840,zoompan=z='1+0.06*on/200':x='iw/2-(iw/zoom/2)':y='{neo}':d=200:s=1080x1920:fps=25,format=yuv420p",
           "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 18, ra)
        nen.unlink(missing_ok=True)
        ra.with_suffix(".phang.jpg").unlink(missing_ok=True)
    else:
        ff("-i", f, "-t", 8, "-vf", vf + ",fps=25,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 18, ra)


def doc_so(f):
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except (OSError, ValueError):
        return {}


def kiem_truoc(da, b, dong, loi_doc, so):
    """Trả về (lỗi chặn, nhắc). Chặn trước khi tốn thời gian tạo giọng và dựng."""
    loi, nhac = [], []
    dai = [x for x in dong if len(x) > DONG_TOI_DA]
    if dai:
        loi.append(f"dòng phụ đề dài hơn {DONG_TOI_DA} ký tự sẽ rớt chữ, tách đôi trong loi.txt (và sửa 'phan'): " + " | ".join(dai))
    if len(b.get("ghiNho", "")) > GHI_NHO_TOI_DA:
        loi.append(f"ghiNho {len(b['ghiNho'])} ký tự, thẻ kết sẽ rớt chữ: rút còn ≤ {GHI_NHO_TOI_DA} (câu đọc vẫn có thể dài hơn)")
    for khoa in ("mo", "bangChung"):
        if not b.get(khoa) or len(b[khoa]) < 2:
            loi.append(f"bni.json thiếu '{khoa}' (2 dòng)")
    if len((b.get("lienHe") or "").split()) < 2:
        loi.append("lienHe cần từ 2 chữ trở lên (vd 'ZALO 0900 000 000'), một chữ thì thẻ kết hiện 'XEM BÌNH LUẬN GHIM'")
    n = len(chu(loi_doc))
    if n < CHU_IT:
        loi.append(f"lời chỉ {n} chữ, đọc ra dưới 23 giây: thêm khoảng {100 - n} chữ (chi tiết câu chuyện hoặc dấu hiệu nhận ra người cần giới thiệu)")
    elif n > CHU_NHIEU:
        loi.append(f"lời {n} chữ, đọc ra quá 30 giây: bớt khoảng {n - 105} chữ")
    giong_nhau = difflib.SequenceMatcher(None, chu(" ".join(dong)), chu(loi_doc)).ratio()
    if giong_nhau < 0.85:
        loi.append(f"doc-tts.txt lệch chữ với loi.txt (giống {giong_nhau:.0%}, cần ≥ 85%): viết doc-tts.txt trước rồi cắt loi.txt từ đúng những chữ đó")
    # Nghe một lần phải hiểu: câu vụn, câu kiểu tiêu đề làm bài khó nghe (Founder chấm 3 bài thử 25/11/2026). Chỉ nhắc, không chặn.
    cau = [c for c in re.split(r"[.!?]+", loi_doc) if chu(c)]
    vun = [c.strip() for c in cau[:-2] if len(chu(c)) < 5]
    if len(vun) >= 2:
        nhac.append("câu vụn khó nghe: " + " | ".join(vun) + ". Gộp thành câu đủ ý 10–22 chữ (bni-cong-thuc.md mục 1b)")
    if ":" in loi_doc:
        nhac.append("lời có dấu hai chấm, nghe như đọc tiêu đề: viết thành câu nói thường (mục 1b)")
    phan = b.get("phan", [])
    if len(phan) != 5 or sum(phan) != len(dong):
        loi.append(f"bni.json phan {phan} (tổng {sum(phan)}) phải đủ 5 nhịp và bằng số dòng loi.txt ({len(dong)})")
    else:
        # Tên phải được nói ngay nhịp 1: người lạ cần biết ai đang nói trước khi nghe gì khác
        ten = [x for x in chu((b.get("mo") or [""])[0]) if len(x) > 1]
        if ten and not set(ten) & set(chu(" ".join(dong[:phan[0]]))):
            loi.append(f"nhịp 1 ({phan[0]} dòng đầu loi.txt) chưa nói tên '{b['mo'][0]}': câu đầu phải cho biết ai đang nói")
        # Ý trên thẻ phải có chữ được NÓI trong đúng nhịp đó, không thì thẻ sáng sớm theo mốc chia đều
        # (chấm 25/11/2026: thẻ "NGƯNG KEM, THẢO MỘC" của chuyện bị đặt vào nhịp chủ đề, sáng sớm 5 giây)
        dau = [sum(phan[:i]) for i in range(6)]
        for so_nhip, khoa, ds in ((2, "chuDe", "viec"), (4, "xin", "dong")):
            doan = " ".join(dong[dau[so_nhip - 1]:dau[so_nhip]]).lower()
            for d in ((b.get(khoa) or {}).get(ds) or [])[:3]:
                w = [x for x in chu(d[0]) if len(x) > 1 and x not in {"và", "cho", "các", "có"}]
                if d and d[0] and not any(x in chu(doan) for x in w):
                    loi.append(f"thẻ '{d[0]}' ({khoa}.{ds}) không có chữ nào trong lời của nhịp {so_nhip}: dùng chữ được nói ở nhịp đó, "
                               "hoặc để danh sách rỗng cho thẻ thành cảnh có chữ")
    # Chép ví dụ: trùng nguyên một chuỗi 8 chữ với tệp công thức
    if CONG_THUC.exists():
        mau = chu(CONG_THUC.read_text(encoding="utf-8"))
        bo = {tuple(mau[i:i + CHUOI_CHEP]) for i in range(len(mau) - CHUOI_CHEP + 1)}
        w = chu(loi_doc)
        trung = next((" ".join(w[i:i + CHUOI_CHEP]) for i in range(len(w) - CHUOI_CHEP + 1) if tuple(w[i:i + CHUOI_CHEP]) in bo), None)
        if trung:
            loi.append(f"lời chép nguyên văn từ bni-cong-thuc.md («{trung}»): viết lại bằng chuyện và chữ của chính người này")
    # Trùng tuần cũ: bỏ chữ của câu dễ nhớ và tên (hai phần này được phép lặp) rồi so
    bo_qua = set(chu(so.get("cauDeNho", "")) + chu(so.get("ten", "")) + chu(b.get("mo", [""])[0]) + chu((b.get("soBni") or {}).get("cauDeNho", "")))
    loc = lambda t: [x for x in chu(t) if x not in bo_qua]  # noqa: E731
    cu = [(t.get("ngay", "?") + " " + t.get("duAn", ""), t.get("loi", "")) for t in so.get("tuan", []) if t.get("duAn") != da.name]
    da_co = {t.get("duAn") for t in so.get("tuan", [])}
    if XUONG and (XUONG / "du-an").exists():  # dự án BNI cũ chưa có trong sổ (dựng bằng bản cũ)
        cu += [(f.parent.name, f.read_text(encoding="utf-8")) for f in (XUONG / "du-an").glob("*bni*/doc-tts.txt")
               if f.parent != da and f.parent.name not in da_co]
    nay = loc(loi_doc)
    for ten, t in cu:
        r = difflib.SequenceMatcher(None, nay, loc(t)).ratio()
        if r >= TRUNG_TUAN_CU:
            loi.append(f"lời giống {r:.0%} bài {ten}: tuần này phải khác chủ đề, khác câu chuyện, khác lời xin (chỉ giữ câu dễ nhớ và tên)")
            break
    cd = khong_dau((b.get("soBni") or {}).get("chuDe", ""))
    if cd and any(khong_dau(t.get("chuDe", "")) == cd for t in so.get("tuan", [])[-4:] if t.get("duAn") != da.name):
        nhac.append("chủ đề này đã nói trong 4 tuần gần nhất; nên chọn mảng khác trong sổ BNI")
    # Không đo độ dài vế cho BNI: câu ngắn là giọng của người đó (Founder duyệt 25/11/2026; thử 3 bài đều < 9 chữ/vế mà vẫn ĐẠT).
    return loi, nhac


def chon_nhac(b, so):
    if b.get("nhac"):
        return b["nhac"]
    from kiem_chot import kiem_nhac
    f = XUONG / "tai-nguyen" / "nhac" / "chi-muc.csv"
    if not f.exists():
        return "NH0001"
    ds = [r for r in csv.DictReader(f.open(encoding="utf-8-sig")) if (r.get("trang_thai") or "dung") == "dung" and not kiem_nhac(r["ma"])]
    if not ds:
        return "NH0001"
    tt = khong_dau(b.get("tamTrang", ""))
    muon = TAM_TRANG.get(tt, [tt] if tt else [])
    truoc = (so.get("tuan") or [{}])[-1].get("nhac")

    def diem(r):
        tam = (r.get("tam_trang") or "").split(";")
        hop = r.get("hop_video") or ""
        return (sum(x in tam for x in muon) * 3 + ("bni" in hop or "gioi-thieu" in hop) * 2 - (r["ma"] == truoc) * 4, r["ma"])
    return max(ds, key=diem)["ma"]


def main():
    da = Path(sys.argv[1]).resolve()
    if not XUONG:
        sys.exit("✘ Chưa cài Xưởng Video AI: hãy chạy lại câu lệnh cài Xưởng Video AI.")
    kenh = XUONG
    f_rieng = da / "kenh-rieng.json"
    f_rieng.unlink(missing_ok=True)  # đọc hồ sơ gốc của học viên, rồi ghi lại khóa riêng ở dưới
    h = ho_so(da)
    b = doc(da / "bni.json")
    # Khóa cũ của bản 1
    if "chuDe" not in b and "giup" in b:
        b["chuDe"] = b["giup"]
    if "xin" not in b and "khachTot" in b:
        b["xin"] = {"tren": "Khách tốt", "duoi": "cho tôi là", "dong": b["khachTot"]}
    dong = [x for x in (da / "loi.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    loi_doc = (da / "doc-tts.txt").read_text(encoding="utf-8").strip()
    f_so = kenh / "mau-cua-toi" / "bni" / "so-bni.json"
    so = doc_so(f_so)
    loi, nhac = kiem_truoc(da, b, dong, loi_doc, so)
    for x in nhac:
        print("⚠", x)
    if loi:
        for x in loi:
            print("✘", x)
        sys.exit("✘ Sửa các dòng ✘ ở trên rồi chạy lại bni.py (chưa tạo giọng, chưa tốn thời gian dựng).")
    phan = b["phan"]

    # Hồ sơ riêng của video này: tên kênh khi hồ sơ còn chữ mẫu, giọng AI theo người. Không sửa ho-so-kenh.json của học viên.
    rieng = {}
    # Video giới thiệu bản thân luôn mang thương hiệu của chính người nói (mo[1]), không lấy tên kênh trong hồ sơ: hồ sơ có thể
    # là kênh khác hay còn sót từ lần thử trước (thử 25/11/2026: video của Founder hiện nhãn "BẢO HIỂM TẬN TÂM").
    nhan_kenh = b["mo"][1]
    if nhan_kenh != h.get("ten", ""):
        rieng["ten"] = nhan_kenh
    g = dict(b.get("giongAI") or h.get("giongAI") or {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural"})
    if g.get("provider") == "edge" and "toc" not in g:
        # Giọng miễn phí đọc chậm (đo 25/11/2026: 123 chữ ra 37 giây): nhanh hơn 8% cho nhịp giới thiệu, vẫn tự nhiên
        g["toc"] = 1.08
    if b.get("giongAI") or g != (h.get("giongAI") or {}):
        rieng["giongAI"] = g
    if rieng:
        ghi(f_rieng, {"_ghi": "bni.py ghi: khóa riêng cho video này, đè lên ho-so-kenh.json", **rieng})

    # 1. Ảnh, video của người dẫn
    thu_muc_toi = kenh / "anh-video-cua-toi"
    giong_tu_quay = b.get("giongTuQuay")
    toi = sorted(f for f in thu_muc_toi.glob("*") if f.suffix.lower() in ANH | VIDEO and "doc-loi" not in f.name) if thu_muc_toi.exists() else []
    toi.sort(key=lambda f: (f.suffix.lower() not in VIDEO, f.name))  # video trước, ảnh sau
    canh_dir = da / "public" / "canh"
    canh_dir.mkdir(parents=True, exist_ok=True)
    ma_toi = []
    for i, f in enumerate(toi[:5], 1):
        ma = f"TOI{i}"
        clip_toi(f, canh_dir / f"{ma}.mp4")
        ma_toi.append(ma)
    co_mat = bool(ma_toi)
    print(f"{'✔ có' if co_mat else '• không có'} ảnh/video của người dẫn trong {thu_muc_toi}"
          + (f": {', '.join(f.name for f in toi[:5])}" if co_mat else " → chế độ không mặt, dùng cảnh thật không người"))
    (da / "loai.txt").write_text("gioi-thieu" + ("" if co_mat else " khong-mat"), encoding="utf-8")
    if not (da / "nhac.txt").exists() or b.get("nhac"):
        (da / "nhac.txt").write_text(chon_nhac(b, so), encoding="utf-8")
    print("✔ nhạc:", (da / "nhac.txt").read_text(encoding="utf-8").strip())

    # 2. Clip kho cho chế độ không mặt: khớp ngành trước, rồi cảnh hợp mọi nghề, rồi nền màu
    kho, kho_ds = kho_canh(h)
    tu_khoa = {}
    if (kho / "chi-muc.csv").exists():
        tu_khoa = {r["ma"]: r.get("tu_khoa", "") for r in csv.DictReader((kho / "chi-muc.csv").open(encoding="utf-8-sig"))}
    co = {}
    for ma, r in kho_ds.items():
        if not any("CO MAT" in x.upper() for x in r["file"].relative_to(kho).parts[:-1]) \
                and not any(t in (r["mo_ta"] or "").lower() for t in HOAT_HINH):
            co[ma] = r
    nganh = [khong_dau(x) for x in b.get("nganh", []) if len(khong_dau(x)) >= 4]

    def diem_nganh(ma):
        """Khớp ĐÚNG từ khóa của cảnh (cột tu_khoa), không khớp chuỗi con: "banh" từng khớp "banh-rang" (thử 25/11/2026)."""
        kw = {khong_dau(x) for x in tu_khoa.get(ma, "").split(";") if x.strip()}
        return sum(k in kw for k in nganh)
    khop = sorted((x for x in co if nganh and diem_nganh(x) > 0), key=lambda x: (-diem_nganh(x), x))

    def dia_danh_la(ma):
        chu_canh = khong_dau(co[ma]["mo_ta"] or "") + "-" + khong_dau(tu_khoa.get(ma, ""))
        return any(d in chu_canh and not any(d in k for k in nganh) for d in DIA_DANH)
    for ma in [x for x in co if dia_danh_la(x)]:
        co.pop(ma)
    khop = [x for x in khop if x in co]
    # Dự phòng hợp mọi nghề: bỏ cảnh laptop, văn phòng (chấm 25/11/2026: laptop ở cả 3 bài thử, lạc với tiệm bánh, spa)
    hop_moi_nghe = [x for x in sorted(co) if co[x]["file"].parent.name in ("viet-nam", "nganh-nghe", "nen-chu")
                    and not any(t in khong_dau(tu_khoa.get(x, "")) for t in ("laptop", "van-phong", "lam-viec"))]
    if not co_mat:
        print(f"• cảnh khớp ngành {nganh}: {', '.join(khop[:6]) or 'không có'}")
    da_dung = set()
    dem = [0]

    def chon(vai):
        i = dem[0]
        dem[0] += 1
        if co_mat:
            return ma_toi[i % len(ma_toi)]
        for ma in [*([b["canh"][vai]] if b.get("canh", {}).get(vai) else []), *khop, *UU_TIEN[vai], *hop_moi_nghe]:
            if ma in co and ma not in da_dung:
                da_dung.add(ma)
                return ma
        ma = f"NEN{i + 1}"
        c0, c1, c2 = NEN_MEM[i % len(NEN_MEM)]
        ff("-f", "lavfi", "-i", f"gradients=s=1080x1920:c0={c0}:c1={c1}:c2={c2}:n=3:speed=0.015:d=8:r=25,format=yuv420p",
           "-t", 8, "-c:v", "libx264", "-preset", "fast", "-crf", 20, canh_dir / f"{ma}.mp4")
        print(f"• kho cảnh trống: tự tạo nền màu {ma} cho vai '{vai}' (thả ảnh, video của mình vào anh-video-cua-toi sẽ đẹp hơn)")
        return ma

    # 3. Giọng
    giong = da / "giong"
    giong.mkdir(exist_ok=True)
    from kiem_chot import sua_doc
    chu_doc, _ = sua_doc(loi_doc)
    cu = giong / "ca-bai.da-gui.txt"
    tho_cu = next((x for x in (giong / "ca-bai.mp3", giong / "ca-bai.wav") if x.exists() and x.stat().st_size > 20000), None)
    if not giong_tu_quay and tho_cu and cu.exists() and cu.read_text(encoding="utf-8").strip() == chu_doc:
        tho = tho_cu  # lời đọc không đổi: giữ giọng cũ, không tốn credit
        print(f"✔ lời đọc không đổi, dùng lại giọng {tho.name}")
    elif giong_tu_quay:
        nguon = Path(giong_tu_quay) if Path(giong_tu_quay).is_absolute() else kenh / giong_tu_quay
        if not nguon.exists():
            nguon = thu_muc_toi / giong_tu_quay
        ff("-i", nguon, "-vn", "-ac", 1, "-ar", 48000, giong / "ca-bai.wav")
        (giong / "ca-bai.da-gui.txt").write_text(chu_doc, encoding="utf-8")
        tho = giong / "ca-bai.wav"
        print(f"✔ dùng tiếng người dẫn tự quay: {nguon.name}")
    else:
        r = subprocess.run([sys.executable, ND / "tao_giong.py", da, "--chu-file", "doc-tts.txt", "--ra", "giong/ca-bai"])
        if r.returncode:
            sys.exit("✘ Tạo giọng chưa được, sửa doc-tts.txt theo dòng ✘ ở trên rồi chạy lại bni.py.")
        tho = giong / "ca-bai.mp3"
    ff("-i", tho, "-af", "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-40dB:stop_silence=0.2",
       "-ar", 48000, giong / "giong-gon.wav")
    subprocess.run([sys.executable, ND / "nghi_dau_phay.py", giong / "giong-gon.wav", da / "loi.txt", giong / "giong-nghi.wav"], check=True)
    dai = giay(giong / "giong-nghi.wav")
    n = len(chu(loi_doc))
    if not GIAY_IT <= dai <= GIAY_NHIEU:
        can = round((25.5 - dai) * n / max(dai, 1))
        sys.exit(f"✘ Giọng dài {dai:.1f} giây (cần {GIAY_IT:.0f}–{GIAY_NHIEU:.0f}): {'thêm' if can > 0 else 'bớt'} khoảng {abs(can)} chữ "
                 "trong doc-tts.txt và loi.txt rồi chạy lại.")
    print(f"✔ giọng {dai:.1f} giây, {n} chữ")
    ghi(da / "doan.json", {"nguon": [], "giong": str(giong / "giong-nghi.wav").replace("\\", "/")})

    # 4. Cảnh: tu: N là lúc dòng N (đếm từ 1) bắt đầu, tu: 0 là đầu video; den là lúc dòng đầu của phần sau bắt đầu.
    m, cong = [0], 0
    for k in phan:
        cong += k
        m.append(cong + 1)

    def moc_theo_chu(ten, tu, den):
        """moc: N là lúc dòng N bắt đầu. Dò dòng đầu tiên trong [tu, den) có một chữ riêng của mục."""
        ra, truoc = [], tu
        tach = [[w for w in t.lower().replace(",", " ").split() if len(w) > 1 and w not in {"và", "cho", "các", "có"}] for t in ten]
        chung = {w for w in {x for c in tach for x in c} if sum(w in c for c in tach) > 1}
        for i, t in enumerate(ten):
            chu_rieng = [w for w in tach[i] if w not in chung] or tach[i]
            bat_dau = truoc + (1 if i and truoc + 1 < den else 0)
            tim = next((j for j in range(bat_dau, den) if any(w in dong[j - 1].lower() for w in chu_rieng)), None)
            if tim is None:
                tim = tu + round(i * (den - tu) / max(len(ten), 1))
            ra.append(min(max(tim, bat_dau), den - 1))
            truoc = ra[-1]
        return ra

    def the(vai, x, tu, den, loai, mau=("xanh", "vang", "xanh")):
        """Thẻ của nhịp 2 hoặc 4: có danh sách thì thẻ liệt kê hiện dần, không có thì cảnh có chữ."""
        x = x or {}
        ds = [d for d in (x.get("viec") or x.get("dong") or []) if d and d[0]][:3]
        if not ds:
            return {"loai": "flow-chu", "nen": True, "ten": chon(vai), "tren": x.get("tren", ""), "duoi": x.get("duoi", ""),
                    "tu": tu, "den": den, "viTriPhuDe": 1420, "y": 150}
        moc = moc_theo_chu([d[0] for d in ds], tu, den)
        if loai == "danh-sach-buoc":
            return {"loai": loai, "kieuNen": "luoi", "tren": x.get("tren", ""), "duoi": x.get("duoi", ""),
                    "buoc": [{"ten": d[0], **({"phu": d[1]} if len(d) > 1 and d[1] else {})} for d in ds],
                    "moc": moc, "tu": tu, "den": den, "viTriPhuDe": 1420, "amMoc": "hien-the"}
        return {"loai": loai, "kieuNen": "toi", "tren": x.get("tren", ""), "duoi": x.get("duoi", ""),
                "dong": [[c, d[0], d[1] if len(d) > 1 else ""] for c, d in zip(mau, ds)],
                "moc": moc, "tu": tu, "den": den, "viTriPhuDe": 1500, "linhVat": False}

    canh = [
        {"loai": "flow-chu", "nen": True, "ten": chon("mo"), "tren": b["mo"][0], "duoi": b["mo"][1],
         "tu": m[0], "den": m[1], "viTriPhuDe": 1420, "y": 150},
        the("chu", b.get("chuDe"), m[1], m[2], "danh-sach-buoc"),
        {"loai": "flow-chu", "nen": True, "ten": chon("bang"), "tren": b["bangChung"][0], "duoi": b["bangChung"][1],
         "tu": m[2], "den": m[3], "viTriPhuDe": 1420, "y": 150},
        the("xin", b.get("xin"), m[3], m[4], "canh-bao"),
        {"loai": "ket-comment", "clip": chon("ket"), "nhan": nhan_kenh, "tieuDe": b["ghiNho"],
         "tuKhoa": b["lienHe"], "tu": m[4], "den": "het", "viTriPhuDe": 1480, "am": "thong-bao", "choLapCanhKet": True},
    ]
    ghi(da / "canh.json", {"canh": canh}, 1)
    print("✔ canh.json:", ", ".join(f"{c['loai']}({c.get('ten') or c.get('clip') or ''})" for c in canh))

    # 5. Dựng một mạch
    r = subprocess.run([sys.executable, ND / "dung.py", da, "--het"])
    if r.returncode:
        sys.exit(r.returncode)
    tp = da / "render" / "thanh-pham.mp4"

    # 6. Bàn giao vào thanh-pham/ và ghi sổ BNI
    thu_muc_tp = duong_dan(h, h.get("thanhPham") or "thanh-pham")
    thu_muc_tp.mkdir(parents=True, exist_ok=True)
    dich = thu_muc_tp / f"{da.name}.mp4"
    try:
        shutil.copy2(tp, dich)
    except PermissionError:  # đang mở trong trình phát
        dich = thu_muc_tp / f"{da.name}-v2.mp4"
        shutil.copy2(tp, dich)
    sb = b.get("soBni") or {}
    so.setdefault("_ghi", "Sổ BNI: bni.py ghi thêm một dòng sau mỗi video. Câu dễ nhớ giữ nguyên qua các tuần; chủ đề đổi mỗi tuần.")
    so["ten"] = sb.get("ten") or so.get("ten") or b["mo"][0].title()
    for k in ("cauDeNho", "giong"):
        if sb.get(k):
            so[k] = sb[k]
    so["ghiNho"] = b["ghiNho"]
    so["mang"] = list(dict.fromkeys([*so.get("mang", []), *sb.get("mang", [])]))
    so["tuan"] = [t for t in so.get("tuan", []) if t.get("duAn") != da.name]  # dựng lại cùng dự án: thay dòng cũ
    so["tuan"].append({"ngay": datetime.date.today().isoformat(), "chuDe": sb.get("chuDe", ""), "xin": sb.get("xin", ""),
                       "duAn": da.name, "nhac": (da / "nhac.txt").read_text(encoding="utf-8").strip(), "loi": loi_doc})
    f_so.parent.mkdir(parents=True, exist_ok=True)
    f_so.write_text(json.dumps(so, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✔ Video giới thiệu: {dich}")
    print(f"✔ Sổ BNI: {f_so} ({len(so['tuan'])} tuần)")


if __name__ == "__main__":
    main()
