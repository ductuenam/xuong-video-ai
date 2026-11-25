"""Soát kịch bản loi.json trước khi gửi Muse (máy soát; người soát là agent nd-soi-loi-giong).

  soat_loi.py <thư mục video>
Chặn (thoát mã 1): cảnh quá 40 chữ, cả bài ngoài 170–235 chữ, cụm hứa hẹn/tuyệt đối, chữ viết tắt,
KOL kể trải nghiệm đã ở thật, thiếu tự nhận người mẫu ảo (khi không có nhãn trên hình), thiếu kêu gọi.
Cảnh báo: cảnh không có chữ đệm khẩu ngữ, chữ đệm lặp quá 3 lần, câu dài quá 28 chữ (mẫu dài nhất 25), từ văn viết.
"""
import re, sys
from pathlib import Path
from collections import Counter
from chung import doc_json

CAM = ["cam kết", "đảm bảo", "chắc chắn", "100%", "một trăm phần trăm", "rẻ nhất", "tốt nhất", "đẹp nhất", "duy nhất",
       "số một", "kín phòng", "cháy phòng", "triệu view", "giảm giá", "khuyến mãi", "sắp hết", "chỉ còn", "miễn phí"]
TRAI_NGHIEM = ["em ngủ", "tối qua", "hôm qua em", "em đã ở", "em ở đây mấy", "em ăn thử", "em tắm"]
VAN_VIET = ["tọa lạc", "sở hữu", "mang đến", "trải nghiệm tuyệt vời", "đẳng cấp", "hoàn hảo", "lý tưởng", "không gian sang trọng"]
DEM = ["nhá", "nhé", "đấy", "thôi", "luôn", "cơ chứ", "nữa", "nha", "ơi", "á", "mà", "đâu", "chứ"]

def chu(s):
    return re.findall(r"[\wÀ-ỹ%]+", s.lower())

if __name__ == "__main__":
    d = Path(sys.argv[1]); lj = doc_json(d / "loi.json")
    chan, bao = [], []
    tong, dem = 0, Counter()
    canh = lj["canh"]
    for c in canh:
        t = c["loi"]; n = len(chu(t)); tong += n
        if n > 40: chan.append(f"{c['id']}: {n} chữ (tối đa 40 để Muse nói xong trước giây 8,5)")
        if n < 14: bao.append(f"{c['id']}: chỉ {n} chữ, cảnh sẽ ngắn hoặc trống tiếng")
        tl = " " + t.lower() + " "
        for k in CAM:
            if k in tl: chan.append(f"{c['id']}: có cụm hứa hẹn/tuyệt đối '{k}'")
        for k in TRAI_NGHIEM:
            if k in tl: chan.append(f"{c['id']}: KOL ảo kể trải nghiệm thật '{k}'")
        for k in VAN_VIET:
            if k in tl: bao.append(f"{c['id']}: văn viết '{k}' (nói như người thật thì đổi)")
        if re.search(r"\b[A-ZĐ]{2,}\b", t) and "AI" not in re.findall(r"\b[A-ZĐ]{2,}\b", t):
            chan.append(f"{c['id']}: có chữ viết tắt in hoa, Muse đọc sai — viết theo cách đọc")
        if re.search(r"\d", t): chan.append(f"{c['id']}: có chữ số — viết bằng chữ theo cách đọc")
        co_dem = [k for k in DEM if re.search(rf"(?<![\wÀ-ỹ]){k}(?![\wÀ-ỹ])", t.lower())]
        if not co_dem: bao.append(f"{c['id']}: không có chữ đệm khẩu ngữ — dễ nghe như đọc")
        dem.update(co_dem)
        for cau in re.split(r"[.?!]", t):
            if len(chu(cau)) > 28: bao.append(f"{c['id']}: câu dài {len(chu(cau))} chữ: '{cau.strip()[:50]}…'")
    for k, v in dem.items():
        if v > 3 and k not in ("mà", "ơi"): bao.append(f"chữ đệm '{k}' lặp {v} lần cả bài")
    if not 170 <= tong <= 235: chan.append(f"cả bài {tong} chữ (cần 170–235 cho 45–55 giây)")
    toan = " ".join(c["loi"].lower() for c in canh)
    if "người mẫu ảo" not in toan and not lj.get("nhan_ai_tren_hinh", True):
        chan.append("không tự nhận người mẫu ảo và không có nhãn AI trên hình")
    if not any(k in chu(canh[-1]["loi"]) for k in ["link", "nhắn", "bình", "luận", "đăng", "ký", "kí", "inbox", "gọi", "đặt"]):
        chan.append("cảnh cuối không có lời kêu gọi (đăng ký / nhắn / bình luận / đặt phòng)")
    print(f"Cả bài {tong} chữ, {len(canh)} cảnh, ước {tong/4.6:.0f} giây nói. Chữ đệm: {dict(dem)}")
    for b in bao: print("  cảnh báo:", b)
    if chan:
        print("CHẶN:"); [print("  -", c) for c in chan]; sys.exit(1)
    print("QUA máy soát lời (vẫn phải qua agent nd-soi-loi-giong).")
