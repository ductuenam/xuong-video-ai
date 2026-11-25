"""Sinh lệnh Muse L2 (đặt KOL vào bối cảnh) và L3 (clip nói) từ video.json + loi.json.

  viet_lenh.py anh  <thư mục video>   → lenh/L2-<nhóm>.txt (mỗi tin 3 cảnh)
  viet_lenh.py clip <thư mục video> [--nhom 3]  → lenh/L3-<nhóm>.txt (mỗi tin 3 clip)
Cảnh có cùng bối cảnh với cảnh khác vẫn tạo ảnh riêng (tư thế khác).
L3 chặn nếu soat_loi.py chưa QUA.
"""
import argparse, subprocess, sys
from pathlib import Path
from chung import doc_json

CACH_NOI = ("Cách nói: như cô gái trẻ đang đi chơi khu nghỉ quay vlog kể chuyện với người quen, giọng nữ miền Bắc trẻ, tươi, thân thiện, "
            "tự nhiên, có lên xuống giọng, nhấn nhẹ chữ quan trọng, chữ đệm cuối câu như nhá, đấy, thôi nói nhẹ và ngắn; ngắt hơi ngắn ở dấu phẩy "
            "và dấu chấm; tốc độ vừa khoảng 4,8 chữ mỗi giây, câu kể chậm hơn câu liệt kê; KHÔNG giọng đọc quảng cáo, không giọng livestream bán hàng, "
            "không điệu, không kéo dài cuối câu; nói ngay từ khung đầu, đọc đúng từng chữ như lời, không thêm không bớt, không lặp chữ. "
            "QUAN TRỌNG: nói hết lời trước giây 8,5, chữ cuối rõ trọn, sau đó im lặng, chỉ cười nhẹ nhìn máy đến hết video. "
            "Da mặt: da mặt trắng sáng, mịn màng, đều màu, xinh, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, nhưng vẫn là da người thật không bóng nhựa. Nét mặt: luôn tươi, cười khi nói, lông mày thả lỏng, không nhíu mày, không nheo mắt. Mắt: mở tự nhiên nhìn thẳng máy, chớp hai mắt cùng lúc, chớp thưa. "
            "Tay có động tác theo lời, đổi khoảng mỗi 1,5–2 giây, tay đủ năm ngón.")

def nhom(ds, n):
    return [ds[i:i + n] for i in range(0, len(ds), n)]

def lenh_anh(d, vj):
    out = []
    for k, g in enumerate(nhom(vj["canh"], 3), 1):
        chu = "ABC"
        phan = " ".join(f"ẢNH {chu[i]} (bối cảnh ảnh {i + 2}): {c['tu_the']}." for i, c in enumerate(g))
        t = (f"Ảnh 1 là cô gái người mẫu (giữ CHÍNH XÁC gương mặt, trang điểm, kiểu tóc, màu da, vóc dáng và TOÀN BỘ trang phục như ảnh 1: {vj['bo_do']}). "
             f"Ảnh 2{', 3' if len(g) > 1 else ''}{', 4' if len(g) > 2 else ''} là {len(g)} chỗ trong khu nghỉ. Tạo {len(g)} ảnh riêng, khung dọc 9:16, đặt cô ấy vào đúng từng chỗ, "
             "giữ nguyên bối cảnh như ảnh gốc (đồ vật, màu gỗ, ánh sáng), như ảnh bạn đi cùng chụp bằng điện thoại cầm tay ngang ngực. Ánh sáng trên người khớp ánh sáng "
             f"của chỗ đó, có bóng đổ thật, người đúng tỉ lệ với cửa và ghế. {phan} Giữ đúng mặt ảnh 1: trái xoan thon, cằm nhỏ, mắt to hai mí, mũi thon, tóc nâu hạt dẻ gợn sóng, mái thưa rẽ ngôi; không đổi màu tóc, không làm mặt bè. TRUNG CẢNH GẦN từ hông trở lên, mặt rộng khoảng một phần năm bề ngang khung (không chụp toàn thân trừ cảnh kết). Mặt nhìn thẳng máy, mắt mở to, cười mỉm vừa phải để mắt vẫn to; da mặt trắng sáng, mịn màng, đều màu, xinh, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, nhưng vẫn là da người thật không bóng nhựa; tay đủ năm ngón. "
             "Không hình xăm, không vòng cổ, không thêm phụ kiện, không chữ, không logo.")
        p = d / "lenh" / f"L2-{k}.txt"; p.parent.mkdir(exist_ok=True); p.write_text(t, encoding="utf-8")
        out.append(p); print(p.name, "đính: ảnh KOL bộ đồ đã duyệt +", ", ".join(c["boi_canh"] for c in g), "→", ", ".join(c["anh_kol"] for c in g))

def lenh_clip(d, vj, lj, n):
    r = subprocess.run([sys.executable, "-X", "utf8", str(Path(__file__).parent / "soat_loi.py"), str(d)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout); sys.exit("Lời chưa qua soat_loi.py — sửa loi.json trước.")
    loi = {c["id"]: c["loi"] for c in lj["canh"]}
    for k, g in enumerate(nhom(vj["canh"], n), 1):
        ten = ", ".join(f"video {i + 1} → {c['id']}-noi.mp4" for i, c in enumerate(g))
        than = " ".join(f"VIDEO {i + 1}: {c['dong_tac']}. Lời VIDEO {i + 1}: \"{loi[c['id']]}\"" for i, c in enumerate(g))
        t = (f"Tạo {len(g)} video riêng bằng Muse Video, mỗi video 10 giây, một cảnh liền, giữ nguyên tỉ lệ dọc 9:16, giữ CHÍNH XÁC khuôn mặt, trang điểm, tóc, "
             f"trang phục ({vj['bo_do']}) và bối cảnh như ảnh. Đặt tên tệp: {ten}. Video k dùng ảnh k làm khung hình đầu tiên. "
             "MÁY CỐ ĐỊNH như đặt trên chân máy ngang ngực, khoảng cách giữ nguyên suốt 10 giây, KHÔNG đẩy vào mặt, không xoay, không cắt cảnh, bối cảnh giữ nguyên y như khung đầu. "
             f"Ảnh cuối cùng đính kèm CHỈ là ảnh tham chiếu gương mặt chuẩn, không dùng làm khung. Giữ đúng gương mặt như ảnh tham chiếu suốt clip: trái xoan thon, cằm V, má không phồng, mắt to hai mí, tròng mắt nâu đen tự nhiên (không lens), mái thưa, tóc nâu đen; son hồng cam (không đỏ); kính râm tròng nâu (không tráng gương) cài đầu suốt clip. "
             f"{CACH_NOI} Không nhạc nền, không chữ, không phụ đề. {than} Gửi đủ {len(g)} video, xong chỉ báo kích thước và thời lượng.")
        p = d / "lenh" / f"L3-{k}.txt"; p.write_text(t, encoding="utf-8")
        print(p.name, f"({len(t)} ký tự) đính:", ", ".join(c["anh_kol"] for c in g), "+ ảnh bộ đồ đã duyệt (tham chiếu mặt, đính CUỐI)")

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("lenh"); a.add_argument("thu_muc"); a.add_argument("--nhom", type=int, default=3)
    x = a.parse_args(); d = Path(x.thu_muc); vj = doc_json(d / "video.json")
    if x.lenh == "anh": lenh_anh(d, vj)
    elif x.lenh == "clip": lenh_clip(d, vj, doc_json(d / "loi.json"), x.nhom)
    else: sys.exit(__doc__)
