"""Kiểm bản đọc theo luật đã chốt trong references/da-chot.json. Luật nằm trong code, không dựa vào trí nhớ.
  python kiem_chot.py <dự án>                 kiểm doc-tts.txt (sau khi đã tự thay cách đọc)
  python kiem_chot.py <dự án> --file x.txt     kiểm file khác
  python kiem_chot.py --chu "một câu" --cau    kiểm một câu lẻ (chỉ cách đọc, không kiểm cảm xúc)
Mã thoát 1 là còn lỗi. tao_giong.py và nghiem_thu.py gọi cùng các hàm này."""
import argparse
import json
import re
import sys
from pathlib import Path

CHOT = json.loads((Path(__file__).resolve().parent.parent / "references" / "da-chot.json").read_text(encoding="utf-8"))


def sua_doc(chu):
    """Thay các từ máy đọc sai theo docDung. Trả về (chữ đã sửa, danh sách thay)."""
    thay = []
    for goc, doc in CHOT["docDung"].items():
        if goc.startswith("_"):
            continue
        mau = re.compile(rf"(?<![\w‑-]){re.escape(goc)}(?![\w‑-])")
        n = len(mau.findall(chu))
        if n:
            chu = mau.sub(doc, chu)
            thay.append(f"{goc} → {doc} ({n} chỗ)")
    # Ây-Ai, Ây Ai gõ tay: đổi sang gạch không ngắt
    chu2 = re.sub(r"Ây[ -]Ai", "Ây‑Ai", chu)
    if chu2 != chu:
        thay.append("Ây Ai → Ây‑Ai (gạch không ngắt)")
    return chu2, thay


def loai_du_an(da):
    """Loại video ghi trong <dự án>/loai.txt (nhiều từ cách nhau bằng dấu cách, vd "gioi-thieu khong-mat").
    'khong-mat': người dẫn chưa có kho cảnh mặt mình, lap_canh.py chặn clip nằm trong thư mục "... CO MAT ...". 'gioi-thieu': video giới thiệu bản thân/BNI (24/11/2026), không phải video
    kênh nên không ép đoạn cuối hỏi người xem và chỉ về bình luận ghim; vẫn giữ cách đọc, luật 9 và cảm xúc."""
    f = Path(da) / "loai.txt"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""


