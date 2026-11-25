"""Ráp lệnh gửi Muse từ du-an.json: lệnh tạo ảnh và lệnh tạo video, chia lượt (Muse tạo tối đa 4 mỗi lượt).

Dùng: python lap_lenh.py <thu_muc_du_an>
Ghi ra <du_an>/lenh/anh-1.txt, anh-2.txt…, video-1.txt…  In số lượt cần gửi.
Chặn lỗi trước khi tốn lượt: trùng mã, thiếu mô tả, mô tả quá ngắn, có người trong cảnh.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, doc_du_an, in_utf8, ten_canh  # noqa: E402

CHUNG_ANH = ("Yêu cầu chung cho MỌI ảnh: ảnh chụp thật như ảnh tạp chí kiến trúc cảnh quan (không phải tranh vẽ, "
             "không 3D), dọc 9:16, {phong_cach}, cây xếp tầng cao - trung - thấp, có chiều sâu và tiền cảnh lá mờ nhẹ. "
             "Ánh sáng có hướng rõ (tia nắng xuyên lá, sương sớm, hoàng hôn hoặc đèn vàng ấm) và một điểm nhấn màu "
             "nổi trên nền xanh (lá phong đỏ, hoa giấy, hoa, cá koi đỏ cam, chậu men màu hoặc đèn vàng). "
             "Không có người, không chữ, không logo. Mỗi ảnh đặt đúng tên file như mình ghi.")
CHUNG_VIDEO = ("Yêu cầu chung cho MỌI video: dùng đúng ảnh đính kèm cùng tên làm khung hình đầu, dọc 9:16, 10 giây, "
               "Muse Video. Một cú máy liền, thật chậm và mượt như quay bằng gimbal, không cắt cảnh, không đổi góc đột "
               "ngột, máy chỉ đi một đoạn ngắn (khoảng một phần tư quãng đường), không lao sâu. Giữ nguyên thiết kế, "
               "hình dáng cây và chậu. Có chuyển động sống: lá khẽ đung đưa trong gió nhẹ, nước gợn, ánh sáng đổi rất nhẹ; không có hạt sáng hay đốm sáng bay lơ lửng trong không khí. "
               "Không người, không chữ. Đặt tên file video đúng như tên ảnh, thêm đuôi -video.mp4.")
# 3 thứ lô đã được khách duyệt luôn có (xem references/kho-canh.md mục "Ba thứ phải có")
NUOC = re.compile(r"hồ|koi|cá|thác|nước|bể|suối|vũng|ao|đài phun|chum", re.I)
SANG = re.compile(r"nắng|sương|đèn|hoàng hôn|bình minh|tia|vệt sáng|ánh sáng|chập tối|sau mưa|rọi", re.I)
MAU = re.compile(r"đỏ|cam|vàng|hồng|tím|hoa|men lam|phong|thiên điểu|đèn", re.I)
CAM_NGUOI = re.compile(r"\b(người|công nhân|cô gái|chàng trai|em bé|khách)\b", re.I)


def kiem(canh):
    loi, thay = [], set()
    for c in canh:
        t = ten_canh(c) if c.get("ma") and c.get("ten") else "?"
        if t in thay:
            loi.append(f"Trùng tên cảnh {t}")
        thay.add(t)
        if not re.fullmatch(r"[a-z0-9-]+", c.get("ten", "")):
            loi.append(f"{t}: 'ten' chỉ dùng chữ thường không dấu, số và dấu gạch (vd san-vuon-koi)")
        if len(c.get("anh", "")) < 80:
            loi.append(f"{t}: mô tả ảnh quá ngắn (<80 ký tự), ảnh ra sẽ đơn giản, ít cây")
        if len(c.get("may", "")) < 20:
            loi.append(f"{t}: thiếu mô tả chuyển động máy")
        if CAM_NGUOI.search(c.get("anh", "") + " " + c.get("may", "")):
            loi.append(f"{t}: có người trong mô tả; loại video này không có người")
    return loi


def canh_bao(canh):
    """Không chặn, chỉ nhắc: cảnh thiếu ánh sáng có hướng / điểm nhấn màu, lô ít cảnh có nước."""
    cb = []
    for c in canh:
        t, a = ten_canh(c), c.get("anh", "")
        if not SANG.search(a):
            cb.append(f"{t}: chưa tả ánh sáng có hướng (tia nắng, sương, hoàng hôn, đèn ấm) — ảnh dễ phẳng, nhạt")
        if not MAU.search(a):
            cb.append(f"{t}: chưa có điểm nhấn màu (phong đỏ, hoa giấy, koi cam, chậu men, đèn vàng) — dễ toàn một màu xanh")
    co_nuoc = sum(1 for c in canh if NUOC.search(c.get("anh", "")))
    if canh and co_nuoc * 2 < len(canh):
        cb.append(f"Chỉ {co_nuoc}/{len(canh)} cảnh có nước chuyển động; lô đã duyệt có hơn một nửa (hồ koi, thác, bể)")
    return cb


def main():
    in_utf8()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d, da = doc_du_an(sys.argv[1])
    cfg, _ = doc_cau_hinh()
    phong_cach = (cfg or {}).get("shop", {}).get("phong_cach", "nhiều cây, dày, xanh mướt, chậu cùng một bộ, sạch sẽ, sang trọng")
    n = int((cfg or {}).get("so_canh_moi_luot", 4))
    canh = da.get("canh", [])
    loi = kiem(canh)
    if loi:
        print("✘ CHƯA RÁP ĐƯỢC LỆNH:")
        for x in loi:
            print("  -", x)
        sys.exit(1)
    for x in canh_bao(canh):
        print("⚠", x)
    ra = d / "lenh"
    ra.mkdir(exist_ok=True)
    for f in ra.glob("*.txt"):
        f.unlink()
    lo = [canh[i:i + n] for i in range(0, len(canh), n)]
    for i, nhom in enumerate(lo, 1):
        ten = ", ".join(ten_canh(c) for c in nhom)
        anh = [f"Tạo {len(nhom)} ảnh thiết kế cho shop cây cảnh, mỗi ảnh một không gian khác hẳn nhau ({ten}).",
               CHUNG_ANH.format(phong_cach=phong_cach), ""]
        anh += [f"{ten_canh(c)}: {c['anh']}" for c in nhom]
        (ra / f"anh-{i}.txt").write_text("\n".join(anh), encoding="utf-8")
        vid = [f"Tạo {len(nhom)} video từ {len(nhom)} ảnh đính kèm ({ten}).", CHUNG_VIDEO, ""]
        vid += [f"{ten_canh(c)}: {c['may']}" for c in nhom]
        (ra / f"video-{i}.txt").write_text("\n".join(vid), encoding="utf-8")
    print(f"✔ {len(canh)} cảnh → {len(lo)} lượt ảnh + {len(lo)} lượt video, lệnh ở {ra}")
    for i, nhom in enumerate(lo, 1):
        print(f"  Lượt {i}: " + ", ".join(ten_canh(c) for c in nhom))


if __name__ == "__main__":
    main()
