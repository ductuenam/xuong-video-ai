"""Sinh lệnh Muse cho video KOL mặc thử đứng một chỗ (một khung đầu–giữa đùi, 2 cảnh nói 10 giây, có quay lưng).

Dùng:
  python viet_lenh.py anh   <thư mục video> → lenh-anh.txt (ảnh KOL mặc sản phẩm, toàn thân, trang điểm xinh hơn chút)
  python viet_lenh.py video <thư mục video> → tin1.txt (2 cảnh nói s1-noi, s2-noi), loi1.txt, loi2.txt

KOL lấy từ <thu_muc_kol>/kol.json (cau-hinh.json). video.json trong thư mục video có:
  ten, mo_ta, chi_tiet_khoa[], phoi (đồ phối), v1, l1, v2, l2  (mẫu: video.mau.json của skill)
Các câu về giọng, nét mặt, mắt, máy đứng yên, quay lưng, dứt lời là phần chặn lỗi đã học: không sửa,
chỉ đổi mô tả trang phục, động tác chi tiết và lời. Lời qua 2 cổng: độ dài/chữ viết tắt và CỔNG NGUỒN.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, in_utf8, thu_muc  # noqa: E402

TOI_DA_CHU = 46
NEN_CHU = (38, 46)

DAU = ("Tạo 2 video riêng bằng Muse Video, mỗi video 10 giây, một cảnh liền, giữ nguyên tỉ lệ dọc 9:16 của ảnh. CẢ HAI video đều dùng ảnh 1 làm khung hình đầu tiên; ảnh 2 là ảnh cận khuôn mặt chuẩn của chính cô ấy, chỉ để giữ đúng mặt, không dùng làm khung hình. "
       "Đặt tên tệp: video 1 → s1-noi.mp4, video 2 → s2-noi.mp4. "
       "Máy quay đặt trên chân máy, đứng yên tuyệt đối suốt 10 giây, không zoom, không tiến, không lùi, không lia: khung hình luôn đúng như ảnh 1, từ trên đỉnh đầu xuống giữa đùi, cô ấy đứng giữa khung, không bước đi. "
       "Giữ nguyên khuôn mặt, kiểu tóc, lớp trang điểm, {ten}, đồ phối và căn phòng như ảnh 1. "
       "Cách nói: như một người bán hàng online miền Bắc nhiều kinh nghiệm đang giới thiệu áo cho khách quen, nói nhanh và liền mạch khoảng 5,5 chữ mỗi giây, câu nối nhau tự nhiên, nhấn nhẹ từ khóa, giọng nói chuyện tự tin, vui vẻ; {giong}, rõ từng chữ; "
       "KHÔNG điệu, không nũng nịu, không làm giọng trẻ con, không kéo dài cuối câu, không cảm thán quá đà; nói ngay từ khung đầu, không ngập ngừng, đọc đúng từng chữ như lời, không thêm, không bớt, không lặp chữ nào. "
       "QUAN TRỌNG: nói hết lời trước giây 9,3, chữ cuối nói rõ trọn vẹn, sau đó im lặng, chỉ cười nhẹ nhìn máy đến hết video. "
       "Nét mặt: luôn tươi, cười khi nói, lông mày thả lỏng để yên, KHÔNG nhíu mày, không nhăn trán, không nheo mắt; năng lượng nằm ở giọng nói và đôi tay. "
       "GIỮ ĐÚNG GƯƠNG MẶT NHƯ ẢNH 1 VÀ ẢNH 2 trong mọi khung từ đầu tới cuối, kể cả khi nói và sau khi quay lưng rồi quay lại: mặt trái xoan thon, cằm thon nhỏ, hai má KHÔNG bầu ra, mặt không tròn hay bè ra khi nói, mắt to hai mí rõ như ảnh 2, mái thưa mỏng như ảnh, không nhướn mày, không cười toác lộ lợi, không ngửa cằm; đầu luôn thẳng, nghiêng tối đa 10 độ; son hồng nhạt và má hồng giữ đúng màu như ảnh. "
       "Da mặt xinh, mịn, trắng sáng đều màu, KHÔNG có nốt ruồi, không chấm nâu, không tàn nhang, không mụn trên mặt và cổ. "
       "Mắt: nhìn thẳng máy, chỉ chớp hai mắt cùng lúc và chớp thưa, khoảng 3 đến 4 giây mới chớp một lần, không nhắm mắt khi cười, không nháy một mắt. "
       "Tay: đổi động tác khoảng mỗi 1 đến 1,5 giây như người bán hàng thật; khi lời nhắc tới chi tiết nào thì tay chạm đúng chi tiết đó trên áo; ngón tay chạm nhẹ, đủ năm ngón, không kéo áo, không xuyên vào vải, không đặt tay lên ngực. "
       "Trang phục luôn giữ nguyên: {mo_ta}.{khoa} Đồ phối giữ nguyên: {phoi}. Da tay và da đùi trắng sáng mịn đều màu như ảnh. Không nhạc nền, không chữ, không phụ đề, không logo. ")
QUAY_LUNG = ("Khi quay lưng: trước khi xoay, tóc dài vén gọn sang trước một bên vai để thấy rõ lưng áo; xoay người chậm tại chỗ, hai chân gần như giữ nguyên chỗ; "
             "lưng áo trơn đúng như mặt trước, KHÔNG có chữ, logo, nhãn, khóa hay túi ở lưng, không có đường may giữa lưng, hai đường may tay raglan sau lưng cân hai bên; "
             "bo gấu sau lưng là một dải dệt kim liền; xoay lại thì khóa kéo vẫn một đường, một đầu khóa, không tự mở, hai túi vẫn ở thân dưới phía trước, mặt vẫn y như ảnh 1. ")
CUOI1 = "giây 9,3-10 im lặng, đứng thẳng đúng tư thế như ảnh 1, hai tay buông nhẹ hai bên, cười nhẹ nhìn máy."
CUOI2 = "giây 9,3-10 im lặng, một tay chống nhẹ hông, cười nhẹ nhìn máy, mắt vẫn mở."

ANH = ("Sửa ảnh 1 (ảnh người mẫu). Giữ CHÍNH XÁC khuôn mặt, đường nét, kiểu tóc, màu da, tuổi và vóc dáng của cô ấy, giữ nguyên căn phòng: {mo_ta_phong}. Ảnh 1 là mặt KOL đã được duyệt: KHÔNG vẽ lại khuôn mặt. "
       "Giữ nguyên lớp trang điểm đúng như ảnh 1 (son hồng nude nhạt, má hồng nhẹ, mắt cười cong, không kẻ đuôi mắt), không trang điểm thêm, không đổi mắt, mũi, môi, dáng mặt; Da mặt xinh, mịn, trắng sáng đều màu, KHÔNG có nốt ruồi, không chấm nâu, không tàn nhang, không mụn trên mặt và cổ. da thật có vân, không bóng sáp, không mịn như lọc. "
       "Chỉ thay toàn bộ trang phục cho đúng như sản phẩm ở các ảnh sau (ảnh của nhà bán): {mo_ta}.{khoa} Đồ phối: {phoi}. Bỏ hết trang phục cũ, không thêm túi xách, không thêm vòng cổ. "
       "Chân: {mo_ta_chan}; da chân cùng màu sáng với da mặt và tay. "
       "Tư thế: đứng giữa khung nhìn thẳng máy, thoải mái, hai tay buông nhẹ hai bên, cười nhẹ. Khung dọc 9:16, TOÀN THÂN từ đỉnh đầu tới bàn chân, giày nằm trọn trong khung, "
       "máy ngang ngực. Ảnh chụp điện thoại chân thực, màu tự nhiên, đúng màu sản phẩm, không chữ, không logo lạ. Tạo 2 ảnh để tôi chọn.")

CHAN_MAC_DINH = ("đôi chân thon thẳng, da chân trắng sáng mịn đều màu như da mặt, đầu gối sáng sạch không thâm không đỏ, "
                 "không vết, không sần, không gân xanh")


def cau_khoa(v):
    k = [x.strip() for x in v.get("chi_tiet_khoa", []) if x.strip()]
    return (" BẮT BUỘC đúng từng chi tiết: " + "; ".join(k) + ".") if k else ""


VIET_TAT = re.compile(r"\b(\d*X{1,3}L|XS|[SML]\b|cm\b|kg\b|\d+%|UV)", re.I)


def dem(s):
    return len(s.split())


def soat_loi(i, s):
    n, loi = dem(s), []
    if n > TOI_DA_CHU:
        loi.append(f"{n} chữ, quá {TOI_DA_CHU}: Muse sẽ nói tới mép 10 giây và cắt chữ cuối")
    elif n < NEN_CHU[0]:
        print(f"  ! Lời {i}: {n} chữ (nên {NEN_CHU[0]}–{TOI_DA_CHU}); ít chữ thì Muse nói chậm, kém nhịp video mẫu 5,6 chữ/giây")
    m = VIET_TAT.findall(s)
    if m:
        loi.append(f"có chữ viết tắt/ký hiệu {sorted(set(m))}: viết theo cách đọc (size lờ, năm mươi cân, tia cực tím)")
    if re.search(r"\bshop\b", s, re.I):
        loi.append("có chữ 'shop': viết 'nhà bán'")
    if any(ch.isdigit() for ch in s):
        loi.append("có chữ số: viết số bằng chữ để Muse đọc đúng")
    return loi


CAU_KEO = ("các anh", "anh em mình", "anh em", "các bác", "chị em", "cả nhà", "nhìn cho em", "nhìn này", "đúng không",
           "nhắn", "nhắn em", "tư vấn", "bấm vào", "bấm giỏ hàng", "giỏ hàng", "ưng", "đây", "đấy", "xem này", "mua tặng")


def chuan(s):
    return " ".join(re.sub(r"[^\w\s]", " ", s.lower()).split())


def y_duoc_noi(nguon):
    y, trong = [], False
    for dong in nguon.splitlines():
        if dong.startswith("## "):
            trong = dong.lower().startswith("## được nói")
            continue
        if trong and dong.startswith("|"):
            o = dong.strip("|").split("|")[0]
            if o.strip().lower().startswith("ý trong lời") or not (set(o) - {"-", " "}):
                continue
            y += [chuan(x) for x in o.split(",") if chuan(x)]
    return y


DEM = set("nhưng mẫu mà thì là cũng đều rất lắm này kia luôn nha nhé ạ đấy đây rồi cho em mình các chị cả nhà với và có được "
          "nhìn hẳn cực quá nữa thế vậy ơi nào của một những nên thôi lại còn khi vẫn phải chiếc cái đâu "
          "mặc kiểu gì thấy bên trong lên áo hơn ngay nó trông anh bác này đó bởi vì nếu như từ tới đến cho phần "
          "ai thì ra vào khoác chỉ ở sẽ hay không ấy để".split())

LUON_CHAN = ("sắp hết", "cháy hàng", "số lượng có hạn", "có hạn", "giảm giá", "sale", "khuyến mãi", "hàng hiệu",
             "chính hãng", "duy nhất", "rẻ nhất", "tốt nhất", "số một", "chỉ hôm nay", "bảo hành", "cam kết",
             "chống nước", "không thấm", "giữ ấm", "nỉ")


def soat_nguon(s, y):
    loi = []
    for c in LUON_CHAN:
        if re.search(r"(?<!\w)" + re.escape(c) + r"(?!\w)", chuan(s)):
            loi.append(f"có cụm \"{c}\": không có nguồn hoặc bị cấm (xem mục Không nói của nguon.md)")
    for ve in re.split(r"[,.;?!]", s):
        v = " " + chuan(ve) + " "
        for c in sorted(y + list(CAU_KEO), key=len, reverse=True):
            v = v.replace(" " + c + " ", " | ")
        con = [w for w in v.replace("|", " ").split() if w not in DEM]
        if con:
            loi.append(f"vế \"{ve.strip()}\" còn chữ không có nguồn: {' '.join(con)} (thêm vào bảng 'Được nói' kèm nguồn, hoặc bỏ)")
    return loi


def main():
    in_utf8()
    if len(sys.argv) < 3 or sys.argv[1] not in ("anh", "video"):
        sys.exit(__doc__)
    cfg = doc_cau_hinh()
    kol = json.loads((thu_muc(cfg, "thu_muc_kol") / "kol.json").read_text(encoding="utf-8"))
    d = Path(sys.argv[2])
    v = json.loads((d / "video.json").read_text(encoding="utf-8"))
    if not v.get("chi_tiet_khoa"):
        sys.exit("video.json chưa có \"chi_tiet_khoa\": 3–6 chi tiết dễ sai (cổ, khóa, túi, bo, lưng áo), ghi cả cái KHÔNG được thành.")
    if sys.argv[1] == "anh":
        t = ANH.format(mo_ta_phong=kol["mo_ta_phong"], mo_ta=v["mo_ta"], khoa=cau_khoa(v), phoi=v.get("phoi", ""),
                       mo_ta_chan=kol.get("mo_ta_chan", CHAN_MAC_DINH))
        (d / "lenh-anh.txt").write_text(t, encoding="utf-8")
        print(f"Đã ghi {d / 'lenh-anh.txt'}. Đính kol-chuan.png TRƯỚC, rồi 1–2 ảnh nhà bán (ảnh trải phẳng + ảnh cận chi tiết).")
        return
    from khoa_mat import cong
    cong(d, "anh")
    f_nguon = d / "nguon.md"
    if not f_nguon.is_file():
        sys.exit("Chưa có nguon.md (Bước 1).")
    y = y_duoc_noi(f_nguon.read_text(encoding="utf-8"))
    hong = []
    for i in (1, 2):
        hong += [f"Lời {i}: {x}" for x in soat_loi(i, v[f"l{i}"])]
        hong += [f"Lời {i}: {x}" for x in soat_nguon(v[f"l{i}"], y)]
    if "quay lưng" not in v["v1"]:
        hong.append("v1 chưa có động tác quay lưng khoe áo (video mẫu quay lưng ở giây 3–4,5)")
    if hong:
        print("✘ Chưa ghi lệnh, sửa video.json:\n  " + "\n  ".join(hong))
        sys.exit(1)
    dau = DAU.format(ten=v["ten"], mo_ta=v["mo_ta"], khoa=cau_khoa(v), phoi=v.get("phoi", ""),
                     giong=kol.get("giong", "giọng nữ miền Bắc trẻ"))
    t1 = dau + QUAY_LUNG + (f"VIDEO 1: {v['v1']} {CUOI1} Lời VIDEO 1: \"{v['l1']}\" "
                            f"VIDEO 2: {v['v2']} {CUOI2} Lời VIDEO 2: \"{v['l2']}\" Gửi đủ 2 video, xong chỉ báo kích thước và thời lượng.")
    (d / "tin1.txt").write_text(t1, encoding="utf-8")
    for i in (1, 2):
        (d / f"loi{i}.txt").write_text(v[f"l{i}"], encoding="utf-8")
    print(f"Đã ghi tin1.txt, loi1.txt, loi2.txt. Số chữ: {[dem(v[f'l{i}']) for i in (1, 2)]}")


if __name__ == "__main__":
    main()
