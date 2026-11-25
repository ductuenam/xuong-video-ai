"""Sinh lệnh Muse cho KOL giọng livestream, từ kol.json và video.json. Tự soát lời trước khi gửi.

Dùng:
  python viet_lenh.py kol                 → <thu_muc_kol>/lenh-kol.txt (Bước 0: dựng KOL)
  python viet_lenh.py anh  <thư mục video> → lenh-anh.txt (Bước 2: ảnh KOL mặc sản phẩm)
  python viet_lenh.py video <thư mục video> → tin1.txt (3 cảnh nói), tin2.txt (2 cảnh cận), loi1-3.txt

kol.json nằm trong thu_muc_kol (mẫu: kol.mau.json của skill). video.json nằm trong thư mục video
(mẫu: video.mau.json). Các câu về giọng, nét mặt, mắt, tay, dứt câu trước giây 8,5 là phần đã chạy đạt,
không sửa; chỉ đổi mô tả trang phục, động tác chi tiết và lời.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, in_utf8, thu_muc  # noqa: E402

TOI_DA_CHU = 44
NEN_CHU = (35, 42)

DAU = ("Tạo 3 video riêng bằng Muse Video, mỗi video 10 giây, một cảnh liền, giữ nguyên tỉ lệ dọc 9:16 của ảnh, giữ nguyên khuôn mặt, tóc, {ten} và căn phòng như ảnh. "
       "Đặt tên tệp: video 1 → s1-noi.mp4, video 2 → s2-noi.mp4, video 3 → s3-xoay.mp4. Video 1 và video 2 dùng ảnh 1 làm khung hình đầu tiên; video 3 dùng ảnh 2 làm khung hình đầu tiên. Máy quay đứng yên tuyệt đối, không zoom. "
       "Cách nói: như một người bán hàng livestream chuyên nghiệp đang lên sóng chốt đơn, nhiệt tình, tự tin, hào hứng thật sự; nói nhanh và liền mạch khoảng 5,5 chữ mỗi giây, nhấn mạnh từ khóa, lên giọng ở câu hỏi kéo khách như \"đúng không {goi}\"; {giong}, rõ từng chữ; KHÔNG điệu, không nũng nịu, không làm giọng trẻ con, không kéo dài cuối câu; nói ngay từ khung đầu, không ngập ngừng, đọc đúng từng chữ như lời, không thêm không bớt, không lặp chữ nào. "
       "QUAN TRỌNG: nói hết lời trước giây 8,5, chữ cuối nói rõ trọn vẹn, sau đó im lặng hoàn toàn, chỉ cười nhẹ nhìn máy đến hết video. "
       "Nét mặt: luôn tươi, cười khi nói, lông mày thả lỏng để yên, KHÔNG nhíu mày, không nhăn trán, không nheo mắt; năng lượng nằm ở giọng nói và đôi tay, không nằm ở lông mày. "
       "GIỮ ĐÚNG GƯƠNG MẶT NHƯ ẢNH trong mọi khung: mặt thon, mắt hiền mở tự nhiên, KHÔNG mở to mắt tròn, không nhướn mày, không cười toác lộ lợi; đầu luôn thẳng, nghiêng tối đa 10 độ. Da mặt, cổ, tay luôn trắng sáng mịn đều màu, KHÔNG có nốt ruồi, không chấm nâu, không tàn nhang, không mụn ở bất kỳ khung nào. "
       "Mắt: mở to tự nhiên, nhìn thẳng máy, chỉ chớp hai mắt cùng lúc và chớp thưa, khoảng 3 đến 4 giây mới chớp một lần, không nhắm mắt khi cười hay khi nhấn giọng, không nháy một mắt. "
       "Tay luôn có động tác như người livestream, đổi động tác khoảng mỗi 1,5 giây, không đặt tay lên ngực. Trang phục luôn giữ nguyên: {mo_ta}.{khoa} Chân luôn giữ như ảnh: {chan}. Không nhạc nền, không chữ, không phụ đề. ")
CUOI1 = "giây 8,5-10 im lặng, hai tay đặt nhẹ hai bên eo, cười nhìn máy."
CUOI2 = "giây 8,5-10 im lặng, hai tay buông tự nhiên, đứng yên cười nhẹ nhìn máy."
V3 = ("máy khóa chặt trên chân máy suốt 10 giây, không zoom, không tiến, luôn thấy toàn thân từ đỉnh đầu tới giày như ảnh 2; "
      "giây 0-1,5 đứng thẳng nhìn máy và bắt đầu nói; giây 1,5-3,5 xoay người nghiêng 30 độ sang trái khoe dáng rồi quay lại nhìn máy, không quay lưng, không bước; "
      "giây 3,5-5 tay phải chống nhẹ hông; giây 5-7 tay phải giơ ngón tay đếm khi nói màu; giây 7-8,5 tay phải đưa ra phía trước như mời; giây 8,5-10 im lặng, gật đầu cười nhẹ nhìn máy, mắt vẫn mở, không híp mắt.")
CAN = ("Tạo 2 video riêng bằng Muse Video, mỗi video 10 giây, đây là cảnh cận chi tiết {ten}, KHÔNG nói, không giọng, không nhạc, không chữ. "
       "Đặt tên tệp: video 1 → q4-can-tren.mp4, video 2 → q5-can-duoi.mp4. Mỗi video là một cảnh liền duy nhất, không cắt cảnh, nền luôn là căn phòng đúng như ảnh. "
       "Giữ nguyên tỉ lệ dọc, màu, chất liệu và kiểu dáng trang phục đúng như ảnh.{khoa} Chân (nếu thấy) giữ như ảnh: {chan}. Máy không ngẩng lên, mắt và mặt không bao giờ vào khung. Bàn tay tự nhiên đủ năm ngón, da tay trắng sáng mịn, không nốt ruồi, không chấm nâu. "
       "VIDEO 1, khung đầu là ảnh 1 (cận thân trên): máy trôi rất chậm lại gần tối đa 5% trong cả video, không tiến sát hơn, rung tay rất nhẹ; {d1} "
       "VIDEO 2 phải giữ nguyên khung hình như ảnh 2 suốt 10 giây: máy khóa chặt trên chân máy, không ngẩng lên, không hạ xuống, không tiến, không lùi, không thêm chi tiết nào; khung đầu là ảnh 2 (phần dưới và giày): {d2} Gửi đủ 2 video, xong chỉ báo kích thước và thời lượng.")

KOL = ("Tạo 4 ảnh chụp chân thực, khung dọc 9:16, mỗi ảnh là cùng MỘT người: {mo_ta_nguoi}. Cô ấy đứng toàn thân giữa khung, từ đỉnh đầu tới bàn chân, "
       "trong {mo_ta_phong}. Trang phục nền đơn giản: {trang_phuc_nen}. Chân: {mo_ta_chan}. Tư thế đứng thẳng thoải mái nhìn thẳng máy, hai tay buông tự nhiên, cười nhẹ mím môi, mắt mở tự nhiên. "
       "Máy đặt ngang ngực, ánh sáng ban ngày mềm, ảnh như chụp bằng điện thoại, da thật có lỗ chân lông, da mặt trắng sáng mịn đều màu, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, không vết thâm, màu tự nhiên. Không chữ, không logo, không giống bất kỳ người nổi tiếng nào. "
       "Bốn ảnh khác nhau nhẹ về gương mặt để tôi chọn một.")
KOL_ANH = (" Ảnh đính kèm là ảnh chân dung người thật đã đồng ý cho dùng: giữ đúng gương mặt, kiểu tóc, màu da và tuổi của người trong ảnh, chỉ đặt vào căn phòng và tư thế như trên.")

ANH = ("Sửa ảnh 1 (ảnh người mẫu). Giữ CHÍNH XÁC khuôn mặt, đường nét, trang điểm, kiểu tóc, màu da, tuổi và vóc dáng của cô ấy, giữ nguyên căn phòng: {mo_ta_phong}. "
       "Chỉ thay toàn bộ trang phục cho đúng như sản phẩm ở các ảnh sau (ảnh của nhà bán): {mo_ta}.{khoa} Bỏ hết trang phục cũ, không thêm túi xách, không thêm vòng cổ. "
       "Chân: {mo_ta_chan}; nếu bộ đồ để lộ chân thì chân phải đúng như vậy, da chân cùng màu sáng với da mặt và tay. Da mặt: da mặt trắng sáng mịn đều màu, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, không vết thâm; ảnh 1 có nốt ruồi, chấm nâu thì xóa đi, giữ nguyên mọi đường nét khác. "
       "Tư thế: đứng giữa khung nhìn thẳng máy, thoải mái, hai tay buông tự nhiên, cười nhẹ mím môi. Khung dọc 9:16, TOÀN THÂN từ đỉnh đầu tới bàn chân, giày nằm trọn trong khung, "
       "máy ngang ngực. Ảnh chụp điện thoại chân thực, màu tự nhiên, đúng màu sản phẩm, không chữ, không logo lạ. Tạo 2 ảnh để tôi chọn.")

CHAN_MAC_DINH = ("đôi chân thon thẳng, da chân trắng sáng mịn đều màu như da mặt, đầu gối sáng sạch không thâm không đỏ, "
                 "không vết, không sần, không gân xanh, không nốt ruồi, không chấm nâu")


def cau_khoa(v):
    """Câu khóa chi tiết dễ bị vẽ sai (vd cổ lá sen bị vẽ thành cổ đứng). Lấy từ video.json "chi_tiet_khoa"."""
    k = [x.strip() for x in v.get("chi_tiet_khoa", []) if x.strip()]
    return (" BẮT BUỘC đúng từng chi tiết: " + "; ".join(k) + ".") if k else ""


VIET_TAT = re.compile(r"\b(\d*X{1,3}L|XS|[SML]\b|cm\b|kg\b|\d+%)", re.I)


def dem(s):
    return len(s.split())


def soat_loi(i, s, goi):
    """Chặn lời quá dài, chữ viết tắt (Muse đọc sai), 'shop' (Muse đọc thành 'sóc')."""
    n, loi = dem(s), []
    if n > TOI_DA_CHU:
        loi.append(f"{n} chữ, quá {TOI_DA_CHU}: Muse sẽ nói tới mép 10 giây và cắt chữ cuối")
    elif not NEN_CHU[0] <= n <= TOI_DA_CHU:
        print(f"  ! Lời {i}: {n} chữ (nên {NEN_CHU[0]}–{TOI_DA_CHU}); dưới 35 chữ Muse nói chậm, nghỉ nhiều")
    m = VIET_TAT.findall(s)
    if m:
        loi.append(f"có chữ viết tắt/ký hiệu {sorted(set(m))}: viết theo cách đọc (size em-mờ, năm mươi cân, phân)")
    if re.search(r"\bshop\b", s, re.I):
        loi.append("có chữ 'shop': viết 'nhà bán' hoặc tên shop đọc được")
    if any(ch.isdigit() for ch in s):
        print(f"  ! Lời {i} có chữ số: Muse đọc được số đơn giản, nhưng an toàn nhất là viết bằng chữ")
    return loi


CAU_KEO = ("cả nhà", "chị em", "các chị", "anh em", "nhìn cho em", "nhìn này", "đúng không", "nhắn", "tư vấn",
           "em chọn size", "xem ngay", "không thể bỏ qua", "nha", "đây", "cách phối", "ưng", "chốt đơn")


def chuan(s):
    return " ".join(re.sub(r"[^\w\s]", " ", s.lower()).split())


def y_duoc_noi(nguon):
    """Cột đầu bảng dưới mục '## Được nói' của nguon.md: mỗi ô là một cụm được phép nói."""
    y, trong = [], False
    for dong in nguon.splitlines():
        if dong.startswith("## "):
            trong = dong.lower().startswith("## được nói")
            continue
        if trong and dong.startswith("|"):
            o = chuan(dong.strip("|").split("|")[0])
            if o and not o.startswith("ý trong lời") and set(o) - {"-", " "}:
                y.append(o)
    return y


DEM = set("mà thì là cũng đều rất lắm này kia luôn nha nhé ạ đấy đây rồi cho em mình các chị cả nhà với và có được "
          "nhìn hẳn cực quá nữa thế vậy ơi nào của một những nên thôi lại còn khi thích phong cách vẫn phải chiếc cái đâu "
          "bận mặc kiểu gì thấy bên trong lên áo hơn ngay chất nó trông".split())


LUON_CHAN = ("sắp hết", "cháy hàng", "số lượng có hạn", "có hạn", "giảm giá", "giảm nửa giá", "sale", "khuyến mãi",
             "hàng hiệu", "chính hãng", "duy nhất", "rẻ nhất", "tốt nhất", "số một", "cuối cùng", "chỉ hôm nay",
             "trả hàng miễn phí", "bảo hành", "cam kết", "chữa", "giảm cân")


def soat_nguon(i, s, y):
    """CỔNG NGUỒN: bỏ khỏi mỗi vế các cụm trong bảng 'Được nói', các cụm kéo khách và chữ đệm;
    còn BẤT KỲ chữ có nghĩa nào là ý không nguồn -> chặn. Cụm khan hiếm, giảm giá, cam kết, so sánh tuyệt đối
    (LUON_CHAN) luôn bị chặn, kể cả khi bảng có ghi. Lỗi đã gặp: dùng lại lời cũ có 'đi Đà Lạt'."""
    loi = []
    for c in LUON_CHAN:
        if re.search(r"(?<!\w)" + re.escape(c) + r"(?!\w)", chuan(s)):
            loi.append(f"có cụm \"{c}\": khan hiếm, giảm giá, cam kết hay so sánh tuyệt đối không được tự nói (luật quảng cáo, sổ lỗi)")
    for ve in re.split(r"[,.;?!]| hay ", s):
        v = " " + chuan(ve) + " "
        for c in sorted(y + list(CAU_KEO), key=len, reverse=True):
            v = v.replace(" " + c + " ", " | ")
        con = [w for w in v.replace("|", " ").split() if w not in DEM]
        if con:
            loi.append(f"vế \"{ve.strip()}\" còn chữ không có nguồn: {' '.join(con)} (thêm vào bảng 'Được nói' kèm nguồn, hoặc bỏ)")
    return loi


def main():
    in_utf8()
    if len(sys.argv) < 2 or sys.argv[1] not in ("kol", "anh", "video"):
        sys.exit(__doc__)
    cfg = doc_cau_hinh()
    d_kol = thu_muc(cfg, "thu_muc_kol")
    f_kol = d_kol / "kol.json"
    if not f_kol.is_file():
        sys.exit(f"Chưa có {f_kol}. Chép kol.mau.json của skill vào đó rồi điền (Bước 0).")
    kol = json.loads(f_kol.read_text(encoding="utf-8"))
    if sys.argv[1] == "kol":
        kol.setdefault("mo_ta_chan", CHAN_MAC_DINH)
        t = KOL.format(**kol) + (KOL_ANH if kol.get("anh_khach") else "")
        (d_kol / "lenh-kol.txt").write_text(t, encoding="utf-8")
        print(f"Đã ghi {d_kol / 'lenh-kol.txt'} ({dem(t)} chữ).")
        return
    if len(sys.argv) < 3:
        sys.exit("Thiếu thư mục video.")
    d = Path(sys.argv[2])
    v = json.loads((d / "video.json").read_text(encoding="utf-8"))
    if sys.argv[1] == "anh":
        if not v.get("chi_tiet_khoa"):
            sys.exit("video.json chưa có \"chi_tiet_khoa\": liệt kê 2–5 chi tiết dễ sai (kiểu cổ, cúc, túi, tay, gấu), "
                     "ghi cả cái KHÔNG được thành, vd \"cổ lá sen bẻ tròn màu kem, không phải cổ đứng\".")
        (d / "lenh-anh.txt").write_text(ANH.format(mo_ta_phong=kol["mo_ta_phong"], mo_ta=v["mo_ta"], khoa=cau_khoa(v),
                                                   mo_ta_chan=kol.get("mo_ta_chan", CHAN_MAC_DINH)), encoding="utf-8")
        print(f"Đã ghi {d / 'lenh-anh.txt'}. Đính ảnh chuẩn KOL TRƯỚC, rồi 1–2 ảnh sản phẩm của nhà bán.")
        return
    goi = kol.get("goi_khach", "cả nhà")
    from khoa_mat import cong  # CỔNG KHÓA MẶT: ảnh gốc phải qua (mặt, chân, mẫu áo) mới được viết lệnh video
    cong(d, "anh")
    hong = []
    f_nguon = d / "nguon.md"
    if not f_nguon.is_file():
        sys.exit(f"Chưa có {f_nguon}. Lập nguồn theo references/mau-ghi-chu.md trước khi viết lời (Bước 1).")
    y = y_duoc_noi(f_nguon.read_text(encoding="utf-8"))
    if not y:
        sys.exit("nguon.md chưa có bảng dưới mục '## Được nói' (cột 1 = cụm được nói, cột 2 = nguồn).")
    for i in (1, 2, 3):
        hong += [f"Lời {i}: {x}" for x in soat_loi(i, v[f"l{i}"], goi)]
        hong += [f"Lời {i}: {x}" for x in soat_nguon(i, v[f"l{i}"], y)]
    if hong:
        print("✘ Chưa ghi lệnh, sửa video.json:\n  " + "\n  ".join(hong))
        sys.exit(1)
    chan = kol.get("mo_ta_chan", CHAN_MAC_DINH)
    dau = DAU.format(ten=v["ten"], mo_ta=v["mo_ta"], goi=goi, giong=kol.get("giong", "giọng nữ miền Bắc trẻ"),
                     khoa=cau_khoa(v), chan=chan)
    t1 = dau + (f"VIDEO 1: {v['v1']} {CUOI1} Lời VIDEO 1: \"{v['l1']}\" VIDEO 2: {v['v2']} {CUOI2} Lời VIDEO 2: \"{v['l2']}\" "
                f"VIDEO 3: {V3} Lời VIDEO 3: \"{v['l3']}\" Gửi đủ 3 video, xong chỉ báo kích thước và thời lượng.")
    (d / "tin1.txt").write_text(t1, encoding="utf-8")
    (d / "tin2.txt").write_text(CAN.format(ten=v["ten"], d1=v["d1"], d2=v["d2"], khoa=cau_khoa(v), chan=chan), encoding="utf-8")
    for i in (1, 2, 3):
        (d / f"loi{i}.txt").write_text(v[f"l{i}"], encoding="utf-8")
    print(f"Đã ghi tin1.txt, tin2.txt, loi1-3.txt. Số chữ: {[dem(v[f'l{i}']) for i in (1, 2, 3)]}")


if __name__ == "__main__":
    main()
