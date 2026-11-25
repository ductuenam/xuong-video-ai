"""Soi nhanh nhắm mắt: cắt cố định vùng mặt, 8 khung mỗi giây, ghép thành 1 trang.

Muse hay cho KOL nhắm mắt khi cười. Soi bảng khung toàn thân dễ bỏ sót vì mắt quá nhỏ;
trang này phóng to riêng vùng mắt, ghi mốc giây, nên chỉ cần lướt một lần là thấy
đoạn nhắm mắt nằm ở giây nào để chọn bản khác hoặc đặt cảnh cận che.

Dùng: python soi_mat.py canh1.mp4 [canh2.mp4 ...] --out-dir soi-mat [--fps 8]
Ra: soi-mat/<ten>-mat.jpg, mỗi ô ghi giây. Vùng mặt cắt cố định theo tỉ lệ khung
(--mx, --my, mặc định hợp với ảnh goc-tren.png do cat_anh.py cắt, máy đứng yên). Đã thử bám mặt bằng khớp mẫu
nhưng lúc nhắm mắt khung trôi lên tóc, nên giữ cắt cố định. Cảnh xoay mặt ra khỏi vùng
thì soi bằng bảng khung thường.
"""
import argparse
import sys
import os

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out-dir", default="soi-mat")
    ap.add_argument("--fps", type=float, default=8)
    ap.add_argument("--cot", type=int, default=8)
    ap.add_argument("--mx", type=float, nargs=2, default=[0.30, 0.70], help="vung mat theo chieu ngang (ti le khung)")
    ap.add_argument("--my", type=float, nargs=2, default=[0.11, 0.31], help="vung mat theo chieu doc (ti le khung)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(a.out_dir, exist_ok=True)
    W, H = 220, 200
    for v in a.videos:
        cap = cv2.VideoCapture(v)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        buoc = max(1, round(fps / a.fps))
        o, i = [], 0
        while i < n:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, f = cap.read()
            if not ok:
                break
            fh, fw = f.shape[:2]
            band = f[int(fh * a.my[0]):int(fh * a.my[1]), int(fw * a.mx[0]):int(fw * a.mx[1])]
            band = cv2.resize(band, (W, H), interpolation=cv2.INTER_CUBIC)
            nhan = f"{i / fps:.2f}"
            cv2.rectangle(band, (0, 0), (92, 20), (0, 0, 0), -1)
            cv2.putText(band, nhan, (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            o.append(band)
            i += buoc
        while len(o) % a.cot:
            o.append(np.zeros((H, W, 3), np.uint8))
        hang = [np.hstack(o[k:k + a.cot]) for k in range(0, len(o), a.cot)]
        ra = os.path.join(a.out_dir, os.path.splitext(os.path.basename(v))[0] + "-mat.jpg")
        cv2.imwrite(ra, np.vstack(hang), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("Xong", ra)


if __name__ == "__main__":
    main()
