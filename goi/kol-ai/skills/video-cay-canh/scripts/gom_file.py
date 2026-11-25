"""Gom ảnh và clip tải từ Muse về đúng thư mục dự án, đặt đúng tên.

    python gom_file.py <du_an> anh   [--tu <thu_muc_tai_ve>]
    python gom_file.py <du_an> clip  [--tu <thu_muc_tai_ve>] [--mau "lo*.mp4"]

anh : tìm <ma>-<ten>.webp/.png/.jpg trong thư mục tải về, đổi sang JPG chất lượng cao vào <du_an>/anh/.
clip: lấy các mp4 khớp mẫu (mặc định: mp4 mới hơn ảnh), so khung đầu với từng ảnh thiết kế để biết clip
      nào của cảnh nào (Muse không giữ tên khi tải), chép vào <du_an>/clip/<ma>-<ten>.mp4.
      Báo ✘ nếu hai clip cùng khớp một cảnh hoặc độ chênh không rõ.
"""
import argparse
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import can, chay, doc_cau_hinh, doc_du_an, in_utf8, ten_canh  # noqa: E402


def nho(path, video=False):
    cmd = [can("ffmpeg"), "-v", "error"] + (["-ss", "0.05"] if video else []) + [
        "-i", str(path), "-frames:v", "1", "-vf", "scale=36:64,format=gray", "-f", "rawvideo", "-"]
    b = chay(cmd, capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).astype(float)
    return a if a.size == 36 * 64 else None


def main():
    in_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("loai", choices=["anh", "clip"])
    ap.add_argument("--tu")
    ap.add_argument("--mau")
    a = ap.parse_args()
    d, da = doc_du_an(a.du_an)
    cfg, _ = doc_cau_hinh()
    tu = Path(a.tu or (cfg or {}).get("thu_muc_tai_ve", str(Path.home() / "Downloads")))
    canh = [ten_canh(c) for c in da["canh"]]

    if a.loai == "anh":
        ra = d / "anh"
        ra.mkdir(exist_ok=True)
        thieu = []
        for t in canh:
            ung = [p for ext in ("webp", "png", "jpg", "jpeg") for p in tu.glob(f"{t}*.{ext}")]
            if not ung:
                thieu.append(t)
                continue
            src = max(ung, key=lambda p: p.stat().st_mtime)
            chay([can("ffmpeg"), "-v", "error", "-y", "-i", str(src), "-q:v", "2", str(ra / f"{t}.jpg")], check=True)
            goc = d / "tai-ve-goc"
            goc.mkdir(exist_ok=True)
            shutil.move(str(src), goc / src.name)  # chuyển hẳn khỏi thư mục tải về, không để bừa
            print(f"✔ {t} ← {src.name}")
        if thieu:
            print("✘ Chưa thấy ảnh: " + ", ".join(thieu))
            sys.exit(1)
        return

    anh = {t: nho(d / "anh" / f"{t}.jpg") for t in canh}
    if any(v is None for v in anh.values()):
        sys.exit("✘ Thiếu ảnh thiết kế trong anh/. Chạy bước 'anh' trước.")
    moc = min((d / "anh" / f"{t}.jpg").stat().st_mtime for t in canh)
    clips = sorted(tu.glob(a.mau)) if a.mau else sorted(p for p in tu.glob("*.mp4") if p.stat().st_mtime > moc)
    if not clips:
        sys.exit(f"✘ Không thấy clip mp4 nào trong {tu}")
    ra = d / "clip"
    ra.mkdir(exist_ok=True)
    da_khop, nghi = {}, []
    for f in clips:
        v = nho(f, True)
        if v is None:
            print(f"  bỏ qua {f.name}: không đọc được")
            continue
        diem = sorted((float(np.mean((v - m) ** 2)), t) for t, m in anh.items())
        t, s1, s2 = diem[0][1], diem[0][0], diem[1][0]
        if s2 < s1 * 1.5:
            nghi.append(f"{f.name}: không rõ là {t} hay {diem[1][1]}")
            continue
        if t in da_khop:
            nghi.append(f"{f.name} và {da_khop[t]} cùng khớp {t} (giữ bản mới hơn)")
        da_khop[t] = f.name
        shutil.copy(f, ra / f"{t}.mp4")
        (d / "tai-ve-goc").mkdir(exist_ok=True)
        shutil.move(str(f), d / "tai-ve-goc" / f.name)  # chuyển hẳn khỏi thư mục tải về
        print(f"✔ {f.name} → {t}")
    thieu = [t for t in canh if t not in da_khop and not (ra / f"{t}.mp4").exists()]  # cảnh đã gom ở lượt trước thì không báo thiếu
    for x in nghi:
        print("✘", x)
    if thieu:
        print("✘ Chưa có clip: " + ", ".join(thieu))
    sys.exit(1 if thieu or nghi else 0)


if __name__ == "__main__":
    main()
