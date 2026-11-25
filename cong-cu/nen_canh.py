"""Bước 2: nén cảnh mới theo chuẩn kho (giống hệt cách nén 226 cảnh bản 1).

Chuẩn: H.264 (libx264) CRF 22 preset slow, 720x1280 (tự phóng và cắt giữa về 9:16), 24 hình/giây,
GOP 48, bỏ tiếng, nhãn màu bt709, faststart. SSIM so với gốc phải >= 0,97; thiếu thì nén lại CRF 20;
vẫn thiếu thì ghi CAN_XEM. Bản nén to hơn gốc thì giữ gốc (chỉ bỏ tiếng).

Chạy (máy vẫn dùng được trong lúc nén vì tiến trình để mức ưu tiên thấp):
    python -I -X utf8 cong-cu/nen_canh.py                     # nén mọi .mp4 trong _kho-nang/nguon-moi/canh
    python -I -X utf8 cong-cu/nen_canh.py <thu_muc_nguon> --luong 4

Đầu ra: _kho-nang/nguon-moi/_da-nen/
    <ten-goc>.mp4           bản đã nén
    5khung/<ten-goc>.jpg    ảnh 5 khung (5% · 27,5% · 50% · 72,5% · 95%) để gắn nhãn
    bao-cao-nen.csv         tep_goc, kb_goc, kb_moi, ty_le, ssim, giay, ghi_chu
Không xóa, không sửa tệp gốc.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chung import NGUON_MOI, ffprobe_giay  # noqa: E402

KHUNG = 'scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24'
UU_TIEN = 0x00004000 if os.name == 'nt' else 0  # BELOW_NORMAL_PRIORITY_CLASS


def chay(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                          stdin=subprocess.DEVNULL, creationflags=UU_TIEN)


def nen(src, dst, crf, luong):
    r = chay(['ffmpeg', '-y', '-i', str(src), '-map', '0:v:0', '-an', '-vf', KHUNG,
              '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-threads', str(luong),
              '-profile:v', 'high', '-level', '4.0', '-pix_fmt', 'yuv420p',
              '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
              '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
              '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709',
              '-movflags', '+faststart', str(dst)])
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])


def ssim(out, src):
    r = chay(['ffmpeg', '-i', str(out), '-i', str(src), '-lavfi', '[1:v]%s[g];[0:v][g]ssim' % KHUNG, '-f', 'null', '-'])
    m = re.findall(r'All:([0-9.]+)', r.stderr)
    return float(m[-1]) if m else 0.0


def nam_khung(mp4, jpg):
    d = ffprobe_giay(mp4)
    a = []
    for p in (0.05, 0.275, 0.5, 0.725, 0.95):
        a += ['-ss', '%.2f' % (d * p), '-i', str(mp4)]
    fc = ';'.join('[%d:v]scale=216:384,pad=224:384:4:0:white[v%d]' % (i, i) for i in range(5)) + ';' + ''.join('[v%d]' % i for i in range(5)) + 'hstack=5'
    chay(['ffmpeg', '-v', 'error', '-y'] + a + ['-filter_complex', fc, '-frames:v', '1', str(jpg)])


def lam_mot(src, ra, luong):
    dst = ra / src.name
    ghi = []
    nen(src, dst, 22, luong)
    s = ssim(dst, src)
    if s < 0.97:
        nen(src, dst, 20, luong)
        s = ssim(dst, src)
        ghi.append('crf20' if s >= 0.97 else 'CAN_XEM')
    kg, km = src.stat().st_size, dst.stat().st_size
    if km > kg:
        ghi.append('ban_nen_to_hon_goc')
    nam_khung(dst, ra / '5khung' / (src.stem + '.jpg'))
    return [src.name, round(kg / 1024), round(km / 1024), '%.0f%%' % (100 * km / kg), '%.4f' % s,
            '%.2f' % ffprobe_giay(dst), ';'.join(ghi)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nguon', nargs='?', default=str(NGUON_MOI / 'canh'))
    ap.add_argument('--luong', type=int, default=max(1, (os.cpu_count() or 4) // 2), help='số luồng mỗi tệp (mặc định nửa số lõi)')
    a = ap.parse_args()
    ds = sorted(Path(a.nguon).glob('*.mp4'))
    if not ds:
        sys.exit('Không có .mp4 nào trong ' + a.nguon)
    ra = NGUON_MOI / '_da-nen'
    if ra.exists() and any(ra.glob('*.mp4')):
        sys.exit('DỪNG: %s còn tệp của lượt trước. Nhập kho xong (hoặc dọn) rồi mới nén lượt mới.' % ra)
    (ra / '5khung').mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(2) as ex:
        kq = list(ex.map(lambda p: lam_mot(p, ra, a.luong), ds))
    with open(ra / 'bao-cao-nen.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tep_goc', 'kb_goc', 'kb_moi', 'ty_le', 'ssim', 'giay', 'ghi_chu'])
        w.writerows(kq)
    for r in kq:
        print(*r)
    print('Xong %d tệp. Cần xem lại: %s' % (len(kq), [r[0] for r in kq if 'CAN_XEM' in r[6]] or 'không'))


if __name__ == '__main__':
    main()