def kiem_doc(chu, ca_bai=True, gioi_thieu=False):
    """Trả về danh sách lỗi (rỗng là đạt)."""
    loi = []
    for luat in CHOT["camViet"]:
        for m in re.finditer(luat["mau"], chu):
            loi.append(f"'{m.group(0)}' ở ...{chu[max(0, m.start() - 20):m.end() + 10]}...: {luat['ly_do']}")
            break
    for goc in CHOT["docDung"]:
        if not goc.startswith("_") and re.search(rf"(?<![\w‑-]){re.escape(goc)}(?![\w‑-])", chu):
            loi.append(f"còn '{goc}' chưa đổi thành '{CHOT['docDung'][goc]}'")
    loi += kiem_cau_ket(chu)
    if not ca_bai:
        return loi
    if gioi_thieu:
        nhan = chu.count("!") + chu.count("?")
        if nhan < CHOT["cam"]["nhanToiThieu"]:
            loi.append("thiếu cảm xúc: chưa có câu cảm thán nào, thêm dấu chấm than ở câu chào hoặc câu ghi nhớ")
        return loi + kiem_ve(chu)[0]
    doan = [d.strip() for d in chu.strip().split("\n") if d.strip()]
    if len(doan) < 2:
        loi.append("bản đọc cần chia đoạn, đoạn cuối là câu hỏi và câu chỉ về bình luận ghim")
        return loi
    giua, cuoi = " ".join(doan[:-1]), doan[-1]
    c = CHOT["cam"]
    nhan = giua.count("!") + giua.count("?")
    if nhan < c["nhanToiThieu"]:
        loi.append(f"thiếu cảm xúc: ngoài đoạn cuối chưa có câu cảm thán hay câu hỏi tu từ nào (cần ≥ {c['nhanToiThieu']}), "
                   "thêm ở móc câu hoặc chỗ bất ngờ, xem kich-ban.md")
    thap = giua.lower()
    tro = [t for t in c["troTu"] if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", thap)]
    if len(tro) < c["troTuToiThieu"]:
        loi.append(f"thiếu giọng nói chuyện: chưa có tiểu từ nào ({', '.join(c['troTu'][:6])}...)")
    if "?" not in cuoi or not cuoi.rstrip().endswith("!"):
        loi.append("đoạn cuối phải có câu hỏi cho người xem và kết bằng câu chỉ về bình luận ghim có dấu chấm than")
    loi += kiem_ve(chu)[0]
    return loi


# Luật 9 (16/11/2026): không xin bình luận một chữ để đổi tài liệu. Meta coi là kéo tương tác (engagement bait),
# YouTube cấm đổi phần thưởng lấy tương tác. Kết bằng câu hỏi thật rồi chỉ về bình luận ghim.
_XIN = r"(?:comment|còm ?men|bình luận chữ|inbox|nhắn tin chữ)"
_HOA = "A-ZĐÂĂÊÔƠƯÁÀẢÃẠÉÈẺẼẸÍÌỈĨỊÓÒỎÕỌÚÙỦŨỤÝỲỶỸỴẤẦẨẪẬẮẰẲẴẶẾỀỂỄỆỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰ"
_MAU_KET = [
    re.compile(_XIN + r"[^.!?\n]{0,60}?(?:gửi|nhận)", re.I),
    re.compile(r"(?:gửi|nhận)[^.!?\n]{0,40}?" + _XIN, re.I),
    re.compile(r"(?i:comment|bình luận)\s*:?\s+(?:chữ\s+)?(?!GHIM)[" + _HOA + r"]{2,}(?![a-zđà-ỹ])"),
]


def kiem_cau_ket(chu):
    """Trả về lỗi nếu chữ còn mời 'comment <TỪ KHÓA>' hay 'comment ... gửi/nhận'. Dùng cho bản đọc, loi.txt và chữ trên hình."""
    for m in _MAU_KET:
        g = m.search(chu)
        if g:
            return [f"câu kết xin bình luận đổi tài liệu ('{g.group(0)}'): bỏ vế này, giữ câu hỏi thật rồi chỉ về bình luận ghim "
                    "(ví dụ 'Hướng dẫn cài từng bước mình để sẵn ở bình luận ghim nhé!'), xem luật 9 trong da-chot.md"]
    return []


def kiem_ket_du_an(da):
    """Nghiệm thu luật 9 trên loi.txt (phụ đề), doc-tts.txt và chữ trên hình (canh.json). Trả về danh sách lỗi."""
    da = Path(da)
    loi = []
    for ten in ("loi.txt", "doc-tts.txt"):
        if (da / ten).exists():
            loi += [f"{ten}: {l}" for l in kiem_cau_ket((da / ten).read_text(encoding="utf-8").replace("\n", " "))]
    if (da / "canh.json").exists():
        c = json.loads((da / "canh.json").read_text(encoding="utf-8"))
        canh = c.get("canh", []) if isinstance(c, dict) else c
        # chỉ chữ hiện trên hình; bỏ tên loại cảnh và mã clip (24/11/2026: "ket-comment" + clip "TOI3" bị đọc nhầm thành "comment TOI")
        bo = {"tuKhoa", "loai", "clip", "ten", "canhNen", "kieuNen", "am", "amMoc", "anh", "video", "nguon"}
        chu = " | ".join(v for x in canh if isinstance(x, dict) for k, v in x.items() if k not in bo and isinstance(v, str))
        loi += [f"canh.json: {l}" for l in kiem_cau_ket(chu)]
        for x in canh:
            if isinstance(x, dict) and x.get("loai") == "ket-comment" and "comment" in str(x.get("tuKhoa", "")).lower():
                loi.append("canh.json: tuKhoa của ket-comment còn chữ comment")
    return loi


# Cảnh kết (21/11/2026): người dẫn chê cảnh giơ hai tay P02 lặp ở 6/8 video gần nhất. Clip kết không được trùng clip kết
# của 5 video đã dựng xong gần nhất. Gợi ý theo ý câu hỏi kết; P06, P09 (nửa sau), P17, P32 có logo nên không nằm trong gợi ý.
GOI_Y_KET = {"P01": "chỉ tay lên khung câu hỏi", "P09": "nghiêng người tò mò (chỉ nửa đầu)", "P12": "cười, video vui",
             "P38": "chỉnh micro, như đang nói với người xem", "P40": "đánh dấu danh sách, video hướng dẫn",
             "P35": "làm ở nhà, nhẹ nhàng", "P36": "cầm cà phê ngoài ban công, thư giãn", "P22": "chạm giao diện AI",
             "P08": "suy nghĩ, câu hỏi để ngẫm", "P04": "khoanh tay, chốt ý", "P03": "kinh ngạc", "P02": "giơ hai tay giới thiệu"}
LOAI_KET = ("ket-comment", "ket-phe")


def clip_ket(da):
    f = Path(da) / "canh.json"
    if not f.exists():
        return None
    c = json.loads(f.read_text(encoding="utf-8"))
    canh = c.get("canh", []) if isinstance(c, dict) else c
    for x in canh:
        if isinstance(x, dict) and x.get("loai") in LOAI_KET and x.get("clip"):
            return x["clip"], bool(x.get("choLapCanhKet"))
    return None


def kiem_canh_ket(da, so=5):
    """Clip kết của dự án không trùng clip kết của `so` video gần nhất đã có render/thanh-pham.mp4 cùng thư mục du-an.
    Trả về (danh sách lỗi, danh sách clip kết gần đây). Cố tình lặp thì ghi "choLapCanhKet": true trong cảnh kết."""
    da = Path(da).resolve()
    nay = clip_ket(da)
    xong = []
    for d in da.parent.iterdir():
        tp = d / "render" / "thanh-pham.mp4"
        if d.is_dir() and d != da and not d.name.startswith("_") and tp.exists() and clip_ket(d):
            xong.append((tp.stat().st_mtime, d.name, clip_ket(d)[0]))
    gan = [(t, ten, ma) for t, ten, ma in sorted(xong, reverse=True)[:so]]
    if not nay or nay[1]:
        return [], gan
    ma = nay[0]
    trung = [ten for _, ten, m in gan if m == ma]
    if not trung:
        return [], gan
    da_dung = {m for _, _, m in gan}
    goi_y = [f"{k} ({v})" for k, v in GOI_Y_KET.items() if k not in da_dung]
    return [f"cảnh kết dùng {ma} trùng video gần đây: {', '.join(trung)}. Đổi clip hợp ý câu hỏi kết, chưa dùng ở {so} video gần nhất: "
            + "; ".join(goi_y[:6])], gan


VE_CHAN, VE_NHAC = 9.0, 10.0


def kiem_ve(chu):
    """Đo độ dài vế (chữ giữa hai dấu câu) trước khi tạo giọng. Vế ngắn thì máy đọc rời, phải tạo lại cả bài.
    Đo 13/11/2026 trên 13 bản đã tạo: bản rời (dưới 1,6 giây mỗi hơi) có trung bình 6,7 đến 8,4 chữ mỗi vế
    (21 bản 1, 22 bản 1, 23 bản 1 và 3); bản đạt từ 9,2 trở lên; 9 đến 10 là vùng giáp ranh (15, 16, 18 được duyệt
    dù 1,54 đến 1,59 giây). Trả về (lỗi, nhắc)."""
    ve = [x.strip() for x in re.split(r"[,.?!:;…]+", chu) if x.strip()]
    if len(ve) < 8:
        return [], []
    so = [len(x.split()) for x in ve]
    tb = sum(so) / len(so)
    ngan = sorted(((n, x) for n, x in zip(so, ve)), key=lambda y: y[0])[:4]
    goi_y = "; ".join(f"«{x}»" for _, x in ngan)
    if tb < VE_CHAN:
        return [f"vế quá ngắn: trung bình {tb:.1f} chữ mỗi vế (cần ≥ {VE_CHAN}), máy sẽ đọc rời rạc. Bỏ bớt dấu phẩy, "
                f"nối vế bằng 'nên', 'thì', 'và', 'mà'. Vế ngắn nhất: {goi_y}"], []
    if tb < VE_NHAC:
        return [], [f"vế hơi ngắn: trung bình {tb:.1f} chữ mỗi vế, nhịp dễ dưới 1,6 giây. Nên nối thêm: {goi_y}"]
    return [], []


def kiem_nhac(ten):
    """Trả về lỗi (chuỗi) nếu bài nhạc không nằm trong nhacDuocDung, rỗng là đạt. Tên rỗng (dùng nhạc mặc định) cũng là lỗi:
    phải chọn rõ một bài được phép (20-Atrifie suýt dùng cong-nghe từ YouTube Audio Library)."""
    duoc = CHOT["nhacDuocDung"]["ten"]
    if ten not in duoc:
        return f"nhạc '{ten or '(mặc định)'}' chưa kiểm quyền dùng ngoài YouTube; chỉ dùng: {', '.join(duoc)} (ghi vào nhac.txt)"
    return ""


TRANG_THAI = {"co-san": "có sẵn trong công cụ, gõ lệnh là dùng", "plugin-chinh-thuc": "plugin trong chợ chính thức", "cai-them": "cài thêm từ nguồn khác"}


def _chuan(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "


def kiem_tinh_trang(da):
    """Luật 15 (12/11/2026, người dẫn góp ý video 22): video giới thiệu công cụ, skill, plugin phải kiểm tình trạng HIỆN TẠI
    của từng món ở nguồn gốc, ghi vào tinh-trang.json. Món đã tích hợp sẵn thì lời phải nói rõ có sẵn, không gọi là thứ phải cài.
    Trả về danh sách lỗi, rỗng là đạt."""
    import datetime
    da = Path(da)
    loi_txt = (da / "loi.txt").read_text(encoding="utf-8") if (da / "loi.txt").exists() else ""
    # Video giới thiệu bản thân và video edit từ file quay của học viên không phải video giới thiệu công cụ: bỏ luật 15
    # (thử máy học viên 24/11/2026: chữ "cái" bỏ dấu thành "cai" làm mọi video edit bị đòi tinh-trang.json)
    if {"edit", "gioi-thieu"} & set(loai_du_an(da).split()):
        return []
    chu = _chuan(loi_txt)
    co_cai = re.search(r"(?<!\w)cài(?!\w)", loi_txt.lower()) is not None  # dò "cài" trên bản CÒN dấu, không nhầm "cái"
    if not co_cai and not any(f" {k} " in chu for k in ("skill", "skills", "plugin", "mcp", "github", "repo", "extension")):
        return []
    f = da / "tinh-trang.json"
    if not f.exists():
        return ["video nói về công cụ, skill, plugin mà chưa có tinh-trang.json: kiểm từng món ở nguồn gốc (có sẵn, plugin chính thức hay cài thêm) rồi ghi vào đó"]
    d = json.loads(f.read_text(encoding="utf-8"))
    loi = []
    try:
        ngay = datetime.datetime.strptime(d.get("ngayKiem", ""), "%d/%m/%Y").date()
        if (datetime.date.today() - ngay).days > 14:
            loi.append(f"tình trạng công cụ kiểm từ {d['ngayKiem']}, quá 14 ngày: kiểm lại ở nguồn gốc")
    except ValueError:
        loi.append("tinh-trang.json thiếu ngayKiem dạng dd/mm/yyyy")
    mon = d.get("mon") or []
    if not mon:
        loi.append("tinh-trang.json chưa liệt kê món nào")
    chu_hinh = chu
    if (da / "canh.json").exists():
        c = json.loads((da / "canh.json").read_text(encoding="utf-8"))
        chu_hinh += _chuan(" ".join(str(x.get(k, "")) for x in c.get("canh", []) for k in ("tren", "duoi", "tieuDe")))
    for m in mon:
        ten, tt = m.get("ten", ""), m.get("trangThai", "")
        if tt not in TRANG_THAI:
            loi.append(f"{ten or '(không tên)'}: trangThai phải là một trong {', '.join(TRANG_THAI)}")
        if not m.get("nguon") or not m.get("cachLay"):
            loi.append(f"{ten}: thiếu nguon hoặc cachLay")
        if tt == "co-san":
            if " co san " not in chu and " tich hop san " not in chu:
                loi.append(f"{ten} đã có sẵn mà lời không nói 'có sẵn' hoặc 'tích hợp sẵn'")
            if f" cai {_chuan(ten).strip()} " in chu_hinh:
                loi.append(f"{ten} đã có sẵn mà lời hoặc chữ trên hình bảo 'cài {ten}'")
    return loi


def kiem_file(f, ca_bai=True):
    chu, thay = sua_doc(Path(f).read_text(encoding="utf-8"))
    return chu, thay, kiem_doc(chu, ca_bai)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an", nargs="?")
    ap.add_argument("--file", default="doc-tts.txt")
    ap.add_argument("--chu")
    ap.add_argument("--cau", action="store_true", help="câu lẻ: bỏ kiểm cảm xúc")
    a = ap.parse_args()
    if a.chu:
        chu, thay = sua_doc(a.chu)
        loi = kiem_doc(chu, not a.cau)
    else:
        chu, thay, loi = kiem_file(Path(a.du_an) / a.file, not a.cau)
    for t in thay:
        print("  tự thay:", t)
    for l in loi:
        print("✘", l)
    if loi:
        sys.exit(1)
    print("✔ bản đọc đúng luật đã chốt")
