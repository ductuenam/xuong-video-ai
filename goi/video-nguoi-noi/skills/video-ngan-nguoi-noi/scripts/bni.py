"""Video giới thiệu bản thân theo khung BNI (30 giây, hoặc 60), chạy một lệnh. Bản 2.2 (25/11/2026): khung sườn 5 nhịp
"tôi là ai → làm gì, cho ai → vì sao tin → nhờ giới thiệu ai → câu dễ nhớ + tên", lời do AI viết theo từng người.

  python bni.py "<dự án>" --kiem     chỉ kiểm lời và bni.json (vài giây), sửa tới khi đạt
  python bni.py "<dự án>"            tạo giọng, dựng, bàn giao

Đọc references/bni-cong-thuc.md trước khi viết lời. Trong thư mục dự án (<Xưởng>/du-an/<yyyy-mm-dd>_bni-<tên>/) cần có:
  doc-tts.txt  lời đọc một đoạn, theo giọng người đó (bài 30 giây thường 75–118 chữ; máy đo độ dài giọng thật)
  loi.txt      phụ đề cắt từ đúng chữ của doc-tts.txt, mỗi dòng ≤ 28 ký tự
  anh/         (nên có) 1–5 ảnh, video của chính người đó, tên 1-…5- theo vai: mở, làm gì, bằng chứng, nhờ giới thiệu, kết
  bni.json     {"phan": [số dòng loi.txt của 5 nhịp: tôi là ai, làm gì cho ai, vì sao tin, nhờ giới thiệu ai, câu dễ nhớ + tên],
                "mo": ["TÊN", "THƯƠNG HIỆU"],
                "chuDe": {"tren": "<dòng trên>", "duoi": "<dòng dưới>", "viec": [["ý", "chữ nhỏ dưới ý, có thể rỗng"], ...] 0–3},
                "bangChung": ["DÒNG 1", "DÒNG 2 (có thể bỏ)"],
                "xin": {"tren": "<dòng trên>", "duoi": "<dòng dưới>", "dong": [["ai", "dấu hiệu"], ...] 0–3},
                "ghiNho": "<chữ thẻ kết ≤ 18 ký tự>", "lienHe": "<ít nhất 2 chữ, vd ZALO 09xx...>",
                "nganh": ["tu-khoa-nghe", ...], "tamTrang": "vui|am-ap|cam-xuc|chuyen-nghiep|manh-me|moc-mac",
                "doDai": 30 | 60,                                                      (tùy chọn, mặc định 30)
                "kieu": "lan-dau" | "tuan",                                            (mặc định lan-dau; tuan thì chặn trùng tuần cũ)
                "docDung": {"VCCI": "Vê Xê Xê I", "SME": "Ét Em I"},                  (tùy chọn: cách đọc tên riêng, viết tắt)
                "giongAI": {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural"},   (tùy chọn; ghi tắt tên giọng cũng được)
                "giongTuQuay": "<tệp giọng tự quay trong anh/>",                       (tùy chọn)
                "canh": {"mo", "chu", "bang", "xin", "ket"}, "nhac": "NH000x",       (tùy chọn, đè lựa chọn tự động)
                "soBni": {"ten", "chuDe", "xin", "cauDeNho", "giong", "mang": [...],  (mang nối thêm vào sổ)
                          "cauDeNhoDuyet": false, "xinDuyet": false,   (AI tự chọn khi "làm luôn": lần sau hỏi lại)
                          "deDanh": ["lời xin để tuần sau"]}}
  "viec" hoặc "dong" rỗng thì thẻ đó thành cảnh có chữ. Khóa cũ "giup", "khachTot" vẫn đọc được.

Script tự làm:
  0. Kiểm trước. Chặn (✘) chỉ chỗ làm hỏng video: dòng phụ đề, ghiNho dài, thiếu khóa, tên chưa nói trong 20 chữ đầu,
     số chữ lệch rất xa, lời lệch phụ đề, trùng tuần cũ, chép ví dụ, thiếu tệp giọng tự quay. Còn lại chỉ nhắc (⚠).
  1. Ảnh, video của người dẫn (anh/ của dự án, không có thì <Xưởng>/anh-video-cua-toi/) làm cảnh theo vai; bỏ logo.
     Không có thì chế độ không mặt: cảnh kho khớp "nganh", rồi cảnh hợp mọi nghề, cuối cùng nền màu tự tạo.
  2. loai.txt, nhạc theo tamTrang (đổi bài so với tuần trước), kenh-rieng.json, doc-dung.json, goi-y.txt.
  3. Giọng: tự quay thì giữ nhịp người nói (chỉ rút khoảng lặng dài); giọng máy thì cắt nghỉ, chèn nghỉ dấu phẩy.
     Đo độ dài theo doDai (30: giọng máy 20–30 giây, tự quay 18–33; 60: 45–60, tự quay 40–65).
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
    "mo": ["CA0116", "CA0110", "CA0175", "CA0113"],  # bỏ CA0182 (bàn laptop) 25/11/2026
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
# Giọng bài -> từ tâm trạng (theo thứ tự ưu tiên) trong từ điển references/tu-dien-am.json, khớp cột tam_trang của
# tai-nguyen/nhac/chi-muc.csv sau khi đã đưa về từ điển (kho_am.chuan_tam). Giọng bài ghi đúng một từ của từ điển cũng được.
TAM_TRANG = {
    "vui": ["vui", "am-ap", "soi-dong"],
    "am-ap": ["am-ap", "thu-gian", "vui"],
    "cam-xuc": ["cam-xuc", "truyen-cam-hung", "am-ap"],
    "chuyen-nghiep": ["tin-cay", "truyen-cam-hung", "sang-trong"],
    "manh-me": ["soi-dong", "truyen-cam-hung", "tin-cay"],
    "moc-mac": ["am-ap", "thu-gian", "tin-cay"],  # thẳng, mộc, gần gũi (thử vai chủ xưởng mộc 25/11/2026)
}
DONG_TOI_DA, GHI_NHO_TOI_DA, THE_TOI_DA = 28, 18, 14
# Theo độ dài bài ("doDai" trong bni.json, mặc định 30). Luật thật là độ dài GIỌNG đo sau khi tạo; số chữ chỉ để nhắc sớm
# (giọng miễn phí đo 25/11/2026 khoảng 3,5–4 chữ/giây kể cả nghỉ). Chỉ chặn số chữ khi lệch xa, để khỏi tốn credit giọng.
# Bản 2.2 (25/11/2026): bỏ chặn 85–118 chữ: hồ sơ mỏng bị ép "thêm chuyện" làm AI bịa, người tự quay nói nhanh bị cắt chi tiết thật.
DO_DAI = {
    # Sàn 18 giây: hồ sơ mỏng ra bài ngắn thật thà, không ép độn chữ (thử vai chủ spa 25/11/2026)
    30: {"chu": (70, 118), "chan": (50, 140), "giay": (18.0, 30.0), "tuQuay": (18.0, 33.0), "tuQuayChu": (70, 150)},
    60: {"chu": (150, 230), "chan": (110, 260), "giay": (40.0, 60.0), "tuQuay": (40.0, 65.0), "tuQuayChu": (150, 300)},
}
# Chữ hứa hẹn: nhắc theo mục 5 của bni-cong-thuc.md (ngành có quy định quảng cáo)
HUA = ("trị dứt", "dứt điểm", "khỏi hẳn", "hết hẳn", "cam kết", "100%", "một trăm phần trăm",
       "thu nhập", "lợi nhuận", "sinh lời", "lãi suất", "giảm phí", "phần trăm phí", "khuyến mãi của hãng")
NGANH_QUY_DINH = ("bảo hiểm", "tài chính", "đầu tư", "chứng khoán", "tiền số", "nha khoa", "phòng khám", "thẩm mỹ", "trị mụn",
                  "spa", "thực phẩm chức năng", "cam kết đầu ra", "nhân thọ", "quyền lợi chi trả", "tiền chi trả")
TRUNG_TUAN_CU = 0.60                 # lời giống một tuần cũ từ mức này là chặn
CHUOI_CHEP = 8                       # trùng nguyên 8 chữ liền với tệp công thức là chép ví dụ
TEN_TRONG = 20                       # tên gọi phải nằm trong ngần này chữ đầu (khoảng 5 giây)
# Chữ quá phổ biến: không tính khi dò chữ của thẻ trong lời (thẻ "AI ĐI LÀM MỆT" từng qua nhờ chữ "ai")
CHU_RONG = {"và", "cho", "các", "có", "ai", "là", "của", "người", "những", "một", "khi", "thì", "với", "đang", "được", "mình", "tôi", "em"}
XIN_CHUNG = ("ai cần", "bất kỳ ai", "bạn nào muốn", "ai cũng", "ai có nhu cầu", "mọi người cần")
# Chữ máy đọc sai dễ gặp: viết tắt IN HOA hoặc chữ có f, j, w, z (không có trong tiếng Việt)
LA = re.compile(r"\b(?:[A-Z]{2,}|\w*[fjwzFJWZ]\w*)\b")
QUEN = {"zalo", "facebook", "tiktok", "zoom", "youtube", "shopee", "online", "web", "website", "fanpage", "ok"}  # giọng máy đọc được


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
        # Ảnh ngang: thu trọn vào khung 1080x1000 (không cắt mép; ảnh 3:2 từng mất người đứng hai mép, thử 25/11/2026)
        fg, y, neo = (("scale=1080:1000:force_original_aspect_ratio=decrease", "330+(1000-h)/2", "ih/2-(ih/zoom/2)") if ngang else
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
        import cv2
        c = cv2.VideoCapture(str(f))
        w, h = c.get(cv2.CAP_PROP_FRAME_WIDTH), c.get(cv2.CAP_PROP_FRAME_HEIGHT)
        c.release()
        if w > h * 1.1:
            # Video ngang: giữ trọn khung trên nền chính nó làm mờ, như ảnh ngang (cắt giữa thành dọc từng mất 2/3 khung, thử 25/11/2026)
            ff("-i", f, "-t", 8, "-filter_complex",
               "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2[bg];"
               "[0]scale=1080:1000:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:330+(1000-h)/2,fps=25,format=yuv420p",
               "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 18, ra)
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
    if not b.get("mo") or len(b["mo"]) < 2:
        loi.append("bni.json thiếu 'mo' (2 dòng: tên, thương hiệu)")
    if not b.get("bangChung") or not str(b["bangChung"][0]).strip():
        loi.append("bni.json thiếu 'bangChung' (1–2 dòng; hồ sơ không có số thì ghi điều thật nhất đã có, vd 'KHÁCH QUEN')")
    if len((b.get("lienHe") or "").split()) < 2:
        loi.append("lienHe cần từ 2 chữ trở lên (vd 'ZALO 0900 000 000'), một chữ thì thẻ kết hiện 'XEM BÌNH LUẬN GHIM'")
    # Không tính mo (tên người, tên thương hiệu không rút được; thẻ mở tự xuống 2 dòng, bước cảnh đo phông thật)
    the_dai = [x for x in [*(b.get("bangChung") or []),
                           *[(b.get(k) or {}).get(t, "") for k in ("chuDe", "xin") for t in ("tren", "duoi")]] if len(str(x)) > THE_TOI_DA]
    the_xin = " ".join(str((b.get("xin") or {}).get(t, "")) for t in ("tren", "duoi"))
    if re.search(r"[Kk]hách (hàng )?tốt (cho|của) tôi", the_xin):
        loi.append(f"thẻ nhờ giới thiệu '{the_xin}' là câu dịch sát, nghe máy móc: viết tự nhiên, vd 'Rất mong được' / 'giới thiệu đến'")
    if the_dai:
        nhac.append(f"chữ trên thẻ dài hơn {THE_TOI_DA} ký tự, dễ tràn (bước cảnh đo bằng phông thật và chặn nếu tràn): " + " | ".join(the_dai))
    if b.get("doDai", 30) not in DO_DAI:
        loi.append(f"doDai {b.get('doDai')} chưa làm được: chọn 30 (mặc định) hoặc 60 giây")
    dd = DO_DAI.get(b.get("doDai", 30), DO_DAI[30])
    tu_quay = b.get("giongTuQuay")
    if tu_quay:
        nguon = [p for p in (Path(tu_quay), da / "anh" / tu_quay, *([XUONG / tu_quay, XUONG / "anh-video-cua-toi" / tu_quay] if XUONG else []))
                 if p.is_file()]
        if not nguon:
            loi.append(f"giongTuQuay '{tu_quay}' chưa có tệp: gửi lời đã chốt cho người dùng, chờ họ quay rồi thả vào thư mục anh/ của dự án")
    n = len(chu(loi_doc))
    if tu_quay:  # giọng người thật: nhanh chậm theo người, không chặn, chỉ nhắc trước khi họ quay (người nói khoảng 3,5–5 chữ/giây)
        it, nhieu = dd["tuQuayChu"]
        if not it <= n <= nhieu:
            nhac.append(f"lời {n} chữ để tự quay; bài {b.get('doDai', 30)} giây thường {it}–{nhieu} chữ, nói trước với người dùng để khỏi quay lại")
    else:
        it, nhieu = dd["chu"]
        if not dd["chan"][0] <= n <= dd["chan"][1]:
            loi.append(f"lời {n} chữ, quá xa khoảng {it}–{nhieu} chữ của bài {b.get('doDai', 30)} giây: "
                       + ("bớt ý" if n > nhieu else "thêm bằng điều THẬT đã có trong hồ sơ (nơi làm, năm nghề, cách liên hệ), không bịa chuyện"))
        elif not it <= n <= nhieu:
            nhac.append(f"lời {n} chữ (thường {it}–{nhieu}); máy sẽ đo độ dài giọng thật và báo nếu lệch")
    phan = b.get("phan", [])
    if len(phan) == 5 and 0 in phan:
        loi.append(f"phan {phan} có nhịp 0 dòng: mỗi nhịp cần ít nhất 1 dòng phụ đề (gộp hai nhịp trong một câu thì vẫn tách dòng ở chỗ chuyển ý)")
    thap = loi_doc.lower()
    hua = [x for x in HUA if x in thap]
    if hua:
        cau_hua = (f"lời có chữ hứa hẹn ({', '.join(hua)}): ngành bảo hiểm, tài chính, y tế, làm đẹp không được hứa kết quả, thu nhập, "
                   "không nêu khuyến mãi của hãng (bni-cong-thuc.md mục 5); kể việc đã làm cho khách thay vì hứa")
        # Ngành có quy định thì chặn trước khi dựng (thử vai bảo hiểm 25/11/2026: "thu nhập trăm triệu", "giảm 15% phí" đều lọt)
        # Ngành dò cả trong bni.json (lời có thể không nói chữ "bảo hiểm", như bản thử chỉ nói "nhận tiền chi trả")
        ca = thap + " " + khong_dau(json.dumps(b, ensure_ascii=False)).replace("-", " ") + " " + json.dumps(b, ensure_ascii=False).lower()
        (loi if any(x in ca or khong_dau(x).replace("-", " ") in ca for x in NGANH_QUY_DINH) else nhac).append(cau_hua)
    if not tu_quay and re.search(r"\d", loi_doc):
        nhac.append("doc-tts.txt có chữ số: viết số bằng chữ để máy đọc đúng (phụ đề cắt từ đúng chữ đó)")
    if b.get("tamTrang") and khong_dau(b["tamTrang"]) not in TAM_TRANG:
        nhac.append(f"tamTrang '{b['tamTrang']}' không có; chọn {', '.join(TAM_TRANG)}")
    if b.get("nganh") and XUONG and (XUONG / "tai-nguyen" / "canh" / "chi-muc.csv").exists():
        kw = {khong_dau(k) for r in csv.DictReader((XUONG / "tai-nguyen" / "canh" / "chi-muc.csv").open(encoding="utf-8-sig"))
              for k in (r.get("tu_khoa") or "").split(";") if k.strip()}
        la = [x for x in b["nganh"] if khong_dau(x) not in kw]
        if la:
            nhac.append(f"nganh không có trong kho cảnh: {', '.join(la)} (chỉ khớp nguyên từ khóa trong tai-nguyen/canh/CHI_MUC.md)")
    ten_goi = chu((b.get("mo") or [""])[0])[-1:]
    if ten_goi and ten_goi[0] not in chu(loi_doc)[:TEN_TRONG]:
        loi.append(f"chưa nói tên gọi '{ten_goi[0]}' trong {TEN_TRONG} chữ đầu (khoảng 5 giây): người lạ cần biết ai đang nói trước; "
                   "rút câu mở (câu hỏi, câu gợi chuyện) cho ngắn lại, hoặc nói tên trước")
    from kiem_chot import CHOT
    da_biet = {*(b.get("docDung") or {}), *CHOT["docDung"]}
    viet_tat = [] if tu_quay else sorted({x for x in LA.findall(loi_doc) if x not in da_biet and x.lower() not in QUEN})
    if viet_tat:
        nhac.append("chữ máy dễ đọc sai: " + ", ".join(viet_tat) + ". Thay bằng lời thường, hoặc ghi cách đọc vào \"docDung\" của bni.json")
    chung = [x for x in XIN_CHUNG if x in loi_doc.lower()]  # cả bài: lời xin chung chung đặt ở nhịp khác cũng bắt
    if chung:
        nhac.append(f"lời xin chung chung ({', '.join(chung)}): nói rõ một nhóm người và dấu hiệu nhận ra họ")
    giong_nhau = difflib.SequenceMatcher(None, chu(" ".join(dong)), chu(loi_doc)).ratio()
    if giong_nhau < 0.85:
        loi.append(f"doc-tts.txt lệch chữ với loi.txt (giống {giong_nhau:.0%}, cần ≥ 85%): viết doc-tts.txt trước rồi cắt loi.txt từ đúng những chữ đó")
    # Nghe một lần phải hiểu: câu vụn, câu kiểu tiêu đề làm bài khó nghe (Founder chấm 3 bài thử 25/11/2026). Chỉ nhắc, không chặn.
    cau = [c for c in re.split(r"[.!?]+", loi_doc) if chu(c)]
    vun = [c.strip() for c in cau[:-2] if len(chu(c)) < 5]
    if len(vun) >= 2:
        nhac.append("câu vụn khó nghe: " + " | ".join(vun) + ". Gộp thành câu đủ ý, nói liền như lời nói (bni-cong-thuc.md mục 3)")
    if ":" in loi_doc:
        nhac.append("lời có dấu hai chấm, nghe như đọc tiêu đề: viết thành câu nói thường (mục 3)")
    phan = b.get("phan", [])
    if len(phan) != 5 or sum(phan) != len(dong):
        loi.append(f"bni.json phan {phan} (tổng {sum(phan)}) phải đủ 5 nhịp và bằng số dòng loi.txt ({len(dong)})")
    else:
        # Ý trên thẻ phải có chữ được NÓI trong đúng nhịp đó, không thì thẻ sáng sớm theo mốc chia đều
        # (chấm 25/11/2026: thẻ "NGƯNG KEM, THẢO MỘC" của chuyện bị đặt vào nhịp chủ đề, sáng sớm 5 giây)
        dau = [sum(phan[:i]) for i in range(6)]
        for so_nhip, khoa, ds in ((2, "chuDe", "viec"), (4, "xin", "dong")):
            doan = " ".join(dong[dau[so_nhip - 1]:dau[so_nhip]]).lower()
            for d in ((b.get(khoa) or {}).get(ds) or [])[:3]:
                w = [x for x in chu(d[0]) if len(x) > 1 and x not in CHU_RONG]
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
    # Trùng tuần cũ: cắt đúng CỤM câu dễ nhớ và tên (được phép lặp) rồi so. Trước đây bỏ từng chữ của câu dễ nhớ ở mọi chỗ,
    # nghề kế toán mất luôn chữ "sổ" khi so (thử 25/11/2026).
    cum = sorted({" ".join(chu(x)) for x in (so.get("cauDeNho", ""), so.get("ten", ""), b.get("mo", [""])[0],
                                              (b.get("soBni") or {}).get("cauDeNho", "")) if chu(x)}, key=len, reverse=True)

    def loc(t):
        s = " " + " ".join(chu(t)) + " "
        for c in cum:
            s = s.replace(f" {c} ", " ")
        return s.split()
    cu = [(t.get("ngay", "?") + " " + t.get("duAn", ""), t.get("loi", "")) for t in so.get("tuan", []) if t.get("duAn") != da.name]
    da_co = {t.get("duAn") for t in so.get("tuan", [])}
    if XUONG and (XUONG / "du-an").exists():  # dự án BNI cũ chưa có trong sổ (dựng bằng bản cũ)
        cu += [(f.parent.name, f.read_text(encoding="utf-8")) for f in (XUONG / "du-an").glob("*bni*/doc-tts.txt")
               if f.parent != da and f.parent.name not in da_co]
    # Bản 30 và bản 60 giây của cùng một bài (thư mục chỉ khác đuôi -60) không so với nhau (thử vai bảo hiểm 25/11/2026)
    goc = re.sub(r"-60$", "", da.name)
    cu = [(ten, t) for ten, t in cu if re.sub(r"-60$", "", ten.split()[-1]) != goc]
    nay = loc(loi_doc)
    for ten, t in cu:
        r = difflib.SequenceMatcher(None, nay, loc(t)).ratio()
        if r >= TRUNG_TUAN_CU:
            # Chỉ bài tuần mới phải khác tuần cũ; làm lại video giới thiệu lần đầu (đổi ảnh, đổi giọng) với lời cũ là bình thường
            # (thử 25/11/2026: dựng lại bản của Founder với ảnh mới bị chặn oan)
            if b.get("kieu") == "tuan":
                loi.append(f"lời giống {r:.0%} bài {ten}: bài tuần phải khác chủ đề, khác câu chuyện, khác lời xin (chỉ giữ câu dễ nhớ, tên, câu mở)")
            else:
                nhac.append(f"lời giống {r:.0%} bài {ten}: được nếu đây là làm lại video giới thiệu; bài tuần BNI thì ghi \"kieu\": \"tuan\" và viết khác")
            break
    # Chủ đề gần một tuần cũ: trùng từ 2 chữ nội dung (trước đây chỉ bắt tên giống hệt: "hóa đơn sai thời điểm" lọt sau "hóa đơn điện tử")
    cd = {x for x in chu((b.get("soBni") or {}).get("chuDe", "")) if x not in CHU_RONG}
    gan = [t.get("chuDe", "") for t in so.get("tuan", [])[-4:] if t.get("duAn") != da.name]
    giong_cd = [t for t in gan if len(cd & set(chu(t))) >= min(2, len(cd))]
    if cd and giong_cd and b.get("kieu") == "tuan":
        nhac.append(f"chủ đề gần với tuần cũ ({' | '.join(giong_cd)}); bài tuần nên đổi mảng, trừ khi người dùng muốn nói tiếp")
    # Không đo độ dài vế cho BNI: câu ngắn là giọng của người đó (Founder duyệt 25/11/2026; thử 3 bài đều < 9 chữ/vế mà vẫn ĐẠT).
    return loi, nhac


def chon_nhac(b, so):
    if b.get("nhac"):
        return b["nhac"]
    import kho_am
    from kiem_chot import kiem_nhac
    ds = [r for r in kho_am.doc_chi_muc("nhac") if r["_file"].is_file() and not kiem_nhac(r["ma"])]
    if not ds:
        return "NH0001"
    tt = kho_am.khong_dau(b.get("tamTrang", ""))
    muon = TAM_TRANG.get(tt) or kho_am.chuan_tam(tt)[0]
    truoc = (so.get("tuan") or [{}])[-1].get("nhac")
    can = b.get("doDai", 30) + 6  # giây nhạc cần (tính cả đoạn mở, kết); bài ngắn hơn vẫn dùng được nhờ nối vòng nhưng xếp sau

    def diem(r):
        tam = kho_am.chuan_tam(r.get("tam_trang"))[0]
        hop = r.get("hop_video") or ""
        khop = sum((3 - i) * 2 for i, x in enumerate(muon) if x in tam)  # từ đầu tiên nặng nhất
        con = (kho_am.giay_cua(r) or 999) - (kho_am.so(r.get("bat_dau_goi_y")) or 0)
        return (khop + ("bni" in hop) * 2 + ("gioi-thieu" in hop) - (r["ma"] == truoc) * 4 - (con < can) * 3
                + (r.get("chu") == "hoc-vien") * 1, r["ma"])  # bài học viên tự thêm được ưu tiên nhẹ khi ngang điểm
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
        # Bản 1 ghi cứng "Khách tốt / cho tôi là": dịch sát từ tiếng Anh, nghe máy móc (Founder 25/11/2026). Hồ sơ cũ đổi sang câu tự nhiên.
        b["xin"] = {"tren": "Rất mong được", "duoi": "giới thiệu đến", "dong": b["khachTot"]}
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
    if "--kiem" in sys.argv:  # chỉ kiểm lời và bni.json, vài giây, không tạo giọng, không dựng
        print(f"✔ Kiểm trước đạt ({len(chu(loi_doc))} chữ). Chạy lại không có --kiem để dựng.")
        return
    phan = b["phan"]

    # Hồ sơ riêng của video này: tên kênh khi hồ sơ còn chữ mẫu, giọng AI theo người. Không sửa ho-so-kenh.json của học viên.
    rieng = {}
    # Video giới thiệu bản thân luôn mang thương hiệu của chính người nói (mo[1]), không lấy tên kênh trong hồ sơ: hồ sơ có thể
    # là kênh khác hay còn sót từ lần thử trước (thử 25/11/2026: video của Founder hiện nhãn "BẢO HIỂM TẬN TÂM").
    nhan_kenh = b["mo"][1]
    if nhan_kenh != h.get("ten", ""):
        rieng["ten"] = nhan_kenh
    if isinstance(b.get("giongAI"), str):  # ghi tắt tên giọng ("vi-VN-NamMinhNeural"): hiểu là giọng miễn phí (thử 25/11/2026 văng lỗi)
        b["giongAI"] = {"provider": "edge", "voice_id": b["giongAI"]}
    g = dict(b.get("giongAI") or h.get("giongAI") or {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural"})
    if g.get("provider") == "edge" and "toc" not in g:
        # Giọng miễn phí đọc chậm (đo 25/11/2026: 123 chữ ra 37 giây): nhanh hơn 8% cho nhịp giới thiệu, vẫn tự nhiên
        g["toc"] = 1.08
    if b.get("giongAI") or g != (h.get("giongAI") or {}):
        rieng["giongAI"] = g
    if rieng:
        ghi(f_rieng, {"_ghi": "bni.py ghi: khóa riêng cho video này, đè lên ho-so-kenh.json", **rieng})
    # Cách đọc riêng (tao_giong.py đọc doc-dung.json) và tên riêng để Whisper nghe đúng lúc làm phụ đề, nghiệm thu
    ghi(da / "doc-dung.json", {"_ghi": "bni.py chép từ docDung của bni.json: chữ gốc -> cách đọc, chỉ đổi lúc gửi máy đọc", **(b.get("docDung") or {})})
    goi_y = list(dict.fromkeys(x for x in [*b["mo"], *(b.get("docDung") or {})] if x.strip()))
    (da / "goi-y.txt").write_text(", ".join(goi_y), encoding="utf-8")

    # 1. Ảnh, video của người dẫn: thư mục anh/ của dự án trước (mỗi video một bộ, không lẫn ảnh tuần trước hay người khác),
    # không có thì <Xưởng>/anh-video-cua-toi/. Xếp đúng theo tên tệp 1-…5- (trước đây video bị đưa lên đầu, phá thứ tự; thử 25/11/2026).
    # Bỏ logo (nhãn thương hiệu đã lấy từ mo[1]) và tệp giọng tự quay (doc-loi).
    # Có thư mục anh/ (kể cả rỗng) là dự án đã chọn ảnh riêng: rỗng thì làm chế độ không mặt, không lấy ảnh cũ trong Xưởng
    thu_muc_toi = da / "anh" if (da / "anh").is_dir() else kenh / "anh-video-cua-toi"
    giong_tu_quay = b.get("giongTuQuay")
    toi = sorted(f for f in thu_muc_toi.glob("*") if f.suffix.lower() in ANH | VIDEO
                 and not any(x in f.name.lower() for x in ("doc-loi", "logo")) and f.name != giong_tu_quay) if thu_muc_toi.exists() else []
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
    # Bỏ cả thư mục nganh-nghe (tòa án, phòng bệnh, nhà máy robot: cảnh của MỘT nghề) và nền khoa học viễn tưởng
    # (thử vai chủ spa 25/11/2026: video spa không ảnh có thể ra cảnh phòng bệnh, dây chuyền robot)
    hop_moi_nghe = [x for x in sorted(co) if co[x]["file"].parent.name in ("viet-nam", "nen-chu")
                    and not any(t in khong_dau(tu_khoa.get(x, "") + "-" + (co[x]["mo_ta"] or ""))
                                for t in ("laptop", "van-phong", "lam-viec", "neon", "vien-tuong", "khoa-hoc", "kinh-vo", "hologram", "vu-tru", "thien-ha"))]  # vũ trụ: kết video spa ra thiên hà (thử 25/11)
    if not co_mat:
        print(f"• cảnh khớp ngành {nganh}: {', '.join(khop[:6]) or 'không có'}")
    da_dung = set()
    dem = [0]

    def chon(vai):
        i = dem[0]
        dem[0] += 1
        if co_mat:
            # Ảnh theo VAI (1- mở, 2- làm gì, 3- bằng chứng, 4- nhờ giới thiệu, 5- kết), không theo lượt gọi: thẻ có danh sách
            # không dùng cảnh nên trước đây ảnh 2- rơi vào nhịp bằng chứng, 3- vào cảnh kết (thử 25/11/2026)
            vt = ["mo", "chu", "bang", "xin", "ket"].index(vai)
            if vt < len(ma_toi):
                return ma_toi[vt]
            return ma_toi[0] if vai == "ket" else ma_toi[(vt - len(ma_toi) + 1) % len(ma_toi)]  # thiếu ảnh: kết quay về mặt rõ
        for ma in [*([b["canh"][vai]] if b.get("canh", {}).get(vai) else []), *khop, *UU_TIEN[vai], *hop_moi_nghe]:
            # Kết được lặp nền mềm đã dùng (đầu cuối cùng tông) thay vì vớt cảnh gắt cuối danh sách (thử spa 25/11: thiên hà, khói cam)
            if ma in co and (ma not in da_dung or (vai == "ket" and ma in UU_TIEN["ket"])):
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
    chu_doc, _ = sua_doc(loi_doc, {k: v for k, v in (b.get("docDung") or {}).items() if not k.startswith("_")})
    cu = giong / "ca-bai.da-gui.txt"
    tho_cu = next((x for x in (giong / "ca-bai.mp3", giong / "ca-bai.wav") if x.exists() and x.stat().st_size > 20000), None)
    if not giong_tu_quay and tho_cu and cu.exists() and cu.read_text(encoding="utf-8").strip() == chu_doc:
        tho = tho_cu  # lời đọc không đổi: giữ giọng cũ, không tốn credit
        print(f"✔ lời đọc không đổi, dùng lại giọng {tho.name}")
    elif giong_tu_quay:
        nguon = next(p for p in (Path(giong_tu_quay), da / "anh" / giong_tu_quay, kenh / giong_tu_quay,
                                 kenh / "anh-video-cua-toi" / giong_tu_quay) if p.is_file())  # kiem_truoc đã chặn khi thiếu
        ff("-i", nguon, "-vn", "-ac", 1, "-ar", 48000, giong / "ca-bai.wav")
        (giong / "ca-bai.da-gui.txt").write_text(chu_doc, encoding="utf-8")
        tho = giong / "ca-bai.wav"
        print(f"✔ dùng tiếng người dẫn tự quay: {nguon.name}")
    else:
        r = subprocess.run([sys.executable, ND / "tao_giong.py", da, "--chu-file", "doc-tts.txt", "--ra", "giong/ca-bai"])
        if r.returncode:
            sys.exit("✘ Tạo giọng chưa được, sửa doc-tts.txt theo dòng ✘ ở trên rồi chạy lại bni.py.")
        tho = giong / "ca-bai.mp3"
    dd = DO_DAI[b.get("doDai", 30)]
    if giong_tu_quay:
        # Giọng người thật: giữ nhịp thở của họ, chỉ rút khoảng lặng dài (> 0,7 giây) còn 0,5 giây, không chèn nghỉ dấu phẩy
        # Đo lặng bằng VAD như máy kiểm (dung.py, nghiem_thu.py): đo theo dB thì hơi thở, tiếng nền lọt qua, khe 0,9 giây
        # vẫn còn và bước dựng chặn (thử giọng tự quay 25/11/2026). Mỗi khe > 0,6 giây giữ 0,25 giây mỗi bên.
        ff("-i", tho, "-af", "silenceremove=start_periods=1:start_threshold=-45dB", "-ar", 48000, giong / "giong-dau.wav")
        from faster_whisper.vad import VadOptions, get_speech_timestamps
        from whisper_vi import doc_am_thanh
        ts = get_speech_timestamps(doc_am_thanh(giong / "giong-dau.wav"),
                                   VadOptions(threshold=0.5, min_silence_duration_ms=150, speech_pad_ms=0))
        bo = [(a["end"] / 16000 + 0.25, b["start"] / 16000 - 0.25) for a, b in zip(ts, ts[1:])
              if (b["start"] - a["end"]) / 16000 > 0.6]
        if ts:
            bo.append((ts[-1]["end"] / 16000 + 0.4, 9999))
        loc = f"aselect='not({'+'.join(f'between(t,{x:.3f},{y:.3f})' for x, y in bo)})',asetpts=N/SR/TB" if bo else "anull"
        ff("-i", giong / "giong-dau.wav", "-af", loc, "-ar", 48000, giong / "giong-nghi.wav")
        print(f"✔ rút {len(bo)} khoảng lặng dài trong giọng tự quay")
        it, nhieu = dd["tuQuay"]
    else:
        ff("-i", tho, "-af", "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-40dB:stop_silence=0.2",
           "-ar", 48000, giong / "giong-gon.wav")
        subprocess.run([sys.executable, ND / "nghi_dau_phay.py", giong / "giong-gon.wav", da / "loi.txt", giong / "giong-nghi.wav"], check=True)
        it, nhieu = dd["giay"]
    dai = giay(giong / "giong-nghi.wav")
    n = len(chu(loi_doc))
    if not it <= dai <= nhieu:
        if giong_tu_quay:
            sys.exit(f"✘ Giọng tự quay dài {dai:.1f} giây (cần {it:.0f}–{nhieu:.0f}): nhờ người dùng đọc {'chậm' if dai < it else 'nhanh'} hơn "
                     f"và quay lại, hoặc {'thêm' if dai < it else 'bớt'} một ý trong lời rồi quay lại.")
        can = round(((it + nhieu) / 2 - dai) * n / max(dai, 1))
        sys.exit(f"✘ Giọng dài {dai:.1f} giây (cần {it:.0f}–{nhieu:.0f}): {'thêm' if can > 0 else 'bớt'} khoảng {abs(can)} chữ "
                 "trong doc-tts.txt và loi.txt rồi chạy lại" + (" (thêm bằng điều thật trong hồ sơ, không bịa)." if can > 0 else "."))
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
        {"loai": "flow-chu", "nen": True, "ten": chon("bang"), "tren": b["bangChung"][0], "duoi": (b["bangChung"] + [""])[1],
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
    # Cờ "AI tự chọn, chưa duyệt" (làm luôn): lần sau đọc sổ thấy false thì hỏi lại cho chốt (thử vai chủ spa 25/11/2026)
    for k in ("cauDeNhoDuyet", "xinDuyet"):
        if k in sb:
            so[k] = bool(sb[k])
    so["ghiNho"] = b["ghiNho"]
    so["mang"] = list(dict.fromkeys([*so.get("mang", []), *sb.get("mang", [])]))
    so["deDanh"] = list(dict.fromkeys([*so.get("deDanh", []), *sb.get("deDanh", [])]))  # lời xin, mục tiêu để video sau
    so["tuan"] = [t for t in so.get("tuan", []) if t.get("duAn") != da.name]  # dựng lại cùng dự án: thay dòng cũ
    so["tuan"].append({"ngay": datetime.date.today().isoformat(), "chuDe": sb.get("chuDe", ""), "xin": sb.get("xin", ""),
                       "duAn": da.name, "nhac": (da / "nhac.txt").read_text(encoding="utf-8").strip(), "loi": loi_doc})
    f_so.parent.mkdir(parents=True, exist_ok=True)
    f_so.write_text(json.dumps(so, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✔ Video giới thiệu: {dich}")
    print(f"✔ Sổ BNI: {f_so} ({len(so['tuan'])} tuần)")


if __name__ == "__main__":
    main()
