"""Dò xem chủ đề sắp làm đã có video chưa, để nhắc người dẫn trước khi làm trùng. Chạy TRƯỚC khi viết kịch bản.
  python tim_trung.py <thư mục kênh> <từ khóa> [<từ khóa>...]
Ví dụ: python tim_trung.py "<thư mục kênh>" "Story Cutter" "Chat Video Pro"
Tìm trong tên thư mục, loi.txt, doc-tts.txt, content.md của du-an/ và các bài trong BAI-DANG/ (kèm trạng thái: sẵn sàng, đã lên lịch, đã đăng).
Không phân biệt hoa thường, có dấu hay không dấu, gạch nối hay khoảng trắng. Mã thoát 1 khi có trùng."""
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TRANG_THAI = {"0-can-bo-sung": "cần bổ sung", "1-san-sang": "sẵn sàng đăng", "2-da-len-lich": "đã lên lịch", "3-da-dang": "ĐÃ ĐĂNG"}
FILE_DO = ("loi.txt", "doc-tts.txt", "content.md")
# Từ quá chung, kênh nhắc ở gần như mọi video: không dùng làm từ khóa trùng (video 22 bị khớp nhầm video 01 vì "Claude")
CHUNG = {"claude", "claude code", "ai", "github", "skill", "skills", "agent", "ai agent", "ai agents", "chatgpt", "gpt", "gemini", "mien phi", "ma nguon mo", "code", "video"}


def chuan(s):
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def co(k, noi):
    return f" {k} " in f" {noi} "  # khớp nguyên từ: "rag" không khớp "storage"


def do(thu_muc, tu_khoa):
    kq = []
    for tm in sorted(thu_muc.iterdir()) if thu_muc.exists() else []:
        if not tm.is_dir():
            continue
        cho = []
        if any(co(k, chuan(tm.name)) for k in tu_khoa):
            cho.append("tên thư mục")
        for f in tm.iterdir():
            if f.is_file() and (f.name in FILE_DO or f.name.endswith("-content.md")):
                noi = chuan(f.read_text(encoding="utf-8", errors="ignore"))
                trung = [k for k in tu_khoa if co(k, noi)]
                if trung:
                    cho.append(f"{f.name} có «{', '.join(trung)}»")
        if cho:
            kq.append((tm, cho))
    return kq


def do_so(kenh, tu_khoa, cau):
    """Sổ video (so-video.csv, ghi bằng ghi_so_video.py). Dò hai chiều: từ khóa mới nằm trong chủ đề hoặc từ khóa cũ,
    và từ khóa cũ nằm trong câu yêu cầu (người dẫn gõ cả câu, có thể chứa tên công cụ cũ)."""
    import csv
    f = kenh / "so-video.csv"
    if not f.exists():
        print(f"⚠ Chưa có sổ video {f.name}: ghi bằng ghi_so_video.py sau mỗi lần bàn giao.")
        return []
    kq = []
    with open(f, encoding="utf-8-sig", newline="") as g:
        for x in csv.DictReader(g):
            cu = [chuan(t) for t in x.get("tu_khoa", "").split(";") if len(chuan(t)) >= 3 and chuan(t) not in CHUNG]
            noi = chuan(x.get("chu_de", "") + " " + x.get("tu_khoa", ""))
            trung = [k for k in tu_khoa if co(k, noi)] + [k for k in cu if any(co(k, c) for c in cau)]
            if trung:
                kq.append((x, sorted(set(trung))))
    return kq


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    kenh = Path(sys.argv[1])
    tu_khoa = [chuan(x) for x in sys.argv[2:] if len(chuan(x)) >= 3 and chuan(x) not in CHUNG]
    if not tu_khoa:
        sys.exit("✘ Từ khóa quá ngắn (cần ít nhất 3 ký tự), dễ khớp nhầm.")
    so = do_so(kenh, tu_khoa, [chuan(x) for x in sys.argv[2:]])
    gap = [("dự án", tm, cho) for tm, cho in do(kenh / "du-an", tu_khoa)]
    for ma, ten in TRANG_THAI.items():
        gap += [(ten, tm, cho) for tm, cho in do(kenh / "BAI-DANG" / ma, tu_khoa)]
    if not (gap or so):
        print("✔ Chưa có video nào về chủ đề này (đã dò sổ video, du-an, BAI-DANG).")
        return
    print("⚠ CHỦ ĐỀ NÀY ĐÃ CÓ VIDEO, nhắc người dẫn trước khi làm:")
    for x, trung in so:
        print(f"  [sổ video] {x['du_an']} ({x['ngay_xong']}): {x['chu_de']} · khớp «{', '.join(trung)}»")
    for loai, tm, cho in gap:
        print(f"  [{loai}] {tm.name}: {'; '.join(cho)}")
    sys.exit(1)


if __name__ == "__main__":
    main()
