"""Chuyển tệp vừa tải từ Muse về thư mục video, bỏ tiền tố, đổi webp → png.

  nhan_tai.py <thư mục video> --tien-to vNN- [--tai-ve ~/Downloads] [--vao boi-canh|kol|anh-kol|.]
Ảnh (.webp/.png/.jpg) vào thư mục --vao (mặc định: ảnh → anh-kol, video → thư mục video).
Không xóa gì ngoài tệp đã chuyển; trùng tên thì giữ tệp cũ, đặt tệp mới thêm -b, -c.
"""
import argparse, shutil, os
from pathlib import Path
from PIL import Image

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("thu_muc"); a.add_argument("--tien-to", required=True)
    a.add_argument("--tai-ve", default=os.environ.get("ND_TAI_VE", os.path.expanduser("~/Downloads"))); a.add_argument("--vao")
    x = a.parse_args(); d = Path(x.thu_muc)
    for f in sorted(Path(x.tai_ve).glob(x.tien_to + "*")):
        ten = f.name[len(x.tien_to):]
        anh = f.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg")
        dich = d / (x.vao or ("anh-kol" if anh else "."))
        dich.mkdir(parents=True, exist_ok=True)
        goc = Path(ten).stem; duoi = ".png" if anh else f.suffix
        ra = dich / (goc + duoi); k = 0
        while ra.exists():
            k += 1; ra = dich / f"{goc}-{'bcdefgh'[k - 1]}{duoi}"
        if anh:
            Image.open(f).convert("RGB").save(ra); f.unlink()
        else:
            shutil.move(str(f), ra)
        print(f.name, "→", ra)
